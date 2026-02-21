"""Test that arc radius is variable when the parameter is not fixed.

Demonstrates that when the radius parameter is created with fixed=False,
the solver will adjust it to satisfy other constraints, yielding a
different radius than the initial value.
"""

import math

from planegcs import Sketch, SolveStatus


def _make_arc_between(s: Sketch, start_id, end_id, *, radius_guess: float, fixed: bool):
    """Create an arc between two existing points with a radius guess.

    Computes a plausible center from the geometry and returns the arc ID
    and radius ParamId.
    """
    sx, sy = s.get_point(start_id)
    ex, ey = s.get_point(end_id)

    dx, dy = ex - sx, ey - sy
    half_chord = math.sqrt(dx * dx + dy * dy) / 2.0
    r = max(abs(radius_guess), half_chord)
    h = math.sqrt(max(r * r - half_chord * half_chord, 0.0))

    mx, my = (sx + ex) / 2, (sy + ey) / 2
    perp_x, perp_y = -dy / (2 * half_chord), dx / (2 * half_chord)
    cx, cy = mx + h * perp_x, my + h * perp_y

    center = s.add_point(cx, cy)
    sa = math.atan2(sy - cy, sx - cx)
    ea = math.atan2(ey - cy, ex - cx)

    rad = s.add_param(r, fixed=fixed)
    arc = s.add_arc_cse(center, start_id, end_id, r, sa, ea)
    return arc, rad


def test_arc_radius_changes_when_variable():
    """Radius parameter created with fixed=False is adjusted by the solver.

    Setup: two lines meeting at a corner, with an arc connecting their
    endpoints.  Tangency constraints on both lines fully determine the
    arc radius, forcing it away from its initial value.

    The geometry:
      - A horizontal line from (0, 0) to (2, 0).
      - A vertical line from (4, 2) to (4, 5).
      - An arc from (2, 0) to (4, 2) tangent to both lines.

    For a quarter-circle arc tangent to both lines at a right-angle corner,
    with start point at (2, 0) and end point at (4, 2), the radius equals
    the inset distance from the corner: r = 2.
    """
    s = Sketch()

    # Horizontal segment from origin to (2, 0)
    ph1 = s.add_fixed_point(0, 0)
    ph2 = s.add_fixed_point(2, 0)
    h_line = s.add_line(ph1, ph2)
    s.horizontal(h_line)

    # Vertical segment from (4, 2) to (4, 5)
    pv1 = s.add_fixed_point(4, 2)
    pv2 = s.add_fixed_point(4, 5)
    v_line = s.add_line(pv1, pv2)
    s.vertical(v_line)

    # Arc from ph2=(2,0) to pv1=(4,2) with variable radius starting at 20
    arc, rad = _make_arc_between(s, ph2, pv1, radius_guess=20.0, fixed=False)

    # Tangency
    s.tangent_line_arc(h_line, arc)
    s.tangent_line_arc(v_line, arc)

    status = s.solve()
    assert status == SolveStatus.Success

    solved_radius = s.get_arc(arc).radius
    assert abs(solved_radius - 2.0) < 1e-3, f"Expected radius ~2.0 but got {solved_radius}"
    assert abs(solved_radius - 20.0) > 1.0, (
        f"Radius should have changed from 20.0 but got {solved_radius}"
    )


def test_arc_radius_fixed_stays_constant():
    """Contrast: when fixed=True (default), the radius does NOT change."""
    s = Sketch()

    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(6, 0)

    initial_radius = 10.0
    arc, rad = _make_arc_between(s, p1, p2, radius_guess=initial_radius, fixed=True)

    status = s.solve()
    assert status == SolveStatus.Success

    solved_radius = s.get_arc(arc).radius
    assert abs(solved_radius - initial_radius) < 1e-6, (
        f"Fixed radius should stay at {initial_radius} but got {solved_radius}"
    )


def test_arc_radius_adjusted_by_tangent_constraint():
    """Tangency to a line forces the solver to adjust a variable radius.

    A horizontal line at y=0 from x=-5 to x=5, with an arc from (5,0)
    to (0,5).  The arc is tangent to the line at its start point.
    Initial radius guess is 20 (way off); the solver must find r=5.
    """
    s = Sketch()

    # Horizontal line
    pl1 = s.add_fixed_point(-5, 0)
    pl2 = s.add_fixed_point(5, 0)
    line = s.add_line(pl1, pl2)
    s.horizontal(line)

    # Arc from (5,0) to (0,5)
    pa1 = s.add_fixed_point(5, 0)
    pa2 = s.add_fixed_point(0, 5)

    arc, rad = _make_arc_between(s, pa1, pa2, radius_guess=20.0, fixed=False)

    # Make pl2 and pa1 coincident
    s.coincident(pl2, pa1)

    # Tangency constraint
    s.tangent_line_arc(line, arc)

    status = s.solve()
    assert status == SolveStatus.Success

    solved_radius = s.get_arc(arc).radius
    assert abs(solved_radius - 5.0) < 1e-3, f"Expected radius ~5.0 but got {solved_radius}"
    assert abs(solved_radius - 20.0) > 1.0, "Radius should have changed significantly from 20.0"
