"""Broad constraint coverage tests."""

import math
import pytest
from planegcs import Sketch, SketchSolver, SolveStatus


def _dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def test_parallel_lines():
    """Two lines constrained parallel."""
    s = Sketch()
    p1 = s.add_point(0, 0)
    p2 = s.add_point(5, 0)
    p3 = s.add_point(0, 3)
    p4 = s.add_point(5, 4)

    l1 = s.add_line(p1, p2)
    l2 = s.add_line(p3, p4)

    s.fix_point(p1, 0, 0)
    s.fix_point(p2, 5, 0)
    s.fix_point(p3, 0, 3)
    s.horizontal(l1)
    s.parallel(l1, l2)

    status = s.solve()
    assert status == SolveStatus.Success

    pt3 = s.get_point(p3)
    pt4 = s.get_point(p4)
    # Parallel to horizontal line means same y
    assert abs(pt3[1] - pt4[1]) < 1e-6


def test_perpendicular_lines():
    """Two lines constrained perpendicular."""
    s = Sketch()
    p1 = s.add_point(0, 0)
    p2 = s.add_point(5, 0)
    p3 = s.add_point(0, 0)
    p4 = s.add_point(0, 5)

    l1 = s.add_line(p1, p2)
    l2 = s.add_line(p3, p4)

    s.fix_point(p1, 0, 0)
    s.fix_point(p3, 0, 0)
    s.horizontal(l1)
    s.perpendicular(l1, l2)

    d1 = s.add_param(5.0)
    d2 = s.add_param(5.0)
    s.p2p_distance(p1, p2, d1)
    s.p2p_distance(p3, p4, d2)

    status = s.solve()
    assert status == SolveStatus.Success

    pt4 = s.get_point(p4)
    # l2 should be vertical if l1 is horizontal
    assert abs(pt4[0]) < 1e-4


def test_midpoint_on_line():
    """Midpoint of one line constrained to lie on another."""
    s = Sketch()
    # Line 1: from (0,0) to (6,0)
    p1 = s.add_point(0, 0)
    p2 = s.add_point(6, 0)
    l1 = s.add_line(p1, p2)
    s.fix_point(p1, 0, 0)
    s.fix_point(p2, 6, 0)

    # Line 2: vertical line at x=3
    p3 = s.add_point(3, -5)
    p4 = s.add_point(3, 5)
    l2 = s.add_line(p3, p4)
    s.vertical(l2)

    s.midpoint_on_line(l1, l2)

    status = s.solve()
    assert status == SolveStatus.Success

    # Midpoint of l1 is (3, 0). This must lie on l2.
    # l2 is vertical, and midpoint x=3, so l2 must pass through x=3
    pt3 = s.get_point(p3)
    pt4 = s.get_point(p4)
    assert abs(pt3[0] - 3.0) < 1e-4
    assert abs(pt4[0] - 3.0) < 1e-4


def test_symmetric_about_line():
    """Points symmetric about a line."""
    s = Sketch()
    # Symmetry line: y-axis (vertical)
    lp1 = s.add_point(0, -10)
    lp2 = s.add_point(0, 10)
    sym_line = s.add_line(lp1, lp2)
    s.fix_point(lp1, 0, -10)
    s.fix_point(lp2, 0, 10)

    # Two symmetric points
    pa = s.add_point(3, 2)
    pb = s.add_point(-4, 2)  # initial guess, should move to (-3, 2)
    s.fix_point(pa, 3, 2)
    s.symmetric_line(pa, pb, sym_line)

    status = s.solve()
    assert status == SolveStatus.Success

    a = s.get_point(pa)
    b = s.get_point(pb)
    # Symmetric about y-axis: b = (-a.x, a.y)
    assert abs(b[0] + a[0]) < 1e-4
    assert abs(b[1] - a[1]) < 1e-4


def test_symmetric_about_point():
    """Points symmetric about a center point."""
    s = Sketch()
    center = s.add_point(0, 0)
    s.fix_point(center, 0, 0)

    pa = s.add_point(3, 4)
    pb = s.add_point(-2, -3)  # initial guess
    s.fix_point(pa, 3, 4)
    s.symmetric_point(pa, pb, center)

    status = s.solve()
    assert status == SolveStatus.Success

    a = s.get_point(pa)
    b = s.get_point(pb)
    c = s.get_point(center)
    # b = 2*c - a
    assert abs(b[0] - (2 * c[0] - a[0])) < 1e-4
    assert abs(b[1] - (2 * c[1] - a[1])) < 1e-4


def test_equal_length():
    """Two lines with equal length constraint."""
    s = Sketch()
    p1 = s.add_point(0, 0)
    p2 = s.add_point(5, 0)
    p3 = s.add_point(10, 0)
    p4 = s.add_point(10, 3)

    l1 = s.add_line(p1, p2)
    l2 = s.add_line(p3, p4)

    s.fix_point(p1, 0, 0)
    s.fix_point(p2, 5, 0)
    s.fix_point(p3, 10, 0)
    s.vertical(l2)  # l2 is vertical from p3
    s.equal_length(l1, l2)

    status = s.solve()
    assert status == SolveStatus.Success

    pt3 = s.get_point(p3)
    pt4 = s.get_point(p4)
    len1 = _dist(s.get_point(p1), s.get_point(p2))
    len2 = _dist(pt3, pt4)
    assert abs(len1 - len2) < 1e-5


def test_l2l_angle():
    """Angle between two lines."""
    s = Sketch()
    p1 = s.add_point(0, 0)
    p2 = s.add_point(5, 0)
    p3 = s.add_point(0, 0)
    p4 = s.add_point(3, 4)

    l1 = s.add_line(p1, p2)
    l2 = s.add_line(p3, p4)

    s.fix_point(p1, 0, 0)
    s.fix_point(p3, 0, 0)
    s.horizontal(l1)

    d1 = s.add_param(5.0)
    s.p2p_distance(p1, p2, d1)
    d2 = s.add_param(5.0)
    s.p2p_distance(p3, p4, d2)

    angle = s.add_param(math.pi / 4)  # 45 degrees
    s.l2l_angle(l1, l2, angle)

    status = s.solve()
    assert status == SolveStatus.Success

    pt4 = s.get_point(p4)
    # l2 from origin at 45 degrees should have equal x and y
    assert abs(pt4[0] - pt4[1]) < 1e-3


def test_p2l_distance():
    """Point to line distance."""
    s = Sketch()
    lp1 = s.add_point(0, 0)
    lp2 = s.add_point(10, 0)
    l = s.add_line(lp1, lp2)
    s.fix_point(lp1, 0, 0)
    s.fix_point(lp2, 10, 0)

    pt = s.add_point(5, 3)
    d = s.add_param(7.0)
    s.p2l_distance(pt, l, d)

    # Also fix x of pt
    px = s.add_param(5.0)
    s.solver.coordinate_x(pt, px)

    status = s.solve()
    assert status == SolveStatus.Success

    pt_pos = s.get_point(pt)
    # Point should be at distance 7 from the horizontal line y=0
    assert abs(abs(pt_pos[1]) - 7.0) < 1e-4


def test_constraint_error():
    """Constraint error calculation."""
    solver = SketchSolver()
    p1 = solver.add_point(0, 0)
    p2 = solver.add_point(3, 4)
    d = solver.add_param(10.0)  # wrong distance
    tag = solver.p2p_distance(p1, p2, d)
    # Before solving, the error should be non-zero
    err = solver.constraint_error(tag)
    assert abs(err) > 0.1


def test_clear_by_tag():
    """Removing constraints by tag."""
    solver = SketchSolver()
    p1 = solver.add_point(0, 0)
    p2 = solver.add_point(5, 0)
    d = solver.add_param(5.0)
    tag = solver.p2p_distance(p1, p2, d)
    solver.clear_by_tag(tag)  # should not crash


def test_horizontal_vertical_points():
    """Horizontal/vertical constraints between points."""
    s = Sketch()
    p1 = s.add_point(0, 0)
    p2 = s.add_point(5, 3)
    p3 = s.add_point(2, 7)

    s.fix_point(p1, 0, 0)
    s.horizontal_points(p1, p2)
    s.vertical_points(p1, p3)

    status = s.solve()
    assert status == SolveStatus.Success

    pt2 = s.get_point(p2)
    pt3 = s.get_point(p3)
    assert abs(pt2[1]) < 1e-6  # same y as p1
    assert abs(pt3[0]) < 1e-6  # same x as p1
