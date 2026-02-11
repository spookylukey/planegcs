"""High-level Pythonic interface for the PlaneGCS constraint solver."""

from dataclasses import dataclass
from typing import NewType

from planegcs._planegcs import Algorithm, SketchSolver, SolveStatus

# ── Typed IDs ──────────────────────────────────────────────────────
# These are all ints at runtime, but static type checkers will treat
# them as distinct types so you can't accidentally mix them up.

ParamId = NewType("ParamId", int)
"""ID for a solver parameter (returned by :meth:`Sketch.add_param`)."""

PointId = NewType("PointId", int)
"""ID for a point (returned by :meth:`Sketch.add_point`)."""

LineId = NewType("LineId", int)
"""ID for a line (returned by :meth:`Sketch.add_line`)."""

CircleId = NewType("CircleId", int)
"""ID for a circle (returned by :meth:`Sketch.add_circle`)."""

ArcId = NewType("ArcId", int)
"""ID for an arc (returned by :meth:`Sketch.add_arc_from_center`
or :meth:`Sketch.add_arc_from_start_end`)."""

EllipseId = NewType("EllipseId", int)
"""ID for an ellipse (returned by :meth:`Sketch.add_ellipse`)."""

ConstraintTag = NewType("ConstraintTag", int)
"""Tag for a constraint (returned by constraint methods)."""


@dataclass(frozen=True, slots=True)
class ArcInfo:
    """Properties of an arc, returned by :meth:`Sketch.get_arc`."""

    center: tuple[float, float]
    """(x, y) of the arc center."""

    radius: float
    """Arc radius."""

    start_angle: float
    """Start angle in radians."""

    end_angle: float
    """End angle in radians."""

    start_point: tuple[float, float]
    """(x, y) of the arc start point."""

    end_point: tuple[float, float]
    """(x, y) of the arc end point."""


@dataclass(frozen=True, slots=True)
class Diagnosis:
    """Result of constraint system diagnosis.

    Returned by :meth:`Sketch.diagnose`.
    """

    dof: int
    """Degrees of freedom.

    - ``0``: Fully constrained.
    - ``> 0``: Under-constrained (this many degrees of freedom remain).
    """

    conflicting: list[ConstraintTag]
    """Tags of conflicting constraints.

    Non-empty means the system is over-constrained. These are the
    constraint tags that conflict with each other.
    """

    redundant: list[ConstraintTag]
    """Tags of redundant constraints.

    Redundant constraints are satisfied but provide no additional
    information (they duplicate information already present).
    """

    partially_redundant: list[ConstraintTag]
    """Tags of partially redundant constraints."""

    @property
    def is_fully_constrained(self) -> bool:
        """True if the system has zero degrees of freedom and no conflicts."""
        return self.dof == 0 and not self.conflicting

    @property
    def is_under_constrained(self) -> bool:
        """True if the system has degrees of freedom remaining."""
        return self.dof > 0

    @property
    def is_over_constrained(self) -> bool:
        """True if there are conflicting constraints."""
        return bool(self.conflicting)


class Sketch:
    """A 2D constraint sketch.

    Provides a convenient Pythonic API on top of :class:`SketchSolver`.
    Geometry is added with ``add_*`` methods which return typed IDs.
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
        s.set_p2p_distance(p1, p2, 5.0)
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

    def add_param(self, value: float = 0.0, *, fixed: bool = True) -> ParamId:
        """Allocate a standalone parameter.

        Args:
            value: Initial value.
            fixed: If True (default), this is a driving constraint value
                   that the solver will not change. Set False to make it
                   an unknown the solver can adjust.

        Returns:
            Parameter ID.
        """
        return ParamId(self._solver.add_param(value, fixed))

    def add_fixed_param(self, value: float) -> ParamId:
        """Allocate a fixed parameter with the given value.

        This is a convenience shorthand for ``add_param(value, fixed=True)``.

        Args:
            value: The fixed value for the parameter.

        Returns:
            Parameter ID.
        """
        return self.add_param(value, fixed=True)

    def get_param(self, param_id: ParamId) -> float:
        """Read current value of a parameter."""
        return self._solver.get_param(param_id)

    def set_param(self, param_id: ParamId, value: float) -> None:
        """Write a new value to a parameter."""
        self._solver.set_param(param_id, value)

    # ── Geometry ───────────────────────────────────────────────────

    def add_point(self, x: float, y: float) -> PointId:
        """Add a point at (x, y). Returns point ID."""
        return PointId(self._solver.add_point(x, y))

    def get_point(self, point_id: PointId) -> tuple[float, float]:
        """Get current (x, y) of a point."""
        return self._solver.get_point(point_id)

    def add_fixed_point(self, x: float, y: float, *, driving: bool = True) -> PointId:
        """Add a point and fix it at (x, y) in one step.

        This is a convenience method equivalent to calling :meth:`add_point`
        followed by :meth:`fix_point`.

        Args:
            x: X coordinate.
            y: Y coordinate.
            driving: Whether the fix constraints are driving.

        Returns:
            Point ID.
        """
        pt_id = self.add_point(x, y)
        self.fix_point(pt_id, x, y, driving=driving)
        return pt_id

    def add_line(self, p1_id: PointId, p2_id: PointId) -> LineId:
        """Add a line between two existing points. Returns line ID."""
        return LineId(self._solver.add_line(p1_id, p2_id))

    def add_line_xy(self, x1: float, y1: float, x2: float, y2: float) -> LineId:
        """Add a line with endpoint coordinates. Returns line ID."""
        return LineId(self._solver.add_line(x1, y1, x2, y2))

    def add_circle(self, center_id: PointId, radius: float) -> CircleId:
        """Add a circle. Returns circle ID."""
        return CircleId(self._solver.add_circle(center_id, radius))

    def add_arc_from_center(
        self,
        center_id: PointId,
        radius: float,
        start_angle: float,
        end_angle: float,
    ) -> ArcId:
        """Add an arc from center point, radius and angles. Returns arc ID."""
        return ArcId(self._solver.add_arc_from_center(center_id, radius, start_angle, end_angle))

    def add_arc_from_start_end(
        self,
        start_id: PointId,
        end_id: PointId,
        radius_id: ParamId,
    ) -> ArcId:
        """Add an arc from start/end points and a radius parameter.

        Automatically adds arc rules and coincident constraints so that the
        arc passes through the given start and end points.

        The caller supplies a :class:`ParamId` for the radius (created via
        :meth:`add_param`).  Use ``fixed=True`` (the default) to lock the
        radius, or ``fixed=False`` to let the solver adjust it.

        Args:
            start_id: Start point of the arc.
            end_id: End point of the arc.
            radius_id: Parameter ID for the radius (from :meth:`add_param`).

        Returns:
            Arc ID.
        """
        return ArcId(self._solver.add_arc_from_start_end(start_id, end_id, radius_id))

    def get_arc(self, arc_id: ArcId) -> ArcInfo:
        """Get all properties of an arc.

        Returns an :class:`ArcInfo` dataclass with ``center``,
        ``radius``, ``start_angle``, ``end_angle``, ``start_point``,
        and ``end_point`` fields.
        """
        return ArcInfo(
            center=self._solver.get_arc_center(arc_id),
            radius=self._solver.get_arc_radius(arc_id),
            start_angle=self._solver.get_arc_start_angle(arc_id),
            end_angle=self._solver.get_arc_end_angle(arc_id),
            start_point=self._solver.get_arc_start_point(arc_id),
            end_point=self._solver.get_arc_end_point(arc_id),
        )

    def get_arc_center(self, arc_id: ArcId) -> tuple[float, float]:
        """Get the (x, y) of an arc's center."""
        return self._solver.get_arc_center(arc_id)

    def get_arc_radius(self, arc_id: ArcId) -> float:
        """Get the radius of an arc."""
        return self._solver.get_arc_radius(arc_id)

    def get_arc_start_angle(self, arc_id: ArcId) -> float:
        """Get the start angle of an arc (radians)."""
        return self._solver.get_arc_start_angle(arc_id)

    def get_arc_end_angle(self, arc_id: ArcId) -> float:
        """Get the end angle of an arc (radians)."""
        return self._solver.get_arc_end_angle(arc_id)

    def add_ellipse(self, center_id: PointId, focus1_id: PointId, radmin: float) -> EllipseId:
        """Add an ellipse. Returns ellipse ID."""
        return EllipseId(self._solver.add_ellipse(center_id, focus1_id, radmin))

    # ── Constraints ────────────────────────────────────────────────

    def coincident(
        self, pt1_id: PointId, pt2_id: PointId, *, driving: bool = True
    ) -> ConstraintTag:
        """Make two points coincident. Returns constraint tag."""
        return ConstraintTag(self._solver.coincident(pt1_id, pt2_id, driving))

    def fix_point(
        self, pt_id: PointId, x: float, y: float, *, driving: bool = True
    ) -> tuple[ConstraintTag, ConstraintTag]:
        """Fix a point to (x, y). Returns (tag_x, tag_y)."""
        px = self.add_param(x, fixed=True)
        py = self.add_param(y, fixed=True)
        tx = ConstraintTag(self._solver.coordinate_x(pt_id, px, driving))
        ty = ConstraintTag(self._solver.coordinate_y(pt_id, py, driving))
        return tx, ty

    def horizontal(self, line_id: LineId, *, driving: bool = True) -> ConstraintTag:
        """Constrain a line to be horizontal."""
        return ConstraintTag(self._solver.horizontal_line(line_id, driving))

    def vertical(self, line_id: LineId, *, driving: bool = True) -> ConstraintTag:
        """Constrain a line to be vertical."""
        return ConstraintTag(self._solver.vertical_line(line_id, driving))

    def horizontal_points(
        self, p1_id: PointId, p2_id: PointId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain two points to be at the same Y."""
        return ConstraintTag(self._solver.horizontal_points(p1_id, p2_id, driving))

    def vertical_points(
        self, p1_id: PointId, p2_id: PointId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain two points to be at the same X."""
        return ConstraintTag(self._solver.vertical_points(p1_id, p2_id, driving))

    def p2p_distance(
        self, pt1_id: PointId, pt2_id: PointId, distance_id: ParamId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain point-to-point distance using a parameter.

        For a simpler API that takes a float directly, see :meth:`set_p2p_distance`.
        """
        return ConstraintTag(self._solver.p2p_distance(pt1_id, pt2_id, distance_id, driving))

    def set_p2p_distance(
        self, pt1_id: PointId, pt2_id: PointId, distance: float, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain point-to-point distance to a value.

        Convenience method that creates the parameter internally.
        To use an explicit parameter (e.g. to read back the solved value
        or share it between constraints), use :meth:`p2p_distance` with
        :meth:`add_param`.
        """
        d = self.add_param(distance, fixed=True)
        return self.p2p_distance(pt1_id, pt2_id, d, driving=driving)

    def p2l_distance(
        self, pt_id: PointId, line_id: LineId, distance_id: ParamId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain point-to-line distance using a parameter.

        For a simpler API that takes a float directly, see :meth:`set_p2l_distance`.
        """
        return ConstraintTag(self._solver.p2l_distance(pt_id, line_id, distance_id, driving))

    def set_p2l_distance(
        self, pt_id: PointId, line_id: LineId, distance: float, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain point-to-line distance to a value.

        Convenience method that creates the parameter internally.
        To use an explicit parameter, use :meth:`p2l_distance` with
        :meth:`add_param`.
        """
        d = self.add_param(distance, fixed=True)
        return self.p2l_distance(pt_id, line_id, d, driving=driving)

    def point_on_line(
        self, pt_id: PointId, line_id: LineId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain point on line."""
        return ConstraintTag(self._solver.point_on_line(pt_id, line_id, driving))

    def parallel(self, l1_id: LineId, l2_id: LineId, *, driving: bool = True) -> ConstraintTag:
        """Constrain lines to be parallel."""
        return ConstraintTag(self._solver.parallel(l1_id, l2_id, driving))

    def perpendicular(
        self, l1_id: LineId, l2_id: LineId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain lines to be perpendicular."""
        return ConstraintTag(self._solver.perpendicular(l1_id, l2_id, driving))

    def equal_length(self, l1_id: LineId, l2_id: LineId, *, driving: bool = True) -> ConstraintTag:
        """Constrain two lines to equal length."""
        return ConstraintTag(self._solver.equal_length(l1_id, l2_id, driving))

    def equal(
        self, param1_id: ParamId, param2_id: ParamId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain two parameters to be equal."""
        return ConstraintTag(self._solver.equal(param1_id, param2_id, driving))

    def l2l_angle(
        self, l1_id: LineId, l2_id: LineId, angle_id: ParamId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain angle between two lines using a parameter.

        For a simpler API that takes a float directly, see :meth:`set_l2l_angle`.
        """
        return ConstraintTag(self._solver.l2l_angle(l1_id, l2_id, angle_id, driving))

    def set_l2l_angle(
        self, l1_id: LineId, l2_id: LineId, angle: float, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain angle between two lines to a value (in radians).

        Convenience method that creates the parameter internally.
        To use an explicit parameter, use :meth:`l2l_angle` with
        :meth:`add_param`.
        """
        a = self.add_param(angle, fixed=True)
        return self.l2l_angle(l1_id, l2_id, a, driving=driving)

    def point_on_circle(
        self, pt_id: PointId, circle_id: CircleId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain point on circle."""
        return ConstraintTag(self._solver.point_on_circle(pt_id, circle_id, driving))

    def circle_radius(
        self, circle_id: CircleId, radius_id: ParamId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain circle radius using a parameter.

        For a simpler API that takes a float directly, see :meth:`set_circle_radius`.
        """
        return ConstraintTag(self._solver.circle_radius(circle_id, radius_id, driving))

    def set_circle_radius(
        self, circle_id: CircleId, radius: float, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain circle radius to a value.

        Convenience method that creates the parameter internally.
        To use an explicit parameter, use :meth:`circle_radius` with
        :meth:`add_param`.
        """
        r = self.add_param(radius, fixed=True)
        return self.circle_radius(circle_id, r, driving=driving)

    def tangent_line_circle(
        self, line_id: LineId, circle_id: CircleId, *, driving: bool = True
    ) -> ConstraintTag:
        """Line tangent to circle."""
        return ConstraintTag(self._solver.tangent_line_circle(line_id, circle_id, driving))

    def tangent_circle_circle(
        self, c1_id: CircleId, c2_id: CircleId, *, driving: bool = True
    ) -> ConstraintTag:
        """Circle tangent to circle."""
        return ConstraintTag(self._solver.tangent_circle_circle(c1_id, c2_id, driving))

    def tangent_line_arc(
        self, line_id: LineId, arc_id: ArcId, *, driving: bool = True
    ) -> ConstraintTag:
        """Line tangent to arc."""
        return ConstraintTag(self._solver.tangent_line_arc(line_id, arc_id, driving))

    def symmetric_line(
        self, p1_id: PointId, p2_id: PointId, line_id: LineId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain points symmetric about a line."""
        return ConstraintTag(self._solver.symmetric_points_line(p1_id, p2_id, line_id, driving))

    def symmetric_point(
        self, p1_id: PointId, p2_id: PointId, center_id: PointId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain points symmetric about a center point."""
        return ConstraintTag(self._solver.symmetric_points_point(p1_id, p2_id, center_id, driving))

    def arc_rules(self, arc_id: ArcId, *, driving: bool = True) -> ConstraintTag:
        """Add arc rules (start/end points computed from center, radius, angles)."""
        return ConstraintTag(self._solver.arc_rules(arc_id, driving))

    def midpoint_on_line(
        self, l1_id: LineId, l2_id: LineId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain midpoint of l1 to lie on l2."""
        return ConstraintTag(self._solver.midpoint_on_line(l1_id, l2_id, driving))

    # ── Solving ────────────────────────────────────────────────────

    def solve(self, algorithm: Algorithm = Algorithm.DogLeg) -> SolveStatus:
        """Solve the constraint system.

        Returns :class:`SolveStatus` indicating result.
        """
        return self._solver.solve(algorithm)

    def diagnose(self, algorithm: Algorithm = Algorithm.DogLeg) -> Diagnosis:
        """Diagnose the constraint system.

        Runs the solver's diagnosis to determine the degrees of freedom
        and identify any conflicting or redundant constraints.

        Returns a :class:`Diagnosis` with:

        - ``dof``: Degrees of freedom (0 = fully constrained).
        - ``conflicting``: Over-constraining constraint tags.
        - ``redundant``: Redundant constraint tags.
        - ``partially_redundant``: Partially redundant constraint tags.
        - Convenience properties: ``is_fully_constrained``,
          ``is_under_constrained``, ``is_over_constrained``.

        Example::

            s = Sketch()
            p1 = s.add_point(0, 0)
            p2 = s.add_point(5, 0)
            l = s.add_line(p1, p2)
            s.horizontal(l)
            diag = s.diagnose()
            print(diag.dof)  # 3 (under-constrained)
            print(diag.is_under_constrained)  # True
        """
        r = self._solver.diagnose(algorithm)
        return Diagnosis(
            dof=r.dof,
            conflicting=[ConstraintTag(t) for t in r.conflicting],
            redundant=[ConstraintTag(t) for t in r.redundant],
            partially_redundant=[ConstraintTag(t) for t in r.partially_redundant],
        )

    def dof(self) -> int:
        """Return degrees of freedom of the constraint system.

        Shorthand for ``diagnose().dof``. Returns 0 when fully
        constrained, positive when under-constrained.
        """
        return self._solver.dof()

    def clear(self) -> None:
        """Clear all geometry, constraints and parameters."""
        self._solver.clear()
