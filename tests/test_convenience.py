"""Tests for convenience methods that accept float values directly."""

import math

from planegcs import Sketch, SolveStatus


def _dist(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def test_set_p2p_distance():
    """set_p2p_distance constrains distance with a float value."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(1, 0)
    s.horizontal_points(p1, p2)
    s.set_p2p_distance(p1, p2, 7.0)
    status = s.solve()
    assert status == SolveStatus.Success
    x2, y2 = s.get_point(p2)
    assert abs(math.sqrt(x2**2 + y2**2) - 7.0) < 1e-8


def test_set_p2p_distance_non_integer():
    """set_p2p_distance works with non-integer distances (e.g. 3.7)."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(1, 0)
    s.horizontal_points(p1, p2)
    s.set_p2p_distance(p1, p2, 3.7)
    status = s.solve()
    assert status == SolveStatus.Success
    pt2 = s.get_point(p2)
    assert abs(pt2[0] - 3.7) < 1e-8


def test_set_p2p_distance_equilateral_triangle():
    """Equilateral triangle using set_p2p_distance."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(5, 0)
    p3 = s.add_point(2.5, 4)

    l1 = s.add_line(p1, p2)
    l2 = s.add_line(p2, p3)
    l3 = s.add_line(p3, p1)

    s.equal_length(l1, l2)
    s.equal_length(l2, l3)
    s.horizontal(l1)
    s.set_p2p_distance(p1, p2, 5.0)

    status = s.solve()
    assert status == SolveStatus.Success

    pt1 = s.get_point(p1)
    pt2 = s.get_point(p2)
    pt3 = s.get_point(p3)
    assert abs(_dist(pt1, pt2) - 5.0) < 1e-6
    assert abs(_dist(pt2, pt3) - 5.0) < 1e-6
    assert abs(_dist(pt3, pt1) - 5.0) < 1e-6


def test_set_p2l_distance():
    """set_p2l_distance constrains point-to-line distance with a float value."""
    s = Sketch()
    lp1 = s.add_fixed_point(0, 0)
    lp2 = s.add_fixed_point(10, 0)
    line = s.add_line(lp1, lp2)

    pt = s.add_point(5, 3)
    s.set_p2l_distance(pt, line, 7.0)

    # Also fix x of pt via a param
    px = s.add_param(5.0)
    s.solver.coordinate_x(pt, px)

    status = s.solve()
    assert status == SolveStatus.Success

    pt_pos = s.get_point(pt)
    assert abs(abs(pt_pos[1]) - 7.0) < 1e-4


def test_set_l2l_angle():
    """set_l2l_angle constrains angle with a float value."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(5, 0)
    p3 = s.add_fixed_point(0, 0)
    p4 = s.add_point(3, 4)

    l1 = s.add_line(p1, p2)
    l2 = s.add_line(p3, p4)
    s.horizontal(l1)

    s.set_p2p_distance(p1, p2, 5.0)
    s.set_p2p_distance(p3, p4, 5.0)
    s.set_l2l_angle(l1, l2, math.pi / 4)  # 45 degrees

    status = s.solve()
    assert status == SolveStatus.Success

    pt4 = s.get_point(p4)
    assert abs(pt4[0] - pt4[1]) < 1e-3


def test_set_circle_radius():
    """set_circle_radius constrains radius with a float value."""
    s = Sketch()
    center = s.add_fixed_point(0, 0)

    c = s.add_circle(center, 3.0)  # initial guess radius 3
    s.set_circle_radius(c, 5.0)  # constrain to 5

    pt = s.add_point(5, 0)
    s.point_on_circle(pt, c)

    status = s.solve()
    assert status == SolveStatus.Success

    center_pos = s.get_point(center)
    pt_pos = s.get_point(pt)
    dist = _dist(center_pos, pt_pos)
    assert abs(dist - 5.0) < 1e-6
