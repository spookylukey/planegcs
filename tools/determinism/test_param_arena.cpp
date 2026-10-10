// Unit test for src/param_arena.h.
//
// The arena's growth path (more parameters than fit in the initial
// reservation) is not reachable from Python without allocating tens of
// millions of parameters, so it is tested here with a deliberately tiny
// reservation.
//
// Build and run with ./tools/determinism/run_arena_test.sh

#include "../../src/param_arena.h"

#include <cstdio>
#include <cstdlib>

using planegcs_wrapper::ParamArena;

static int failures = 0;

static void check(bool ok, const char* what) {
    if (!ok) {
        std::printf("FAIL: %s\n", what);
        ++failures;
    }
}

static void exercise(std::size_t reserve_bytes, std::size_t count) {
    ParamArena arena(reserve_bytes);
    std::vector<double*> ptrs;
    ptrs.reserve(count);
    for (std::size_t i = 0; i < count; ++i) {
        ptrs.push_back(arena.push_back(double(i)));
    }
    check(arena.size() == count, "size");
    check(arena.monotonic(), "addresses are monotonic");
    bool values_ok = true;
    bool ptrs_ok = true;
    bool index_ok = true;
    for (std::size_t i = 0; i < count; ++i) {
        values_ok = values_ok && *ptrs[i] == double(i);
        index_ok = index_ok && arena.ptr(i) == ptrs[i] && arena[i] == double(i);
        if (i > 0) {
            ptrs_ok = ptrs_ok && ptrs[i] > ptrs[i - 1];
        }
    }
    check(values_ok, "values survive growth");
    check(ptrs_ok, "pointers strictly increase");
    check(index_ok, "index lookup matches the returned pointers");

    // clear() releases the extra blocks and starts over.
    arena.clear();
    check(arena.size() == 0, "size after clear");
    double* first = arena.push_back(1.5);
    check(*first == 1.5 && arena.size() == 1, "reuse after clear");
    check(arena.monotonic(), "monotonic after clear");

    bool threw = false;
    try {
        (void)arena.ptr(99);
    }
    catch (const std::out_of_range&) {
        threw = true;
    }
    check(threw, "out of range index throws");
}

int main() {
    // One block, no growth.
    exercise(ParamArena::kDefaultReserveBytes, 10000);
    // Tiny reservation: forces several blocks, i.e. the growth path.
    exercise(1, 200000);
    if (failures == 0) {
        std::printf("param arena: all checks passed\n");
    }
    return failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
