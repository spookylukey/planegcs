"""The solver must give the same answer every time it is asked.

PlaneGCS orders its unknowns by the memory address of each parameter (see
docs/freecad_nondeterminism.md), so an under-constrained sketch used to settle
on a different - equally valid - solution depending on the heap layout.  The
wrapper allocates parameters from an arena with strictly increasing addresses,
which pins the ordering to declaration order.

These tests build a deliberately ordering-sensitive sketch repeatedly, with
unrelated allocations in between to move the heap around, and require the
answers to be bit-for-bit identical.
"""

from __future__ import annotations

import math

import pytest

from planegcs import Sketch

NSIDES = 60


def build_polygon(
    churn: int, *, with_equal: bool = False, recycle: bool = False
) -> tuple[Sketch, list[float]]:
    """An under-constrained equal-length polygon: many valid solutions."""
    ballast: list[object] = []
    s = Sketch()
    pts = []
    for i in range(NSIDES):
        a = 2.0 * math.pi * i / NSIDES
        r = 10.0 + 0.3 * ((i * 7919) % 13)
        pts.append(s.add_point(r * math.cos(a), r * math.sin(a)))
        ballast.append([0.0] * (churn % 29 + 1))
    lines = [s.add_line(pts[i], pts[(i + 1) % NSIDES]) for i in range(NSIDES)]

    if recycle:
        # Make later constraint objects land in recycled heap cells.
        for tag in [s.horizontal(line) for line in lines[::3]]:
            s.clear_by_tag(tag)

    for i in range(NSIDES):
        s.equal_length(lines[i], lines[(i + 1) % NSIDES])
    s.coordinate_x(pts[0], s.add_fixed_param(10.0))
    s.coordinate_y(pts[0], s.add_fixed_param(0.0))
    s.horizontal(lines[0])
    for i in range(0, NSIDES - NSIDES // 2, 3):
        s.set_p2p_distance(pts[i], pts[i + NSIDES // 2], 19.0 + 0.5 * i)

    if with_equal:
        # Exact-equality reductions: planegcs merges the two parameters into
        # one unknown, seeded by whichever had the higher address.
        for i in range(0, NSIDES // 2, 5):
            x1, _ = s.get_point_param_ids(pts[i])
            x2, _ = s.get_point_param_ids(pts[i + NSIDES // 2])
            s.equal(x1, x2)

    s.solve()
    del ballast
    return s, [c for p in pts for c in s.get_point(p)]


@pytest.mark.parametrize("with_equal", [False, True])
@pytest.mark.parametrize("recycle", [False, True])
def test_repeated_solves_identical(with_equal: bool, recycle: bool) -> None:
    results = [
        build_polygon(churn, with_equal=with_equal, recycle=recycle)[1]
        for churn in (0, 7, 101, 1013)
    ]
    for other in results[1:]:
        assert other == results[0]


def test_params_are_ordered() -> None:
    s, _ = build_polygon(0)
    assert s.results_are_reproducible


def test_clear_keeps_determinism() -> None:
    """Reusing a solver after clear() must give the same answer as a fresh one."""
    s, expected = build_polygon(0)
    s.clear()
    assert s.results_are_reproducible
    assert build_polygon(5)[1] == expected
