#!/usr/bin/env python3
"""Apply the candidate determinism fixes to a *copy* of the planegcs sources.

Each patch removes one place where planegcs lets the *pointer value* of a
parameter (or the heap layout generally) decide an ordering:

  1. SubSystem::initialize - the subsystem's unknown vector is built with
     std::set_intersection over std::set<double*>, i.e. sorted by address.
     This sets the Jacobian column order.
  2. SubSystem::initialize - the per-constraint parameter sets used to build
     c2p/p2c are std::set<double*>, so gradient accumulation order varies.
  3. System::solve(subsysA, subsysB) - the combined unknown vector is built
     with std::sort + std::set_union on pointers.
  4. SubSystem::redirectParams - values are copied into pvals by iterating
     pmap (std::map<double*,double*>).  After an exact-equality reduction two
     originals share one pvals slot, so *last write wins* - and which one is
     last depends on the heap addresses.  This one is not just rounding: it
     changes the starting value of the merged unknown.

Usage: patch_planegcs.py <srcdir> <n-patches>
"""

import sys
from pathlib import Path


def sub(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, f"pattern not found exactly once: {old[:60]!r}"
    return text.replace(old, new)


def patch_subsystem_order(srcdir: Path) -> None:
    p = srcdir / "SubSystem.cpp"
    src = sub(
        p.read_text(),
        "        std::set_intersection(s1.begin(), s1.end(), s2.begin(), s2.end(), std::back_inserter(tmpplist));",
        """        // PATCHED: keep the caller's parameter order.
        for (VEC_pD::const_iterator p = params.begin(); p != params.end(); ++p) {
            if (s2.count(*p)) {
                tmpplist.push_back(*p);
            }
        }
        (void)s1;""",
    )
    p.write_text(src)


def patch_constr_params(srcdir: Path) -> None:
    p = srcdir / "SubSystem.cpp"
    src = p.read_text()
    src = sub(
        src,
        "        SET_pD constr_params;",
        "        VEC_pD constr_params;  // PATCHED: insertion order, deduped",
    )
    src = sub(
        src,
        "                constr_params.insert(pmapfind->second);",
        """                if (std::find(constr_params.begin(), constr_params.end(), pmapfind->second)
                    == constr_params.end()) {
                    constr_params.push_back(pmapfind->second);
                }""",
    )
    src = sub(
        src,
        "        for (SET_pD::const_iterator p = constr_params.begin(); p != constr_params.end(); ++p) {",
        "        for (VEC_pD::const_iterator p = constr_params.begin(); p != constr_params.end(); ++p) {",
    )
    if "#include <algorithm>" not in src:
        src = "#include <algorithm>\n" + src
    p.write_text(src)


def patch_solve_ab(srcdir: Path) -> None:
    p = srcdir / "GCS.cpp"
    src = sub(
        p.read_text(),
        """        std::sort(plistA.begin(), plistA.end());
        std::sort(plistB.begin(), plistB.end());

        VEC_pD::const_iterator it;
        it = std::set_union(plistA.begin(), plistA.end(), plistB.begin(), plistB.end(), plistAB.begin());
        plistAB.resize(it - plistAB.begin());""",
        """        // PATCHED: order-preserving union.
        plistAB.clear();
        SET_pD seen;
        for (const auto& p : plistA) {
            if (seen.insert(p).second) {
                plistAB.push_back(p);
            }
        }
        for (const auto& p : plistB) {
            if (seen.insert(p).second) {
                plistAB.push_back(p);
            }
        }""",
    )
    p.write_text(src)


def patch_redirect_params(srcdir: Path) -> None:
    h = srcdir / "SubSystem.h"
    h.write_text(
        sub(
            h.read_text(),
            "    MAP_pD_pD pmap;  // redirection map from the original parameters to pvals",
            """    MAP_pD_pD pmap;  // redirection map from the original parameters to pvals
    VEC_pD pmap_order;  // PATCHED: insertion order of the pmap keys""",
        )
    )
    p = srcdir / "SubSystem.cpp"
    src = p.read_text()
    src = sub(
        src,
        "    pmap.clear();",
        """    pmap.clear();
    pmap_order = tmpplist;  // PATCHED""",
    )
    src = sub(
        src,
        """    // copying values to pvals
    for (MAP_pD_pD::const_iterator p = pmap.begin(); p != pmap.end(); ++p) {""",
        """    // copying values to pvals -- PATCHED: insertion order, not pointer order
    for (VEC_pD::const_iterator q = pmap_order.begin(); q != pmap_order.end(); ++q) {
        MAP_pD_pD::const_iterator p = pmap.find(*q);
        if (p == pmap.end()) {
            continue;
        }""",
    )
    p.write_text(src)


PATCHES = [
    patch_subsystem_order,
    patch_constr_params,
    patch_solve_ab,
    patch_redirect_params,
]


def main() -> None:
    srcdir = Path(sys.argv[1])
    n = int(sys.argv[2])
    assert 0 <= n <= len(PATCHES)
    for patch in PATCHES[:n]:
        patch(srcdir)
    print(f"applied {n} patch(es) to {srcdir}")


if __name__ == "__main__":
    main()
