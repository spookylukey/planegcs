"""Tests covering Sketch methods that other test files don't exercise.

Targeted at:
- set_param (via Sketch wrapper)
- add_line_xy
- get_line
- get_circle
- add_arc / add_arc3p
- add_ellipse / get_ellipse
- equal (parameter equality)
"""

import math

from planegcs import Sketch, SolveStatus
from planegcs._planegcs import InternalAlignmentType


def test_set_param():
    """Sketch.set_param writes a new value to an existing parameter."""
    s = Sketch()
    p = s.add_param(1.0)
    assert abs(s.get_param(p) - 1.0) < 1e-12
    s.set_param(p, 99.0)
    assert abs(s.get_param(p) - 99.0) < 1e-12


def test_add_line_xy():
    """add_line_xy creates a line from raw coordinates."""
    s = Sketch()
    line = s.add_line_xy(0.0, 0.0, 5.0, 0.0)
    info = s.get_line(line)
    assert abs(info.p1[0] - 0.0) < 1e-8
    assert abs(info.p1[1] - 0.0) < 1e-8
    assert abs(info.p2[0] - 5.0) < 1e-8
    assert abs(info.p2[1] - 0.0) < 1e-8


def test_get_line():
    """get_line returns a LineInfo with correct endpoints."""
    s = Sketch()
    p1 = s.add_fixed_point(1.0, 2.0)
    p2 = s.add_fixed_point(3.0, 4.0)
    line = s.add_line(p1, p2)
    s.solve()
    info = s.get_line(line)
    assert abs(info.p1[0] - 1.0) < 1e-8
    assert abs(info.p1[1] - 2.0) < 1e-8
    assert abs(info.p2[0] - 3.0) < 1e-8
    assert abs(info.p2[1] - 4.0) < 1e-8


def test_get_circle():
    """get_circle returns a CircleInfo with center and radius."""
    s = Sketch()
    center = s.add_fixed_point(1.0, 2.0)
    c = s.add_circle(center, s.add_param(4.0))
    s.set_circle_radius(c, 5.0)
    s.solve()
    info = s.get_circle(c)
    assert abs(info.center[0] - 1.0) < 1e-6
    assert abs(info.center[1] - 2.0) < 1e-6
    assert abs(info.radius - 5.0) < 1e-6


def test_add_arc3p_and_arc_rules():
    """add_arc3p: start/end points match angles (arc rules applied automatically)."""
    s = Sketch()
    radius = 5.0
    start_angle = 0.0
    end_angle = math.pi / 2

    arc = s.add_arc3p((0.0, 0.0), radius, start_angle, end_angle)
    status = s.solve()
    assert status == SolveStatus.Success

    info = s.get_arc(arc)
    # Start point should be at (radius, 0)
    assert abs(info.start_point[0] - radius) < 1e-4
    assert abs(info.start_point[1] - 0.0) < 1e-4
    # End point should be at (0, radius)
    assert abs(info.end_point[0] - 0.0) < 1e-4
    assert abs(info.end_point[1] - radius) < 1e-4
    assert abs(info.radius - radius) < 1e-4
    assert abs(info.arc_size - (end_angle - start_angle)) < 1e-4


def test_arc_rules_python_method():
    """Exercise the Python-level arc_rules method directly.

    Builds an arc via the low-level add_arc (which calls arc_rules in C++),
    then adds a *second* arc_rules from Python to verify the method works.
    """
    s = Sketch()
    center = s.add_point(0.0, 0.0)
    sp = s.add_point(5.0, 0.0)
    ep = s.add_point(0.0, 5.0)
    r = s.add_param(5.0, fixed=False)
    sa = s.add_param(0.0, fixed=False)
    ea = s.add_param(math.pi / 2, fixed=False)
    arc = s.add_arc(center, sp, ep, r, sa, ea)
    # add_arc already calls arc_rules; calling again is redundant but exercises the method
    tag = s.arc_rules(arc)
    assert isinstance(tag, int)
    status = s.solve()
    assert status == SolveStatus.Success


def test_add_ellipse_and_get_ellipse():
    """add_ellipse + get_ellipse round-trips correctly."""
    s = Sketch()
    center = s.add_fixed_point(0.0, 0.0)
    focus1 = s.add_fixed_point(3.0, 0.0)
    radmin = 2.0

    eid = s.add_ellipse(center, focus1, radmin)
    s.solve()

    info = s.get_ellipse(eid)
    assert abs(info.center[0] - 0.0) < 1e-6
    assert abs(info.center[1] - 0.0) < 1e-6
    assert abs(info.focus1[0] - 3.0) < 1e-6
    assert abs(info.focus1[1] - 0.0) < 1e-6
    assert abs(info.radmin - radmin) < 1e-6


def test_equal_params():
    """equal() constrains two parameters to be the same value."""
    s = Sketch()
    p1 = s.add_param(3.0, fixed=True)
    p2 = s.add_param(10.0, fixed=False)
    s.equal(p1, p2)
    status = s.solve()
    assert status == SolveStatus.Success
    assert abs(s.get_param(p2) - 3.0) < 1e-8


def test_p2p_angle():
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(1, 0)
    angle = s.add_param(math.pi / 4, fixed=True)
    s.p2p_angle(p1, p2, angle)
    status = s.solve()
    assert status == SolveStatus.Success


def test_set_p2p_angle():
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(1, 0)
    s.set_p2p_angle(p1, p2, math.pi / 4)
    status = s.solve()
    assert status == SolveStatus.Success


def test_point_on_perp_bisector():
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(4, 0)
    line = s.add_line(p1, p2)
    pt = s.add_point(2, 5)
    s.point_on_perp_bisector(pt, line)
    status = s.solve()
    assert status == SolveStatus.Success
    coords = s.get_point(pt)
    assert abs(coords[0] - 2.0) < 1e-6


def test_equal_radius_cc():
    s = Sketch()
    c1_center = s.add_fixed_point(0, 0)
    c2_center = s.add_fixed_point(10, 0)
    c1 = s.add_circle(c1_center, s.add_param(3.0))
    c2 = s.add_circle(c2_center, s.add_param(5.0))
    s.set_circle_radius(c1, 3.0)
    s.equal_radius_cc(c1, c2)
    status = s.solve()
    assert status == SolveStatus.Success
    assert abs(s.get_circle(c2).radius - 3.0) < 1e-6


def test_equal_radius_ca():
    s = Sketch()
    c_center = s.add_fixed_point(0, 0)
    c = s.add_circle(c_center, s.add_param(3.0))
    s.set_circle_radius(c, 3.0)
    a = s.add_arc3p((10, 0), 5.0, 0.0, math.pi / 2)
    s.equal_radius_ca(c, a)
    status = s.solve()
    assert status == SolveStatus.Success


def test_equal_radius_aa():
    s = Sketch()
    a1 = s.add_arc3p((0, 0), 3.0, 0.0, math.pi / 2)
    s.set_arc_radius(a1, 3.0)
    a2 = s.add_arc3p((10, 0), 5.0, 0.0, math.pi / 2)
    s.equal_radius_aa(a1, a2)
    status = s.solve()
    assert status == SolveStatus.Success


def test_point_on_arc():
    s = Sketch()
    arc = s.add_arc3p((0, 0), 5.0, 0.0, math.pi)
    pt = s.add_point(3, 4)
    s.point_on_arc(pt, arc)
    status = s.solve()
    assert status == SolveStatus.Success


def test_point_on_ellipse():
    s = Sketch()
    center = s.add_fixed_point(0, 0)
    focus1 = s.add_fixed_point(3, 0)
    eid = s.add_ellipse(center, focus1, 2.0)
    pt = s.add_point(1, 1)
    s.point_on_ellipse(pt, eid)
    status = s.solve()
    assert status == SolveStatus.Success


def test_circle_diameter():
    s = Sketch()
    center = s.add_fixed_point(0, 0)
    c = s.add_circle(center, s.add_param(5.0))
    d = s.add_param(10.0, fixed=True)
    s.circle_diameter(c, d)
    status = s.solve()
    assert status == SolveStatus.Success
    assert abs(s.get_circle(c).radius - 5.0) < 1e-6


def test_set_circle_diameter():
    s = Sketch()
    center = s.add_fixed_point(0, 0)
    c = s.add_circle(center, s.add_param(5.0))
    s.set_circle_diameter(c, 10.0)
    status = s.solve()
    assert status == SolveStatus.Success
    assert abs(s.get_circle(c).radius - 5.0) < 1e-6


def test_arc_radius():
    s = Sketch()
    arc = s.add_arc3p((0, 0), 5.0, 0.0, math.pi / 2)
    r = s.add_param(3.0, fixed=True)
    s.arc_radius(arc, r)
    status = s.solve()
    assert status == SolveStatus.Success


def test_arc_diameter():
    s = Sketch()
    arc = s.add_arc3p((0, 0), 5.0, 0.0, math.pi / 2)
    d = s.add_param(6.0, fixed=True)
    s.arc_diameter(arc, d)
    status = s.solve()
    assert status == SolveStatus.Success


def test_set_arc_diameter():
    s = Sketch()
    arc = s.add_arc3p((0, 0), 5.0, 0.0, math.pi / 2)
    s.set_arc_diameter(arc, 6.0)
    status = s.solve()
    assert status == SolveStatus.Success


def test_tangent_line_ellipse():
    s = Sketch()
    center = s.add_fixed_point(0, 0)
    focus1 = s.add_fixed_point(3, 0)
    eid = s.add_ellipse(center, focus1, 2.0)
    p1 = s.add_point(0, 2)
    p2 = s.add_point(5, 2)
    line = s.add_line(p1, p2)
    s.tangent_line_ellipse(line, eid)
    status = s.solve()
    assert status == SolveStatus.Success


def test_tangent_arc_arc():
    s = Sketch()
    a1 = s.add_arc3p((0, 0), 3.0, 0.0, math.pi)
    s.set_arc_radius(a1, 3.0)
    a2 = s.add_arc3p((6, 0), 3.0, 0.0, math.pi)
    s.set_arc_radius(a2, 3.0)
    s.tangent_arc_arc(a1, a2)
    status = s.solve()
    assert status == SolveStatus.Success


def test_tangent_circle_arc():
    s = Sketch()
    c_center = s.add_fixed_point(0, 0)
    c = s.add_circle(c_center, s.add_param(3.0))
    s.set_circle_radius(c, 3.0)
    arc = s.add_arc3p((6, 0), 3.0, 0.0, math.pi)
    s.set_arc_radius(arc, 3.0)
    s.tangent_circle_arc(c, arc)
    status = s.solve()
    assert status == SolveStatus.Success


def test_tangent_circumf():
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(6, 0)
    r1 = s.add_param(3.0, fixed=True)
    r2 = s.add_param(3.0, fixed=True)
    s.tangent_circumf(p1, p2, r1, r2)
    status = s.solve()
    assert status == SolveStatus.Success


def test_p2c_distance():
    s = Sketch()
    pt = s.add_point(10, 0)
    center = s.add_fixed_point(0, 0)
    c = s.add_circle(center, s.add_param(3.0))
    s.set_circle_radius(c, 3.0)
    d = s.add_param(2.0, fixed=True)
    s.p2c_distance(pt, c, d)
    status = s.solve()
    assert status == SolveStatus.Success


def test_set_p2c_distance():
    s = Sketch()
    pt = s.add_point(10, 0)
    center = s.add_fixed_point(0, 0)
    c = s.add_circle(center, s.add_param(3.0))
    s.set_circle_radius(c, 3.0)
    s.set_p2c_distance(pt, c, 2.0)
    status = s.solve()
    assert status == SolveStatus.Success


def test_c2c_distance():
    s = Sketch()
    c1_center = s.add_fixed_point(0, 0)
    c1 = s.add_circle(c1_center, s.add_param(2.0))
    s.set_circle_radius(c1, 2.0)
    c2_center = s.add_point(10, 0)
    c2 = s.add_circle(c2_center, s.add_param(2.0))
    s.set_circle_radius(c2, 2.0)
    d = s.add_param(3.0, fixed=True)
    s.c2c_distance(c1, c2, d)
    status = s.solve()
    assert status == SolveStatus.Success


def test_set_c2c_distance():
    s = Sketch()
    c1_center = s.add_fixed_point(0, 0)
    c1 = s.add_circle(c1_center, s.add_param(2.0))
    s.set_circle_radius(c1, 2.0)
    c2_center = s.add_point(10, 0)
    c2 = s.add_circle(c2_center, s.add_param(2.0))
    s.set_circle_radius(c2, 2.0)
    s.set_c2c_distance(c1, c2, 3.0)
    status = s.solve()
    assert status == SolveStatus.Success


def test_c2l_distance():
    s = Sketch()
    center = s.add_fixed_point(0, 0)
    c = s.add_circle(center, s.add_param(2.0))
    s.set_circle_radius(c, 2.0)
    lp1 = s.add_fixed_point(-10, 10)
    lp2 = s.add_fixed_point(10, 10)
    line = s.add_line(lp1, lp2)
    d = s.add_param(8.0, fixed=True)  # distance from circle edge to line
    s.c2l_distance(c, line, d)
    status = s.solve()
    assert status == SolveStatus.Success


def test_set_c2l_distance():
    s = Sketch()
    center = s.add_fixed_point(0, 0)
    c = s.add_circle(center, s.add_param(2.0))
    s.set_circle_radius(c, 2.0)
    lp1 = s.add_fixed_point(-10, 10)
    lp2 = s.add_fixed_point(10, 10)
    line = s.add_line(lp1, lp2)
    s.set_c2l_distance(c, line, 8.0)
    status = s.solve()
    assert status == SolveStatus.Success


def test_p2a_distance():
    """Point-to-arc distance constraint (param-based)."""
    s = Sketch()
    arc = s.add_arc3p((0.0, 0.0), 3.0, 0.0, math.pi / 2)
    s.set_arc_radius(arc, 3.0)
    pt = s.add_fixed_point(5, 0)
    d = s.add_param(2.0, fixed=True)
    s.p2a_distance(pt, arc, d)
    status = s.solve()
    assert status == SolveStatus.Success


def test_set_p2a_distance():
    """Point-to-arc distance constraint (convenience float-based)."""
    s = Sketch()
    arc = s.add_arc3p((0.0, 0.0), 3.0, 0.0, math.pi / 2)
    s.set_arc_radius(arc, 3.0)
    pt = s.add_fixed_point(5, 0)
    s.set_p2a_distance(pt, arc, 2.0)
    status = s.solve()
    assert status == SolveStatus.Success


def test_a2l_distance():
    """Arc-to-line distance constraint (param-based)."""
    s = Sketch()
    arc = s.add_arc3p((0.0, 0.0), 2.0, 0.0, math.pi / 2)
    s.set_arc_radius(arc, 2.0)
    lp1 = s.add_fixed_point(-10, 10)
    lp2 = s.add_fixed_point(10, 10)
    line = s.add_line(lp1, lp2)
    d = s.add_param(3.0, fixed=True)
    s.a2l_distance(arc, line, d)
    status = s.solve()
    assert status == SolveStatus.Success


def test_set_a2l_distance():
    """Arc-to-line distance constraint (convenience float-based)."""
    s = Sketch()
    arc = s.add_arc3p((0.0, 0.0), 2.0, 0.0, math.pi / 2)
    s.set_arc_radius(arc, 2.0)
    lp1 = s.add_fixed_point(-10, 10)
    lp2 = s.add_fixed_point(10, 10)
    line = s.add_line(lp1, lp2)
    s.set_a2l_distance(arc, line, 3.0)
    status = s.solve()
    assert status == SolveStatus.Success


def test_c2a_distance():
    """Circle-to-arc distance constraint (param-based)."""
    s = Sketch()
    arc = s.add_arc3p((0.0, 0.0), 2.0, 0.0, math.pi / 2)
    s.set_arc_radius(arc, 2.0)
    c_center = s.add_point(10.0, 0.0)
    circle = s.add_circle(c_center, s.add_param(3.0))
    s.set_circle_radius(circle, 3.0)
    d = s.add_param(1.0, fixed=True)
    s.c2a_distance(circle, arc, d)
    status = s.solve()
    assert status == SolveStatus.Success


def test_set_c2a_distance():
    """Circle-to-arc distance constraint (convenience float-based)."""
    s = Sketch()
    arc = s.add_arc3p((0.0, 0.0), 2.0, 0.0, math.pi / 2)
    s.set_arc_radius(arc, 2.0)
    c_center = s.add_point(10.0, 0.0)
    circle = s.add_circle(c_center, s.add_param(3.0))
    s.set_circle_radius(circle, 3.0)
    s.set_c2a_distance(circle, arc, 1.0)
    status = s.solve()
    assert status == SolveStatus.Success


def test_a2a_distance():
    """Arc-to-arc distance constraint (param-based)."""
    s = Sketch()
    a1 = s.add_arc3p((0.0, 0.0), 2.0, 0.0, math.pi / 2)
    s.set_arc_radius(a1, 2.0)
    a2 = s.add_arc3p((10.0, 0.0), 2.0, 0.0, math.pi / 2)
    s.set_arc_radius(a2, 2.0)
    d = s.add_param(2.0, fixed=True)
    s.a2a_distance(a1, a2, d)
    status = s.solve()
    assert status == SolveStatus.Success


def test_set_a2a_distance():
    """Arc-to-arc distance constraint (convenience float-based)."""
    s = Sketch()
    a1 = s.add_arc3p((0.0, 0.0), 2.0, 0.0, math.pi / 2)
    s.set_arc_radius(a1, 2.0)
    a2 = s.add_arc3p((10.0, 0.0), 2.0, 0.0, math.pi / 2)
    s.set_arc_radius(a2, 2.0)
    s.set_a2a_distance(a1, a2, 2.0)
    status = s.solve()
    assert status == SolveStatus.Success


def test_arc_length():
    s = Sketch()
    arc = s.add_arc3p((0, 0), 5.0, 0.0, math.pi / 2)
    length = s.add_param(math.pi * 5.0 / 2, fixed=True)
    s.arc_length(arc, length)
    status = s.solve()
    assert status == SolveStatus.Success


def test_set_arc_length():
    s = Sketch()
    arc = s.add_arc3p((0, 0), 5.0, 0.0, math.pi / 2)
    s.set_arc_length(arc, math.pi * 5.0 / 2)
    status = s.solve()
    assert status == SolveStatus.Success


def test_proportional():
    s = Sketch()
    p1 = s.add_param(5.0, fixed=True)
    p2 = s.add_param(1.0)
    s.proportional(p1, p2, 2.0)
    status = s.solve()
    assert status == SolveStatus.Success


def test_difference():
    """difference constrains param2 - param1 = diff."""
    s = Sketch()
    p1 = s.add_param(3.0, fixed=True)
    p2 = s.add_param(10.0)
    diff = s.add_param(5.0, fixed=True)
    s.difference(p1, p2, diff)
    status = s.solve()
    assert status == SolveStatus.Success


def test_clear_by_tag():
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(5, 0)
    line = s.add_line(p1, p2)
    tag = s.horizontal(line)
    s.clear_by_tag(tag)
    # After clearing, constraint is gone - solve should still work
    status = s.solve()
    assert status == SolveStatus.Success


def test_constraint_error():
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(5, 0)
    line = s.add_line(p1, p2)
    tag = s.horizontal(line)
    s.solve()
    err = s.constraint_error(tag)
    # Constraint is satisfied, error should be small
    assert isinstance(err, float)


def test_internal_alignment_point2ellipse():
    s = Sketch()
    center = s.add_fixed_point(0, 0)
    focus1 = s.add_fixed_point(3, 0)
    eid = s.add_ellipse(center, focus1, 2.0)
    pt = s.add_point(-3, 0)
    s.internal_alignment_point2ellipse(eid, pt, InternalAlignmentType.EllipseFocus2X)
    status = s.solve()
    assert status == SolveStatus.Success
