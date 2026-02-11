"""
Python bindings for FreeCAD's PlaneGCS 2D geometric constraint solver
"""

from __future__ import annotations

import typing

__all__: list[str] = [
    "Algorithm",
    "BFGS",
    "Converged",
    "DebugMode",
    "DiagnosisResult",
    "DogLeg",
    "EllipseFocus2X",
    "EllipseFocus2Y",
    "EllipseNegativeMajorX",
    "EllipseNegativeMajorY",
    "EllipseNegativeMinorX",
    "EllipseNegativeMinorY",
    "EllipsePositiveMajorX",
    "EllipsePositiveMajorY",
    "EllipsePositiveMinorX",
    "EllipsePositiveMinorY",
    "Failed",
    "HyperbolaNegativeMajorX",
    "HyperbolaNegativeMajorY",
    "HyperbolaNegativeMinorX",
    "HyperbolaNegativeMinorY",
    "HyperbolaPositiveMajorX",
    "HyperbolaPositiveMajorY",
    "HyperbolaPositiveMinorX",
    "HyperbolaPositiveMinorY",
    "InternalAlignmentType",
    "IterationLevel",
    "LevenbergMarquardt",
    "Minimal",
    "NoDebug",
    "SketchSolver",
    "SolveStatus",
    "Success",
    "SuccessfulSolutionInvalid",
]

class Algorithm:
    """
    Members:

      BFGS

      LevenbergMarquardt

      DogLeg
    """

    BFGS: typing.ClassVar[Algorithm]  # value = <Algorithm.BFGS: 0>
    DogLeg: typing.ClassVar[Algorithm]  # value = <Algorithm.DogLeg: 2>
    LevenbergMarquardt: typing.ClassVar[Algorithm]  # value = <Algorithm.LevenbergMarquardt: 1>
    __members__: typing.ClassVar[
        dict[str, Algorithm]
    ]  # value = {'BFGS': <Algorithm.BFGS: 0>, 'LevenbergMarquardt': <Algorithm.LevenbergMarquardt: 1>, 'DogLeg': <Algorithm.DogLeg: 2>}
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: typing.SupportsInt) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: typing.SupportsInt) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class DebugMode:
    """
    Members:

      NoDebug

      Minimal

      IterationLevel
    """

    IterationLevel: typing.ClassVar[DebugMode]  # value = <DebugMode.IterationLevel: 2>
    Minimal: typing.ClassVar[DebugMode]  # value = <DebugMode.Minimal: 1>
    NoDebug: typing.ClassVar[DebugMode]  # value = <DebugMode.NoDebug: 0>
    __members__: typing.ClassVar[
        dict[str, DebugMode]
    ]  # value = {'NoDebug': <DebugMode.NoDebug: 0>, 'Minimal': <DebugMode.Minimal: 1>, 'IterationLevel': <DebugMode.IterationLevel: 2>}
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: typing.SupportsInt) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: typing.SupportsInt) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class DiagnosisResult:
    @property
    def conflicting(self) -> list[int]:
        """
        Tags of conflicting (over-constraining) constraints.
        """
    @property
    def dof(self) -> int:
        """
        Degrees of freedom. 0 = fully constrained, >0 = under-constrained.
        """
    @property
    def partially_redundant(self) -> list[int]:
        """
        Tags of partially redundant constraints.
        """
    @property
    def redundant(self) -> list[int]:
        """
        Tags of redundant constraints.
        """

class InternalAlignmentType:
    """
    Members:

      EllipsePositiveMajorX

      EllipsePositiveMajorY

      EllipseNegativeMajorX

      EllipseNegativeMajorY

      EllipsePositiveMinorX

      EllipsePositiveMinorY

      EllipseNegativeMinorX

      EllipseNegativeMinorY

      EllipseFocus2X

      EllipseFocus2Y

      HyperbolaPositiveMajorX

      HyperbolaPositiveMajorY

      HyperbolaNegativeMajorX

      HyperbolaNegativeMajorY

      HyperbolaPositiveMinorX

      HyperbolaPositiveMinorY

      HyperbolaNegativeMinorX

      HyperbolaNegativeMinorY
    """

    EllipseFocus2X: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.EllipseFocus2X: 8>
    EllipseFocus2Y: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.EllipseFocus2Y: 9>
    EllipseNegativeMajorX: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.EllipseNegativeMajorX: 2>
    EllipseNegativeMajorY: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.EllipseNegativeMajorY: 3>
    EllipseNegativeMinorX: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.EllipseNegativeMinorX: 6>
    EllipseNegativeMinorY: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.EllipseNegativeMinorY: 7>
    EllipsePositiveMajorX: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.EllipsePositiveMajorX: 0>
    EllipsePositiveMajorY: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.EllipsePositiveMajorY: 1>
    EllipsePositiveMinorX: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.EllipsePositiveMinorX: 4>
    EllipsePositiveMinorY: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.EllipsePositiveMinorY: 5>
    HyperbolaNegativeMajorX: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.HyperbolaNegativeMajorX: 12>
    HyperbolaNegativeMajorY: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.HyperbolaNegativeMajorY: 13>
    HyperbolaNegativeMinorX: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.HyperbolaNegativeMinorX: 16>
    HyperbolaNegativeMinorY: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.HyperbolaNegativeMinorY: 17>
    HyperbolaPositiveMajorX: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.HyperbolaPositiveMajorX: 10>
    HyperbolaPositiveMajorY: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.HyperbolaPositiveMajorY: 11>
    HyperbolaPositiveMinorX: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.HyperbolaPositiveMinorX: 14>
    HyperbolaPositiveMinorY: typing.ClassVar[
        InternalAlignmentType
    ]  # value = <InternalAlignmentType.HyperbolaPositiveMinorY: 15>
    __members__: typing.ClassVar[
        dict[str, InternalAlignmentType]
    ]  # value = {'EllipsePositiveMajorX': <InternalAlignmentType.EllipsePositiveMajorX: 0>, 'EllipsePositiveMajorY': <InternalAlignmentType.EllipsePositiveMajorY: 1>, 'EllipseNegativeMajorX': <InternalAlignmentType.EllipseNegativeMajorX: 2>, 'EllipseNegativeMajorY': <InternalAlignmentType.EllipseNegativeMajorY: 3>, 'EllipsePositiveMinorX': <InternalAlignmentType.EllipsePositiveMinorX: 4>, 'EllipsePositiveMinorY': <InternalAlignmentType.EllipsePositiveMinorY: 5>, 'EllipseNegativeMinorX': <InternalAlignmentType.EllipseNegativeMinorX: 6>, 'EllipseNegativeMinorY': <InternalAlignmentType.EllipseNegativeMinorY: 7>, 'EllipseFocus2X': <InternalAlignmentType.EllipseFocus2X: 8>, 'EllipseFocus2Y': <InternalAlignmentType.EllipseFocus2Y: 9>, 'HyperbolaPositiveMajorX': <InternalAlignmentType.HyperbolaPositiveMajorX: 10>, 'HyperbolaPositiveMajorY': <InternalAlignmentType.HyperbolaPositiveMajorY: 11>, 'HyperbolaNegativeMajorX': <InternalAlignmentType.HyperbolaNegativeMajorX: 12>, 'HyperbolaNegativeMajorY': <InternalAlignmentType.HyperbolaNegativeMajorY: 13>, 'HyperbolaPositiveMinorX': <InternalAlignmentType.HyperbolaPositiveMinorX: 14>, 'HyperbolaPositiveMinorY': <InternalAlignmentType.HyperbolaPositiveMinorY: 15>, 'HyperbolaNegativeMinorX': <InternalAlignmentType.HyperbolaNegativeMinorX: 16>, 'HyperbolaNegativeMinorY': <InternalAlignmentType.HyperbolaNegativeMinorY: 17>}
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: typing.SupportsInt) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: typing.SupportsInt) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class SketchSolver:
    def __init__(self) -> None: ...
    def add_arc_from_center(
        self,
        center_id: typing.SupportsInt,
        radius: typing.SupportsFloat,
        start_angle: typing.SupportsFloat,
        end_angle: typing.SupportsFloat,
    ) -> int:
        """
        Add an arc from center point, radius and angles. Returns arc ID.
        """
    def add_arc_from_start_end(
        self,
        start_id: typing.SupportsInt,
        end_id: typing.SupportsInt,
        radius_id: typing.SupportsInt,
    ) -> int:
        """
        Add an arc from start/end points and a radius parameter. Automatically adds arc rules and coincident constraints. Returns arc ID.
        """
    def add_arc_of_ellipse(
        self,
        center_id: typing.SupportsInt,
        focus1_id: typing.SupportsInt,
        radmin: typing.SupportsFloat,
        start_angle: typing.SupportsFloat,
        end_angle: typing.SupportsFloat,
        start_id: typing.SupportsInt,
        end_id: typing.SupportsInt,
    ) -> int:
        """
        Add an arc of ellipse. Returns ID.
        """
    def add_arc_of_hyperbola(
        self,
        center_id: typing.SupportsInt,
        focus1_id: typing.SupportsInt,
        radmin: typing.SupportsFloat,
        start_angle: typing.SupportsFloat,
        end_angle: typing.SupportsFloat,
        start_id: typing.SupportsInt,
        end_id: typing.SupportsInt,
    ) -> int:
        """
        Add an arc of hyperbola. Returns ID.
        """
    def add_arc_of_parabola(
        self,
        vertex_id: typing.SupportsInt,
        focus1_id: typing.SupportsInt,
        start_angle: typing.SupportsFloat,
        end_angle: typing.SupportsFloat,
        start_id: typing.SupportsInt,
        end_id: typing.SupportsInt,
    ) -> int:
        """
        Add an arc of parabola. Returns ID.
        """
    def add_circle(self, center_id: typing.SupportsInt, radius: typing.SupportsFloat) -> int:
        """
        Add a circle. Returns circle ID.
        """
    def add_ellipse(
        self,
        center_id: typing.SupportsInt,
        focus1_id: typing.SupportsInt,
        radmin: typing.SupportsFloat,
    ) -> int:
        """
        Add an ellipse. Returns ellipse ID.
        """
    def add_hyperbola(
        self,
        center_id: typing.SupportsInt,
        focus1_id: typing.SupportsInt,
        radmin: typing.SupportsFloat,
    ) -> int:
        """
        Add a hyperbola. Returns ID.
        """
    @typing.overload
    def add_line(self, p1_id: typing.SupportsInt, p2_id: typing.SupportsInt) -> int:
        """
        Add a line between two existing points. Returns line ID.
        """
    @typing.overload
    def add_line(
        self,
        x1: typing.SupportsFloat,
        y1: typing.SupportsFloat,
        x2: typing.SupportsFloat,
        y2: typing.SupportsFloat,
    ) -> int:
        """
        Add a line with endpoint coordinates. Returns line ID.
        """
    def add_parabola(self, vertex_id: typing.SupportsInt, focus1_id: typing.SupportsInt) -> int:
        """
        Add a parabola. Returns ID.
        """
    def add_param(self, value: typing.SupportsFloat = 0.0, fixed: bool = False) -> int:
        """
        Allocate a parameter. fixed=True for driving constraint values. Returns param ID.
        """
    def add_point(self, x: typing.SupportsFloat, y: typing.SupportsFloat) -> int:
        """
        Add a point. Returns point ID.
        """
    def arc_diameter(
        self, arc_id: typing.SupportsInt, diameter_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Set arc diameter.
        """
    def arc_length(
        self, arc_id: typing.SupportsInt, dist_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Constrain arc length.
        """
    def arc_radius(
        self, arc_id: typing.SupportsInt, radius_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Set arc radius.
        """
    def arc_rules(self, arc_id: typing.SupportsInt, driving: bool = True) -> int:
        """
        Add arc rules constraint (start/end computed from center+radius+angles).
        """
    def c2c_distance(
        self,
        c1_id: typing.SupportsInt,
        c2_id: typing.SupportsInt,
        dist_id: typing.SupportsInt,
        driving: bool = True,
    ) -> int:
        """
        Add circle-to-circle distance constraint.
        """
    def c2l_distance(
        self,
        circle_id: typing.SupportsInt,
        line_id: typing.SupportsInt,
        dist_id: typing.SupportsInt,
        driving: bool = True,
    ) -> int:
        """
        Add circle-to-line distance constraint.
        """
    def circle_diameter(
        self, circle_id: typing.SupportsInt, diameter_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Set circle diameter.
        """
    def circle_radius(
        self, circle_id: typing.SupportsInt, radius_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Set circle radius.
        """
    def clear(self) -> None:
        """
        Clear all geometry, constraints, and parameters.
        """
    def clear_by_tag(self, tag: typing.SupportsInt) -> None:
        """
        Clear all constraints with the given tag.
        """
    def coincident(
        self, pt1_id: typing.SupportsInt, pt2_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Add coincident constraint between two points.
        """
    def constraint_error(self, tag: typing.SupportsInt) -> float:
        """
        Calculate RMS error of all constraints with given tag.
        """
    def coordinate_x(
        self, pt_id: typing.SupportsInt, x_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Fix the X coordinate of a point.
        """
    def coordinate_y(
        self, pt_id: typing.SupportsInt, y_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Fix the Y coordinate of a point.
        """
    def diagnose(self, algorithm: Algorithm = Algorithm.DogLeg) -> DiagnosisResult:
        """
        Run full diagnosis. Returns DiagnosisResult with dof, conflicting, redundant, and partially_redundant constraint tags.
        """
    def difference(
        self,
        param1_id: typing.SupportsInt,
        param2_id: typing.SupportsInt,
        diff_id: typing.SupportsInt,
        driving: bool = True,
    ) -> int:
        """
        Add difference constraint.
        """
    def dof(self) -> int:
        """
        Return degrees of freedom after running diagnosis. 0 = fully constrained, >0 = under-constrained.
        """
    def equal(
        self, param1_id: typing.SupportsInt, param2_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Add equality constraint between two parameters.
        """
    def equal_length(
        self, l1_id: typing.SupportsInt, l2_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Constrain two lines to have equal length.
        """
    def equal_radius_aa(
        self, a1_id: typing.SupportsInt, a2_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Constrain two arcs to have equal radius.
        """
    def equal_radius_ca(
        self, circle_id: typing.SupportsInt, arc_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Constrain circle and arc to have equal radius.
        """
    def equal_radius_cc(
        self, c1_id: typing.SupportsInt, c2_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Constrain two circles to have equal radius.
        """
    def get_arc_center(self, arc_id: typing.SupportsInt) -> tuple[float, float]:
        """
        Get the (x, y) of an arc's center.
        """
    def get_arc_end_angle(self, arc_id: typing.SupportsInt) -> float:
        """
        Get the end angle of an arc (radians).
        """
    def get_arc_end_point(self, arc_id: typing.SupportsInt) -> tuple[float, float]:
        """
        Get the (x, y) of an arc's end point.
        """
    def get_arc_radius(self, arc_id: typing.SupportsInt) -> float:
        """
        Get the radius of an arc.
        """
    def get_arc_start_angle(self, arc_id: typing.SupportsInt) -> float:
        """
        Get the start angle of an arc (radians).
        """
    def get_arc_start_point(self, arc_id: typing.SupportsInt) -> tuple[float, float]:
        """
        Get the (x, y) of an arc's start point.
        """
    def get_param(self, param_id: typing.SupportsInt) -> float:
        """
        Get the current value of a parameter.
        """
    def get_point(self, point_id: typing.SupportsInt) -> tuple[float, float]:
        """
        Get the (x, y) of a point.
        """
    def horizontal_line(self, line_id: typing.SupportsInt, driving: bool = True) -> int:
        """
        Constrain line to be horizontal.
        """
    def horizontal_points(
        self, p1_id: typing.SupportsInt, p2_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Constrain two points to have same Y.
        """
    def internal_alignment_point2ellipse(
        self,
        ellipse_id: typing.SupportsInt,
        pt_id: typing.SupportsInt,
        alignment_type: InternalAlignmentType,
        driving: bool = True,
    ) -> int:
        """
        Internal alignment: point to ellipse.
        """
    def is_param_fixed(self, param_id: typing.SupportsInt) -> bool:
        """
        Check if a parameter is fixed (not an unknown).
        """
    def l2l_angle(
        self,
        l1_id: typing.SupportsInt,
        l2_id: typing.SupportsInt,
        angle_id: typing.SupportsInt,
        driving: bool = True,
    ) -> int:
        """
        Add line-to-line angle constraint.
        """
    def midpoint_on_line(
        self, l1_id: typing.SupportsInt, l2_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Constrain midpoint of l1 to lie on l2.
        """
    def p2c_distance(
        self,
        pt_id: typing.SupportsInt,
        circle_id: typing.SupportsInt,
        distance_id: typing.SupportsInt,
        driving: bool = True,
    ) -> int:
        """
        Add point-to-circle distance constraint.
        """
    def p2l_distance(
        self,
        pt_id: typing.SupportsInt,
        line_id: typing.SupportsInt,
        distance_id: typing.SupportsInt,
        driving: bool = True,
    ) -> int:
        """
        Add point-to-line distance constraint.
        """
    def p2p_angle(
        self,
        pt1_id: typing.SupportsInt,
        pt2_id: typing.SupportsInt,
        angle_id: typing.SupportsInt,
        driving: bool = True,
    ) -> int:
        """
        Add point-to-point angle constraint.
        """
    def p2p_distance(
        self,
        pt1_id: typing.SupportsInt,
        pt2_id: typing.SupportsInt,
        distance_id: typing.SupportsInt,
        driving: bool = True,
    ) -> int:
        """
        Add point-to-point distance constraint.
        """
    def parallel(
        self, l1_id: typing.SupportsInt, l2_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Add parallel constraint.
        """
    def perpendicular(
        self, l1_id: typing.SupportsInt, l2_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Add perpendicular constraint.
        """
    def point_on_arc(
        self, pt_id: typing.SupportsInt, arc_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Constrain point to lie on arc.
        """
    def point_on_circle(
        self, pt_id: typing.SupportsInt, circle_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Constrain point to lie on circle.
        """
    def point_on_ellipse(
        self, pt_id: typing.SupportsInt, ellipse_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Constrain point to lie on ellipse.
        """
    def point_on_line(
        self, pt_id: typing.SupportsInt, line_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Constrain point to lie on line.
        """
    def point_on_perp_bisector(
        self, pt_id: typing.SupportsInt, line_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Constrain point to lie on perpendicular bisector of line.
        """
    def proportional(
        self,
        param1_id: typing.SupportsInt,
        param2_id: typing.SupportsInt,
        ratio: typing.SupportsFloat,
        driving: bool = True,
    ) -> int:
        """
        Add proportional constraint.
        """
    def set_param(self, param_id: typing.SupportsInt, value: typing.SupportsFloat) -> None:
        """
        Set the value of a parameter.
        """
    def set_param_fixed(self, param_id: typing.SupportsInt, fixed: bool) -> None:
        """
        Set whether a parameter is fixed.
        """
    def solve(self, algorithm: Algorithm = Algorithm.DogLeg) -> SolveStatus:
        """
        Solve the system. Returns SolveStatus.
        """
    def symmetric_points_line(
        self,
        p1_id: typing.SupportsInt,
        p2_id: typing.SupportsInt,
        line_id: typing.SupportsInt,
        driving: bool = True,
    ) -> int:
        """
        Constrain points symmetric about a line.
        """
    def symmetric_points_point(
        self,
        p1_id: typing.SupportsInt,
        p2_id: typing.SupportsInt,
        center_id: typing.SupportsInt,
        driving: bool = True,
    ) -> int:
        """
        Constrain points symmetric about a center point.
        """
    def tangent_arc_arc(
        self, a1_id: typing.SupportsInt, a2_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Add arc-arc tangent constraint.
        """
    def tangent_circle_arc(
        self, circle_id: typing.SupportsInt, arc_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Add circle-arc tangent constraint.
        """
    def tangent_circle_circle(
        self, c1_id: typing.SupportsInt, c2_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Add circle-circle tangent constraint.
        """
    def tangent_circumf(
        self,
        p1_id: typing.SupportsInt,
        p2_id: typing.SupportsInt,
        rd1_id: typing.SupportsInt,
        rd2_id: typing.SupportsInt,
        internal: bool = False,
        driving: bool = True,
    ) -> int:
        """
        Tangent circumference constraint.
        """
    def tangent_line_arc(
        self, line_id: typing.SupportsInt, arc_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Add line-arc tangent constraint.
        """
    def tangent_line_circle(
        self, line_id: typing.SupportsInt, circle_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Add line-circle tangent constraint.
        """
    def tangent_line_ellipse(
        self, line_id: typing.SupportsInt, ellipse_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Add line-ellipse tangent constraint.
        """
    def vertical_line(self, line_id: typing.SupportsInt, driving: bool = True) -> int:
        """
        Constrain line to be vertical.
        """
    def vertical_points(
        self, p1_id: typing.SupportsInt, p2_id: typing.SupportsInt, driving: bool = True
    ) -> int:
        """
        Constrain two points to have same X.
        """

class SolveStatus:
    """
    Members:

      Success

      Converged

      Failed

      SuccessfulSolutionInvalid
    """

    Converged: typing.ClassVar[SolveStatus]  # value = <SolveStatus.Converged: 1>
    Failed: typing.ClassVar[SolveStatus]  # value = <SolveStatus.Failed: 2>
    Success: typing.ClassVar[SolveStatus]  # value = <SolveStatus.Success: 0>
    SuccessfulSolutionInvalid: typing.ClassVar[
        SolveStatus
    ]  # value = <SolveStatus.SuccessfulSolutionInvalid: 3>
    __members__: typing.ClassVar[
        dict[str, SolveStatus]
    ]  # value = {'Success': <SolveStatus.Success: 0>, 'Converged': <SolveStatus.Converged: 1>, 'Failed': <SolveStatus.Failed: 2>, 'SuccessfulSolutionInvalid': <SolveStatus.SuccessfulSolutionInvalid: 3>}
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: typing.SupportsInt) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: typing.SupportsInt) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

BFGS: Algorithm  # value = <Algorithm.BFGS: 0>
Converged: SolveStatus  # value = <SolveStatus.Converged: 1>
DogLeg: Algorithm  # value = <Algorithm.DogLeg: 2>
EllipseFocus2X: InternalAlignmentType  # value = <InternalAlignmentType.EllipseFocus2X: 8>
EllipseFocus2Y: InternalAlignmentType  # value = <InternalAlignmentType.EllipseFocus2Y: 9>
EllipseNegativeMajorX: (
    InternalAlignmentType  # value = <InternalAlignmentType.EllipseNegativeMajorX: 2>
)
EllipseNegativeMajorY: (
    InternalAlignmentType  # value = <InternalAlignmentType.EllipseNegativeMajorY: 3>
)
EllipseNegativeMinorX: (
    InternalAlignmentType  # value = <InternalAlignmentType.EllipseNegativeMinorX: 6>
)
EllipseNegativeMinorY: (
    InternalAlignmentType  # value = <InternalAlignmentType.EllipseNegativeMinorY: 7>
)
EllipsePositiveMajorX: (
    InternalAlignmentType  # value = <InternalAlignmentType.EllipsePositiveMajorX: 0>
)
EllipsePositiveMajorY: (
    InternalAlignmentType  # value = <InternalAlignmentType.EllipsePositiveMajorY: 1>
)
EllipsePositiveMinorX: (
    InternalAlignmentType  # value = <InternalAlignmentType.EllipsePositiveMinorX: 4>
)
EllipsePositiveMinorY: (
    InternalAlignmentType  # value = <InternalAlignmentType.EllipsePositiveMinorY: 5>
)
Failed: SolveStatus  # value = <SolveStatus.Failed: 2>
HyperbolaNegativeMajorX: (
    InternalAlignmentType  # value = <InternalAlignmentType.HyperbolaNegativeMajorX: 12>
)
HyperbolaNegativeMajorY: (
    InternalAlignmentType  # value = <InternalAlignmentType.HyperbolaNegativeMajorY: 13>
)
HyperbolaNegativeMinorX: (
    InternalAlignmentType  # value = <InternalAlignmentType.HyperbolaNegativeMinorX: 16>
)
HyperbolaNegativeMinorY: (
    InternalAlignmentType  # value = <InternalAlignmentType.HyperbolaNegativeMinorY: 17>
)
HyperbolaPositiveMajorX: (
    InternalAlignmentType  # value = <InternalAlignmentType.HyperbolaPositiveMajorX: 10>
)
HyperbolaPositiveMajorY: (
    InternalAlignmentType  # value = <InternalAlignmentType.HyperbolaPositiveMajorY: 11>
)
HyperbolaPositiveMinorX: (
    InternalAlignmentType  # value = <InternalAlignmentType.HyperbolaPositiveMinorX: 14>
)
HyperbolaPositiveMinorY: (
    InternalAlignmentType  # value = <InternalAlignmentType.HyperbolaPositiveMinorY: 15>
)
IterationLevel: DebugMode  # value = <DebugMode.IterationLevel: 2>
LevenbergMarquardt: Algorithm  # value = <Algorithm.LevenbergMarquardt: 1>
Minimal: DebugMode  # value = <DebugMode.Minimal: 1>
NoDebug: DebugMode  # value = <DebugMode.NoDebug: 0>
Success: SolveStatus  # value = <SolveStatus.Success: 0>
SuccessfulSolutionInvalid: SolveStatus  # value = <SolveStatus.SuccessfulSolutionInvalid: 3>
