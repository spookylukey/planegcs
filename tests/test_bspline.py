"""Tests for B-spline geometry and related constraints."""

import pytest

from planegcs import (
    BSplineInfo,
    Sketch,
    SolveStatus,
)


def _make_line_bspline(s: Sketch):
    """Create a degree-1 B-spline that is effectively a line from (0,0) to (10,0).

    A degree-1 B-spline with 2 poles is just a line segment.
    Knots: [0, 1], multiplicities: [2, 2].
    """
    pole0 = s.add_point(0, 0)
    pole1 = s.add_point(10, 0)
    w0 = s.add_param(1.0)
    w1 = s.add_param(1.0)
    k0 = s.add_param(0.0, fixed=True)
    k1 = s.add_param(1.0, fixed=True)
    start = s.add_point(0, 0)
    end = s.add_point(10, 0)
    bs = s.add_bspline(
        start_id=start,
        end_id=end,
        pole_ids=[pole0, pole1],
        weight_ids=[w0, w1],
        knot_ids=[k0, k1],
        mult=[2, 2],
        degree=1,
    )
    return bs, start, end, pole0, pole1


def _make_quadratic_bspline(s: Sketch):
    """Create a degree-2 B-spline with 3 control points.

    Poles: (0,0), (5,10), (10,0)
    Knots: [0, 1], multiplicities: [3, 3] (clamped)
    """
    pole0 = s.add_point(0, 0)
    pole1 = s.add_point(5, 10)
    pole2 = s.add_point(10, 0)
    w0 = s.add_param(1.0)
    w1 = s.add_param(1.0)
    w2 = s.add_param(1.0)
    k0 = s.add_param(0.0, fixed=True)
    k1 = s.add_param(1.0, fixed=True)
    start = s.add_point(0, 0)
    end = s.add_point(10, 0)
    bs = s.add_bspline(
        start_id=start,
        end_id=end,
        pole_ids=[pole0, pole1, pole2],
        weight_ids=[w0, w1, w2],
        knot_ids=[k0, k1],
        mult=[3, 3],
        degree=2,
    )
    return bs, start, end, [pole0, pole1, pole2], [w0, w1, w2]


class TestBSplineCreation:
    def test_add_and_get(self):
        """Create a B-spline and read back properties."""
        s = Sketch()
        bs, start, end, *_ = _make_line_bspline(s)
        info = s.get_bspline(bs)
        assert isinstance(info, BSplineInfo)
        assert info.start == pytest.approx((0, 0))
        assert info.end == pytest.approx((10, 0))

    def test_entity_info(self):
        """get_entity returns correct type for B-spline."""
        s = Sketch()
        bs, *_ = _make_line_bspline(s)
        info = s.get_entity(bs)
        assert info is not None
        assert info.type == "bspline"
        assert isinstance(info.value, BSplineInfo)

    def test_quadratic_bspline(self):
        """Create a quadratic B-spline with 3 poles."""
        s = Sketch()
        bs, start, end, poles, weights = _make_quadratic_bspline(s)
        info = s.get_bspline(bs)
        assert isinstance(info, BSplineInfo)


class TestBSplineConstraints:
    def test_internal_alignment_control_point(self):
        """B-spline control point alignment with a circle."""
        s = Sketch()
        bs, start, end, poles, weights = _make_quadratic_bspline(s)

        # Create a circle to represent control point 1 (center = pole, radius = weight)
        cp_center = s.add_point(5, 10)  # same as pole1
        cp_radius = s.add_param(1.0)  # same as weight1
        cp_circle = s.add_circle(cp_center, cp_radius)

        tag = s.internal_alignment_bspline_control_point(bs, cp_circle, pole_index=1)
        assert tag > 0

        # Fix the other poles and weights
        s.fix_point(poles[0], 0, 0)
        s.fix_point(poles[2], 10, 0)

        status = s.solve()
        assert status == SolveStatus.Success

        # The circle center should coincide with pole1
        circle_info = s.get_circle(cp_circle)
        pole1_pos = s.get_point(poles[1])
        assert circle_info.center[0] == pytest.approx(pole1_pos[0], abs=1e-3)
        assert circle_info.center[1] == pytest.approx(pole1_pos[1], abs=1e-3)

    def test_curve_value_on_bspline(self):
        """Constrain a point to lie on a B-spline at a given parameter."""
        s = Sketch()
        bs, start, end, pole0, pole1 = _make_line_bspline(s)

        # Fix poles and tie start/end to poles for a clamped spline
        s.fix_point(pole0, 0, 0)
        s.fix_point(pole1, 10, 0)
        s.coincident(start, pole0)
        s.coincident(end, pole1)

        # Point constrained to be at parameter u=0.5 on the line-spline
        pt = s.add_point(5.0, 0.0)  # close initial guess needed for BSpline solver
        u = s.add_param(0.5, fixed=True)
        tag = s.curve_value(pt, bs, u)
        assert tag > 0

        status = s.solve()
        assert status == SolveStatus.Success

        pt_val = s.get_point(pt)
        assert pt_val[0] == pytest.approx(5.0, abs=0.1)
        assert pt_val[1] == pytest.approx(0.0, abs=0.1)

    def test_angle_via_point_with_bspline(self):
        """Use angle_via_point to constrain tangency at a B-spline point."""
        s = Sketch()
        bs, start, end, pole0, pole1 = _make_line_bspline(s)

        # Create a line that should be tangent at the start
        lp1 = s.add_point(0, 0)
        lp2 = s.add_point(5, 0)
        line = s.add_line(lp1, lp2)

        # Make line start coincide with spline start
        s.coincident(lp1, start)

        # Constrain tangent (angle = 0) at the start point
        angle = s.add_fixed_param(0.0)
        tag = s.angle_via_point(bs, line, start, angle)
        assert tag > 0

        s.fix_point(pole0, 0, 0)
        s.fix_point(pole1, 10, 0)

        status = s.solve()
        assert status == SolveStatus.Success

    def test_point_on_bspline(self):
        """Constrain a point to lie on a B-spline using point_on_bspline."""
        s = Sketch()
        bs, start, end, pole0, pole1 = _make_line_bspline(s)

        s.fix_point(pole0, 0, 0)
        s.fix_point(pole1, 10, 0)
        s.coincident(start, pole0)
        s.coincident(end, pole1)

        pt = s.add_point(5.0, 0.0)
        u = s.add_param(0.5, fixed=True)
        tag = s.point_on_bspline(pt, bs, u)
        assert tag > 0

        status = s.solve()
        assert status == SolveStatus.Success

        pt_val = s.get_point(pt)
        assert pt_val[0] == pytest.approx(5.0, abs=0.1)
        assert pt_val[1] == pytest.approx(0.0, abs=0.1)

    def test_internal_alignment_knot_point(self):
        """B-spline knot point alignment."""
        s = Sketch()
        # Degree-2, 4 poles, 3 knots with mult [3, 1, 3]
        # This gives an interior knot at index 1
        p0 = s.add_point(0, 0)
        p1 = s.add_point(3, 5)
        p2 = s.add_point(7, 5)
        p3 = s.add_point(10, 0)
        w0 = s.add_param(1.0)
        w1 = s.add_param(1.0)
        w2 = s.add_param(1.0)
        w3 = s.add_param(1.0)
        k0 = s.add_param(0.0, fixed=True)
        k1 = s.add_param(0.5, fixed=True)
        k2 = s.add_param(1.0, fixed=True)
        start = s.add_point(0, 0)
        end = s.add_point(10, 0)
        bs = s.add_bspline(
            start_id=start,
            end_id=end,
            pole_ids=[p0, p1, p2, p3],
            weight_ids=[w0, w1, w2, w3],
            knot_ids=[k0, k1, k2],
            mult=[3, 1, 3],
            degree=2,
        )

        # Constrain a point to the interior knot
        knot_pt = s.add_point(5, 3)  # guess
        tag = s.internal_alignment_knot_point(bs, knot_pt, knot_index=1)
        assert tag > 0

    def test_tangent_at_bspline_knot(self):
        """Constrain a line tangent to a B-spline at a knot."""
        s = Sketch()
        bs, start, end, pole0, pole1 = _make_line_bspline(s)

        lp1 = s.add_point(0, 0)
        lp2 = s.add_point(5, 0)
        line = s.add_line(lp1, lp2)

        # Tangent at knot index 0 (start)
        tag = s.tangent_at_bspline_knot(bs, line, knot_index=0)
        assert tag > 0


class TestBSplineFullyConstrained:
    """Test that a minimal BSpline can be fully constrained to 0 DOF
    using InternalAlignment and Weight (circle_radius) constraints."""

    def test_degree1_zero_dof(self):
        """Degree-1 BSpline with 2 poles, fully pinned to 0 DOF.

        This mirrors the FreeCAD approach:
        1. Create a BSpline with start/end points and control poles.
        2. Tie start/end to the first/last poles (clamped endpoints).
        3. Create a helper circle per control point and link it via
           InternalAlignment (pole.x==center.x, pole.y==center.y,
           weight==radius).
        4. Fix each circle's center position (pins the pole locations).
        5. Apply a Weight constraint (= circle_radius with a fixed
           target value) to pin each weight.
        """
        s = Sketch()

        # -- Geometry: degree-1, 2 poles, knots [0,1], mult [2,2] --
        pole0 = s.add_point(0.0, 0.0)
        pole1 = s.add_point(10.0, 0.0)
        w0 = s.add_param(1.0)
        w1 = s.add_param(1.0)
        k0 = s.add_param(0.0, fixed=True)
        k1 = s.add_param(1.0, fixed=True)
        start = s.add_point(0.0, 0.0)
        end = s.add_point(10.0, 0.0)

        bs = s.add_bspline(
            start_id=start,
            end_id=end,
            pole_ids=[pole0, pole1],
            weight_ids=[w0, w1],
            knot_ids=[k0, k1],
            mult=[2, 2],
            degree=1,
        )

        # -- Clamped endpoints: tie start/end to first/last poles --
        s.coincident(start, pole0)
        s.coincident(end, pole1)
        assert s.dof() == 6  # 4 pole coords + 2 weights

        # -- InternalAlignment: one helper circle per control point --
        #    Each circle's center ↔ pole position, radius ↔ weight.
        cp0_center = s.add_point(0.0, 0.0)
        cp0_radius = s.add_param(1.0)
        cp0_circle = s.add_circle(cp0_center, cp0_radius)
        s.internal_alignment_bspline_control_point(bs, cp0_circle, pole_index=0)

        cp1_center = s.add_point(10.0, 0.0)
        cp1_radius = s.add_param(1.0)
        cp1_circle = s.add_circle(cp1_center, cp1_radius)
        s.internal_alignment_bspline_control_point(bs, cp1_circle, pole_index=1)

        # Internal alignment adds 3 equalities per pole but also 3 new
        # free params per circle, so net DOF is unchanged.
        assert s.dof() == 6

        # -- Weight constraints (circle_radius on the helper circles) --
        w0_target = s.add_param(1.0, fixed=True)
        w1_target = s.add_param(1.0, fixed=True)
        s.circle_radius(cp0_circle, w0_target)
        s.circle_radius(cp1_circle, w1_target)
        assert s.dof() == 4  # weights pinned, positions still free

        # -- Fix circle centres (pins pole positions via alignment) --
        s.fix_point(cp0_center, 0.0, 0.0)
        s.fix_point(cp1_center, 10.0, 0.0)
        assert s.dof() == 0  # fully constrained

        # -- Solve and verify --
        status = s.solve()
        assert status == SolveStatus.Success

        diag = s.diagnose()
        assert diag.dof == 0
        assert diag.conflicting == []
        assert diag.redundant == []

        info = s.get_bspline(bs)
        assert info.poles[0] == pytest.approx((0.0, 0.0))
        assert info.poles[1] == pytest.approx((10.0, 0.0))
        assert info.weights == pytest.approx([1.0, 1.0])
        assert info.start == pytest.approx((0.0, 0.0))
        assert info.end == pytest.approx((10.0, 0.0))
