"""Tests verifying documented arc direction conventions.

Angles are measured in radians, counterclockwise (CCW) from the positive
x-axis.  Arc sweep is ``end_angle - start_angle``: positive = CCW,
negative = CW.
"""

import math

import pytest

from planegcs import Sketch, SolveStatus

TOL = 1e-9


def test_ccw_quarter_arc() -> None:
    """A 90° CCW arc from 0° to 90° goes from (r,0) to (0,r)."""
    s = Sketch()
    center = s.add_fixed_point(0, 0)
    start = s.add_point(1, 0)
    end = s.add_point(0, 1)
    arc = s.add_arc_cse(center, start, end, radius=1.0, start_angle=0, end_angle=math.pi / 2)

    assert s.solve() == SolveStatus.Success
    info = s.get_arc(arc)

    assert info.start_angle == pytest.approx(0.0, abs=TOL)
    assert info.end_angle == pytest.approx(math.pi / 2, abs=TOL)
    assert info.start_point[0] == pytest.approx(1.0, abs=TOL)
    assert info.start_point[1] == pytest.approx(0.0, abs=TOL)
    assert info.end_point[0] == pytest.approx(0.0, abs=TOL)
    assert info.end_point[1] == pytest.approx(1.0, abs=TOL)
    assert info.arc_size == pytest.approx(math.pi / 2, abs=TOL)


def test_ccw_270_arc() -> None:
    """A 270° CCW arc from (r,0) to (0,-r) the long way around."""
    s = Sketch()
    center = s.add_fixed_point(0, 0)
    start = s.add_point(1, 0)
    end = s.add_point(0, -1)
    arc = s.add_arc_cse(center, start, end, radius=1.0, start_angle=0, end_angle=3 * math.pi / 2)

    assert s.solve() == SolveStatus.Success
    info = s.get_arc(arc)

    assert info.arc_size == pytest.approx(3 * math.pi / 2, abs=TOL)
    assert info.start_point[0] == pytest.approx(1.0, abs=TOL)
    assert info.end_point[1] == pytest.approx(-1.0, abs=TOL)


def test_cw_quarter_arc_negative_sweep() -> None:
    """A -90° sweep (CW arc) from 0° to -90°.

    Start at (r, 0), end at (0, -r), going clockwise.
    """
    s = Sketch()
    center = s.add_fixed_point(0, 0)
    start = s.add_point(1, 0)
    end = s.add_point(0, -1)
    arc = s.add_arc_cse(center, start, end, radius=1.0, start_angle=0, end_angle=-math.pi / 2)

    assert s.solve() == SolveStatus.Success
    info = s.get_arc(arc)

    assert info.start_angle == pytest.approx(0.0, abs=TOL)
    assert info.end_angle == pytest.approx(-math.pi / 2, abs=TOL)
    assert info.arc_size == pytest.approx(-math.pi / 2, abs=TOL)
    assert info.end_point[0] == pytest.approx(0.0, abs=TOL)
    assert info.end_point[1] == pytest.approx(-1.0, abs=TOL)


def test_negative_start_angle() -> None:
    """An arc starting at -90° (bottom) going CCW to +90° (top)."""
    s = Sketch()
    center = s.add_fixed_point(0, 0)
    start = s.add_point(0, -1)
    end = s.add_point(0, 1)
    arc = s.add_arc_cse(
        center, start, end, radius=1.0, start_angle=-math.pi / 2, end_angle=math.pi / 2
    )

    assert s.solve() == SolveStatus.Success
    info = s.get_arc(arc)

    assert info.start_angle == pytest.approx(-math.pi / 2, abs=TOL)
    assert info.end_angle == pytest.approx(math.pi / 2, abs=TOL)
    assert info.arc_size == pytest.approx(math.pi, abs=TOL)
    assert info.start_point[1] == pytest.approx(-1.0, abs=TOL)
    assert info.end_point[1] == pytest.approx(1.0, abs=TOL)


def test_full_circle_arc() -> None:
    """A full-circle arc (0° to 360°)."""
    s = Sketch()
    center = s.add_fixed_point(0, 0)
    start = s.add_point(1, 0)
    end = s.add_point(1, 0)
    arc = s.add_arc_cse(center, start, end, radius=1.0, start_angle=0, end_angle=2 * math.pi)

    assert s.solve() == SolveStatus.Success
    info = s.get_arc(arc)

    assert info.arc_size == pytest.approx(2 * math.pi, abs=TOL)


def test_start_end_points_match_parametric_equation() -> None:
    """Start/end points equal center + r*(cos θ, sin θ)."""
    s = Sketch()
    cx, cy, r = 3.0, -2.0, 5.0
    sa, ea = math.pi / 6, 5 * math.pi / 4  # 30° to 225°
    center = s.add_fixed_point(cx, cy)
    sx = cx + r * math.cos(sa)
    sy = cy + r * math.sin(sa)
    ex = cx + r * math.cos(ea)
    ey = cy + r * math.sin(ea)
    start = s.add_point(sx, sy)
    end = s.add_point(ex, ey)
    arc = s.add_arc_cse(center, start, end, radius=r, start_angle=sa, end_angle=ea)

    assert s.solve() == SolveStatus.Success
    info = s.get_arc(arc)

    # Verify the parametric equation holds
    assert info.start_point[0] == pytest.approx(cx + r * math.cos(info.start_angle), abs=TOL)
    assert info.start_point[1] == pytest.approx(cy + r * math.sin(info.start_angle), abs=TOL)
    assert info.end_point[0] == pytest.approx(cx + r * math.cos(info.end_angle), abs=TOL)
    assert info.end_point[1] == pytest.approx(cy + r * math.sin(info.end_angle), abs=TOL)


def test_same_endpoints_different_sweeps() -> None:
    """Two arcs with same endpoints but different sweep directions.

    (r,0) to (0,-r) can be reached by:
      - 270° CCW (start=0, end=3π/2)
      - -90° CW  (start=0, end=-π/2)
    Both reach the same end point but represent different arcs.
    """
    # CCW version
    s1 = Sketch()
    c1 = s1.add_fixed_point(0, 0)
    p1 = s1.add_point(1, 0)
    p2 = s1.add_point(0, -1)
    arc1 = s1.add_arc_cse(c1, p1, p2, radius=1.0, start_angle=0, end_angle=3 * math.pi / 2)
    assert s1.solve() == SolveStatus.Success
    info1 = s1.get_arc(arc1)

    # CW version
    s2 = Sketch()
    c2 = s2.add_fixed_point(0, 0)
    p3 = s2.add_point(1, 0)
    p4 = s2.add_point(0, -1)
    arc2 = s2.add_arc_cse(c2, p3, p4, radius=1.0, start_angle=0, end_angle=-math.pi / 2)
    assert s2.solve() == SolveStatus.Success
    info2 = s2.get_arc(arc2)

    # Same end points
    assert info1.end_point[0] == pytest.approx(info2.end_point[0], abs=TOL)
    assert info1.end_point[1] == pytest.approx(info2.end_point[1], abs=TOL)

    # But different sweeps
    assert info1.arc_size == pytest.approx(3 * math.pi / 2, abs=TOL)
    assert info2.arc_size == pytest.approx(-math.pi / 2, abs=TOL)
