"""Test equilateral triangle with rounded corners.

Demonstrates add_arc_from_start_end and tangent_line_arc working together.
"""

import math

from planegcs import Sketch, SolveStatus


def _dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def test_arc_from_start_end_basic():
    """Basic test: arc from start/end points and radius."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(3, 0)

    rad = s.add_param(3.0)
    s.add_arc_from_start_end(p1, p2, rad)
    status = s.solve()
    assert status == SolveStatus.Success

    # Arc endpoints should still be at p1 and p2
    assert abs(s.get_point(p1)[0] - 0.0) < 1e-6
    assert abs(s.get_point(p1)[1] - 0.0) < 1e-6
    assert abs(s.get_point(p2)[0] - 3.0) < 1e-6
    assert abs(s.get_point(p2)[1] - 0.0) < 1e-6


def test_arc_tangent_to_line():
    """Arc tangent to a line at the shared endpoint."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(5, 0)
    # p3 at (10, 5) lies on a circle of radius 5 centered at (5, 5),
    # which is the center when the arc is tangent to the horizontal line at p2.
    p3 = s.add_fixed_point(10, 5)

    line = s.add_line(p1, p2)
    s.horizontal(line)

    rad = s.add_param(5.0)
    arc = s.add_arc_from_start_end(p2, p3, rad)
    s.tangent_line_arc(line, arc)

    status = s.solve()
    assert status == SolveStatus.Success

    # p2 and p3 should remain fixed
    assert abs(s.get_point(p2)[0] - 5.0) < 1e-6
    assert abs(s.get_point(p2)[1] - 0.0) < 1e-6
    assert abs(s.get_point(p3)[0] - 10.0) < 1e-6
    assert abs(s.get_point(p3)[1] - 5.0) < 1e-6

    # Radius should remain close to 5.0
    assert abs(s.get_arc_radius(arc) - 5.0) < 1e-4


def test_equilateral_triangle_rounded_corners():
    """Equilateral triangle with rounded corners using arcs."""
    side = 10.0
    r = 1.5
    h = side * math.sqrt(3) / 2

    # Tangent length from vertex to tangent point: r / tan(30°) = r * sqrt(3)
    t = r * math.sqrt(3)

    # Triangle vertices
    v1, v2, v3 = (0.0, 0.0), (side, 0.0), (side / 2, h)

    # Unit edge directions
    d_r = ((v3[0] - v2[0]) / side, (v3[1] - v2[1]) / side)  # v2 -> v3
    d_l = ((v1[0] - v3[0]) / side, (v1[1] - v3[1]) / side)  # v3 -> v1

    # Tangent points (initial guesses matching the exact solution)
    bs = (v1[0] + t, v1[1])
    be = (v2[0] - t, v2[1])
    rs = (v2[0] + t * d_r[0], v2[1] + t * d_r[1])
    re = (v3[0] - t * d_r[0], v3[1] - t * d_r[1])
    ls = (v3[0] + t * d_l[0], v3[1] + t * d_l[1])
    le = (v1[0] - t * d_l[0], v1[1] - t * d_l[1])

    s = Sketch()

    # Six tangent-point vertices
    p_bs = s.add_fixed_point(*bs)
    p_be = s.add_point(*be)
    p_rs = s.add_fixed_point(*rs)
    p_re = s.add_point(*re)
    p_ls = s.add_point(*ls)
    p_le = s.add_fixed_point(*le)

    # Three straight edges
    line_b = s.add_line(p_bs, p_be)
    line_r = s.add_line(p_rs, p_re)
    line_l = s.add_line(p_ls, p_le)

    # Three corner arcs
    rad = s.add_param(r)
    arc_bl = s.add_arc_from_start_end(p_le, p_bs, rad)
    arc_br = s.add_arc_from_start_end(p_be, p_rs, rad)
    arc_top = s.add_arc_from_start_end(p_re, p_ls, rad)

    # Tangency: each arc tangent to its two adjacent lines
    s.tangent_line_arc(line_b, arc_bl)
    s.tangent_line_arc(line_b, arc_br)
    s.tangent_line_arc(line_r, arc_br)
    s.tangent_line_arc(line_r, arc_top)
    s.tangent_line_arc(line_l, arc_top)
    s.tangent_line_arc(line_l, arc_bl)

    # Equilateral: all edges the same length
    s.equal_length(line_b, line_r)
    s.equal_length(line_r, line_l)

    # Position & orient
    # add_fixed_point for p_bs, p_le, and p_rs pins the shape and resolves
    # the arc center ambiguities (each arc from start/end adds 1 DOF)
    s.horizontal(line_b)
    s.set_p2p_distance(p_bs, p_be, side - 2 * t)

    status = s.solve()
    assert status == SolveStatus.Success

    # All three straight segments should have equal length
    len_b = _dist(s.get_point(p_bs), s.get_point(p_be))
    len_r = _dist(s.get_point(p_rs), s.get_point(p_re))
    len_l = _dist(s.get_point(p_ls), s.get_point(p_le))

    expected_len = side - 2 * t
    assert abs(len_b - expected_len) < 1e-4
    assert abs(len_r - expected_len) < 1e-4
    assert abs(len_l - expected_len) < 1e-4

    # Bottom edge should be horizontal
    assert abs(s.get_point(p_bs)[1] - s.get_point(p_be)[1]) < 1e-6

    # Verify symmetry: the shape should be symmetric about x = side/2
    mid_x = (s.get_point(p_bs)[0] + s.get_point(p_be)[0]) / 2
    le_pt = s.get_point(p_le)
    rs_pt = s.get_point(p_rs)
    # le and rs should be symmetric about mid_x
    assert abs((le_pt[0] + rs_pt[0]) / 2 - mid_x) < 1e-3
    assert abs(le_pt[1] - rs_pt[1]) < 1e-3
