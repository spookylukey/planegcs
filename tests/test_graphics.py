"""Tests for planegcs.graphics — sketch_to_image.

These tests exercise code paths for coverage.  Visual correctness
should be verified by inspecting saved images (see visual_test_graphics.py).
"""

import math

from planegcs import Sketch
from planegcs.graphics import sketch_to_image


def test_empty_sketch():
    """An empty sketch returns a blank image."""
    s = Sketch()
    img = sketch_to_image(s)
    assert img.size == (200, 200)  # default empty size


def test_empty_sketch_custom_size():
    s = Sketch()
    img = sketch_to_image(s, width=300, height=150)
    assert img.size == (300, 150)


def test_single_point():
    """Degenerate bbox — all geometry at one location."""
    s = Sketch()
    s.add_point(5.0, 5.0)
    img = sketch_to_image(s)
    assert img.size[0] > 0 and img.size[1] > 0


def test_line():
    s = Sketch()
    p1 = s.add_point(0.0, 0.0)
    p2 = s.add_point(10.0, 5.0)
    s.add_line(p1, p2)
    img = sketch_to_image(s)
    assert img.size[0] > 0


def test_circle():
    s = Sketch()
    c = s.add_point(0.0, 0.0)
    s.add_circle(c, s.add_fixed_param(5.0))
    img = sketch_to_image(s)
    assert img.size[0] > 0


def test_arc():
    s = Sketch()
    a = s.add_arc3p((5.0, 5.0), 3.0, 0.0, math.pi / 2)
    img = sketch_to_image(s)
    assert img.size[0] > 0
    # Also verify arc info is read correctly
    info = s.get_arc(a)
    assert info.radius > 0


def test_ellipse():
    s = Sketch()
    center = s.add_point(0.0, 0.0)
    focus = s.add_point(3.0, 0.0)
    s.add_ellipse(center, focus, 2.0)
    img = sketch_to_image(s)
    assert img.size[0] > 0


def test_ellipse_circular():
    """Ellipse with focus at center (degenerate — effectively a circle)."""
    s = Sketch()
    center = s.add_point(0.0, 0.0)
    focus = s.add_point(0.0, 0.0)  # same as center
    s.add_ellipse(center, focus, 3.0)
    img = sketch_to_image(s)
    assert img.size[0] > 0


def test_mixed_geometry():
    """Sketch with lines, circles, and arcs."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(10, 0)
    p3 = s.add_point(10, 10)
    s.add_line(p1, p2)
    s.add_line(p2, p3)
    c = s.add_point(5, 5)
    s.add_circle(c, s.add_fixed_param(3.0))
    s.add_arc3p((5, 0), 2.0, 0.0, math.pi)
    s.solve()
    img = sketch_to_image(s)
    assert img.size[0] > 0


def test_scale_override():
    s = Sketch()
    p1 = s.add_point(0.0, 0.0)
    p2 = s.add_point(10.0, 0.0)
    s.add_line(p1, p2)
    img = sketch_to_image(s, scale=50.0)
    # 10 units * 50 px/unit + 2*40 padding = 580
    assert img.size[0] == 580


def test_width_only():
    s = Sketch()
    p1 = s.add_point(0.0, 0.0)
    p2 = s.add_point(10.0, 5.0)
    s.add_line(p1, p2)
    img = sketch_to_image(s, width=400)
    assert img.size[0] == 400


def test_height_only():
    s = Sketch()
    p1 = s.add_point(0.0, 0.0)
    p2 = s.add_point(10.0, 5.0)
    s.add_line(p1, p2)
    img = sketch_to_image(s, height=300)
    assert img.size[1] == 300


def test_width_and_height():
    s = Sketch()
    p1 = s.add_point(0.0, 0.0)
    p2 = s.add_point(10.0, 5.0)
    s.add_line(p1, p2)
    img = sketch_to_image(s, width=600, height=400)
    assert img.size == (600, 400)


def test_custom_colors():
    s = Sketch()
    p1 = s.add_point(0, 0)
    p2 = s.add_point(5, 5)
    s.add_line(p1, p2)
    c = s.add_point(2.5, 2.5)
    s.add_circle(c, s.add_fixed_param(1.0))
    img = sketch_to_image(
        s,
        background="black",
        line_color="white",
        circle_color="yellow",
        point_color="red",
        line_width=3,
        point_radius=5,
    )
    assert img.size[0] > 0


def test_to_image_method():
    """Verify the Sketch.to_image() convenience method."""
    s = Sketch()
    s.add_point(1.0, 2.0)
    img = s.to_image(padding=20)
    assert img is not None
