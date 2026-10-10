// Experiment: does FreeCAD's parameter allocation pattern expose the
// pointer-address-ordering non-determinism in PlaneGCS?
//
// FreeCAD's Sketcher (src/Mod/Sketcher/App/Sketch.cpp) stores every solver
// parameter as an individual heap allocation:
//
//     params.push_back(new double(p->getPoint().x));
//
// and frees them all in Sketch::clear() on every rebuild.  PlaneGCS's
// SubSystem::initialize() then re-orders the unknown vector by *pointer value*
// (std::set_intersection over SET_pD = std::set<double*>), so the Jacobian
// column order - and hence floating point rounding - depends on where malloc
// happened to put each double.
//
// This harness builds the same sketch repeatedly in one process, FreeCAD style,
// and reports:
//   * whether the address order of the parameters matches insertion order
//   * a hash of the solved coordinates
//
// Usage: freecad_alloc_experiment [cycles] [mode]
//   mode: freecad   - one `new double` per parameter (FreeCAD's Sketch.cpp)
//         interleaved - same, but with the small allocations FreeCAD
//                       interleaves (geometry objects, constraints, ...)
//         arena     - all parameters in one contiguous std::vector (control)

#include "GCS.h"
#include "Geo.h"

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <string>
#include <vector>
#include <algorithm>
#include <numeric>

namespace {

enum class Mode { FreeCAD, Interleaved, Arena };

// A FreeCAD-ish sketch: a closed polygon of N lines with coincident corners,
// one corner pinned, plus a few driving dimensions.  Enough constraints to make
// the solver iterate, so column ordering shows up in the last bits.
struct Sketch {
    Mode mode;
    std::vector<double*> Parameters;   // the unknowns, FreeCAD naming
    std::vector<double*> FixParameters;
    std::vector<GCS::Point> Points;
    std::vector<GCS::Line> Lines;
    std::vector<std::unique_ptr<std::string>> junk;  // interleaved allocations
    std::unique_ptr<std::vector<double>> arena;      // used by Mode::Arena
    size_t arena_next = 0;
    GCS::System GCSsys;

    explicit Sketch(Mode m) : mode(m) {}

    ~Sketch() { clear(); }

    void clear()
    {
        if (mode != Mode::Arena) {
            for (auto p : Parameters) {
                delete p;
            }
            for (auto p : FixParameters) {
                delete p;
            }
        }
        Parameters.clear();
        FixParameters.clear();
        Points.clear();
        Lines.clear();
        junk.clear();
        arena.reset();
        arena_next = 0;
        GCSsys.clear();
    }

    double* alloc(double v)
    {
        if (mode == Mode::Arena) {
            double* p = &(*arena)[arena_next++];
            *p = v;
            return p;
        }
        if (mode == Mode::Interleaved) {
            // FreeCAD allocates geometry copies, GCS::Point/Line objects,
            // Constraint objects etc. in between the `new double` calls.
            junk.push_back(std::make_unique<std::string>(32, 'x'));
        }
        return new double(v);
    }

    // Deliberately over-constrained: extra constraints that duplicate
    // information already implied, so diagnose() must pick which ones to call
    // redundant.
    bool redundant_scenario = false;

    void build(size_t nsides, double jitter)
    {
        clear();
        const size_t nparams = nsides * 2;
        if (mode == Mode::Arena) {
            arena = std::make_unique<std::vector<double>>(nparams + 8);
        }
        Points.reserve(nsides);
        Lines.reserve(nsides);

        // corner coordinates, roughly on a circle, deliberately perturbed
        for (size_t i = 0; i < nsides; ++i) {
            double a = 2.0 * 3.14159265358979 * double(i) / double(nsides);
            double r = 10.0 + jitter * double((i * 7919) % 13);
            double* x = alloc(r * std::cos(a));
            double* y = alloc(r * std::sin(a));
            Parameters.push_back(x);
            Parameters.push_back(y);
            Points.emplace_back(x, y);
        }
        for (size_t i = 0; i < nsides; ++i) {
            GCS::Line l;
            l.p1 = Points[i];
            l.p2 = Points[(i + 1) % nsides];
            Lines.push_back(l);
        }

        int tag = 0;
        // closed polygon: endpoints are shared by construction, so instead add
        // real geometric constraints that couple everything together.
        for (size_t i = 0; i < nsides; ++i) {
            GCSsys.addConstraintEqualLength(Lines[i], Lines[(i + 1) % nsides], ++tag);
        }
        // pin one corner
        double* px = alloc(10.0);
        double* py = alloc(0.0);
        FixParameters.push_back(px);
        FixParameters.push_back(py);
        GCSsys.addConstraintCoordinateX(Points[0], px, ++tag);
        GCSsys.addConstraintCoordinateY(Points[0], py, ++tag);
        // one side horizontal, and a few driving distances across the polygon
        GCSsys.addConstraintHorizontal(Lines[0], ++tag);
        for (size_t i = 0; i + nsides / 2 < nsides; i += 3) {
            double* d = alloc(19.0 + 0.5 * double(i));
            FixParameters.push_back(d);
            GCSsys.addConstraintP2PDistance(Points[i], Points[i + nsides / 2], d, ++tag);
        }
        if (redundant_scenario) {
            // every side the same length again (already implied by the
            // equal-length chain), plus a duplicated diagonal distance
            for (size_t i = 0; i < nsides; i += 2) {
                GCSsys.addConstraintEqualLength(Lines[i], Lines[(i + 2) % nsides], ++tag);
            }
            double* d = alloc(19.0);
            FixParameters.push_back(d);
            GCSsys.addConstraintP2PDistance(Points[0], Points[nsides / 2], d, ++tag);
        }
    }

    struct Diagnosis {
        int dofs;
        GCS::VEC_I conflicting, redundant, partiallyRedundant;
        std::vector<size_t> dependentParamIdx;  // insertion indices
    };

    Diagnosis diagnose()
    {
        GCSsys.declareUnknowns(Parameters);
        GCSsys.initSolution(GCS::DogLeg);
        GCSsys.diagnose(GCS::DogLeg);
        Diagnosis d;
        d.dofs = GCSsys.dofsNumber();
        GCSsys.getConflicting(d.conflicting);
        GCSsys.getRedundant(d.redundant);
        GCSsys.getPartiallyRedundant(d.partiallyRedundant);
        GCS::VEC_pD dep;
        GCSsys.getDependentParams(dep);
        for (auto p : dep) {
            auto it = std::find(Parameters.begin(), Parameters.end(), p);
            d.dependentParamIdx.push_back(size_t(it - Parameters.begin()));
        }
        return d;
    }

    int solve()
    {
        GCSsys.declareUnknowns(Parameters);
        GCSsys.initSolution(GCS::DogLeg);
        int ret = GCSsys.solve(true, GCS::DogLeg);
        GCSsys.applySolution();
        return ret;
    }

    // Is the parameter order the solver will derive from pointer values the
    // same as the order the caller handed them over in?
    bool address_order_matches_insertion() const
    {
        return std::is_sorted(Parameters.begin(), Parameters.end());
    }

    // Permutation of insertion indices when sorted by address (what the
    // SubSystem's unknown vector ends up looking like).
    std::vector<size_t> address_permutation() const
    {
        std::vector<size_t> idx(Parameters.size());
        std::iota(idx.begin(), idx.end(), 0);
        std::sort(idx.begin(), idx.end(), [&](size_t a, size_t b) {
            return Parameters[a] < Parameters[b];
        });
        return idx;
    }

    std::string result_hash() const
    {
        // FNV-1a over the exact bit patterns of the solution
        uint64_t h = 1469598103934665603ULL;
        for (auto p : Parameters) {
            uint64_t bits;
            std::memcpy(&bits, p, sizeof(bits));
            for (int i = 0; i < 8; ++i) {
                h ^= (bits >> (8 * i)) & 0xff;
                h *= 1099511628211ULL;
            }
        }
        char buf[32];
        std::snprintf(buf, sizeof(buf), "%012llx", (unsigned long long)(h & 0xffffffffffffULL));
        return buf;
    }
};

std::string perm_hash(const std::vector<size_t>& perm)
{
    uint64_t h = 1469598103934665603ULL;
    for (size_t v : perm) {
        h ^= v;
        h *= 1099511628211ULL;
    }
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%08llx", (unsigned long long)(h & 0xffffffffULL));
    return buf;
}

}  // namespace

std::string join(const GCS::VEC_I& v)
{
    std::string s;
    for (size_t i = 0; i < v.size(); ++i) {
        s += (i ? "," : "") + std::to_string(v[i]);
    }
    return s.empty() ? "-" : s;
}

std::string join(const std::vector<size_t>& v)
{
    std::vector<size_t> c = v;
    std::string s;
    for (size_t i = 0; i < c.size(); ++i) {
        s += (i ? "," : "") + std::to_string(c[i]);
    }
    return s.empty() ? "-" : s;
}

int main(int argc, char** argv)
{
    int cycles = argc > 1 ? std::atoi(argv[1]) : 10;
    std::string modestr = argc > 2 ? argv[2] : "freecad";
    std::string scenario = argc > 3 ? argv[3] : "solve";
    Mode mode = modestr == "arena"         ? Mode::Arena
        : modestr == "interleaved"         ? Mode::Interleaved
                                           : Mode::FreeCAD;

    printf("mode=%s scenario=%s cycles=%d\n", modestr.c_str(), scenario.c_str(), cycles);

    if (scenario == "diagnose") {
        std::vector<std::string> reports;
        printf("%-6s %-10s %-5s %-12s %-12s %-14s %s\n",
               "cycle", "addr-order", "dofs", "conflicting", "redundant", "partially-red", "dependent-params");
        for (int c = 0; c < cycles; ++c) {
            Sketch sk(mode);
            sk.redundant_scenario = true;
            sk.build(12, 0.03);
            bool sorted = sk.address_order_matches_insertion();
            auto d = sk.diagnose();
            std::string rep = std::to_string(d.dofs) + "|" + join(d.conflicting) + "|"
                + join(d.redundant) + "|" + join(d.partiallyRedundant) + "|"
                + join(d.dependentParamIdx);
            reports.push_back(rep);
            printf("%-6d %-10s %-5d %-12s %-12s %-14s %s\n",
                   c,
                   sorted ? "insertion" : "SHUFFLED",
                   d.dofs,
                   join(d.conflicting).c_str(),
                   join(d.redundant).c_str(),
                   join(d.partiallyRedundant).c_str(),
                   join(d.dependentParamIdx).substr(0, 40).c_str());
        }
        std::sort(reports.begin(), reports.end());
        reports.erase(std::unique(reports.begin(), reports.end()), reports.end());
        printf("distinct diagnoses: %zu\n", reports.size());
        return 0;
    }
    printf("%-6s %-10s %-9s %-14s %s\n", "cycle", "addr-order", "perm", "result-hash", "x[1]");

    std::vector<std::string> hashes;
    std::vector<std::string> perms;
    std::vector<double> minv, maxv;
    for (int c = 0; c < cycles; ++c) {
        Sketch sk(mode);
        sk.build(12, 0.03);
        auto perm = sk.address_permutation();
        bool sorted = sk.address_order_matches_insertion();
        sk.solve();
        if (minv.empty()) {
            for (auto p : sk.Parameters) {
                minv.push_back(*p);
                maxv.push_back(*p);
            }
        }
        else {
            for (size_t i = 0; i < sk.Parameters.size(); ++i) {
                minv[i] = std::min(minv[i], *sk.Parameters[i]);
                maxv[i] = std::max(maxv[i], *sk.Parameters[i]);
            }
        }
        std::string h = sk.result_hash();
        hashes.push_back(h);
        perms.push_back(perm_hash(perm));
        printf("%-6d %-10s %-9s %-14s %.17g\n",
               c,
               sorted ? "insertion" : "SHUFFLED",
               perms.back().c_str(),
               h.c_str(),
               *sk.Parameters[1]);
    }

    std::sort(hashes.begin(), hashes.end());
    hashes.erase(std::unique(hashes.begin(), hashes.end()), hashes.end());
    std::sort(perms.begin(), perms.end());
    perms.erase(std::unique(perms.begin(), perms.end()), perms.end());
    double spread = 0;
    for (size_t i = 0; i < minv.size(); ++i) {
        spread = std::max(spread, maxv[i] - minv[i]);
    }
    printf("distinct param orderings: %zu, distinct results: %zu, max coord spread: %.3g\n",
           perms.size(), hashes.size(), spread);
    return 0;
}
