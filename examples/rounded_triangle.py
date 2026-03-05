"""Equilateral triangle with rounded corners.

Builds an equilateral triangle whose sharp corners are replaced by
circular arcs of a given radius.
"""

import math

from planegcs import Sketch, SolveStatus

# ── Parameters ──────────────────────────────────────────────
side = 10.0  # side length of the underlying triangle
r = 1.5  # corner arc radius
h = side * math.sqrt(3) / 2  # triangle height

# Tangent length from each vertex to the tangent point.
# For an interior angle of 60°: t = r / tan(30°) = r * √3
t = r * math.sqrt(3)

# ── Compute initial guesses ─────────────────────────────────
# Triangle vertices
v1, v2, v3 = (0.0, 0.0), (side, 0.0), (side / 2, h)

# Unit edge directions
d_r = ((v3[0] - v2[0]) / side, (v3[1] - v2[1]) / side)
d_l = ((v1[0] - v3[0]) / side, (v1[1] - v3[1]) / side)

# Tangent points (where arcs meet lines)
bs = (v1[0] + t, v1[1])  # bottom start
be = (v2[0] - t, v2[1])  # bottom end
rs = (v2[0] + t * d_r[0], v2[1] + t * d_r[1])  # right start
re = (v3[0] - t * d_r[0], v3[1] - t * d_r[1])  # right end
ls = (v3[0] + t * d_l[0], v3[1] + t * d_l[1])  # left start
le = (v1[0] - t * d_l[0], v1[1] - t * d_l[1])  # left end


def _arc_center_and_angles(
    sx: float, sy: float, ex: float, ey: float, radius: float
) -> tuple[tuple[float, float], float, float]:
    """Compute a plausible center and start/end angles for an arc
    through (sx, sy) -> (ex, ey) with the given radius.

    Returns ((cx, cy), start_angle, end_angle).
    The center is placed on the *inward* side of the triangle.
    """
    mx, my = (sx + ex) / 2, (sy + ey) / 2
    dx, dy = ex - sx, ey - sy
    half_chord = math.sqrt(dx * dx + dy * dy) / 2.0
    h_arc = math.sqrt(max(radius * radius - half_chord * half_chord, 0.0))
    # Perpendicular direction pointing inward (to the left of start→end)
    perp_x, perp_y = -dy / (2 * half_chord), dx / (2 * half_chord)
    cx, cy = mx + h_arc * perp_x, my + h_arc * perp_y
    sa = math.atan2(sy - cy, sx - cx)
    ea = math.atan2(ey - cy, ex - cx)
    # Ensure CCW sweep (positive direction)
    if ea < sa:
        ea += 2 * math.pi
    return (cx, cy), sa, ea


# ── Build the sketch ────────────────────────────────────────
s = Sketch()

# Six tangent-point vertices
p_bs = s.add_fixed_point(*bs)  # anchor one point
p_be = s.add_point(*be)
p_rs = s.add_point(*rs)
p_re = s.add_point(*re)
p_ls = s.add_point(*ls)
p_le = s.add_point(*le)

# Three straight edges
line_b = s.add_line(p_bs, p_be)  # bottom
line_r = s.add_line(p_rs, p_re)  # right
line_l = s.add_line(p_ls, p_le)  # left

# Radius parameter – fixed so the solver treats it as a driving value
rad = s.add_fixed_param(r)

# Three corner arcs – each arc needs its own center point and angles.
# We use add_arc_cse to create arcs from center/start/end points,
# then coincident constraints to tie the arc endpoints to the tangent points.

# Bottom-left corner arc: from p_le to p_bs
center_bl, sa_bl, ea_bl = _arc_center_and_angles(*le, *bs, r)
c_bl = s.add_point(*center_bl)
arc_bl = s.add_arc_cse(c_bl, p_le, p_bs, r, sa_bl, ea_bl)

# Bottom-right corner arc: from p_be to p_rs
center_br, sa_br, ea_br = _arc_center_and_angles(*be, *rs, r)
c_br = s.add_point(*center_br)
arc_br = s.add_arc_cse(c_br, p_be, p_rs, r, sa_br, ea_br)

# Top corner arc: from p_re to p_ls
center_top, sa_top, ea_top = _arc_center_and_angles(*re, *ls, r)
c_top = s.add_point(*center_top)
arc_top = s.add_arc_cse(c_top, p_re, p_ls, r, sa_top, ea_top)

# ── Tangency constraints ────────────────────────────────────
# Each arc must be tangent to its two adjacent lines.
s.tangent_line_arc(line_b, arc_bl)
s.tangent_line_arc(line_b, arc_br)
s.tangent_line_arc(line_r, arc_br)
s.tangent_line_arc(line_r, arc_top)
s.tangent_line_arc(line_l, arc_top)
s.tangent_line_arc(line_l, arc_bl)

# ── Arc radius constraints ──────────────────────────────────
# Constrain each arc's radius to the shared parameter.
s.arc_radius(arc_bl, rad)
s.arc_radius(arc_br, rad)
s.arc_radius(arc_top, rad)

# ── Equilateral constraint ──────────────────────────────────
s.equal_length(line_b, line_r)
s.equal_length(line_r, line_l)

# ── Positioning and sizing ──────────────────────────────────
s.horizontal(line_b)  # bottom is horizontal
s.set_p2p_distance(p_bs, p_be, side - 2 * t)  # set edge length

# ── Solve ───────────────────────────────────────────────────
status = s.solve()
assert status == SolveStatus.Success

# ── Read results ────────────────────────────────────────────
for name, pid in [
    ("bs", p_bs),
    ("be", p_be),
    ("rs", p_rs),
    ("re", p_re),
    ("ls", p_ls),
    ("le", p_le),
]:
    x, y = s.get_point(pid)
    print(f"{name}: ({x:.4f}, {y:.4f})")
