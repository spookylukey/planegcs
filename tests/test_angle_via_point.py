"""Tests for *ViaPoint constraint support."""

import math
from typing import cast

import pytest

from planegcs import LineId, Sketch, SolveStatus


def _approx(val: float, *, abs: float = 1e-6):
    return pytest.approx(val, abs=abs)


# ── angle_via_point: two lines meeting at a point ─────────────────


class TestAngleViaPointTwoLines:
    """Basic angle-via-point between two lines meeting at the origin."""

    def test_right_angle(self):
        s = Sketch()
        origin = s.add_fixed_point(0, 0)
        p1 = s.add_point(3, 0)
        p2 = s.add_point(0, 3)
        l1 = s.add_line(origin, p1)
        l2 = s.add_line(origin, p2)

        # Constrain the angle at the origin to pi/2
        s.set_angle_via_point(l1, l2, origin, math.pi / 2)

        status = s.solve()
        assert status == SolveStatus.Success

        measured = s.calculate_angle_via_point(l1, l2, origin)
        assert measured == _approx(math.pi / 2)

    def test_acute_angle(self):
        s = Sketch()
        origin = s.add_fixed_point(0, 0)
        p1 = s.add_fixed_point(5, 0)
        p2 = s.add_point(3, 3)
        l1 = s.add_line(origin, p1)
        l2 = s.add_line(origin, p2)

        target = math.pi / 6  # 30 degrees
        s.set_angle_via_point(l1, l2, origin, target)
        status = s.solve()
        assert status == SolveStatus.Success

        measured = s.calculate_angle_via_point(l1, l2, origin)
        assert measured == _approx(target)


# ── angle_via_point: line and circle ──────────────────────────────


class TestAngleViaPointLineCircle:
    """Angle between a line and a circle at a point on both."""

    def test_line_circle_angle(self):
        s = Sketch()
        # Circle centred at origin, radius 5
        center = s.add_fixed_point(0, 0)
        circ = s.add_circle(center, s.add_param(5.0))

        # A point on the circle (will be intersection)
        pt = s.add_point(5, 0)
        s.point_on_circle(pt, circ)

        # A line through the point
        p_far = s.add_point(10, 5)
        line = s.add_line(pt, p_far)
        s.coincident(pt, pt)  # already coincident, but ensure

        # Constrain angle at pt between line and circle to 45 deg
        target = math.pi / 4
        s.set_angle_via_point(line, circ, pt, target)

        status = s.solve()
        assert status == SolveStatus.Success

        measured = s.calculate_angle_via_point(line, circ, pt)
        assert measured == _approx(target)


# ── calculate_angle_via_point (query, no constraint) ──────────────


class TestCalculateAngleViaPoint:
    """Test the query-only calculate functions."""

    def test_perpendicular_lines(self):
        s = Sketch()
        o = s.add_fixed_point(0, 0)
        px = s.add_fixed_point(1, 0)
        py = s.add_fixed_point(0, 1)
        l1 = s.add_line(o, px)
        l2 = s.add_line(o, py)

        angle = s.calculate_angle_via_point(l1, l2, o)
        assert angle == _approx(math.pi / 2)

    def test_parallel_lines(self):
        """Two collinear lines should give angle ~0 or ~pi."""
        s = Sketch()
        o = s.add_fixed_point(0, 0)
        p1 = s.add_fixed_point(1, 0)
        p2 = s.add_fixed_point(2, 0)
        l1 = s.add_line(o, p1)
        l2 = s.add_line(o, p2)

        angle = s.calculate_angle_via_point(l1, l2, o)
        # Parallel/collinear → angle is 0 or pi
        assert abs(math.sin(angle)) == _approx(0.0)


# ── curve_value: point on curve at parameter u ────────────────────


class TestCurveValue:
    def test_point_on_circle(self):
        s = Sketch()
        center = s.add_fixed_point(0, 0)
        circ = s.add_circle(center, s.add_param(5.0))
        s.set_circle_radius(circ, 5.0)

        pt = s.add_point(5, 0)
        u = s.add_param(0.0, fixed=True)  # u=0 → rightmost point
        s.curve_value(pt, circ, u)

        status = s.solve()
        assert status == SolveStatus.Success

        x, y = s.get_point(pt)
        assert x == _approx(5.0)
        assert y == _approx(0.0)

    def test_point_on_circle_quarter(self):
        s = Sketch()
        center = s.add_fixed_point(0, 0)
        circ = s.add_circle(center, s.add_param(5.0))
        s.set_circle_radius(circ, 5.0)

        pt = s.add_point(0, 5)
        u = s.add_param(math.pi / 2, fixed=True)  # u=pi/2 → top
        s.curve_value(pt, circ, u)

        status = s.solve()
        assert status == SolveStatus.Success

        x, y = s.get_point(pt)
        assert x == _approx(0.0)
        assert y == _approx(5.0)


# ── get_curve error for unknown ID ────────────────────────────────


class TestGetCurveError:
    def test_unknown_curve_raises(self):
        s = Sketch()
        pt = s.add_point(0, 0)
        u = s.add_param(0.0)
        with pytest.raises(IndexError, match="get_curve"):
            # 9999 is not a valid geometry id
            s.curve_value(pt, LineId(9999), u)


# ── angle_via_two_points ──────────────────────────────────────────


class TestAngleViaTwoPoints:
    """Angle between two curves measured at two distinct points."""

    def test_two_lines_two_points(self):
        s = Sketch()
        # Two lines sharing no point, but we measure angle at one point on each
        p1 = s.add_fixed_point(0, 0)
        p2 = s.add_fixed_point(5, 0)
        p3 = s.add_fixed_point(0, 0)
        p4 = s.add_point(0, 5)
        l1 = s.add_line(p1, p2)  # horizontal
        l2 = s.add_line(p3, p4)  # vertical-ish

        target = math.pi / 2
        s.set_angle_via_two_points(l1, l2, p1, p3, target)

        status = s.solve()
        assert status == SolveStatus.Success

        measured = s.calculate_angle_via_two_points(l1, l2, p1, p3)
        assert measured == _approx(target)

    def test_angle_via_two_points_param_api(self):
        """Use the param-based angle_via_two_points (not the set_ convenience)."""
        s = Sketch()
        p1 = s.add_fixed_point(0, 0)
        p2 = s.add_fixed_point(5, 0)
        p3 = s.add_fixed_point(0, 0)
        p4 = s.add_point(3, 3)
        l1 = s.add_line(p1, p2)
        l2 = s.add_line(p3, p4)

        angle_param = s.add_param(math.pi / 2, fixed=True)
        tag = s.angle_via_two_points(l1, l2, p1, p3, angle_param)
        assert tag > 0

        status = s.solve()
        assert status == SolveStatus.Success


# ── angle_via_point_and_param / angle_via_point_and_two_params ────


class TestAngleViaPointAndParam:
    """Test the *_and_param variants."""

    def test_angle_via_point_and_param(self):
        s = Sketch()
        center = s.add_fixed_point(0, 0)
        circ = s.add_circle(center, s.add_param(5.0))
        s.set_circle_radius(circ, 5.0)

        origin = s.add_fixed_point(0, 0)
        px = s.add_fixed_point(5, 0)
        line = s.add_line(origin, px)

        pt = s.add_point(5, 0)
        s.point_on_circle(pt, circ)

        cparam = s.add_param(0.0, fixed=False)
        angle_p = s.add_param(math.pi / 4, fixed=True)
        tag = s.angle_via_point_and_param(line, circ, pt, cparam, angle_p)
        assert tag > 0

        status = s.solve()
        assert status == SolveStatus.Success

    def test_angle_via_point_and_two_params(self):
        s = Sketch()
        center1 = s.add_fixed_point(0, 0)
        circ1 = s.add_circle(center1, s.add_param(5.0))
        s.set_circle_radius(circ1, 5.0)

        center2 = s.add_fixed_point(10, 0)
        circ2 = s.add_circle(center2, s.add_param(5.0))
        s.set_circle_radius(circ2, 5.0)

        # Point at (5, 0) is on both circles
        pt = s.add_point(5, 0)
        s.point_on_circle(pt, circ1)
        s.point_on_circle(pt, circ2)

        cp1 = s.add_param(0.0, fixed=False)
        cp2 = s.add_param(math.pi, fixed=False)
        angle_p = s.add_param(math.pi, fixed=True)
        tag = s.angle_via_point_and_two_params(circ1, circ2, pt, cp1, cp2, angle_p)
        assert tag > 0

        status = s.solve()
        assert status == SolveStatus.Success


# ── snells_law ────────────────────────────────────────────────────


class TestSnellsLaw:
    """Test Snell's law refraction constraint."""

    def test_snells_law_basic(self):
        """Set up two rays and a boundary line, constrain with Snell's law."""
        s = Sketch()
        # Boundary: horizontal line
        bp1 = s.add_fixed_point(-10, 0)
        bp2 = s.add_fixed_point(10, 0)
        boundary = s.add_line(bp1, bp2)

        # Refraction point
        pt = s.add_fixed_point(0, 0)

        # Incoming ray from upper-left
        rp1 = s.add_fixed_point(-5, 5)
        ray1 = s.add_line(rp1, pt)

        # Outgoing ray to lower-right (solver adjusts)
        rp2 = s.add_point(3, -4)
        ray2 = s.add_line(pt, rp2)

        n1 = s.add_param(1.0, fixed=True)  # refractive index medium 1
        n2 = s.add_param(1.5, fixed=True)  # refractive index medium 2

        tag = s.snells_law(
            ray1,
            ray2,
            boundary,
            pt,
            n1,
            n2,
        )
        assert tag > 0

        status = s.solve()
        assert status == SolveStatus.Success


# ── CurveId import ────────────────────────────────────────────────


def test_curveid_importable():
    from planegcs import CurveId  # noqa: F811

    assert cast(CurveId, 42) == 42
