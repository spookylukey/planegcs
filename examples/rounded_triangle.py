"""Equilateral triangle with rounded corners.

Builds an equilateral triangle whose sharp corners are replaced by
circular arcs of a given radius.
"""

import math

from planegcs import Sketch, SolveStatus

# ── Parameters ──────────────────────────────────────────────
side = 10.0  # side length of the underlying triangle
r = 1.5  # corner arc radius

# For an interior angle of 60°, the tangent length from vertex to
# tangent point is t = r / tan(30°) = r * √3.  We need this to set
# the exact edge length in the constraint below.
t = r * math.sqrt(3)

# ── Rough initial guesses ───────────────────────────────────
# These don't need to be exact — the solver will find the right
# positions.  They just need to be in roughly the right place so
# the solver converges to the intended configuration.

# Triangle vertices
v1, v2, v3 = (0.0, 0.0), (side, 0.0), (side / 2, side * 0.87)

# Tangent points: inset each vertex along each edge by ~r.
bs = (v1[0] + r, v1[1])  # bottom-left tangent point
be = (v2[0] - r, v2[1])  # bottom-right tangent point
rs = (v2[0] - r / 2, v2[1] + r)  # right-side start
re = (v3[0] + r / 2, v3[1] - r)  # right-side end
ls = (v3[0] - r / 2, v3[1] - r)  # left-side start
le = (v1[0] + r / 2, v1[1] + r)  # left-side end

# Arc centers: roughly at each vertex, shifted inward by r.
center_bl = (v1[0] + r, v1[1] + r)
center_br = (v2[0] - r, v2[1] + r)
center_top = (v3[0], v3[1] - r)

# ── Build the sketch ────────────────────────────────────────
s = Sketch()

# Six tangent-point vertices (rough positions)
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

# Three corner arcs.  add_arc_cse takes center/start/end points
# plus rough initial values for radius and angles.  The angles
# don't need to be precise — just approximate the sweep.
c_bl = s.add_point(*center_bl)
arc_bl = s.add_arc_cse(c_bl, p_le, p_bs, r, -math.pi / 2, 0.0)

c_br = s.add_point(*center_br)
arc_br = s.add_arc_cse(c_br, p_be, p_rs, r, math.pi / 2, math.pi)

c_top = s.add_point(*center_top)
arc_top = s.add_arc_cse(c_top, p_re, p_ls, r, math.pi, 2 * math.pi)

# ── Tangency constraints ────────────────────────────────────
# Each arc must be tangent to its two adjacent lines.
s.tangent_line_arc(line_b, arc_bl)
s.tangent_line_arc(line_b, arc_br)
s.tangent_line_arc(line_r, arc_br)
s.tangent_line_arc(line_r, arc_top)
s.tangent_line_arc(line_l, arc_top)
s.tangent_line_arc(line_l, arc_bl)

# ── Arc radius constraints ──────────────────────────────────
# Constrain each arc's radius to the shared fixed parameter.
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
assert s.dof() == 0, f"{s.dof()=}"

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
