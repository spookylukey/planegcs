"""Tests for circle and arc constraints."""

import math
import pytest
from planegcs import Sketch, SolveStatus


def _dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def test_point_on_circle():
    """A point constrained on a circle lies at the right distance from center."""
    s = Sketch()
    center = s.add_point(0, 0)
    s.fix_point(center, 0, 0)

    c = s.add_circle(center, 5.0)
    r_param = s.add_param(5.0)
    s.circle_radius(c, r_param)

    pt = s.add_point(3, 4)  # initial guess on the circle
    s.point_on_circle(pt, c)

    status = s.solve()
    assert status == SolveStatus.Success

    center_pos = s.get_point(center)
    pt_pos = s.get_point(pt)
    dist = _dist(center_pos, pt_pos)
    assert abs(dist - 5.0) < 1e-6


def test_tangent_line_circle():
    """A line tangent to a circle touches at exactly one point."""
    s = Sketch()
    center = s.add_point(0, 0)
    s.fix_point(center, 0, 0)
    c = s.add_circle(center, 3.0)

    # Horizontal line at y=3 (tangent to circle of radius 3)
    lp1 = s.add_point(-5, 3)
    lp2 = s.add_point(5, 3)
    l = s.add_line(lp1, lp2)
    s.horizontal(l)

    s.tangent_line_circle(l, c)

    status = s.solve()
    assert status == SolveStatus.Success

    # The line should be at distance = radius from center
    center_pos = s.get_point(center)
    lp1_pos = s.get_point(lp1)
    lp2_pos = s.get_point(lp2)

    # For a horizontal line y=k, distance from (0,0) is |k|
    # Since tangent, |k| should equal radius
    # The line y-coords should be the same (horizontal)
    assert abs(lp1_pos[1] - lp2_pos[1]) < 1e-8
    dist_to_line = abs(lp1_pos[1] - center_pos[1])
    assert abs(dist_to_line - 3.0) < 1e-4


def test_concentric_circles_equal_radius():
    """Two concentric circles with equal radius constraint."""
    s = Sketch()
    center = s.add_point(0, 0)
    s.fix_point(center, 0, 0)

    c1 = s.add_circle(center, 3.0)
    c2 = s.add_circle(center, 7.0)  # different initial radius

    s.solver.equal_radius_cc(c1, c2)

    r_param = s.add_param(5.0)
    s.circle_radius(c1, r_param)

    status = s.solve()
    assert status == SolveStatus.Success

    # Both circles should have radius 5
    r1 = s.get_param(r_param)
    assert abs(r1 - 5.0) < 1e-6


def test_two_tangent_circles():
    """Two circles tangent to each other."""
    s = Sketch()
    c1_center = s.add_point(0, 0)
    c2_center = s.add_point(8, 0)
    s.fix_point(c1_center, 0, 0)
    s.horizontal_points(c1_center, c2_center)

    c1 = s.add_circle(c1_center, 3.0)
    c2 = s.add_circle(c2_center, 5.0)

    r1 = s.add_param(3.0)
    r2 = s.add_param(5.0)
    s.circle_radius(c1, r1)
    s.circle_radius(c2, r2)

    s.tangent_circle_circle(c1, c2)

    status = s.solve()
    assert status == SolveStatus.Success

    p1 = s.get_point(c1_center)
    p2 = s.get_point(c2_center)
    dist = _dist(p1, p2)

    # Distance between centers should be r1 + r2 or |r1 - r2|
    assert (abs(dist - 8.0) < 1e-4) or (abs(dist - 2.0) < 1e-4)
