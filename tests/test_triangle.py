"""Tests demonstrating equilateral and right triangle constraint solving."""

import math

from planegcs import Sketch, SolveStatus


def _dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def test_equilateral_triangle():
    """Solve for an equilateral triangle with side length 5."""
    s = Sketch()

    # Three points (initial guess)
    p1 = s.add_point(0, 0)
    p2 = s.add_point(5, 0)
    p3 = s.add_point(2.5, 4)

    # Three lines forming a triangle
    l1 = s.add_line(p1, p2)
    l2 = s.add_line(p2, p3)
    l3 = s.add_line(p3, p1)

    # All sides equal length
    s.equal_length(l1, l2)
    s.equal_length(l2, l3)

    # Fix p1 at origin, make base horizontal
    s.fix_point(p1, 0, 0)
    s.horizontal(l1)

    # Side length = 5
    d = s.add_param(5.0)
    s.p2p_distance(p1, p2, d)

    status = s.solve()
    assert status == SolveStatus.Success

    pt1 = s.get_point(p1)
    pt2 = s.get_point(p2)
    pt3 = s.get_point(p3)

    # Check all sides are ~5
    assert abs(_dist(pt1, pt2) - 5.0) < 1e-6
    assert abs(_dist(pt2, pt3) - 5.0) < 1e-6
    assert abs(_dist(pt3, pt1) - 5.0) < 1e-6

    # p1 at origin
    assert abs(pt1[0]) < 1e-6
    assert abs(pt1[1]) < 1e-6

    # Base is horizontal
    assert abs(pt1[1] - pt2[1]) < 1e-6

    # p3 should be above the base
    assert pt3[1] > 0

    # Height of equilateral triangle = 5 * sqrt(3)/2 ~ 4.330
    expected_height = 5.0 * math.sqrt(3) / 2
    assert abs(pt3[1] - expected_height) < 1e-4


def test_right_triangle():
    """Solve for a right triangle with legs 3 and 4."""
    s = Sketch()

    p1 = s.add_point(0, 0)
    p2 = s.add_point(3, 0)
    p3 = s.add_point(0, 4)

    l_base = s.add_line(p1, p2)
    l_height = s.add_line(p1, p3)
    s.add_line(p2, p3)  # hypotenuse

    # Fix p1 at origin
    s.fix_point(p1, 0, 0)

    # Base horizontal, height vertical
    s.horizontal(l_base)
    s.vertical(l_height)

    # Perpendicular at p1
    s.perpendicular(l_base, l_height)

    # Set lengths
    d_base = s.add_param(3.0)
    d_height = s.add_param(4.0)
    s.p2p_distance(p1, p2, d_base)
    s.p2p_distance(p1, p3, d_height)

    status = s.solve()
    assert status == SolveStatus.Success

    pt1 = s.get_point(p1)
    pt2 = s.get_point(p2)
    pt3 = s.get_point(p3)

    # Check legs
    assert abs(_dist(pt1, pt2) - 3.0) < 1e-6
    assert abs(_dist(pt1, pt3) - 4.0) < 1e-6

    # Hypotenuse should be 5
    assert abs(_dist(pt2, pt3) - 5.0) < 1e-4


def test_isoceles_triangle():
    """Solve for an isosceles triangle."""
    s = Sketch()

    p1 = s.add_point(0, 0)
    p2 = s.add_point(6, 0)
    p3 = s.add_point(3, 5)

    l1 = s.add_line(p1, p2)  # base
    l2 = s.add_line(p1, p3)  # left side
    l3 = s.add_line(p2, p3)  # right side

    s.fix_point(p1, 0, 0)
    s.horizontal(l1)

    # Two sides equal
    s.equal_length(l2, l3)

    # Base = 6
    d = s.add_param(6.0)
    s.p2p_distance(p1, p2, d)

    # Side = 5
    d_side = s.add_param(5.0)
    s.p2p_distance(p1, p3, d_side)

    status = s.solve()
    assert status == SolveStatus.Success

    pt1 = s.get_point(p1)
    pt2 = s.get_point(p2)
    pt3 = s.get_point(p3)

    assert abs(_dist(pt1, pt2) - 6.0) < 1e-5
    assert abs(_dist(pt1, pt3) - 5.0) < 1e-5
    assert abs(_dist(pt2, pt3) - 5.0) < 1e-5

    # Apex should be above midpoint of base
    midx = (pt1[0] + pt2[0]) / 2
    assert abs(pt3[0] - midx) < 1e-4
