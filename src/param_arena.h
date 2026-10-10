#ifndef PLANEGCS_PARAM_ARENA_H
#define PLANEGCS_PARAM_ARENA_H

// ── Monotonic, pointer-stable storage for solver parameters ──────────
//
// Why this exists
// ---------------
// PlaneGCS orders several of its internal containers by the *address* of a
// parameter (`std::set<double*>`, `std::map<double*, ...>`, `std::sort` over
// `VEC_pD`); see docs/freecad_nondeterminism.md.  Those orderings decide the
// Jacobian column order, the gradient accumulation order and - after an
// equality reduction - which of two merged parameters seeds the shared
// unknown.  So the solution the solver lands on depends on where the
// parameters happen to sit in memory.
//
// We do not want to patch the vendored solver, so instead we remove the
// ambiguity from the input side: if parameter addresses increase strictly
// with declaration order, then every address-ordered container in the solver
// is in declaration order too.  That is both deterministic and the order the
// caller would expect.
//
// A `std::vector<double>` is contiguous but moves its elements when it grows;
// a `std::deque<double>` is pointer-stable but its chunks can land in any
// order on the heap (that is exactly the bug we saw).  So we reserve a large
// region of *address space* up front (no physical memory, no commit charge)
// and hand out slots from it with a bump pointer, committing more pages as
// needed.  Allocation is O(1), nothing ever moves, and addresses are strictly
// increasing.
//
// Parameters are never individually freed - the API only ever adds geometry
// and constraints, and `clear()` resets the whole arena - so a bump allocator
// is all that is needed.

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <new>
#include <stdexcept>
#include <string>
#include <vector>

#if defined(_WIN32)
#include <windows.h>
#else
#include <sys/mman.h>
#include <unistd.h>
#endif

namespace planegcs_wrapper {

class ParamArena {
public:
    // Address space reserved for the first block.  8.4M parameters (~4.2M
    // points) on 64-bit; nothing is committed until it is used.
    static constexpr std::size_t kDefaultReserveBytes =
        sizeof(void*) >= 8 ? (std::size_t(64) << 20) : (std::size_t(8) << 20);
    // Pages are committed in steps of this size, to keep the number of
    // kernel-side mapping records small.
    static constexpr std::size_t kCommitStep = std::size_t(256) << 10;

    // `reserve_bytes` is address space only - it is not committed until it
    // is used.  Mainly a hook for tests that want to force the arena to grow.
    explicit ParamArena(std::size_t reserve_bytes = kDefaultReserveBytes)
        : first_reserve_bytes_(reserve_bytes < kCommitStep ? kCommitStep : reserve_bytes) {}

    ~ParamArena() {
        for (Block& b : blocks_) {
            release(b);
        }
    }

    ParamArena(const ParamArena&) = delete;
    ParamArena& operator=(const ParamArena&) = delete;

    // Append a parameter and return its stable address.  The returned pointer
    // is strictly greater than every pointer returned before it (unless
    // `monotonic()` is false, see below).
    double* push_back(double value) {
        if (blocks_.empty() || blocks_.back().used == blocks_.back().slots) {
            add_block();
        }
        Block& b = blocks_.back();
        if ((b.used + 1) * sizeof(double) > b.committed) {
            commit(b, (b.used + 1) * sizeof(double));
        }
        double* p = b.base + b.used;
        ++b.used;
        *p = value;
        ++size_;
        return p;
    }

    std::size_t size() const { return size_; }

    double& operator[](std::size_t index) { return *slot(index); }
    const double& operator[](std::size_t index) const { return *slot(index); }

    double* ptr(std::size_t index) { return slot(index); }

    // Drop every parameter, keeping the reservation for reuse.
    void clear() {
        // Keep only the first block, so that reuse starts from a single
        // contiguous (and therefore trivially monotonic) region again.
        for (std::size_t i = 1; i < blocks_.size(); ++i) {
            release(blocks_[i]);
        }
        blocks_.resize(blocks_.empty() ? 0 : 1);
        if (!blocks_.empty()) {
            blocks_[0].used = 0;
        }
        size_ = 0;
        monotonic_ = true;
    }

    // True if every parameter address is greater than the previous one, which
    // is what makes the solver's address-ordered containers deterministic.
    // Only ever false if the arena had to grow beyond its reservation *and*
    // the operating system refused to place the new region above the old one.
    bool monotonic() const { return monotonic_; }

private:
    struct Block {
        double* base = nullptr;
        std::size_t slots = 0;      // capacity, in parameters, of the reservation
        std::size_t committed = 0;  // bytes backed by readable/writable pages
        std::size_t used = 0;       // parameters handed out
        std::size_t first_index = 0;
    };

    double* slot(std::size_t index) const {
        auto block = std::find_if(blocks_.begin(), blocks_.end(), [index](const Block& b) {
            return index < b.first_index + b.used;
        });
        if (block != blocks_.end()) {
            return block->base + (index - block->first_index);
        }
        throw std::out_of_range("ParamArena: index " + std::to_string(index) +
                                " out of range");
    }

    void add_block() {
        std::size_t reserve_bytes = first_reserve_bytes_;
        void* hint = nullptr;
        if (!blocks_.empty()) {
            const Block& last = blocks_.back();
            // Grow geometrically, and ask for the new region to sit directly
            // above the old one so that addresses stay monotonic.
            reserve_bytes = last.slots * sizeof(double) * 2;
            hint = last.base + last.slots;
        }
        Block b;
        if (hint != nullptr) {
            // Linux (and Windows) hand out successive mappings *below* the
            // previous ones, so simply asking for the next address usually
            // fails - the space immediately above us is already taken.  Probe
            // upwards for a free gap instead; anything above the previous
            // block keeps the addresses monotonic.
            static const std::size_t kProbeGaps[] = {
                0,
                std::size_t(1) << 20,   // 1 MiB
                std::size_t(1) << 24,   // 16 MiB
                std::size_t(1) << 28,   // 256 MiB
                std::size_t(1) << 32,   // 4 GiB
                std::size_t(1) << 36,   // 64 GiB
                std::size_t(1) << 40,   // 1 TiB
            };
            for (std::size_t gap : kProbeGaps) {
                if (sizeof(void*) < 8 && gap >= (std::size_t(1) << 28)) {
                    break;
                }
                b.base = reserve(reserve_bytes, static_cast<char*>(hint) + gap);
                if (b.base != nullptr) {
                    break;
                }
            }
        }
        if (b.base == nullptr) {
            b.base = reserve(reserve_bytes, nullptr);
        }
        if (b.base == nullptr) {
            throw std::bad_alloc();
        }
        b.slots = reserve_bytes / sizeof(double);
        b.first_index = size_;
        if (!blocks_.empty() && b.base < blocks_.back().base + blocks_.back().used) {
            // Best effort only: we could not get a higher address, so the
            // solver's address-ordered containers are no longer in
            // declaration order.  Results stay self-consistent within a run
            // but may differ between runs.
            monotonic_ = false;
        }
        blocks_.push_back(b);
    }

    void commit(Block& b, std::size_t needed) {
        std::size_t target = ((needed + kCommitStep - 1) / kCommitStep) * kCommitStep;
        if (target > b.slots * sizeof(double)) {
            target = b.slots * sizeof(double);
        }
        char* from = reinterpret_cast<char*>(b.base) + b.committed;
        if (!commit_range(from, target - b.committed)) {
            throw std::bad_alloc();
        }
        b.committed = target;
    }

    // ── Platform layer ────────────────────────────────────────────────
    // Reserve address space without committing memory, then commit lazily.

    static double* reserve(std::size_t bytes, void* hint) {
#if defined(_WIN32)
        void* p = VirtualAlloc(hint, bytes, MEM_RESERVE, PAGE_NOACCESS);
        return static_cast<double*>(p);
#else
        int flags = MAP_PRIVATE | MAP_ANONYMOUS;
#if defined(MAP_NORESERVE)
        flags |= MAP_NORESERVE;
#endif
#if defined(MAP_FIXED_NOREPLACE)
        if (hint != nullptr) {
            flags |= MAP_FIXED_NOREPLACE;
        }
#endif
        void* p = mmap(hint, bytes, PROT_NONE, flags, -1, 0);
        if (p == MAP_FAILED) {
            return nullptr;
        }
        if (hint != nullptr && p != hint) {
            // The kernel ignored the hint; reject rather than silently
            // breaking monotonicity, the caller retries without a hint.
            munmap(p, bytes);
            return nullptr;
        }
        return static_cast<double*>(p);
#endif
    }

    static bool commit_range(char* addr, std::size_t bytes) {
        if (bytes == 0) {
            return true;
        }
#if defined(_WIN32)
        return VirtualAlloc(addr, bytes, MEM_COMMIT, PAGE_READWRITE) != nullptr;
#else
        return mprotect(addr, bytes, PROT_READ | PROT_WRITE) == 0;
#endif
    }

    static void release(Block& b) {
        if (b.base == nullptr) {
            return;
        }
#if defined(_WIN32)
        VirtualFree(b.base, 0, MEM_RELEASE);
#else
        munmap(b.base, b.slots * sizeof(double));
#endif
        b.base = nullptr;
    }

    std::size_t first_reserve_bytes_ = kDefaultReserveBytes;
    std::vector<Block> blocks_;
    std::size_t size_ = 0;
    bool monotonic_ = true;
};

}  // namespace planegcs_wrapper

#endif  // PLANEGCS_PARAM_ARENA_H
