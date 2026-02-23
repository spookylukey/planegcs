#!/usr/bin/env python
"""One-off visual tests for planegcs.graphics.

Generates a selection of sketches, renders them with to_image(), and saves
them to visual_test_output/ for manual inspection.

Not part of the automated test suite.
"""

import math
import os

from planegcs import Sketch, SolveStatus

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "visual_test_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save(sketch, name, **kwargs):
    img = sketch.to_image(**kwargs)
    path = os.path.join(OUTPUT_DIR, f"{name}.png")
    img.save(path)
    print(f"  Saved {path}  ({img.size[0]}x{img.size[1]})")
    return path


# ── 1. Equilateral triangle ───────────────────────────────────────
print("1. Equilateral triangle")
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
assert s.solve() == SolveStatus.Success
save(s, "01_equilateral_triangle")


# ── 2. Right triangle ────────────────────────────────────────────
print("2. Right triangle (3-4-5)")
s = Sketch()
p1 = s.add_fixed_point(0, 0)
p2 = s.add_point(3, 0)
p3 = s.add_point(0, 4)
l_base = s.add_line(p1, p2)
l_height = s.add_line(p1, p3)
l_hyp = s.add_line(p2, p3)
s.horizontal(l_base)
s.vertical(l_height)
s.perpendicular(l_base, l_height)
s.set_p2p_distance(p1, p2, 3.0)
s.set_p2p_distance(p1, p3, 4.0)
assert s.solve() == SolveStatus.Success
save(s, "02_right_triangle")


# ── 3. Circle ─────────────────────────────────────────────────────
print("3. Circle")
s = Sketch()
c = s.add_point(0, 0)
s.add_circle(c, s.add_param(5.0))
save(s, "03_circle")


# ── 4. Two concentric circles ────────────────────────────────────
print("4. Concentric circles")
s = Sketch()
c = s.add_point(0, 0)
s.add_circle(c, s.add_param(3.0))
s.add_circle(c, s.add_param(5.0))
save(s, "04_concentric_circles")


# ── 5. Arc (quarter circle) ──────────────────────────────────────
print("5. Quarter circle arc")
s = Sketch()
s.add_arc3p((0, 0), 5.0, 0.0, math.pi / 2)
save(s, "05_quarter_arc")


# ── 6. Arc (three-quarter circle, CW) ───────────────────────────
print("6. Three-quarter arc")
s = Sketch()
s.add_arc3p((0, 0), 5.0, 0.0, 3 * math.pi / 2)
save(s, "06_three_quarter_arc")


# ── 7. Semicircle arc ────────────────────────────────────────────
print("7. Semicircle arc")
s = Sketch()
s.add_arc3p((0, 0), 4.0, -math.pi / 2, math.pi / 2)
save(s, "07_semicircle_arc")


# ── 8. Ellipse (axis-aligned) ────────────────────────────────────
print("8. Ellipse (axis-aligned)")
s = Sketch()
center = s.add_point(0, 0)
focus = s.add_point(3, 0)  # c=3, so a=sqrt(9+4)=sqrt(13)~3.6, b=2
s.add_ellipse(center, focus, 2.0)
save(s, "08_ellipse_axis_aligned")


# ── 9. Ellipse (tilted) ─────────────────────────────────────────
print("9. Ellipse (tilted 45°)")
s = Sketch()
center = s.add_point(0, 0)
# Focus at 45 degrees, distance 2
focus = s.add_point(math.sqrt(2), math.sqrt(2))
s.add_ellipse(center, focus, 1.5)
save(s, "09_ellipse_tilted")


# ── 10. Square (four lines, constrained) ─────────────────────────
print("10. Square")
s = Sketch()
p1 = s.add_fixed_point(0, 0)
p2 = s.add_point(5, 0)
p3 = s.add_point(5, 5)
p4 = s.add_point(0, 5)
l1 = s.add_line(p1, p2)
l2 = s.add_line(p2, p3)
l3 = s.add_line(p3, p4)
l4 = s.add_line(p4, p1)
s.horizontal(l1)
s.horizontal(l3)
s.vertical(l2)
s.vertical(l4)
s.equal_length(l1, l2)
s.set_p2p_distance(p1, p2, 5.0)
assert s.solve() == SolveStatus.Success
save(s, "10_square")


# ── 11. Mixed: triangle with inscribed circle ────────────────────
print("11. Triangle with inscribed circle")
s = Sketch()
p1 = s.add_fixed_point(0, 0)
p2 = s.add_point(10, 0)
p3 = s.add_point(5, 8)
l1 = s.add_line(p1, p2)
l2 = s.add_line(p2, p3)
l3 = s.add_line(p3, p1)
s.horizontal(l1)
s.set_p2p_distance(p1, p2, 10.0)
assert s.solve() == SolveStatus.Success
# Add a circle at approximate incenter
c = s.add_point(5, 2.5)
s.add_circle(c, s.add_param(2.5))
save(s, "11_triangle_with_circle")


# ── 12. Multiple arcs (house shape with arched roof) ─────────────
print("12. House with arched roof")
s = Sketch()
p1 = s.add_fixed_point(0, 0)
p2 = s.add_point(6, 0)
p3 = s.add_point(6, 4)
p4 = s.add_point(0, 4)
s.add_line(p1, p2)  # bottom
s.add_line(p2, p3)  # right
s.add_line(p4, p1)  # left
# Arched roof: semicircle from p4 to p3
s.add_arc3p((3, 4), 3.0, 0.0, math.pi)
save(s, "12_house_with_arch")


# ── 13. Custom colors on dark background ─────────────────────────
print("13. Custom colors")
s = Sketch()
p1 = s.add_fixed_point(0, 0)
p2 = s.add_point(8, 0)
p3 = s.add_point(8, 6)
p4 = s.add_point(0, 6)
s.add_line(p1, p2)
s.add_line(p2, p3)
s.add_line(p3, p4)
s.add_line(p4, p1)
c = s.add_point(4, 3)
s.add_circle(c, s.add_param(2.5))
save(
    s,
    "13_custom_colors",
    background="#1e1e2e",
    line_color="#89b4fa",
    circle_color="#f38ba8",
    point_color="#a6e3a1",
    line_width=3,
    point_radius=5,
)


# ── 14. Clockwise arc ────────────────────────────────────────────
print("14. Clockwise arc")
s = Sketch()
# CW arc: end_angle < start_angle
s.add_arc3p((0, 0), 5.0, math.pi / 2, 0.0)
save(s, "14_clockwise_arc")


print(f"\nAll images saved to {OUTPUT_DIR}/")
