"""
Python bindings for FreeCAD's PlaneGCS 2D geometric constraint solver
"""

from __future__ import annotations

import collections.abc
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
    def __init__(self, value: typing.SupportsInt | typing.SupportsIndex) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: typing.SupportsInt | typing.SupportsIndex) -> None: ...
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
    def __init__(self, value: typing.SupportsInt | typing.SupportsIndex) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: typing.SupportsInt | typing.SupportsIndex) -> None: ...
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
    def __init__(self, value: typing.SupportsInt | typing.SupportsIndex) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: typing.SupportsInt | typing.SupportsIndex) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class SketchSolver:
    def __init__(self) -> None: ...
    def a2a_distance(
        self,
        a1_id: typing.SupportsInt | typing.SupportsIndex,
        a2_id: typing.SupportsInt | typing.SupportsIndex,
        dist_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add arc-to-arc distance constraint.
        """
    def a2l_distance(
        self,
        arc_id: typing.SupportsInt | typing.SupportsIndex,
        line_id: typing.SupportsInt | typing.SupportsIndex,
        dist_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add arc-to-line distance constraint.
        """
    def add_arc(
        self,
        center_id: typing.SupportsInt | typing.SupportsIndex,
        start_id: typing.SupportsInt | typing.SupportsIndex,
        end_id: typing.SupportsInt | typing.SupportsIndex,
        radius_id: typing.SupportsInt | typing.SupportsIndex,
        start_angle_id: typing.SupportsInt | typing.SupportsIndex,
        end_angle_id: typing.SupportsInt | typing.SupportsIndex,
    ) -> int:
        """
        Add an arc from explicit points and parameters. Automatically adds arc rules. Returns arc ID.
        """
    def add_arc_of_ellipse(
        self,
        center_id: typing.SupportsInt | typing.SupportsIndex,
        focus1_id: typing.SupportsInt | typing.SupportsIndex,
        radmin: typing.SupportsFloat | typing.SupportsIndex,
        start_angle: typing.SupportsFloat | typing.SupportsIndex,
        end_angle: typing.SupportsFloat | typing.SupportsIndex,
        start_id: typing.SupportsInt | typing.SupportsIndex,
        end_id: typing.SupportsInt | typing.SupportsIndex,
    ) -> int:
        """
        Add an arc of ellipse. Returns ID.
        """
    def add_arc_of_hyperbola(
        self,
        center_id: typing.SupportsInt | typing.SupportsIndex,
        focus1_id: typing.SupportsInt | typing.SupportsIndex,
        radmin: typing.SupportsFloat | typing.SupportsIndex,
        start_angle: typing.SupportsFloat | typing.SupportsIndex,
        end_angle: typing.SupportsFloat | typing.SupportsIndex,
        start_id: typing.SupportsInt | typing.SupportsIndex,
        end_id: typing.SupportsInt | typing.SupportsIndex,
    ) -> int:
        """
        Add an arc of hyperbola. Returns ID.
        """
    def add_arc_of_parabola(
        self,
        vertex_id: typing.SupportsInt | typing.SupportsIndex,
        focus1_id: typing.SupportsInt | typing.SupportsIndex,
        start_angle: typing.SupportsFloat | typing.SupportsIndex,
        end_angle: typing.SupportsFloat | typing.SupportsIndex,
        start_id: typing.SupportsInt | typing.SupportsIndex,
        end_id: typing.SupportsInt | typing.SupportsIndex,
    ) -> int:
        """
        Add an arc of parabola. Returns ID.
        """
    def add_bspline(
        self,
        start_id: typing.SupportsInt | typing.SupportsIndex,
        end_id: typing.SupportsInt | typing.SupportsIndex,
        pole_ids: collections.abc.Sequence[typing.SupportsInt | typing.SupportsIndex],
        weight_ids: collections.abc.Sequence[typing.SupportsInt | typing.SupportsIndex],
        knot_ids: collections.abc.Sequence[typing.SupportsInt | typing.SupportsIndex],
        mult: collections.abc.Sequence[typing.SupportsInt | typing.SupportsIndex],
        degree: typing.SupportsInt | typing.SupportsIndex,
        periodic: bool,
    ) -> int:
        """
        Add a B-spline. Returns ID.
        """
    def add_circle(
        self,
        center_id: typing.SupportsInt | typing.SupportsIndex,
        radius_id: typing.SupportsInt | typing.SupportsIndex,
    ) -> int:
        """
        Add a circle. Returns circle ID.
        """
    def add_ellipse(
        self,
        center_id: typing.SupportsInt | typing.SupportsIndex,
        focus1_id: typing.SupportsInt | typing.SupportsIndex,
        radmin: typing.SupportsFloat | typing.SupportsIndex,
    ) -> int:
        """
        Add an ellipse. Returns ellipse ID.
        """
    def add_hyperbola(
        self,
        center_id: typing.SupportsInt | typing.SupportsIndex,
        focus1_id: typing.SupportsInt | typing.SupportsIndex,
        radmin: typing.SupportsFloat | typing.SupportsIndex,
    ) -> int:
        """
        Add a hyperbola. Returns ID.
        """
    @typing.overload
    def add_line(
        self,
        p1_id: typing.SupportsInt | typing.SupportsIndex,
        p2_id: typing.SupportsInt | typing.SupportsIndex,
    ) -> int:
        """
        Add a line between two existing points. Returns line ID.
        """
    @typing.overload
    def add_line(
        self,
        x1: typing.SupportsFloat | typing.SupportsIndex,
        y1: typing.SupportsFloat | typing.SupportsIndex,
        x2: typing.SupportsFloat | typing.SupportsIndex,
        y2: typing.SupportsFloat | typing.SupportsIndex,
    ) -> int:
        """
        Add a line with endpoint coordinates. Returns line ID.
        """
    def add_parabola(
        self,
        vertex_id: typing.SupportsInt | typing.SupportsIndex,
        focus1_id: typing.SupportsInt | typing.SupportsIndex,
    ) -> int:
        """
        Add a parabola. Returns ID.
        """
    def add_param(
        self, value: typing.SupportsFloat | typing.SupportsIndex = 0.0, fixed: bool = False
    ) -> int:
        """
        Allocate a parameter. fixed=True for driving constraint values. Returns param ID.
        """
    def add_point(
        self,
        x: typing.SupportsFloat | typing.SupportsIndex,
        y: typing.SupportsFloat | typing.SupportsIndex,
    ) -> int:
        """
        Add a point. Returns point ID.
        """
    def add_point_from_params(
        self,
        px_id: typing.SupportsInt | typing.SupportsIndex,
        py_id: typing.SupportsInt | typing.SupportsIndex,
    ) -> int:
        """
        Add a point from existing parameter IDs for x and y. Returns point ID.
        """
    def angle_via_point(
        self,
        crv1_id: typing.SupportsInt | typing.SupportsIndex,
        crv2_id: typing.SupportsInt | typing.SupportsIndex,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        angle_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain angle between two curves at a point.
        """
    def angle_via_point_and_param(
        self,
        crv1_id: typing.SupportsInt | typing.SupportsIndex,
        crv2_id: typing.SupportsInt | typing.SupportsIndex,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        cparam_id: typing.SupportsInt | typing.SupportsIndex,
        angle_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain angle between two curves at a point with a curve parameter.
        """
    def angle_via_point_and_two_params(
        self,
        crv1_id: typing.SupportsInt | typing.SupportsIndex,
        crv2_id: typing.SupportsInt | typing.SupportsIndex,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        cparam1_id: typing.SupportsInt | typing.SupportsIndex,
        cparam2_id: typing.SupportsInt | typing.SupportsIndex,
        angle_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain angle between two curves at a point with two curve parameters.
        """
    def angle_via_two_points(
        self,
        crv1_id: typing.SupportsInt | typing.SupportsIndex,
        crv2_id: typing.SupportsInt | typing.SupportsIndex,
        pt1_id: typing.SupportsInt | typing.SupportsIndex,
        pt2_id: typing.SupportsInt | typing.SupportsIndex,
        angle_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain angle between two curves via two points.
        """
    def arc_angle(
        self,
        arc_id: typing.SupportsInt | typing.SupportsIndex,
        angle_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain the angular span (sweep) of an arc using a parameter.
        """
    def arc_diameter(
        self,
        arc_id: typing.SupportsInt | typing.SupportsIndex,
        diameter_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Set arc diameter.
        """
    def arc_length(
        self,
        arc_id: typing.SupportsInt | typing.SupportsIndex,
        dist_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain arc length.
        """
    def arc_of_ellipse_rules(
        self, aoe_id: typing.SupportsInt | typing.SupportsIndex, driving: bool = True
    ) -> int:
        """
        Add arc-of-ellipse rules (start/end tied to ellipse parametric equation).
        """
    def arc_of_hyperbola_rules(
        self, aoh_id: typing.SupportsInt | typing.SupportsIndex, driving: bool = True
    ) -> int:
        """
        Add arc-of-hyperbola rules (start/end tied to hyperbola parametric equation).
        """
    def arc_of_parabola_rules(
        self, aop_id: typing.SupportsInt | typing.SupportsIndex, driving: bool = True
    ) -> int:
        """
        Add arc-of-parabola rules (start/end tied to parabola parametric equation).
        """
    def arc_radius(
        self,
        arc_id: typing.SupportsInt | typing.SupportsIndex,
        radius_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Set arc radius.
        """
    def arc_rules(
        self, arc_id: typing.SupportsInt | typing.SupportsIndex, driving: bool = True
    ) -> int:
        """
        Add arc rules constraint (start/end computed from center+radius+angles).
        """
    def c2a_distance(
        self,
        circle_id: typing.SupportsInt | typing.SupportsIndex,
        arc_id: typing.SupportsInt | typing.SupportsIndex,
        dist_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add circle-to-arc distance constraint.
        """
    def c2c_distance(
        self,
        c1_id: typing.SupportsInt | typing.SupportsIndex,
        c2_id: typing.SupportsInt | typing.SupportsIndex,
        dist_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add circle-to-circle distance constraint.
        """
    def c2l_distance(
        self,
        circle_id: typing.SupportsInt | typing.SupportsIndex,
        line_id: typing.SupportsInt | typing.SupportsIndex,
        dist_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add circle-to-line distance constraint.
        """
    def calculate_angle_via_point(
        self,
        crv1_id: typing.SupportsInt | typing.SupportsIndex,
        crv2_id: typing.SupportsInt | typing.SupportsIndex,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
    ) -> float:
        """
        Calculate the angle between two curves at a point (no constraint added).
        """
    def calculate_angle_via_two_points(
        self,
        crv1_id: typing.SupportsInt | typing.SupportsIndex,
        crv2_id: typing.SupportsInt | typing.SupportsIndex,
        pt1_id: typing.SupportsInt | typing.SupportsIndex,
        pt2_id: typing.SupportsInt | typing.SupportsIndex,
    ) -> float:
        """
        Calculate the angle between two curves via two points (no constraint added).
        """
    def circle_diameter(
        self,
        circle_id: typing.SupportsInt | typing.SupportsIndex,
        diameter_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Set circle diameter.
        """
    def circle_radius(
        self,
        circle_id: typing.SupportsInt | typing.SupportsIndex,
        radius_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Set circle radius.
        """
    def clear(self) -> None:
        """
        Clear all geometry, constraints, and parameters.
        """
    def clear_by_tag(self, tag: typing.SupportsInt | typing.SupportsIndex) -> None:
        """
        Clear all constraints with the given tag.
        """
    def coincident(
        self,
        pt1_id: typing.SupportsInt | typing.SupportsIndex,
        pt2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add coincident constraint between two points.
        """
    def constraint_error(self, tag: typing.SupportsInt | typing.SupportsIndex) -> float:
        """
        Calculate RMS error of all constraints with given tag.
        """
    def coordinate_x(
        self,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        x_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Fix the X coordinate of a point.
        """
    def coordinate_y(
        self,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        y_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Fix the Y coordinate of a point.
        """
    def curve_value(
        self,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        curve_id: typing.SupportsInt | typing.SupportsIndex,
        u_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain a point to lie on a curve at parameter u.
        """
    def diagnose(self, algorithm: Algorithm = Algorithm.DogLeg) -> DiagnosisResult:
        """
        Run full diagnosis. Returns DiagnosisResult with dof, conflicting, redundant, and partially_redundant constraint tags.
        """
    def difference(
        self,
        param1_id: typing.SupportsInt | typing.SupportsIndex,
        param2_id: typing.SupportsInt | typing.SupportsIndex,
        diff_id: typing.SupportsInt | typing.SupportsIndex,
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
        self,
        param1_id: typing.SupportsInt | typing.SupportsIndex,
        param2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add equality constraint between two parameters.
        """
    def equal_focus_pp(
        self,
        p1_id: typing.SupportsInt | typing.SupportsIndex,
        p2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain two arcs of parabola to have equal focal distance.
        """
    def equal_length(
        self,
        l1_id: typing.SupportsInt | typing.SupportsIndex,
        l2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain two lines to have equal length.
        """
    def equal_radii_ee(
        self,
        e1_id: typing.SupportsInt | typing.SupportsIndex,
        e2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain two ellipses to have equal major radii.
        """
    def equal_radii_hh(
        self,
        h1_id: typing.SupportsInt | typing.SupportsIndex,
        h2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain two arcs of hyperbola to have equal major radii.
        """
    def equal_radius_aa(
        self,
        a1_id: typing.SupportsInt | typing.SupportsIndex,
        a2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain two arcs to have equal radius.
        """
    def equal_radius_ca(
        self,
        circle_id: typing.SupportsInt | typing.SupportsIndex,
        arc_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain circle and arc to have equal radius.
        """
    def equal_radius_cc(
        self,
        c1_id: typing.SupportsInt | typing.SupportsIndex,
        c2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain two circles to have equal radius.
        """
    def get_arc_center(
        self, arc_id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_arc_end_angle(self, arc_id: typing.SupportsInt | typing.SupportsIndex) -> float: ...
    def get_arc_end_point(
        self, arc_id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_arc_of_ellipse_center(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_arc_of_ellipse_end_angle(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> float: ...
    def get_arc_of_ellipse_end_point(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_arc_of_ellipse_focus1(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_arc_of_ellipse_radmin(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> float: ...
    def get_arc_of_ellipse_start_angle(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> float: ...
    def get_arc_of_ellipse_start_point(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_arc_of_hyperbola_center(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_arc_of_hyperbola_end_angle(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> float: ...
    def get_arc_of_hyperbola_end_point(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_arc_of_hyperbola_focus1(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_arc_of_hyperbola_radmin(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> float: ...
    def get_arc_of_hyperbola_start_angle(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> float: ...
    def get_arc_of_hyperbola_start_point(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_arc_of_parabola_end_angle(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> float: ...
    def get_arc_of_parabola_end_point(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_arc_of_parabola_focus1(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_arc_of_parabola_start_angle(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> float: ...
    def get_arc_of_parabola_start_point(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_arc_of_parabola_vertex(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_arc_radius(self, arc_id: typing.SupportsInt | typing.SupportsIndex) -> float: ...
    def get_arc_start_angle(self, arc_id: typing.SupportsInt | typing.SupportsIndex) -> float: ...
    def get_arc_start_point(
        self, arc_id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_bspline_end_point(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_bspline_start_point(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_circle_center(
        self, circle_id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_circle_radius(self, circle_id: typing.SupportsInt | typing.SupportsIndex) -> float: ...
    def get_ellipse_center(
        self, ellipse_id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_ellipse_focus1(
        self, ellipse_id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_ellipse_radmin(
        self, ellipse_id: typing.SupportsInt | typing.SupportsIndex
    ) -> float: ...
    def get_hyperbola_center(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_hyperbola_focus1(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_hyperbola_radmin(self, id: typing.SupportsInt | typing.SupportsIndex) -> float: ...
    def get_line_p1(
        self, line_id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_line_p2(
        self, line_id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_parabola_focus1(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_parabola_vertex(
        self, id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]: ...
    def get_param(self, param_id: typing.SupportsInt | typing.SupportsIndex) -> float:
        """
        Get the current value of a parameter.
        """
    def get_point(
        self, point_id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[float, float]:
        """
        Get the (x, y) of a point.
        """
    def get_point_param_ids(
        self, point_id: typing.SupportsInt | typing.SupportsIndex
    ) -> tuple[int, int]:
        """
        Get the (x_param_id, y_param_id) for a point.
        """
    def horizontal_line(
        self, line_id: typing.SupportsInt | typing.SupportsIndex, driving: bool = True
    ) -> int:
        """
        Constrain line to be horizontal.
        """
    def horizontal_points(
        self,
        p1_id: typing.SupportsInt | typing.SupportsIndex,
        p2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain two points to have same Y.
        """
    def internal_alignment_bspline_control_point(
        self,
        bspline_id: typing.SupportsInt | typing.SupportsIndex,
        circle_id: typing.SupportsInt | typing.SupportsIndex,
        pole_index: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Internal alignment: B-spline control point.
        """
    def internal_alignment_ellipse_focus1(
        self,
        ellipse_id: typing.SupportsInt | typing.SupportsIndex,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Internal alignment: ellipse focus 1.
        """
    def internal_alignment_ellipse_focus2(
        self,
        ellipse_id: typing.SupportsInt | typing.SupportsIndex,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Internal alignment: ellipse focus 2.
        """
    def internal_alignment_ellipse_major_diameter(
        self,
        ellipse_id: typing.SupportsInt | typing.SupportsIndex,
        p1_id: typing.SupportsInt | typing.SupportsIndex,
        p2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Internal alignment: ellipse major diameter.
        """
    def internal_alignment_ellipse_minor_diameter(
        self,
        ellipse_id: typing.SupportsInt | typing.SupportsIndex,
        p1_id: typing.SupportsInt | typing.SupportsIndex,
        p2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Internal alignment: ellipse minor diameter.
        """
    def internal_alignment_hyperbola_focus(
        self,
        hyperbola_id: typing.SupportsInt | typing.SupportsIndex,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Internal alignment: hyperbola focus.
        """
    def internal_alignment_hyperbola_major_diameter(
        self,
        hyperbola_id: typing.SupportsInt | typing.SupportsIndex,
        p1_id: typing.SupportsInt | typing.SupportsIndex,
        p2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Internal alignment: hyperbola major diameter.
        """
    def internal_alignment_hyperbola_minor_diameter(
        self,
        hyperbola_id: typing.SupportsInt | typing.SupportsIndex,
        p1_id: typing.SupportsInt | typing.SupportsIndex,
        p2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Internal alignment: hyperbola minor diameter.
        """
    def internal_alignment_knot_point(
        self,
        bspline_id: typing.SupportsInt | typing.SupportsIndex,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        knot_index: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Internal alignment: B-spline knot point.
        """
    def internal_alignment_parabola_focus(
        self,
        parabola_id: typing.SupportsInt | typing.SupportsIndex,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Internal alignment: parabola focus.
        """
    def internal_alignment_point2ellipse(
        self,
        ellipse_id: typing.SupportsInt | typing.SupportsIndex,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        alignment_type: InternalAlignmentType,
        driving: bool = True,
    ) -> int:
        """
        Internal alignment: point to ellipse.
        """
    def internal_alignment_point2hyperbola(
        self,
        hyperbola_id: typing.SupportsInt | typing.SupportsIndex,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        alignment_type: InternalAlignmentType,
        driving: bool = True,
    ) -> int:
        """
        Internal alignment: point to hyperbola.
        """
    def is_param_driven(self, param_id: typing.SupportsInt | typing.SupportsIndex) -> bool:
        """
        Check if a parameter is driven (value param of a non-driving constraint).
        """
    def is_param_fixed(self, param_id: typing.SupportsInt | typing.SupportsIndex) -> bool:
        """
        Check if a parameter is fixed (not an unknown).
        """
    def l2l_angle(
        self,
        l1_id: typing.SupportsInt | typing.SupportsIndex,
        l2_id: typing.SupportsInt | typing.SupportsIndex,
        angle_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add line-to-line angle constraint.
        """
    def midpoint_on_line(
        self,
        l1_id: typing.SupportsInt | typing.SupportsIndex,
        l2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain midpoint of l1 to lie on l2.
        """
    def p2a_distance(
        self,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        arc_id: typing.SupportsInt | typing.SupportsIndex,
        distance_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add point-to-arc distance constraint.
        """
    def p2c_distance(
        self,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        circle_id: typing.SupportsInt | typing.SupportsIndex,
        distance_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add point-to-circle distance constraint.
        """
    def p2l_distance(
        self,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        line_id: typing.SupportsInt | typing.SupportsIndex,
        distance_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add point-to-line distance constraint.
        """
    def p2p_angle(
        self,
        pt1_id: typing.SupportsInt | typing.SupportsIndex,
        pt2_id: typing.SupportsInt | typing.SupportsIndex,
        angle_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add point-to-point angle constraint.
        """
    def p2p_distance(
        self,
        pt1_id: typing.SupportsInt | typing.SupportsIndex,
        pt2_id: typing.SupportsInt | typing.SupportsIndex,
        distance_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add point-to-point distance constraint.
        """
    def parallel(
        self,
        l1_id: typing.SupportsInt | typing.SupportsIndex,
        l2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add parallel constraint.
        """
    def perpendicular(
        self,
        l1_id: typing.SupportsInt | typing.SupportsIndex,
        l2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add perpendicular constraint.
        """
    def point_on_arc(
        self,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        arc_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain point to lie on arc.
        """
    def point_on_bspline(
        self,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        bspline_id: typing.SupportsInt | typing.SupportsIndex,
        u_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain point to lie on B-spline at parameter u.
        """
    def point_on_circle(
        self,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        circle_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain point to lie on circle.
        """
    def point_on_ellipse(
        self,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        ellipse_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain point to lie on ellipse.
        """
    def point_on_hyperbolic_arc(
        self,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        arc_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain point to lie on hyperbolic arc.
        """
    def point_on_line(
        self,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        line_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain point to lie on line.
        """
    def point_on_parabolic_arc(
        self,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        arc_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain point to lie on parabolic arc.
        """
    def point_on_perp_bisector(
        self,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        line_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain point to lie on perpendicular bisector of line.
        """
    def proportional(
        self,
        param1_id: typing.SupportsInt | typing.SupportsIndex,
        param2_id: typing.SupportsInt | typing.SupportsIndex,
        ratio: typing.SupportsFloat | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add proportional constraint.
        """
    def set_param(
        self,
        param_id: typing.SupportsInt | typing.SupportsIndex,
        value: typing.SupportsFloat | typing.SupportsIndex,
    ) -> None:
        """
        Set the value of a parameter.
        """
    def set_param_driven(
        self, param_id: typing.SupportsInt | typing.SupportsIndex, driven: bool = True
    ) -> None:
        """
        Set whether a parameter is driven.
        """
    def set_param_fixed(
        self, param_id: typing.SupportsInt | typing.SupportsIndex, fixed: bool
    ) -> None:
        """
        Set whether a parameter is fixed.
        """
    def snells_law(
        self,
        ray1_id: typing.SupportsInt | typing.SupportsIndex,
        ray2_id: typing.SupportsInt | typing.SupportsIndex,
        boundary_id: typing.SupportsInt | typing.SupportsIndex,
        pt_id: typing.SupportsInt | typing.SupportsIndex,
        n1_id: typing.SupportsInt | typing.SupportsIndex,
        n2_id: typing.SupportsInt | typing.SupportsIndex,
        flipn1: bool = False,
        flipn2: bool = False,
        driving: bool = True,
    ) -> int:
        """
        Add Snell's law refraction constraint at a boundary point.
        """
    def solve(self, algorithm: Algorithm = Algorithm.DogLeg) -> SolveStatus:
        """
        Solve the system. Returns SolveStatus.
        """
    def symmetric_points_line(
        self,
        p1_id: typing.SupportsInt | typing.SupportsIndex,
        p2_id: typing.SupportsInt | typing.SupportsIndex,
        line_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain points symmetric about a line.
        """
    def symmetric_points_point(
        self,
        p1_id: typing.SupportsInt | typing.SupportsIndex,
        p2_id: typing.SupportsInt | typing.SupportsIndex,
        center_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain points symmetric about a center point.
        """
    def tangent_arc_arc(
        self,
        a1_id: typing.SupportsInt | typing.SupportsIndex,
        a2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add arc-arc tangent constraint.
        """
    def tangent_at_bspline_knot(
        self,
        bspline_id: typing.SupportsInt | typing.SupportsIndex,
        line_id: typing.SupportsInt | typing.SupportsIndex,
        knot_index: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Constrain line tangent to B-spline at a knot.
        """
    def tangent_circle_arc(
        self,
        circle_id: typing.SupportsInt | typing.SupportsIndex,
        arc_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add circle-arc tangent constraint.
        """
    def tangent_circle_circle(
        self,
        c1_id: typing.SupportsInt | typing.SupportsIndex,
        c2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add circle-circle tangent constraint.
        """
    def tangent_circumf(
        self,
        p1_id: typing.SupportsInt | typing.SupportsIndex,
        p2_id: typing.SupportsInt | typing.SupportsIndex,
        rd1_id: typing.SupportsInt | typing.SupportsIndex,
        rd2_id: typing.SupportsInt | typing.SupportsIndex,
        internal: bool = False,
        driving: bool = True,
    ) -> int:
        """
        Tangent circumference constraint.
        """
    def tangent_line_arc(
        self,
        line_id: typing.SupportsInt | typing.SupportsIndex,
        arc_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add line-arc tangent constraint.
        """
    def tangent_line_circle(
        self,
        line_id: typing.SupportsInt | typing.SupportsIndex,
        circle_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add line-circle tangent constraint.
        """
    def tangent_line_ellipse(
        self,
        line_id: typing.SupportsInt | typing.SupportsIndex,
        ellipse_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
    ) -> int:
        """
        Add line-ellipse tangent constraint.
        """
    def vertical_line(
        self, line_id: typing.SupportsInt | typing.SupportsIndex, driving: bool = True
    ) -> int:
        """
        Constrain line to be vertical.
        """
    def vertical_points(
        self,
        p1_id: typing.SupportsInt | typing.SupportsIndex,
        p2_id: typing.SupportsInt | typing.SupportsIndex,
        driving: bool = True,
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
    def __init__(self, value: typing.SupportsInt | typing.SupportsIndex) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: typing.SupportsInt | typing.SupportsIndex) -> None: ...
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
