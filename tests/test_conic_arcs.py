"""Tests for arc of ellipse, arc of hyperbola, and arc of parabola geometry types."""

import math

import pytest

from planegcs import (
    ArcOfEllipseInfo,
    ArcOfHyperbolaInfo,
    ArcOfParabolaInfo,
    HyperbolaInfo,
    ParabolaInfo,
    Sketch,
    SolveStatus,
)


def _dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# ── Arc of Ellipse ─────────────────────────────────────────────────


class TestArcOfEllipse:
    def test_add_and_get(self):
        """Create an arc of ellipse and read back properties."""
        s = Sketch()
        center = s.add_point(0, 0)
        focus1 = s.add_point(3, 0)
        start = s.add_point(5, 0)  # approximate
        end = s.add_point(0, 4)  # approximate

        aoe = s.add_arc_of_ellipse(
            center,
            focus1,
            radmin=4.0,
            start_angle=0.0,
            end_angle=math.pi / 2,
            start_id=start,
            end_id=end,
        )
        info = s.get_arc_of_ellipse(aoe)
        assert isinstance(info, ArcOfEllipseInfo)
        assert info.center == pytest.approx((0, 0))
        assert info.radmin == pytest.approx(4.0)
        assert info.start_angle == pytest.approx(0.0)
        assert info.end_angle == pytest.approx(math.pi / 2)

    def test_solve_with_fixed_center(self):
        """Arc of ellipse with fixed center and focus solves correctly."""
        s = Sketch()
        center = s.add_point(0, 0)
        focus1 = s.add_point(3, 0)
        # Ellipse: center=(0,0), focus1=(3,0), radmin=4
        # radmaj = sqrt(3^2 + 4^2) = 5
        # At angle 0: point = center + 5*cos(0)*emaj + 4*sin(0)*emin = (5, 0)
        # At angle pi/2: point = center + 5*cos(pi/2)*emaj + 4*sin(pi/2)*emin = (0, 4)
        start = s.add_point(5, 0)
        end = s.add_point(0, 4)

        aoe = s.add_arc_of_ellipse(
            center,
            focus1,
            radmin=4.0,
            start_angle=0.0,
            end_angle=math.pi / 2,
            start_id=start,
            end_id=end,
        )

        # Fix center and focus
        s.fix_point(center, 0, 0)
        s.fix_point(focus1, 3, 0)

        status = s.solve()
        assert status == SolveStatus.Success

        info = s.get_arc_of_ellipse(aoe)
        # Start should be at (5, 0), end at (0, 4)
        assert info.start[0] == pytest.approx(5.0, abs=1e-4)
        assert info.start[1] == pytest.approx(0.0, abs=1e-4)
        assert info.end[0] == pytest.approx(0.0, abs=1e-4)
        assert info.end[1] == pytest.approx(4.0, abs=1e-4)

    def test_entity_info(self):
        """get_entity returns correct type for arc of ellipse."""
        s = Sketch()
        center = s.add_point(0, 0)
        focus1 = s.add_point(3, 0)
        start = s.add_point(5, 0)
        end = s.add_point(0, 4)
        aoe = s.add_arc_of_ellipse(
            center,
            focus1,
            radmin=4.0,
            start_angle=0.0,
            end_angle=math.pi / 2,
            start_id=start,
            end_id=end,
        )
        info = s.get_entity(aoe)
        assert info is not None
        assert info.type == "arc_of_ellipse"
        assert isinstance(info.value, ArcOfEllipseInfo)


# ── Hyperbola ──────────────────────────────────────────────────────


class TestHyperbola:
    def test_add_and_get(self):
        """Create a hyperbola and read back properties."""
        s = Sketch()
        center = s.add_point(0, 0)
        focus1 = s.add_point(5, 0)
        hyp = s.add_hyperbola(center, focus1, radmin=3.0)
        info = s.get_hyperbola(hyp)
        assert isinstance(info, HyperbolaInfo)
        assert info.center == pytest.approx((0, 0))
        assert info.focus1 == pytest.approx((5, 0))
        assert info.radmin == pytest.approx(3.0)

    def test_entity_info(self):
        """get_entity returns correct type for hyperbola."""
        s = Sketch()
        center = s.add_point(0, 0)
        focus1 = s.add_point(5, 0)
        hyp = s.add_hyperbola(center, focus1, radmin=3.0)
        info = s.get_entity(hyp)
        assert info is not None
        assert info.type == "hyperbola"
        assert isinstance(info.value, HyperbolaInfo)


# ── Arc of Hyperbola ───────────────────────────────────────────────


class TestArcOfHyperbola:
    def test_add_and_get(self):
        """Create an arc of hyperbola and read back properties."""
        s = Sketch()
        center = s.add_point(0, 0)
        focus1 = s.add_point(5, 0)
        # radmaj = sqrt(5^2 - 3^2) = 4
        # At u=0: point = center + 4*cosh(0)*emaj + 3*sinh(0)*emin = (4, 0)
        start = s.add_point(4, 0)
        end = s.add_point(6, 4)  # approximate

        aoh = s.add_arc_of_hyperbola(
            center, focus1, radmin=3.0, start_angle=0.0, end_angle=1.0, start_id=start, end_id=end
        )
        info = s.get_arc_of_hyperbola(aoh)
        assert isinstance(info, ArcOfHyperbolaInfo)
        assert info.center == pytest.approx((0, 0))
        assert info.radmin == pytest.approx(3.0)
        assert info.start_angle == pytest.approx(0.0)
        assert info.end_angle == pytest.approx(1.0)

    def test_solve_with_fixed_center(self):
        """Arc of hyperbola with fixed center solves and constrains start/end."""
        s = Sketch()
        center = s.add_point(0, 0)
        focus1 = s.add_point(5, 0)
        # radmaj = sqrt(25 - 9) = 4
        # At u=0: (4*cosh(0), 3*sinh(0)) = (4, 0)
        start = s.add_point(4, 0)
        end = s.add_point(6.2, 3.5)  # crude guess

        aoh = s.add_arc_of_hyperbola(
            center, focus1, radmin=3.0, start_angle=0.0, end_angle=1.0, start_id=start, end_id=end
        )

        s.fix_point(center, 0, 0)
        s.fix_point(focus1, 5, 0)

        status = s.solve()
        assert status == SolveStatus.Success

        info = s.get_arc_of_hyperbola(aoh)
        # At u=0: (4, 0)
        assert info.start[0] == pytest.approx(4.0, abs=0.1)
        assert info.start[1] == pytest.approx(0.0, abs=0.1)

    def test_entity_info(self):
        s = Sketch()
        center = s.add_point(0, 0)
        focus1 = s.add_point(5, 0)
        start = s.add_point(4, 0)
        end = s.add_point(6, 4)
        aoh = s.add_arc_of_hyperbola(
            center, focus1, radmin=3.0, start_angle=0.0, end_angle=1.0, start_id=start, end_id=end
        )
        info = s.get_entity(aoh)
        assert info is not None
        assert info.type == "arc_of_hyperbola"
        assert isinstance(info.value, ArcOfHyperbolaInfo)


# ── Parabola ───────────────────────────────────────────────────────


class TestParabola:
    def test_add_and_get(self):
        """Create a parabola and read back properties."""
        s = Sketch()
        vertex = s.add_point(0, 0)
        focus1 = s.add_point(1, 0)
        par = s.add_parabola(vertex, focus1)
        info = s.get_parabola(par)
        assert isinstance(info, ParabolaInfo)
        assert info.vertex == pytest.approx((0, 0))
        assert info.focus1 == pytest.approx((1, 0))

    def test_entity_info(self):
        s = Sketch()
        vertex = s.add_point(0, 0)
        focus1 = s.add_point(1, 0)
        par = s.add_parabola(vertex, focus1)
        info = s.get_entity(par)
        assert info is not None
        assert info.type == "parabola"
        assert isinstance(info.value, ParabolaInfo)


# ── Arc of Parabola ────────────────────────────────────────────────


class TestArcOfParabola:
    def test_add_and_get(self):
        """Create an arc of parabola and read back properties."""
        s = Sketch()
        vertex = s.add_point(0, 0)
        focus1 = s.add_point(1, 0)
        start = s.add_point(0, 0)  # at u=0, point=vertex
        end = s.add_point(1, 2)  # approximate

        aop = s.add_arc_of_parabola(
            vertex, focus1, start_angle=-2.0, end_angle=2.0, start_id=start, end_id=end
        )
        info = s.get_arc_of_parabola(aop)
        assert isinstance(info, ArcOfParabolaInfo)
        assert info.vertex == pytest.approx((0, 0))
        assert info.focus1 == pytest.approx((1, 0))

    def test_solve_with_fixed_vertex(self):
        """Arc of parabola with fixed vertex/focus solves correctly."""
        s = Sketch()
        vertex = s.add_point(0, 0)
        focus1 = s.add_point(1, 0)
        # Parabola: y^2 = 4*f*x where f = dist(vertex, focus) = 1
        # Parametric: Value(u) = vertex + (u^2/(4*f))*xdir + u*ydir
        # At u=0: (0, 0), at u=2: (1, 2)
        start = s.add_point(0, 0)
        end = s.add_point(1, 2)

        aop = s.add_arc_of_parabola(
            vertex, focus1, start_angle=0.0, end_angle=2.0, start_id=start, end_id=end
        )

        s.fix_point(vertex, 0, 0)
        s.fix_point(focus1, 1, 0)

        status = s.solve()
        assert status == SolveStatus.Success

        info = s.get_arc_of_parabola(aop)
        # At u=0: vertex
        assert info.start == pytest.approx((0, 0), abs=1e-3)
        # At u=2: (4/(4*1), 2) = (1, 2)
        assert info.end[0] == pytest.approx(1.0, abs=1e-3)
        assert info.end[1] == pytest.approx(2.0, abs=1e-3)

    def test_entity_info(self):
        s = Sketch()
        vertex = s.add_point(0, 0)
        focus1 = s.add_point(1, 0)
        start = s.add_point(0, 0)
        end = s.add_point(1, 2)
        aop = s.add_arc_of_parabola(
            vertex, focus1, start_angle=0.0, end_angle=2.0, start_id=start, end_id=end
        )
        info = s.get_entity(aop)
        assert info is not None
        assert info.type == "arc_of_parabola"
        assert isinstance(info.value, ArcOfParabolaInfo)
