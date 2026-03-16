"""Tests for conic-specific constraints: point-on, equal, internal alignment."""

import math

import pytest

from planegcs import (
    InternalAlignmentType,
    Sketch,
    SolveStatus,
)


def _dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# ── Point-on constraints for conic arcs ──────────────────────────


def test_point_on_hyperbolic_arc():
    """A point constrained to lie on an arc of hyperbola."""
    s = Sketch()
    center = s.add_point(0, 0)
    focus1 = s.add_point(5, 0)
    start = s.add_point(4, 0)
    end = s.add_point(6.2, 3.5)
    aoh = s.add_arc_of_hyperbola(
        center,
        focus1,
        radmin=3.0,
        start_angle=0.0,
        end_angle=1.0,
        start_id=start,
        end_id=end,
    )

    pt = s.add_point(5.0, 2.0)  # initial guess
    tag = s.point_on_hyperbolic_arc(pt, aoh)
    assert tag > 0

    s.fix_point(center, 0, 0)
    s.fix_point(focus1, 5, 0)
    # Fix x to constrain the point
    px = s.add_fixed_param(4.0)
    s.coordinate_x(pt, px)

    status = s.solve()
    assert status == SolveStatus.Success

    # Verify the point lies on the hyperbola: radmaj=4, radmin=3
    # x = 4*cosh(u), y = 3*sinh(u)
    # At x=4: cosh(u) = 1, u=0, y=0
    pt_val = s.get_point(pt)
    # On hyperbola: (x/4)^2 - (y/3)^2 = 1
    hx = pt_val[0] / 4.0
    hy = pt_val[1] / 3.0
    assert hx**2 - hy**2 == pytest.approx(1.0, abs=0.1)


def test_point_on_parabolic_arc():
    """A point constrained to lie on an arc of parabola."""
    s = Sketch()
    vertex = s.add_point(0, 0)
    focus1 = s.add_point(1, 0)
    start = s.add_point(0, 0)
    end = s.add_point(1, 2)
    aop = s.add_arc_of_parabola(
        vertex,
        focus1,
        start_angle=0.0,
        end_angle=2.0,
        start_id=start,
        end_id=end,
    )

    pt = s.add_point(0.5, 1.0)  # guess
    tag = s.point_on_parabolic_arc(pt, aop)
    assert tag > 0

    s.fix_point(vertex, 0, 0)
    s.fix_point(focus1, 1, 0)
    # Fix y to constrain
    py_param = s.add_fixed_param(2.0)
    s.coordinate_y(pt, py_param)

    status = s.solve()
    assert status == SolveStatus.Success

    # Parabola: y^2 = 4*f*x, f=1, so x = y^2/4 = 1.0
    pt_val = s.get_point(pt)
    assert pt_val[0] == pytest.approx(1.0, abs=0.1)


# ── Equal constraints for conics ─────────────────────────────────


def test_equal_radii_ee():
    """Two ellipses constrained to have equal major radii."""
    s = Sketch()
    c1 = s.add_point(0, 0)
    f1 = s.add_point(3, 0)
    e1 = s.add_ellipse(c1, f1, radmin=4.0)

    c2 = s.add_point(10, 0)
    f2 = s.add_point(12, 0)  # different focus distance
    e2 = s.add_ellipse(c2, f2, radmin=3.0)  # different radmin

    tag = s.equal_radii_ee(e1, e2)
    assert tag > 0

    # Fix the first ellipse
    s.fix_point(c1, 0, 0)
    s.fix_point(f1, 3, 0)
    s.fix_point(c2, 10, 0)

    status = s.solve()
    assert status == SolveStatus.Success

    # The major radii should be equal
    info1 = s.get_ellipse(e1)
    info2 = s.get_ellipse(e2)
    # radmaj1 = sqrt(3^2 + 4^2) = 5
    d1 = _dist(info1.center, info1.focus1)
    radmaj1 = math.sqrt(d1**2 + info1.radmin**2)
    d2 = _dist(info2.center, info2.focus1)
    radmaj2 = math.sqrt(d2**2 + info2.radmin**2)
    assert radmaj1 == pytest.approx(radmaj2, abs=0.1)


def test_equal_focus_pp():
    """Two arcs of parabola constrained to have equal focal distance."""
    s = Sketch()
    v1 = s.add_point(0, 0)
    f1 = s.add_point(1, 0)
    s1 = s.add_point(0, 0)
    e1 = s.add_point(1, 2)
    ap1 = s.add_arc_of_parabola(v1, f1, start_angle=0.0, end_angle=2.0, start_id=s1, end_id=e1)

    v2 = s.add_point(5, 0)
    f2 = s.add_point(7, 0)  # different focal distance initially
    s2 = s.add_point(5, 0)
    e2 = s.add_point(6, 2)
    ap2 = s.add_arc_of_parabola(v2, f2, start_angle=0.0, end_angle=2.0, start_id=s2, end_id=e2)

    tag = s.equal_focus_pp(ap1, ap2)
    assert tag > 0

    s.fix_point(v1, 0, 0)
    s.fix_point(f1, 1, 0)
    s.fix_point(v2, 5, 0)

    status = s.solve()
    assert status == SolveStatus.Success

    # Focal distances should be equal
    info1 = s.get_arc_of_parabola(ap1)
    info2 = s.get_arc_of_parabola(ap2)
    fd1 = _dist(info1.vertex, info1.focus1)
    fd2 = _dist(info2.vertex, info2.focus1)
    assert fd1 == pytest.approx(fd2, abs=0.1)


# ── Internal alignment constraints ──────────────────────────────


def test_internal_alignment_ellipse_focus2():
    """Internal alignment constrains a point to ellipse focus 2."""
    s = Sketch()
    center = s.add_point(0, 0)
    focus1 = s.add_point(3, 0)
    ell = s.add_ellipse(center, focus1, radmin=4.0)

    focus2_pt = s.add_point(-2, 0)  # guess
    tag = s.internal_alignment_ellipse_focus2(ell, focus2_pt)
    assert tag > 0

    s.fix_point(center, 0, 0)
    s.fix_point(focus1, 3, 0)

    status = s.solve()
    assert status == SolveStatus.Success

    # Focus 2 should be at (-3, 0) for center=(0,0), focus1=(3,0)
    f2 = s.get_point(focus2_pt)
    assert f2[0] == pytest.approx(-3.0, abs=1e-3)
    assert f2[1] == pytest.approx(0.0, abs=1e-3)


def test_internal_alignment_ellipse_major_diameter():
    """Internal alignment ties two points to ellipse major axis endpoints."""
    s = Sketch()
    center = s.add_point(0, 0)
    focus1 = s.add_point(3, 0)
    ell = s.add_ellipse(center, focus1, radmin=4.0)

    p1 = s.add_point(5, 0)  # positive major end
    p2 = s.add_point(-5, 0)  # negative major end
    tag = s.internal_alignment_ellipse_major_diameter(ell, p1, p2)
    assert tag > 0

    s.fix_point(center, 0, 0)
    s.fix_point(focus1, 3, 0)

    status = s.solve()
    assert status == SolveStatus.Success

    # radmaj = sqrt(9 + 16) = 5
    p1_val = s.get_point(p1)
    p2_val = s.get_point(p2)
    assert p1_val[0] == pytest.approx(5.0, abs=1e-3)
    assert p1_val[1] == pytest.approx(0.0, abs=1e-3)
    assert p2_val[0] == pytest.approx(-5.0, abs=1e-3)
    assert p2_val[1] == pytest.approx(0.0, abs=1e-3)


def test_internal_alignment_ellipse_minor_diameter():
    """Internal alignment ties two points to ellipse minor axis endpoints."""
    s = Sketch()
    center = s.add_point(0, 0)
    focus1 = s.add_point(3, 0)
    ell = s.add_ellipse(center, focus1, radmin=4.0)

    p1 = s.add_point(0, 4)  # positive minor end
    p2 = s.add_point(0, -4)  # negative minor end
    tag = s.internal_alignment_ellipse_minor_diameter(ell, p1, p2)
    assert tag > 0

    s.fix_point(center, 0, 0)
    s.fix_point(focus1, 3, 0)

    status = s.solve()
    assert status == SolveStatus.Success

    p1_val = s.get_point(p1)
    p2_val = s.get_point(p2)
    assert p1_val[0] == pytest.approx(0.0, abs=1e-3)
    assert p1_val[1] == pytest.approx(4.0, abs=1e-3)
    assert p2_val[0] == pytest.approx(0.0, abs=1e-3)
    assert p2_val[1] == pytest.approx(-4.0, abs=1e-3)


def test_internal_alignment_ellipse_focus1():
    """Internal alignment constrains a point to ellipse focus 1."""
    s = Sketch()
    center = s.add_point(0, 0)
    focus1 = s.add_point(3, 0)
    ell = s.add_ellipse(center, focus1, radmin=4.0)

    focus1_pt = s.add_point(2, 1)  # guess
    tag = s.internal_alignment_ellipse_focus1(ell, focus1_pt)
    assert tag > 0

    s.fix_point(center, 0, 0)
    s.fix_point(focus1, 3, 0)

    status = s.solve()
    assert status == SolveStatus.Success

    f1 = s.get_point(focus1_pt)
    assert f1[0] == pytest.approx(3.0, abs=1e-3)
    assert f1[1] == pytest.approx(0.0, abs=1e-3)


def test_equal_radii_hh():
    """Two arcs of hyperbola constrained to equal major radii."""
    s = Sketch()
    c1 = s.add_point(0, 0)
    f1 = s.add_point(5, 0)
    s1 = s.add_point(4, 0)
    e1 = s.add_point(6, 4)
    ah1 = s.add_arc_of_hyperbola(
        c1, f1, radmin=3.0, start_angle=0.0, end_angle=1.0, start_id=s1, end_id=e1
    )

    c2 = s.add_point(10, 0)
    f2 = s.add_point(14, 0)
    s2 = s.add_point(13, 0)
    e2 = s.add_point(15, 3)
    ah2 = s.add_arc_of_hyperbola(
        c2, f2, radmin=2.0, start_angle=0.0, end_angle=1.0, start_id=s2, end_id=e2
    )

    tag = s.equal_radii_hh(ah1, ah2)
    assert tag > 0

    s.fix_point(c1, 0, 0)
    s.fix_point(f1, 5, 0)
    s.fix_point(c2, 10, 0)

    status = s.solve()
    assert status == SolveStatus.Success


def test_internal_alignment_hyperbola_major_diameter():
    """Internal alignment ties two points to hyperbola major axis endpoints."""
    s = Sketch()
    center = s.add_point(0, 0)
    focus1 = s.add_point(5, 0)
    hyp = s.add_hyperbola(center, focus1, radmin=3.0)

    # radmaj = sqrt(25-9) = 4
    p1 = s.add_point(4, 0)
    p2 = s.add_point(-4, 0)
    tag = s.internal_alignment_hyperbola_major_diameter(hyp, p1, p2)
    assert tag > 0

    s.fix_point(center, 0, 0)
    s.fix_point(focus1, 5, 0)

    status = s.solve()
    assert status == SolveStatus.Success

    p1_val = s.get_point(p1)
    p2_val = s.get_point(p2)
    assert p1_val[0] == pytest.approx(4.0, abs=1e-3)
    assert p2_val[0] == pytest.approx(-4.0, abs=1e-3)


def test_internal_alignment_hyperbola_minor_diameter():
    """Internal alignment ties two points to hyperbola minor axis endpoints."""
    s = Sketch()
    center = s.add_point(0, 0)
    focus1 = s.add_point(5, 0)
    hyp = s.add_hyperbola(center, focus1, radmin=3.0)

    p1 = s.add_point(0, 3)
    p2 = s.add_point(0, -3)
    tag = s.internal_alignment_hyperbola_minor_diameter(hyp, p1, p2)
    assert tag > 0

    s.fix_point(center, 0, 0)
    s.fix_point(focus1, 5, 0)

    status = s.solve()
    assert status == SolveStatus.Success

    # The two points should be symmetric about the center
    p1_val = s.get_point(p1)
    p2_val = s.get_point(p2)
    assert p1_val[1] == pytest.approx(-p2_val[1], abs=1e-2)


def test_internal_alignment_point2hyperbola():
    """Internal alignment constrains a point relative to a hyperbola."""
    s = Sketch()
    center = s.add_point(0, 0)
    focus1 = s.add_point(5, 0)
    hyp = s.add_hyperbola(center, focus1, radmin=3.0)

    pt = s.add_point(4, 1)  # guess for positive major X
    tag = s.internal_alignment_point2hyperbola(
        hyp, pt, InternalAlignmentType.HyperbolaPositiveMajorX
    )
    assert tag > 0

    s.fix_point(center, 0, 0)
    s.fix_point(focus1, 5, 0)

    status = s.solve()
    assert status == SolveStatus.Success

    # radmaj = 4, so positive major X = 4
    pt_val = s.get_point(pt)
    assert pt_val[0] == pytest.approx(4.0, abs=1e-3)


def test_internal_alignment_hyperbola_focus():
    """Internal alignment constrains a point to hyperbola focus."""
    s = Sketch()
    center = s.add_point(0, 0)
    focus1 = s.add_point(5, 0)
    hyp = s.add_hyperbola(center, focus1, radmin=3.0)

    focus_pt = s.add_point(4, 1)  # guess
    tag = s.internal_alignment_hyperbola_focus(hyp, focus_pt)
    assert tag > 0

    s.fix_point(center, 0, 0)
    s.fix_point(focus1, 5, 0)

    status = s.solve()
    assert status == SolveStatus.Success

    f = s.get_point(focus_pt)
    assert f[0] == pytest.approx(5.0, abs=1e-3)
    assert f[1] == pytest.approx(0.0, abs=1e-3)


def test_internal_alignment_parabola_focus():
    """Internal alignment constrains a point to parabola focus."""
    s = Sketch()
    vertex = s.add_point(0, 0)
    focus1 = s.add_point(1, 0)
    par = s.add_parabola(vertex, focus1)

    focus_pt = s.add_point(0.5, 0.5)  # guess
    tag = s.internal_alignment_parabola_focus(par, focus_pt)
    assert tag > 0

    s.fix_point(vertex, 0, 0)
    s.fix_point(focus1, 1, 0)

    status = s.solve()
    assert status == SolveStatus.Success

    f = s.get_point(focus_pt)
    assert f[0] == pytest.approx(1.0, abs=1e-3)
    assert f[1] == pytest.approx(0.0, abs=1e-3)
