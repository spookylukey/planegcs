"""Tests covering Sketch methods that other test files don't exercise.

Targeted at:
- set_param (via Sketch wrapper)
- add_line_xy
- get_line
- get_circle
- add_arc_from_center / arc_rules
- add_ellipse / get_ellipse
- equal (parameter equality)
"""

import math

from planegcs import Sketch, SolveStatus


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
    c = s.add_circle(center, 5.0)
    s.set_circle_radius(c, 5.0)
    s.solve()
    info = s.get_circle(c)
    assert abs(info.center[0] - 1.0) < 1e-6
    assert abs(info.center[1] - 2.0) < 1e-6
    assert abs(info.radius - 5.0) < 1e-6


def test_add_arc_from_center_and_arc_rules():
    """add_arc_from_center + arc_rules: start/end points match angles."""
    s = Sketch()
    center = s.add_fixed_point(0.0, 0.0)
    radius = 5.0
    start_angle = 0.0
    end_angle = math.pi / 2

    arc = s.add_arc_from_center(center, radius, start_angle, end_angle)
    s.arc_rules(arc)
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
