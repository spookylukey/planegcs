"""A sketch whose solution is sensitive to the solver's internal orderings.

An under-constrained closed polygon with an equal-length chain: it has many
equally valid solutions, so the tiniest perturbation of the Jacobian column
order lands the solver on a different one.  Mirrors the C++ harness in
tools/freecad_alloc_experiment/main.cpp.

Options exercise the different mechanisms described in
docs/freecad_nondeterminism.md:

* ``churn``     - unrelated allocations while the sketch is built, which is
                  what moves the parameters around on the heap.
* ``equal``     - ``equal`` constraints between parameters, which trigger
                  planegcs' exact-equality reduction (site 4: the merged
                  unknown is seeded by whichever parameter has the higher
                  address).
* ``recycle``   - add and then delete constraints, so that later constraint
                  objects reuse freed heap cells and their addresses no
                  longer follow creation order.
* ``redundant`` - extra, implied constraints, for testing the stability of
                  the redundancy diagnosis.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

from planegcs import PointId, Sketch


@dataclass
class Options:
    nsides: int = 100
    jitter: float = 0.3
    churn: int = 0
    equal: bool = False
    recycle: bool = False
    redundant: bool = False


def build(opts: Options) -> tuple[Sketch, list[PointId]]:
    ballast: list[object] = []

    def churn() -> None:
        if opts.churn:
            ballast.append([0.0] * (opts.churn % 23 + 1))
            ballast.append(bytearray(opts.churn % 97 + 1))

    s = Sketch()
    n = opts.nsides
    pts: list[PointId] = []
    for i in range(n):
        a = 2.0 * math.pi * i / n
        r = 10.0 + opts.jitter * ((i * 7919) % 13)
        pts.append(s.add_point(r * math.cos(a), r * math.sin(a)))
        churn()
    lines = [s.add_line(pts[i], pts[(i + 1) % n]) for i in range(n)]

    if opts.recycle:
        # Constraints that are created and dropped again, so that the real
        # constraints below land in recycled heap cells.
        doomed = [s.horizontal(lines[i]) for i in range(0, n, 3)]
        for tag in doomed:
            s.clear_by_tag(tag)

    for i in range(n):
        s.equal_length(lines[i], lines[(i + 1) % n])
        churn()
    s.coordinate_x(pts[0], s.add_fixed_param(10.0))
    s.coordinate_y(pts[0], s.add_fixed_param(0.0))
    s.horizontal(lines[0])
    for i in range(0, n - n // 2, 3):
        s.set_p2p_distance(pts[i], pts[i + n // 2], 19.0 + 0.5 * i)

    if opts.equal:
        # Exact-equality reductions between the x coordinates of opposite
        # corners (planegcs merges these into a single unknown).
        for i in range(0, n // 2, 5):
            x1, _ = s.get_point_param_ids(pts[i])
            x2, _ = s.get_point_param_ids(pts[i + n // 2])
            s.equal(x1, x2)

    if opts.redundant:
        for i in range(0, n, 2):
            s.equal_length(lines[i], lines[(i + 2) % n])
        s.set_p2p_distance(pts[0], pts[n // 2], 19.0)

    ballast.clear()
    return s, pts


def solve_result(opts: Options) -> list[float]:
    s, pts = build(opts)
    s.solve()
    coords: list[float] = []
    for p in pts:
        x, y = s.get_point(p)
        coords += [x, y]
    return coords


def diagnose_result(opts: Options) -> list[float]:
    s, _ = build(opts)
    d = s.diagnose()
    return (
        [float(d.dof)]
        + [float(t) for t in d.conflicting]
        + [-1.0]
        + [float(t) for t in d.redundant]
        + [-2.0]
        + [float(t) for t in d.partially_redundant]
    )


def digest(values: list[float]) -> str:
    h = hashlib.sha256()
    for v in values:
        h.update(f"{v:+.12e}".encode())
    return h.hexdigest()[:12]
