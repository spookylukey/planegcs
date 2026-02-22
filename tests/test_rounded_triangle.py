"""Test equilateral triangle with rounded corners.

Demonstrates add_arc and tangent_line_arc working together.
"""

import math

from planegcs import ArcId, ParamId, PointId, Sketch, SolveStatus


def _dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def _make_arc_between(s: Sketch, start_id: PointId, end_id: PointId, rad: ParamId) -> ArcId:
    """Create an arc between two existing points sharing a radius param.

    Computes a plausible initial center from the geometry (left side for CCW)
    and creates center point + angle params internally.
    """
    sx, sy = s.get_point(start_id)
    ex, ey = s.get_point(end_id)
    r = s.get_param(rad)

    dx, dy = ex - sx, ey - sy
    half_chord = math.sqrt(dx * dx + dy * dy) / 2.0
    r_eff = max(abs(r), half_chord)
    h = math.sqrt(max(r_eff * r_eff - half_chord * half_chord, 0.0))

    mx, my = (sx + ex) / 2, (sy + ey) / 2
    perp_x, perp_y = -dy / (2 * half_chord), dx / (2 * half_chord)
    cx, cy = mx + h * perp_x, my + h * perp_y

    center = s.add_point(cx, cy)
    sa = math.atan2(sy - cy, sx - cx)
    ea = math.atan2(ey - cy, ex - cx)

    return s.add_arc_cse(center, start_id, end_id, r_eff, sa, ea)


def test_arc_basic():
    """Basic test: arc from start/end points and radius."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(3, 0)

    rad = s.add_param(3.0, fixed=True)
    _make_arc_between(s, p1, p2, rad)
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
    p3 = s.add_fixed_point(10, 5)

    line = s.add_line(p1, p2)
    s.horizontal(line)

    rad = s.add_param(5.0, fixed=True)
    arc = _make_arc_between(s, p2, p3, rad)
    s.tangent_line_arc(line, arc)

    status = s.solve()
    assert status == SolveStatus.Success

    assert abs(s.get_point(p2)[0] - 5.0) < 1e-6
    assert abs(s.get_point(p2)[1] - 0.0) < 1e-6
    assert abs(s.get_point(p3)[0] - 10.0) < 1e-6
    assert abs(s.get_point(p3)[1] - 5.0) < 1e-6
    assert abs(s.get_arc(arc).radius - 5.0) < 1e-4


def test_equilateral_triangle_rounded_corners():
    """Equilateral triangle with rounded corners using arcs."""
    side = 10.0
    r = 1.5
    h = side * math.sqrt(3) / 2

    t = r * math.sqrt(3)

    v1, v2, v3 = (0.0, 0.0), (side, 0.0), (side / 2, h)

    d_r = ((v3[0] - v2[0]) / side, (v3[1] - v2[1]) / side)
    d_l = ((v1[0] - v3[0]) / side, (v1[1] - v3[1]) / side)

    bs = (v1[0] + t, v1[1])
    be = (v2[0] - t, v2[1])
    rs = (v2[0] + t * d_r[0], v2[1] + t * d_r[1])
    re = (v3[0] - t * d_r[0], v3[1] - t * d_r[1])
    ls = (v3[0] + t * d_l[0], v3[1] + t * d_l[1])
    le = (v1[0] - t * d_l[0], v1[1] - t * d_l[1])

    s = Sketch()

    p_bs = s.add_fixed_point(*bs)
    p_be = s.add_point(*be)
    p_rs = s.add_fixed_point(*rs)
    p_re = s.add_point(*re)
    p_ls = s.add_point(*ls)
    p_le = s.add_fixed_point(*le)

    line_b = s.add_line(p_bs, p_be)
    line_r = s.add_line(p_rs, p_re)
    line_l = s.add_line(p_ls, p_le)

    rad = s.add_param(r, fixed=True)
    arc_bl = _make_arc_between(s, p_le, p_bs, rad)
    arc_br = _make_arc_between(s, p_be, p_rs, rad)
    arc_top = _make_arc_between(s, p_re, p_ls, rad)

    s.tangent_line_arc(line_b, arc_bl)
    s.tangent_line_arc(line_b, arc_br)
    s.tangent_line_arc(line_r, arc_br)
    s.tangent_line_arc(line_r, arc_top)
    s.tangent_line_arc(line_l, arc_top)
    s.tangent_line_arc(line_l, arc_bl)

    s.equal_length(line_b, line_r)
    s.equal_length(line_r, line_l)

    s.horizontal(line_b)
    s.set_p2p_distance(p_bs, p_be, side - 2 * t)

    status = s.solve()
    assert status == SolveStatus.Success

    len_b = _dist(s.get_point(p_bs), s.get_point(p_be))
    len_r = _dist(s.get_point(p_rs), s.get_point(p_re))
    len_l = _dist(s.get_point(p_ls), s.get_point(p_le))

    expected_len = side - 2 * t
    assert abs(len_b - expected_len) < 1e-4
    assert abs(len_r - expected_len) < 1e-4
    assert abs(len_l - expected_len) < 1e-4

    assert abs(s.get_point(p_bs)[1] - s.get_point(p_be)[1]) < 1e-6

    mid_x = (s.get_point(p_bs)[0] + s.get_point(p_be)[0]) / 2
    le_pt = s.get_point(p_le)
    rs_pt = s.get_point(p_rs)
    assert abs((le_pt[0] + rs_pt[0]) / 2 - mid_x) < 1e-3
    assert abs(le_pt[1] - rs_pt[1]) < 1e-3
