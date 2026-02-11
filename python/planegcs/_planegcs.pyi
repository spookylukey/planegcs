"""Type stubs for the _planegcs C extension module."""

from typing import overload

# ── Enums ──────────────────────────────────────────────────────────

class SolveStatus:
    """Result of a solver run."""

    Success: SolveStatus
    Converged: SolveStatus
    Failed: SolveStatus
    SuccessfulSolutionInvalid: SolveStatus

    __members__: dict[str, SolveStatus]

    def __init__(self, value: int) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __int__(self) -> int: ...
    def __index__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class Algorithm:
    """Solver algorithm."""

    BFGS: Algorithm
    LevenbergMarquardt: Algorithm
    DogLeg: Algorithm

    __members__: dict[str, Algorithm]

    def __init__(self, value: int) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __int__(self) -> int: ...
    def __index__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class DebugMode:
    """Debug verbosity level."""

    NoDebug: DebugMode
    Minimal: DebugMode
    IterationLevel: DebugMode

    __members__: dict[str, DebugMode]

    def __init__(self, value: int) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __int__(self) -> int: ...
    def __index__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class InternalAlignmentType:
    """Internal alignment type for ellipse/hyperbola constraints."""

    EllipsePositiveMajorX: InternalAlignmentType
    EllipsePositiveMajorY: InternalAlignmentType
    EllipseNegativeMajorX: InternalAlignmentType
    EllipseNegativeMajorY: InternalAlignmentType
    EllipsePositiveMinorX: InternalAlignmentType
    EllipsePositiveMinorY: InternalAlignmentType
    EllipseNegativeMinorX: InternalAlignmentType
    EllipseNegativeMinorY: InternalAlignmentType
    EllipseFocus2X: InternalAlignmentType
    EllipseFocus2Y: InternalAlignmentType
    HyperbolaPositiveMajorX: InternalAlignmentType
    HyperbolaPositiveMajorY: InternalAlignmentType
    HyperbolaNegativeMajorX: InternalAlignmentType
    HyperbolaNegativeMajorY: InternalAlignmentType
    HyperbolaPositiveMinorX: InternalAlignmentType
    HyperbolaPositiveMinorY: InternalAlignmentType
    HyperbolaNegativeMinorX: InternalAlignmentType
    HyperbolaNegativeMinorY: InternalAlignmentType

    __members__: dict[str, InternalAlignmentType]

    def __init__(self, value: int) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __int__(self) -> int: ...
    def __index__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

# ── SketchSolver ───────────────────────────────────────────────────

class SketchSolver:
    """Low-level wrapper around the PlaneGCS solver."""

    def __init__(self) -> None: ...

    # Parameters
    def add_param(self, value: float = 0.0, fixed: bool = False) -> int:
        """Allocate a parameter. fixed=True for driving constraint values. Returns param ID."""
        ...
    def is_param_fixed(self, param_id: int) -> bool:
        """Check if a parameter is fixed (not an unknown)."""
        ...
    def set_param_fixed(self, param_id: int, fixed: bool) -> None:
        """Set whether a parameter is fixed."""
        ...
    def get_param(self, param_id: int) -> float:
        """Get the current value of a parameter."""
        ...
    def set_param(self, param_id: int, value: float) -> None:
        """Set the value of a parameter."""
        ...

    # Geometry: Points
    def add_point(self, x: float, y: float) -> int:
        """Add a point. Returns point ID."""
        ...
    def get_point(self, point_id: int) -> tuple[float, float]:
        """Get the (x, y) of a point."""
        ...

    # Geometry: Lines
    @overload
    def add_line(self, p1_id: int, p2_id: int) -> int:
        """Add a line between two existing points. Returns line ID."""
        ...
    @overload
    def add_line(self, x1: float, y1: float, x2: float, y2: float) -> int:
        """Add a line with endpoint coordinates. Returns line ID."""
        ...
    def add_line(self, *args: float | int) -> int: ...

    # Geometry: Circles
    def add_circle(self, center_id: int, radius: float) -> int:
        """Add a circle. Returns circle ID."""
        ...

    # Geometry: Arcs
    def add_arc(self, center_id: int, radius: float, start_angle: float, end_angle: float) -> int:
        """Add an arc. Returns arc ID."""
        ...

    # Geometry: Ellipses
    def add_ellipse(self, center_id: int, focus1_id: int, radmin: float) -> int:
        """Add an ellipse. Returns ellipse ID."""
        ...

    # Geometry: ArcOfEllipse
    def add_arc_of_ellipse(
        self,
        center_id: int,
        focus1_id: int,
        radmin: float,
        start_angle: float,
        end_angle: float,
        start_id: int,
        end_id: int,
    ) -> int:
        """Add an arc of ellipse. Returns ID."""
        ...

    # Geometry: Hyperbola
    def add_hyperbola(self, center_id: int, focus1_id: int, radmin: float) -> int:
        """Add a hyperbola. Returns ID."""
        ...

    # Geometry: ArcOfHyperbola
    def add_arc_of_hyperbola(
        self,
        center_id: int,
        focus1_id: int,
        radmin: float,
        start_angle: float,
        end_angle: float,
        start_id: int,
        end_id: int,
    ) -> int:
        """Add an arc of hyperbola. Returns ID."""
        ...

    # Geometry: Parabola
    def add_parabola(self, vertex_id: int, focus1_id: int) -> int:
        """Add a parabola. Returns ID."""
        ...

    # Geometry: ArcOfParabola
    def add_arc_of_parabola(
        self,
        vertex_id: int,
        focus1_id: int,
        start_angle: float,
        end_angle: float,
        start_id: int,
        end_id: int,
    ) -> int:
        """Add an arc of parabola. Returns ID."""
        ...

    # Solving
    def solve(self, algorithm: Algorithm = ...) -> SolveStatus:
        """Solve the system. Returns SolveStatus."""
        ...
    def clear(self) -> None:
        """Clear all geometry, constraints, and parameters."""
        ...

    # Constraints (all return int constraint tag)
    def coincident(self, pt1_id: int, pt2_id: int, driving: bool = True) -> int:
        """Add coincident constraint between two points."""
        ...
    def equal(self, param1_id: int, param2_id: int, driving: bool = True) -> int:
        """Add equality constraint between two parameters."""
        ...
    def proportional(
        self, param1_id: int, param2_id: int, ratio: float, driving: bool = True
    ) -> int:
        """Add proportional constraint."""
        ...
    def difference(
        self, param1_id: int, param2_id: int, diff_id: int, driving: bool = True
    ) -> int:
        """Add difference constraint."""
        ...
    def p2p_distance(
        self, pt1_id: int, pt2_id: int, distance_id: int, driving: bool = True
    ) -> int:
        """Add point-to-point distance constraint."""
        ...
    def p2p_angle(self, pt1_id: int, pt2_id: int, angle_id: int, driving: bool = True) -> int:
        """Add point-to-point angle constraint."""
        ...
    def p2l_distance(
        self, pt_id: int, line_id: int, distance_id: int, driving: bool = True
    ) -> int:
        """Add point-to-line distance constraint."""
        ...
    def point_on_line(self, pt_id: int, line_id: int, driving: bool = True) -> int:
        """Constrain point to lie on line."""
        ...
    def point_on_perp_bisector(self, pt_id: int, line_id: int, driving: bool = True) -> int:
        """Constrain point to lie on perpendicular bisector of line."""
        ...
    def parallel(self, l1_id: int, l2_id: int, driving: bool = True) -> int:
        """Add parallel constraint."""
        ...
    def perpendicular(self, l1_id: int, l2_id: int, driving: bool = True) -> int:
        """Add perpendicular constraint."""
        ...
    def l2l_angle(self, l1_id: int, l2_id: int, angle_id: int, driving: bool = True) -> int:
        """Add line-to-line angle constraint."""
        ...
    def midpoint_on_line(self, l1_id: int, l2_id: int, driving: bool = True) -> int:
        """Constrain midpoint of l1 to lie on l2."""
        ...
    def horizontal_line(self, line_id: int, driving: bool = True) -> int:
        """Constrain line to be horizontal."""
        ...
    def horizontal_points(self, p1_id: int, p2_id: int, driving: bool = True) -> int:
        """Constrain two points to have same Y."""
        ...
    def vertical_line(self, line_id: int, driving: bool = True) -> int:
        """Constrain line to be vertical."""
        ...
    def vertical_points(self, p1_id: int, p2_id: int, driving: bool = True) -> int:
        """Constrain two points to have same X."""
        ...
    def coordinate_x(self, pt_id: int, x_id: int, driving: bool = True) -> int:
        """Fix the X coordinate of a point."""
        ...
    def coordinate_y(self, pt_id: int, y_id: int, driving: bool = True) -> int:
        """Fix the Y coordinate of a point."""
        ...
    def point_on_circle(self, pt_id: int, circle_id: int, driving: bool = True) -> int:
        """Constrain point to lie on circle."""
        ...
    def point_on_ellipse(self, pt_id: int, ellipse_id: int, driving: bool = True) -> int:
        """Constrain point to lie on ellipse."""
        ...
    def point_on_arc(self, pt_id: int, arc_id: int, driving: bool = True) -> int:
        """Constrain point to lie on arc."""
        ...
    def arc_rules(self, arc_id: int, driving: bool = True) -> int:
        """Add arc rules constraint."""
        ...
    def tangent_line_circle(self, line_id: int, circle_id: int, driving: bool = True) -> int:
        """Add line-circle tangent constraint."""
        ...
    def tangent_line_ellipse(self, line_id: int, ellipse_id: int, driving: bool = True) -> int:
        """Add line-ellipse tangent constraint."""
        ...
    def tangent_line_arc(self, line_id: int, arc_id: int, driving: bool = True) -> int:
        """Add line-arc tangent constraint."""
        ...
    def tangent_circle_circle(self, c1_id: int, c2_id: int, driving: bool = True) -> int:
        """Add circle-circle tangent constraint."""
        ...
    def tangent_arc_arc(self, a1_id: int, a2_id: int, driving: bool = True) -> int:
        """Add arc-arc tangent constraint."""
        ...
    def tangent_circle_arc(self, circle_id: int, arc_id: int, driving: bool = True) -> int:
        """Add circle-arc tangent constraint."""
        ...
    def circle_radius(self, circle_id: int, radius_id: int, driving: bool = True) -> int:
        """Set circle radius."""
        ...
    def arc_radius(self, arc_id: int, radius_id: int, driving: bool = True) -> int:
        """Set arc radius."""
        ...
    def circle_diameter(self, circle_id: int, diameter_id: int, driving: bool = True) -> int:
        """Set circle diameter."""
        ...
    def arc_diameter(self, arc_id: int, diameter_id: int, driving: bool = True) -> int:
        """Set arc diameter."""
        ...
    def equal_length(self, l1_id: int, l2_id: int, driving: bool = True) -> int:
        """Constrain two lines to have equal length."""
        ...
    def equal_radius_cc(self, c1_id: int, c2_id: int, driving: bool = True) -> int:
        """Constrain two circles to have equal radius."""
        ...
    def equal_radius_ca(self, circle_id: int, arc_id: int, driving: bool = True) -> int:
        """Constrain circle and arc to have equal radius."""
        ...
    def equal_radius_aa(self, a1_id: int, a2_id: int, driving: bool = True) -> int:
        """Constrain two arcs to have equal radius."""
        ...
    def symmetric_points_line(
        self, p1_id: int, p2_id: int, line_id: int, driving: bool = True
    ) -> int:
        """Constrain points symmetric about a line."""
        ...
    def symmetric_points_point(
        self, p1_id: int, p2_id: int, center_id: int, driving: bool = True
    ) -> int:
        """Constrain points symmetric about a center point."""
        ...
    def p2c_distance(
        self, pt_id: int, circle_id: int, distance_id: int, driving: bool = True
    ) -> int:
        """Add point-to-circle distance constraint."""
        ...
    def c2c_distance(self, c1_id: int, c2_id: int, dist_id: int, driving: bool = True) -> int:
        """Add circle-to-circle distance constraint."""
        ...
    def c2l_distance(
        self, circle_id: int, line_id: int, dist_id: int, driving: bool = True
    ) -> int:
        """Add circle-to-line distance constraint."""
        ...
    def arc_length(self, arc_id: int, dist_id: int, driving: bool = True) -> int:
        """Constrain arc length."""
        ...
    def internal_alignment_point2ellipse(
        self,
        ellipse_id: int,
        pt_id: int,
        alignment_type: InternalAlignmentType,
        driving: bool = True,
    ) -> int:
        """Internal alignment: point to ellipse."""
        ...
    def tangent_circumf(
        self,
        p1_id: int,
        p2_id: int,
        rd1_id: int,
        rd2_id: int,
        internal: bool = False,
        driving: bool = True,
    ) -> int:
        """Tangent circumference constraint."""
        ...
    def clear_by_tag(self, tag: int) -> None:
        """Clear all constraints with the given tag."""
        ...
    def constraint_error(self, tag: int) -> float:
        """Calculate RMS error of all constraints with given tag."""
        ...
