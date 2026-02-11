"""High-level Pythonic interface for the PlaneGCS constraint solver."""

from planegcs._planegcs import Algorithm, SketchSolver, SolveStatus


class Sketch:
    """A 2D constraint sketch.

    Provides a convenient Pythonic API on top of :class:`SketchSolver`.
    Geometry is added with ``add_*`` methods which return integer IDs.
    Constraints are added with descriptive methods. Call :meth:`solve`
    to find a configuration satisfying all constraints.

    Example::

        s = Sketch()
        p1 = s.add_point(0, 0)
        p2 = s.add_point(5, 0)
        p3 = s.add_point(2.5, 4)
        l1 = s.add_line(p1, p2)
        l2 = s.add_line(p2, p3)
        l3 = s.add_line(p3, p1)
        s.equal_length(l1, l2)
        s.equal_length(l2, l3)
        s.fix_point(p1, 0, 0)
        s.horizontal(l1)
        d = s.add_param(5.0)
        s.p2p_distance(p1, p2, d)
        status = s.solve()
        assert status == SolveStatus.Success
    """

    def __init__(self) -> None:
        self._solver = SketchSolver()

    @property
    def solver(self) -> SketchSolver:
        """Access the underlying :class:`SketchSolver`."""
        return self._solver

    # ── Parameters ─────────────────────────────────────────────────

    def add_param(self, value: float = 0.0, *, fixed: bool = True) -> int:
        """Allocate a standalone parameter.

        Args:
            value: Initial value.
            fixed: If True (default), this is a driving constraint value
                   that the solver will not change. Set False to make it
                   an unknown the solver can adjust.

        Returns:
            Parameter ID.
        """
        return self._solver.add_param(value, fixed)

    def get_param(self, param_id: int) -> float:
        """Read current value of a parameter."""
        return self._solver.get_param(param_id)

    def set_param(self, param_id: int, value: float) -> None:
        """Write a new value to a parameter."""
        self._solver.set_param(param_id, value)

    # ── Geometry ───────────────────────────────────────────────────

    def add_point(self, x: float, y: float) -> int:
        """Add a point at (x, y). Returns point ID."""
        return self._solver.add_point(x, y)

    def get_point(self, point_id: int) -> tuple[float, float]:
        """Get current (x, y) of a point."""
        return self._solver.get_point(point_id)

    def add_line(self, p1_id: int, p2_id: int) -> int:
        """Add a line between two existing points. Returns line ID."""
        return self._solver.add_line(p1_id, p2_id)

    def add_line_xy(self, x1: float, y1: float, x2: float, y2: float) -> int:
        """Add a line with endpoint coordinates. Returns line ID."""
        return self._solver.add_line(x1, y1, x2, y2)

    def add_circle(self, center_id: int, radius: float) -> int:
        """Add a circle. Returns circle ID."""
        return self._solver.add_circle(center_id, radius)

    def add_arc(
        self,
        center_id: int,
        radius: float,
        start_angle: float,
        end_angle: float,
    ) -> int:
        """Add an arc. Returns arc ID."""
        return self._solver.add_arc(center_id, radius, start_angle, end_angle)

    def add_ellipse(self, center_id: int, focus1_id: int, radmin: float) -> int:
        """Add an ellipse. Returns ellipse ID."""
        return self._solver.add_ellipse(center_id, focus1_id, radmin)

    # ── Constraints ────────────────────────────────────────────────

    def coincident(self, pt1_id: int, pt2_id: int, *, driving: bool = True) -> int:
        """Make two points coincident. Returns constraint tag."""
        return self._solver.coincident(pt1_id, pt2_id, driving)

    def fix_point(
        self, pt_id: int, x: float, y: float, *, driving: bool = True
    ) -> tuple[int, int]:
        """Fix a point to (x, y). Returns (tag_x, tag_y)."""
        px = self.add_param(x, fixed=True)
        py = self.add_param(y, fixed=True)
        tx = self._solver.coordinate_x(pt_id, px, driving)
        ty = self._solver.coordinate_y(pt_id, py, driving)
        return tx, ty

    def horizontal(self, line_id: int, *, driving: bool = True) -> int:
        """Constrain a line to be horizontal."""
        return self._solver.horizontal_line(line_id, driving)

    def vertical(self, line_id: int, *, driving: bool = True) -> int:
        """Constrain a line to be vertical."""
        return self._solver.vertical_line(line_id, driving)

    def horizontal_points(self, p1_id: int, p2_id: int, *, driving: bool = True) -> int:
        """Constrain two points to be at the same Y."""
        return self._solver.horizontal_points(p1_id, p2_id, driving)

    def vertical_points(self, p1_id: int, p2_id: int, *, driving: bool = True) -> int:
        """Constrain two points to be at the same X."""
        return self._solver.vertical_points(p1_id, p2_id, driving)

    def p2p_distance(
        self, pt1_id: int, pt2_id: int, distance_id: int, *, driving: bool = True
    ) -> int:
        """Constrain point-to-point distance."""
        return self._solver.p2p_distance(pt1_id, pt2_id, distance_id, driving)

    def p2l_distance(
        self, pt_id: int, line_id: int, distance_id: int, *, driving: bool = True
    ) -> int:
        """Constrain point-to-line distance."""
        return self._solver.p2l_distance(pt_id, line_id, distance_id, driving)

    def point_on_line(self, pt_id: int, line_id: int, *, driving: bool = True) -> int:
        """Constrain point on line."""
        return self._solver.point_on_line(pt_id, line_id, driving)

    def parallel(self, l1_id: int, l2_id: int, *, driving: bool = True) -> int:
        """Constrain lines to be parallel."""
        return self._solver.parallel(l1_id, l2_id, driving)

    def perpendicular(self, l1_id: int, l2_id: int, *, driving: bool = True) -> int:
        """Constrain lines to be perpendicular."""
        return self._solver.perpendicular(l1_id, l2_id, driving)

    def equal_length(self, l1_id: int, l2_id: int, *, driving: bool = True) -> int:
        """Constrain two lines to equal length."""
        return self._solver.equal_length(l1_id, l2_id, driving)

    def equal(self, param1_id: int, param2_id: int, *, driving: bool = True) -> int:
        """Constrain two parameters to be equal."""
        return self._solver.equal(param1_id, param2_id, driving)

    def l2l_angle(self, l1_id: int, l2_id: int, angle_id: int, *, driving: bool = True) -> int:
        """Constrain angle between two lines."""
        return self._solver.l2l_angle(l1_id, l2_id, angle_id, driving)

    def point_on_circle(self, pt_id: int, circle_id: int, *, driving: bool = True) -> int:
        """Constrain point on circle."""
        return self._solver.point_on_circle(pt_id, circle_id, driving)

    def circle_radius(self, circle_id: int, radius_id: int, *, driving: bool = True) -> int:
        """Constrain circle radius."""
        return self._solver.circle_radius(circle_id, radius_id, driving)

    def tangent_line_circle(self, line_id: int, circle_id: int, *, driving: bool = True) -> int:
        """Line tangent to circle."""
        return self._solver.tangent_line_circle(line_id, circle_id, driving)

    def tangent_circle_circle(self, c1_id: int, c2_id: int, *, driving: bool = True) -> int:
        """Circle tangent to circle."""
        return self._solver.tangent_circle_circle(c1_id, c2_id, driving)

    def symmetric_line(self, p1_id: int, p2_id: int, line_id: int, *, driving: bool = True) -> int:
        """Constrain points symmetric about a line."""
        return self._solver.symmetric_points_line(p1_id, p2_id, line_id, driving)

    def symmetric_point(
        self, p1_id: int, p2_id: int, center_id: int, *, driving: bool = True
    ) -> int:
        """Constrain points symmetric about a center point."""
        return self._solver.symmetric_points_point(p1_id, p2_id, center_id, driving)

    def arc_rules(self, arc_id: int, *, driving: bool = True) -> int:
        """Add arc rules (start/end points computed from center, radius, angles)."""
        return self._solver.arc_rules(arc_id, driving)

    def midpoint_on_line(self, l1_id: int, l2_id: int, *, driving: bool = True) -> int:
        """Constrain midpoint of l1 to lie on l2."""
        return self._solver.midpoint_on_line(l1_id, l2_id, driving)

    # ── Solving ────────────────────────────────────────────────────

    def solve(self, algorithm: Algorithm = Algorithm.DogLeg) -> SolveStatus:
        """Solve the constraint system.

        Returns :class:`SolveStatus` indicating result.
        """
        return self._solver.solve(algorithm)

    def clear(self) -> None:
        """Clear all geometry, constraints and parameters."""
        self._solver.clear()
