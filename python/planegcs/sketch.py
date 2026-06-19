"""High-level Pythonic interface for the PlaneGCS constraint solver.

Angle convention
~~~~~~~~~~~~~~~~

All angles (for arcs, ellipses, etc.) are in **radians**, measured
**counterclockwise (CCW) from the positive x-axis** — the standard
mathematical convention.

Arc direction
~~~~~~~~~~~~~

An arc's direction is determined by its **sweep** (``end_angle -
start_angle``).  A positive sweep traces the arc counterclockwise;
a negative sweep traces it clockwise.  FreeCAD always uses CCW arcs
(``end_angle >= start_angle``).

Arc-rules constraints (added automatically by :meth:`Sketch.add_arc`)
tie the start and end *points* to the angles via the parametric
equation ``point = center + radius * (cos θ, sin θ)``.
"""

from __future__ import annotations

import functools
import math
from collections.abc import Callable
from dataclasses import dataclass, field
from types import FunctionType
from typing import Literal, NewType

from planegcs._planegcs import Algorithm, InternalAlignmentType, SketchSolver, SolveStatus

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
"""ID for an arc (returned by :meth:`Sketch.add_arc`)."""

EllipseId = NewType("EllipseId", int)
"""ID for an ellipse (returned by :meth:`Sketch.add_ellipse`)."""

ArcOfEllipseId = NewType("ArcOfEllipseId", int)
"""ID for an arc of ellipse (returned by :meth:`Sketch.add_arc_of_ellipse`)."""

HyperbolaId = NewType("HyperbolaId", int)
"""ID for a hyperbola (returned by :meth:`Sketch.add_hyperbola`)."""

ArcOfHyperbolaId = NewType("ArcOfHyperbolaId", int)
"""ID for an arc of hyperbola (returned by :meth:`Sketch.add_arc_of_hyperbola`)."""

ParabolaId = NewType("ParabolaId", int)
"""ID for a parabola (returned by :meth:`Sketch.add_parabola`)."""

ArcOfParabolaId = NewType("ArcOfParabolaId", int)
"""ID for an arc of parabola (returned by :meth:`Sketch.add_arc_of_parabola`)."""

BSplineId = NewType("BSplineId", int)
"""ID for a B-spline (returned by :meth:`Sketch.add_bspline`)."""

type CurveId = (
    CircleId
    | EllipseId
    | ArcId
    | LineId
    | ArcOfEllipseId
    | HyperbolaId
    | ArcOfHyperbolaId
    | ParabolaId
    | ArcOfParabolaId
    | BSplineId
)
"""ID for any geometry usable as a curve (line, circle, arc, ellipse, etc.)."""

ConstraintTag = NewType("ConstraintTag", int)
"""Tag for a constraint (returned by constraint methods)."""

type PointInfo = tuple[float, float]
"""(x, y) coordinates of a point, returned by :meth:`Sketch.get_point`."""

EntityType = Literal[
    "point",
    "line",
    "circle",
    "arc",
    "ellipse",
    "arc_of_ellipse",
    "hyperbola",
    "arc_of_hyperbola",
    "parabola",
    "arc_of_parabola",
    "bspline",
    "param",
]
"""The kind of geometric entity or parameter an ID refers to."""


@dataclass(frozen=True, slots=True)
class EntityInfo:
    """Description of a geometric entity or parameter in a :class:`Sketch`.

    Returned by :meth:`Sketch.get_entity`.  Gives the entity's type and
    current solver value so that opaque integer IDs become meaningful.
    """

    id: int
    """The numeric ID of the entity (same value as the typed ID)."""

    type: EntityType
    """Kind of entity: ``"point"``, ``"line"``, ``"circle"``, ``"arc"``,
    ``"ellipse"``, or ``"param"``."""

    value: (
        PointInfo
        | LineInfo
        | CircleInfo
        | ArcInfo
        | EllipseInfo
        | ArcOfEllipseInfo
        | HyperbolaInfo
        | ArcOfHyperbolaInfo
        | ParabolaInfo
        | ArcOfParabolaInfo
        | BSplineInfo
        | float
    )
    """Current solver value.

    The concrete type depends on :attr:`type`:

    - ``"point"`` → ``PointInfo`` (an ``(x, y)`` tuple)
    - ``"line"`` → :class:`LineInfo`
    - ``"circle"`` → :class:`CircleInfo`
    - ``"arc"`` → :class:`ArcInfo`
    - ``"ellipse"`` → :class:`EllipseInfo`
    - ``"arc_of_ellipse"`` → :class:`ArcOfEllipseInfo`
    - ``"hyperbola"`` → :class:`HyperbolaInfo`
    - ``"arc_of_hyperbola"`` → :class:`ArcOfHyperbolaInfo`
    - ``"parabola"`` → :class:`ParabolaInfo`
    - ``"arc_of_parabola"`` → :class:`ArcOfParabolaInfo`
    - ``"bspline"`` → :class:`BSplineInfo`
    - ``"param"`` → ``float``
    """

    def __repr__(self) -> str:
        return f"EntityInfo(id={self.id}, type={self.type!r}, value={self.value!r})"


@dataclass(frozen=True, slots=True)
class ConstraintInfo:
    """Metadata about a constraint, recorded when it is added to a :class:`Sketch`.

    Provides human-readable information about what a constraint tag refers to,
    so diagnosis results can be understood without manually tracking tags.
    """

    tag: ConstraintTag
    """The unique constraint tag (same value returned by the constraint method)."""

    type_name: str
    """Human-readable name of the constraint type (e.g. ``"horizontal"``,
    ``"p2p_distance"``, ``"coincident"``)."""

    entities: tuple[int, ...]
    """IDs of the geometry/parameter entities involved in this constraint.

    The meaning depends on ``type_name``. For example:

    - ``"horizontal"`` → ``(line_id,)``
    - ``"p2p_distance"`` → ``(pt1_id, pt2_id, distance_param_id)``
    - ``"coincident"`` → ``(pt1_id, pt2_id)``
    - ``"fix_point_x"`` → ``(pt_id, x_param_id)``
    """

    driving: bool
    """Whether this is a driving constraint."""

    def __repr__(self) -> str:
        return (
            f"ConstraintInfo(tag={self.tag}, type_name={self.type_name!r}, "
            f"entities={self.entities}, driving={self.driving})"
        )

    def get_entities(self, sketch: Sketch) -> list[EntityInfo]:
        """Resolve each entity ID to an :class:`EntityInfo` via *sketch*.

        Returns a list in the same order as :attr:`entities`.  IDs that
        the sketch cannot resolve (e.g. internal solver IDs) are omitted.

        Args:
            sketch: The :class:`Sketch` that owns this constraint.

        Example::

            diag = sketch.diagnose()
            for ci in diag.conflicting_info:
                for entity in ci.get_entities(sketch):
                    print(entity.type, entity.value)
        """
        result: list[EntityInfo] = []
        for eid in self.entities:
            info = sketch.get_entity(eid)
            if info is not None:
                result.append(info)
        return result


@dataclass(frozen=True, slots=True)
class LineInfo:
    """Properties of a line, returned by :meth:`Sketch.get_line`."""

    p1: PointInfo
    """(x, y) of the first endpoint."""

    p2: PointInfo
    """(x, y) of the second endpoint."""


@dataclass(frozen=True, slots=True)
class CircleInfo:
    """Properties of a circle, returned by :meth:`Sketch.get_circle`."""

    center: PointInfo
    """(x, y) of the circle center."""

    radius: float
    """Circle radius."""


@dataclass(frozen=True, slots=True)
class ArcInfo:
    """Properties of an arc, returned by :meth:`Sketch.get_arc`.

    Angles use the standard mathematical convention: measured in radians,
    counterclockwise from the positive x-axis.  The **sweep** of the arc
    is ``end_angle - start_angle``:

    * **Positive sweep** (``end_angle > start_angle``): the arc goes
      **counterclockwise** from start to end.
    * **Negative sweep** (``end_angle < start_angle``): the arc goes
      **clockwise** from start to end.

    Start and end points are kept consistent with the angles via the
    parametric equation::

        point = center + radius * (cos(angle), sin(angle))
    """

    center: PointInfo
    """(x, y) of the arc center."""

    radius: float
    """Arc radius (should be positive)."""

    start_angle: float
    """Start angle in radians (CCW from positive x-axis)."""

    end_angle: float
    """End angle in radians (CCW from positive x-axis)."""

    start_point: PointInfo
    """(x, y) of the arc start point."""

    end_point: PointInfo
    """(x, y) of the arc end point."""

    @property
    def arc_size(self) -> float:
        """Angular sweep of the arc in radians (``end_angle - start_angle``).

        Positive for counterclockwise arcs, negative for clockwise.
        """
        return self.end_angle - self.start_angle


@dataclass(frozen=True, slots=True)
class EllipseInfo:
    """Properties of an ellipse, returned by :meth:`Sketch.get_ellipse`."""

    center: PointInfo
    """(x, y) of the ellipse center."""

    focus1: PointInfo
    """(x, y) of the first focus."""

    radmin: float
    """Semi-minor axis radius."""


@dataclass(frozen=True, slots=True)
class ArcOfEllipseInfo:
    """Properties of an arc of ellipse, returned by :meth:`Sketch.get_arc_of_ellipse`."""

    center: PointInfo
    """(x, y) of the ellipse center."""

    focus1: PointInfo
    """(x, y) of the first focus."""

    radmin: float
    """Semi-minor axis radius."""

    start_angle: float
    """Start angle in radians."""

    end_angle: float
    """End angle in radians."""

    start: PointInfo
    """(x, y) of the arc start point."""

    end: PointInfo
    """(x, y) of the arc end point."""


@dataclass(frozen=True, slots=True)
class HyperbolaInfo:
    """Properties of a hyperbola, returned by :meth:`Sketch.get_hyperbola`."""

    center: PointInfo
    """(x, y) of the hyperbola center."""

    focus1: PointInfo
    """(x, y) of the first focus."""

    radmin: float
    """Semi-minor axis radius."""


@dataclass(frozen=True, slots=True)
class ArcOfHyperbolaInfo:
    """Properties of an arc of hyperbola, returned by :meth:`Sketch.get_arc_of_hyperbola`."""

    center: PointInfo
    """(x, y) of the hyperbola center."""

    focus1: PointInfo
    """(x, y) of the first focus."""

    radmin: float
    """Semi-minor axis radius."""

    start_angle: float
    """Start angle (hyperbolic parameter) in radians."""

    end_angle: float
    """End angle (hyperbolic parameter) in radians."""

    start: PointInfo
    """(x, y) of the arc start point."""

    end: PointInfo
    """(x, y) of the arc end point."""


@dataclass(frozen=True, slots=True)
class ParabolaInfo:
    """Properties of a parabola, returned by :meth:`Sketch.get_parabola`."""

    vertex: PointInfo
    """(x, y) of the parabola vertex."""

    focus1: PointInfo
    """(x, y) of the focus."""


@dataclass(frozen=True, slots=True)
class ArcOfParabolaInfo:
    """Properties of an arc of parabola, returned by :meth:`Sketch.get_arc_of_parabola`."""

    vertex: PointInfo
    """(x, y) of the parabola vertex."""

    focus1: PointInfo
    """(x, y) of the focus."""

    start_angle: float
    """Start parameter."""

    end_angle: float
    """End parameter."""

    start: PointInfo
    """(x, y) of the arc start point."""

    end: PointInfo
    """(x, y) of the arc end point."""


@dataclass(frozen=True, slots=True)
class BSplineInfo:
    """Properties of a B-spline, returned by :meth:`Sketch.get_bspline`."""

    start: PointInfo
    """(x, y) of the spline start point."""

    end: PointInfo
    """(x, y) of the spline end point."""

    poles: list[PointInfo]
    """Control points as a list of (x, y) tuples."""

    weights: list[float]
    """Weight values, one per pole."""

    knots: list[float]
    """Knot values."""

    multiplicities: list[int]
    """Multiplicity vector, one per knot."""

    degree: int
    """Spline degree."""


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

    conflicting_info: list[ConstraintInfo] = field(default_factory=list)
    """Rich information about each conflicting constraint.

    Same constraints as :attr:`conflicting`, but as :class:`ConstraintInfo`
    objects that include the constraint type and involved entities.
    Tags not found in the sketch's constraint registry (e.g. internal
    constraints) are omitted.
    """

    redundant_info: list[ConstraintInfo] = field(default_factory=list)
    """Rich information about each redundant constraint."""

    partially_redundant_info: list[ConstraintInfo] = field(default_factory=list)
    """Rich information about each partially redundant constraint."""

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


@dataclass(frozen=True, slots=True)
class _BSplineData:
    """Internal storage for B-spline construction data."""

    pole_ids: list[PointId]
    weight_ids: list[ParamId]
    knot_ids: list[ParamId]
    mult: list[int]
    degree: int


class Sketch:
    """A 2D constraint sketch.

    Provides a convenient Pythonic API on top of :class:`SketchSolver`.
    Geometry is added with ``add_*`` methods which return typed IDs.
    Constraints are added with descriptive methods. Call :meth:`solve`
    to find a configuration satisfying all constraints.

    Example::

        s = Sketch()
        p1 = s.add_fixed_point(0, 0)
        p2 = s.add_point(5, 0)
        p3 = s.add_point(2.5, 4)
        l1 = s.add_line(p1, p2)
        l2 = s.add_line(p2, p3)
        l3 = s.add_line(p3, p1)
        s.equal_length(l1, l2)
        s.equal_length(l2, l3)
        s.horizontal(l1)
        s.set_p2p_distance(p1, p2, 5.0)
        status = s.solve()
        assert status == SolveStatus.Success
    """

    def __init__(self) -> None:
        self._solver = RecordingSketchSolver(self)
        self._constraints: dict[ConstraintTag, ConstraintInfo] = {}
        self._entity_types: dict[int, EntityType] = {}
        self._bspline_data: dict[BSplineId, _BSplineData] = {}

    @property
    def solver(self) -> SketchSolver:
        """Access the underlying :class:`SketchSolver`."""
        return self._solver

    @property
    def constraints(self) -> dict[ConstraintTag, ConstraintInfo]:
        """All constraints registered in this sketch, keyed by tag.

        This is a read-only view of the constraint metadata recorded
        when constraints are added via the ``Sketch`` API.
        """
        return self._constraints

    def get_constraint_info(self, tag: ConstraintTag) -> ConstraintInfo | None:
        """Look up constraint metadata by tag.

        Returns ``None`` if the tag is not found (e.g. internal constraints
        created by the solver itself).
        """
        return self._constraints.get(tag)

    def get_entity(self, entity_id: int) -> EntityInfo | None:
        """Look up an entity by its numeric ID.

        Returns an :class:`EntityInfo` with the entity's type and current
        solver value, or ``None`` if the ID is not recognised (e.g. an
        internal solver ID that was never registered via the Sketch API).

        This is the primary way to understand the opaque integer IDs that
        appear in :attr:`ConstraintInfo.entities`.

        Example::

            line = sketch.add_line(p1, p2)
            info = sketch.get_entity(line)
            assert info.type == "line"
            assert isinstance(info.value, LineInfo)
        """
        etype = self._entity_types.get(entity_id)
        if etype is None:
            return None
        if etype == "point":
            value = self.get_point(PointId(entity_id))
        elif etype == "line":
            value = self.get_line(LineId(entity_id))
        elif etype == "circle":
            value = self.get_circle(CircleId(entity_id))
        elif etype == "arc":
            value = self.get_arc(ArcId(entity_id))
        elif etype == "ellipse":
            value = self.get_ellipse(EllipseId(entity_id))
        elif etype == "arc_of_ellipse":
            value = self.get_arc_of_ellipse(ArcOfEllipseId(entity_id))
        elif etype == "hyperbola":
            value = self.get_hyperbola(HyperbolaId(entity_id))
        elif etype == "arc_of_hyperbola":
            value = self.get_arc_of_hyperbola(ArcOfHyperbolaId(entity_id))
        elif etype == "parabola":
            value = self.get_parabola(ParabolaId(entity_id))
        elif etype == "arc_of_parabola":
            value = self.get_arc_of_parabola(ArcOfParabolaId(entity_id))
        elif etype == "bspline":
            value = self.get_bspline(BSplineId(entity_id))
        elif etype == "param":
            value = self.get_param(ParamId(entity_id))
        else:  # pragma: no cover
            return None
        return EntityInfo(id=entity_id, type=etype, value=value)

    # ── Parameters ─────────────────────────────────────────────────

    def add_param(self, value: float = 0.0, *, fixed: bool = False) -> ParamId:
        """Allocate a standalone parameter.

        By default the parameter is **free** — the solver may change it.
        For driving-constraint values that the solver should not touch,
        use :meth:`add_fixed_param` or pass ``fixed=True``.

        Args:
            value: Initial value.
            fixed: If True, the solver treats this as a constant.
                   Defaults to False (free unknown).

        Returns:
            Parameter ID.
        """
        pid = ParamId(self._solver.add_param(value, fixed))
        self._entity_types[pid] = "param"
        return pid

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
        pid = PointId(self._solver.add_point(x, y))
        self._entity_types[pid] = "point"
        return pid

    def add_point_from_params(self, px_id: ParamId, py_id: ParamId) -> PointId:
        """Add a point from existing parameter IDs for x and y.

        Unlike :meth:`add_point`, which creates fresh parameters internally,
        this lets you supply parameters you already control — useful when
        you need to apply parameter-level constraints (e.g.
        :meth:`difference`, :meth:`equal`) to the coordinates, or when
        you want to share a parameter between multiple points.
        """
        pid = PointId(self._solver.add_point_from_params(px_id, py_id))
        self._entity_types[pid] = "point"
        return pid

    def get_point(self, point_id: PointId) -> PointInfo:
        """Get current (x, y) of a point."""
        return self._solver.get_point(point_id)

    def get_point_param_ids(self, point_id: PointId) -> tuple[ParamId, ParamId]:
        """Get the (x_param_id, y_param_id) for a point.

        Useful when you need to apply parameter-level constraints
        (e.g. :meth:`difference`, :meth:`equal`, :meth:`proportional`)
        to individual coordinates of a point.
        """
        px, py = self._solver.get_point_param_ids(point_id)
        return ParamId(px), ParamId(py)

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
        lid = LineId(self._solver.add_line(p1_id, p2_id))
        self._entity_types[lid] = "line"
        return lid

    def add_line_xy(self, x1: float, y1: float, x2: float, y2: float) -> LineId:
        """Add a line with endpoint coordinates. Returns line ID."""
        lid = LineId(self._solver.add_line(x1, y1, x2, y2))
        self._entity_types[lid] = "line"
        return lid

    def get_line(self, line_id: LineId) -> LineInfo:
        """Get all properties of a line.

        Returns a :class:`LineInfo` dataclass with ``p1`` and ``p2`` fields.
        """
        return LineInfo(
            p1=self._solver.get_line_p1(line_id),
            p2=self._solver.get_line_p2(line_id),
        )

    def add_circle(self, center_id: PointId, radius_id: ParamId) -> CircleId:
        """Add a circle. Returns circle ID."""
        cid = CircleId(self._solver.add_circle(center_id, radius_id))
        self._entity_types[cid] = "circle"
        return cid

    def get_circle(self, circle_id: CircleId) -> CircleInfo:
        """Get all properties of a circle.

        Returns a :class:`CircleInfo` dataclass with ``center`` and
        ``radius`` fields.
        """
        return CircleInfo(
            center=self._solver.get_circle_center(circle_id),
            radius=self._solver.get_circle_radius(circle_id),
        )

    def add_arc(
        self,
        center_id: PointId,
        start_id: PointId,
        end_id: PointId,
        radius_id: ParamId,
        start_angle_id: ParamId,
        end_angle_id: ParamId,
    ) -> ArcId:
        """Add an arc from explicit points and angle/radius parameters.

        The caller supplies all six components that define an arc:
        three points (center, start, end) and three scalar parameters
        (radius, start angle, end angle).

        **Angle convention:** angles are in radians, measured
        counterclockwise (CCW) from the positive x-axis.  The arc
        traces from *start_angle* to *end_angle*:

        * ``end_angle > start_angle`` → **CCW** arc.
        * ``end_angle < start_angle`` → **CW** arc.

        **Arc rules** are added automatically so that start and end
        points satisfy ``point = center + radius * (cos θ, sin θ)``.
        The radius should be positive.

        No hidden geometry or parameters are created.

        .. note::

           FreeCAD always uses CCW arcs (``end_angle >= start_angle``).
           If you are reproducing a FreeCAD sketch, keep
           ``end_angle >= start_angle``.

        Args:
            center_id: Center point of the arc.
            start_id: Start point of the arc (at *start_angle*).
            end_id: End point of the arc (at *end_angle*).
            radius_id: Parameter for the radius (should be positive).
            start_angle_id: Parameter for the start angle (radians, CCW from +x).
            end_angle_id: Parameter for the end angle (radians, CCW from +x).

        Returns:
            Arc ID.
        """
        aid = ArcId(
            self._solver.add_arc(
                center_id, start_id, end_id, radius_id, start_angle_id, end_angle_id
            )
        )
        self._entity_types[aid] = "arc"
        return aid

    def add_arc_cse(
        self,
        center_id: PointId,
        start_id: PointId,
        end_id: PointId,
        radius: float,
        start_angle: float,
        end_angle: float,
    ) -> ArcId:
        """Add an arc from points and initial scalar values.

        Like :meth:`add_arc`, but creates the radius and angle
        parameters automatically.  *Center*, *start*, and *end* must
        be existing points (created by :meth:`add_point`).

        "CSE" stands for Center–Start–End.

        **Angle convention:** angles are in radians, measured
        counterclockwise (CCW) from the positive x-axis.  A positive
        sweep (``end_angle > start_angle``) gives a CCW arc; a
        negative sweep gives a CW arc.  See :class:`ArcInfo` for
        details.

        Args:
            center_id: Center point of the arc.
            start_id: Start point of the arc.
            end_id: End point of the arc.
            radius: Initial radius value (should be positive).
            start_angle: Initial start angle (radians, CCW from +x).
            end_angle: Initial end angle (radians, CCW from +x).

        Returns:
            Arc ID.
        """
        r = self.add_param(radius, fixed=False)
        sa = self.add_param(start_angle, fixed=False)
        ea = self.add_param(end_angle, fixed=False)
        return self.add_arc(center_id, start_id, end_id, r, sa, ea)

    def add_arc3p(
        self,
        center: tuple[float, float],
        radius: float,
        start_angle: float,
        end_angle: float,
    ) -> ArcId:
        """Add a fully self-contained arc from center coords and angles.

        Creates center, start, and end points plus radius/angle
        parameters internally.  Start and end point coordinates are
        computed from the parametric equation
        ``center + radius * (cos θ, sin θ)``.

        Useful for quick prototyping when you don't need direct
        access to the individual points or parameters.

        **Angle convention:** angles are in radians, measured
        counterclockwise (CCW) from the positive x-axis.  A positive
        sweep (``end_angle > start_angle``) gives a CCW arc; a
        negative sweep gives a CW arc.  See :class:`ArcInfo` for
        details.

        Args:
            center: ``(x, y)`` of the arc center.
            radius: Arc radius (should be positive).
            start_angle: Start angle in radians (CCW from +x).
            end_angle: End angle in radians (CCW from +x).

        Returns:
            Arc ID.
        """
        cx, cy = center
        c = self.add_point(cx, cy)
        sp = self.add_point(
            cx + radius * math.cos(start_angle), cy + radius * math.sin(start_angle)
        )
        ep = self.add_point(cx + radius * math.cos(end_angle), cy + radius * math.sin(end_angle))
        return self.add_arc_cse(c, sp, ep, radius, start_angle, end_angle)

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

    def add_ellipse(self, center_id: PointId, focus1_id: PointId, radmin: float) -> EllipseId:
        """Add an ellipse. Returns ellipse ID."""
        eid = EllipseId(self._solver.add_ellipse(center_id, focus1_id, radmin))
        self._entity_types[eid] = "ellipse"
        return eid

    def get_ellipse(self, ellipse_id: EllipseId) -> EllipseInfo:
        """Get all properties of an ellipse.

        Returns an :class:`EllipseInfo` dataclass with ``center``,
        ``focus1``, and ``radmin`` fields.
        """
        return EllipseInfo(
            center=self._solver.get_ellipse_center(ellipse_id),
            focus1=self._solver.get_ellipse_focus1(ellipse_id),
            radmin=self._solver.get_ellipse_radmin(ellipse_id),
        )

    # ── Geometry: ArcOfEllipse ──────────────────────────────────────

    def add_arc_of_ellipse(
        self,
        center_id: PointId,
        focus1_id: PointId,
        radmin: float,
        start_angle: float,
        end_angle: float,
        start_id: PointId,
        end_id: PointId,
    ) -> ArcOfEllipseId:
        """Add an arc of ellipse.

        The arc is defined by an ellipse (center, focus, semi-minor radius)
        and angular parameters.  Start/end points must be provided and
        are constrained to the ellipse parametric curve via arc-of-ellipse
        rules (added automatically).

        Args:
            center_id: Ellipse center point.
            focus1_id: First focus point.
            radmin: Semi-minor axis radius.
            start_angle: Start angle in radians.
            end_angle: End angle in radians.
            start_id: Start point of the arc.
            end_id: End point of the arc.

        Returns:
            ArcOfEllipseId.
        """
        aoe_id = ArcOfEllipseId(
            self._solver.add_arc_of_ellipse(
                center_id, focus1_id, radmin, start_angle, end_angle, start_id, end_id
            )
        )
        self._entity_types[aoe_id] = "arc_of_ellipse"
        # Add arc-of-ellipse rules to tie start/end to parametric equation
        self._solver.arc_of_ellipse_rules(aoe_id)
        return aoe_id

    def get_arc_of_ellipse(self, aoe_id: ArcOfEllipseId) -> ArcOfEllipseInfo:
        """Get all properties of an arc of ellipse."""
        return ArcOfEllipseInfo(
            center=self._solver.get_arc_of_ellipse_center(aoe_id),
            focus1=self._solver.get_arc_of_ellipse_focus1(aoe_id),
            radmin=self._solver.get_arc_of_ellipse_radmin(aoe_id),
            start_angle=self._solver.get_arc_of_ellipse_start_angle(aoe_id),
            end_angle=self._solver.get_arc_of_ellipse_end_angle(aoe_id),
            start=self._solver.get_arc_of_ellipse_start_point(aoe_id),
            end=self._solver.get_arc_of_ellipse_end_point(aoe_id),
        )

    # ── Geometry: Hyperbola ────────────────────────────────────────

    def add_hyperbola(self, center_id: PointId, focus1_id: PointId, radmin: float) -> HyperbolaId:
        """Add a hyperbola.

        Defined by center, first focus, and semi-minor axis radius.
        The major radius is derived: ``radmaj = sqrt(dist(center, focus1)² - radmin²)``.
        """
        hid = HyperbolaId(self._solver.add_hyperbola(center_id, focus1_id, radmin))
        self._entity_types[hid] = "hyperbola"
        return hid

    def get_hyperbola(self, hyperbola_id: HyperbolaId) -> HyperbolaInfo:
        """Get all properties of a hyperbola."""
        return HyperbolaInfo(
            center=self._solver.get_hyperbola_center(hyperbola_id),
            focus1=self._solver.get_hyperbola_focus1(hyperbola_id),
            radmin=self._solver.get_hyperbola_radmin(hyperbola_id),
        )

    # ── Geometry: ArcOfHyperbola ──────────────────────────────────

    def add_arc_of_hyperbola(
        self,
        center_id: PointId,
        focus1_id: PointId,
        radmin: float,
        start_angle: float,
        end_angle: float,
        start_id: PointId,
        end_id: PointId,
    ) -> ArcOfHyperbolaId:
        """Add an arc of hyperbola.

        Start/end points are constrained to the hyperbola parametric
        curve via arc-of-hyperbola rules (added automatically).
        """
        ahid = ArcOfHyperbolaId(
            self._solver.add_arc_of_hyperbola(
                center_id, focus1_id, radmin, start_angle, end_angle, start_id, end_id
            )
        )
        self._entity_types[ahid] = "arc_of_hyperbola"
        self._solver.arc_of_hyperbola_rules(ahid)
        return ahid

    def get_arc_of_hyperbola(self, ahid: ArcOfHyperbolaId) -> ArcOfHyperbolaInfo:
        """Get all properties of an arc of hyperbola."""
        return ArcOfHyperbolaInfo(
            center=self._solver.get_arc_of_hyperbola_center(ahid),
            focus1=self._solver.get_arc_of_hyperbola_focus1(ahid),
            radmin=self._solver.get_arc_of_hyperbola_radmin(ahid),
            start_angle=self._solver.get_arc_of_hyperbola_start_angle(ahid),
            end_angle=self._solver.get_arc_of_hyperbola_end_angle(ahid),
            start=self._solver.get_arc_of_hyperbola_start_point(ahid),
            end=self._solver.get_arc_of_hyperbola_end_point(ahid),
        )

    # ── Geometry: Parabola ────────────────────────────────────────

    def add_parabola(self, vertex_id: PointId, focus1_id: PointId) -> ParabolaId:
        """Add a parabola.

        Defined by vertex and focus.  The focal length is ``dist(vertex, focus)``.
        """
        pid = ParabolaId(self._solver.add_parabola(vertex_id, focus1_id))
        self._entity_types[pid] = "parabola"
        return pid

    def get_parabola(self, parabola_id: ParabolaId) -> ParabolaInfo:
        """Get all properties of a parabola."""
        return ParabolaInfo(
            vertex=self._solver.get_parabola_vertex(parabola_id),
            focus1=self._solver.get_parabola_focus1(parabola_id),
        )

    # ── Geometry: ArcOfParabola ───────────────────────────────────

    def add_arc_of_parabola(
        self,
        vertex_id: PointId,
        focus1_id: PointId,
        start_angle: float,
        end_angle: float,
        start_id: PointId,
        end_id: PointId,
    ) -> ArcOfParabolaId:
        """Add an arc of parabola.

        Start/end points are constrained to the parabola parametric
        curve via arc-of-parabola rules (added automatically).
        """
        apid = ArcOfParabolaId(
            self._solver.add_arc_of_parabola(
                vertex_id, focus1_id, start_angle, end_angle, start_id, end_id
            )
        )
        self._entity_types[apid] = "arc_of_parabola"
        self._solver.arc_of_parabola_rules(apid)
        return apid

    def get_arc_of_parabola(self, apid: ArcOfParabolaId) -> ArcOfParabolaInfo:
        """Get all properties of an arc of parabola."""
        return ArcOfParabolaInfo(
            vertex=self._solver.get_arc_of_parabola_vertex(apid),
            focus1=self._solver.get_arc_of_parabola_focus1(apid),
            start_angle=self._solver.get_arc_of_parabola_start_angle(apid),
            end_angle=self._solver.get_arc_of_parabola_end_angle(apid),
            start=self._solver.get_arc_of_parabola_start_point(apid),
            end=self._solver.get_arc_of_parabola_end_point(apid),
        )

    # ── Geometry: BSpline ─────────────────────────────────────────

    def add_bspline(
        self,
        start_id: PointId,
        end_id: PointId,
        pole_ids: list[PointId],
        weight_ids: list[ParamId],
        knot_ids: list[ParamId],
        mult: list[int],
        degree: int,
        periodic: bool = False,
    ) -> BSplineId:
        """Add a B-spline curve.

        Args:
            start_id: Start point of the spline.
            end_id: End point of the spline.
            pole_ids: Control point IDs (as :class:`PointId`).
            weight_ids: Weight parameter IDs (one per pole).
            knot_ids: Knot parameter IDs.
            mult: Multiplicity vector (one per knot).
            degree: Spline degree.
            periodic: Whether the spline is periodic.

        Returns:
            BSplineId.
        """
        bsid = BSplineId(
            self._solver.add_bspline(
                start_id,
                end_id,
                list(pole_ids),
                list(weight_ids),
                list(knot_ids),
                list(mult),
                degree,
                periodic,
            )
        )
        self._entity_types[bsid] = "bspline"
        self._bspline_data[bsid] = _BSplineData(
            pole_ids=list(pole_ids),
            weight_ids=list(weight_ids),
            knot_ids=list(knot_ids),
            mult=list(mult),
            degree=degree,
        )
        return bsid

    def get_bspline(self, bspline_id: BSplineId) -> BSplineInfo:
        """Get all properties of a B-spline."""
        data = self._bspline_data[bspline_id]
        return BSplineInfo(
            start=self._solver.get_bspline_start_point(bspline_id),
            end=self._solver.get_bspline_end_point(bspline_id),
            poles=[self._solver.get_point(pid) for pid in data.pole_ids],
            weights=[self._solver.get_param(wid) for wid in data.weight_ids],
            knots=[self._solver.get_param(kid) for kid in data.knot_ids],
            multiplicities=list(data.mult),
            degree=data.degree,
        )

    # ── Constraints ────────────────────────────────────────────────

    def _mark_driven(self, param_id: ParamId, driving: bool) -> None:
        """Mark a constraint-value param as driven when the constraint is non-driving.

        When a constraint is non-driving (``driving=False``), its value
        parameter is an output that the solver should compute, not an
        input that reduces degrees of freedom.  Marking it as *driven*
        excludes it from the DOF calculation in :meth:`diagnose`.
        """
        if not driving:
            self._solver.set_param_driven(param_id, True)

    def coincident(
        self, pt1_id: PointId, pt2_id: PointId, *, driving: bool = True
    ) -> ConstraintTag:
        """Make two points coincident. Returns constraint tag."""
        return ConstraintTag(self._solver.coincident(pt1_id, pt2_id, driving))

    def coordinate_x(
        self, pt_id: PointId, x_id: ParamId, *, driving: bool = True
    ) -> ConstraintTag:
        """Fix the X coordinate of a point to a parameter value."""
        self._mark_driven(x_id, driving)
        return ConstraintTag(self._solver.coordinate_x(pt_id, x_id, driving))

    def coordinate_y(
        self, pt_id: PointId, y_id: ParamId, *, driving: bool = True
    ) -> ConstraintTag:
        """Fix the Y coordinate of a point to a parameter value."""
        self._mark_driven(y_id, driving)
        return ConstraintTag(self._solver.coordinate_y(pt_id, y_id, driving))

    def fix_point(
        self, pt_id: PointId, x: float, y: float, *, driving: bool = True
    ) -> tuple[ConstraintTag, ConstraintTag]:
        """Fix a point to (x, y). Returns (tag_x, tag_y).

        Convenience method that creates parameters internally and calls
        :meth:`coordinate_x` and :meth:`coordinate_y`.
        """
        px = self.add_param(x, fixed=True)
        py = self.add_param(y, fixed=True)
        return self.coordinate_x(pt_id, px, driving=driving), self.coordinate_y(
            pt_id, py, driving=driving
        )

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
        self._mark_driven(distance_id, driving)
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

    def p2p_angle(
        self,
        pt1_id: PointId,
        pt2_id: PointId,
        angle_id: ParamId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain the angle of the line from pt1 to pt2.

        For a simpler API that takes a float directly, see :meth:`set_p2p_angle`.
        """
        self._mark_driven(angle_id, driving)
        return ConstraintTag(self._solver.p2p_angle(pt1_id, pt2_id, angle_id, driving))

    def set_p2p_angle(
        self,
        pt1_id: PointId,
        pt2_id: PointId,
        angle: float,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain the angle of the line from pt1 to pt2 to a value (radians).

        Convenience method that creates the parameter internally.
        To use an explicit parameter, use :meth:`p2p_angle` with :meth:`add_param`.
        """
        a = self.add_param(angle, fixed=True)
        return self.p2p_angle(pt1_id, pt2_id, a, driving=driving)

    def p2l_distance(
        self, pt_id: PointId, line_id: LineId, distance_id: ParamId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain point-to-line distance using a parameter.

        For a simpler API that takes a float directly, see :meth:`set_p2l_distance`.
        """
        self._mark_driven(distance_id, driving)
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

    def point_on_perp_bisector(
        self, pt_id: PointId, line_id: LineId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain point to lie on the perpendicular bisector of a line."""
        return ConstraintTag(self._solver.point_on_perp_bisector(pt_id, line_id, driving))

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

    def equal_radius_cc(
        self, c1_id: CircleId, c2_id: CircleId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain two circles to have equal radius."""
        return ConstraintTag(self._solver.equal_radius_cc(c1_id, c2_id, driving))

    def equal_radius_ca(
        self, circle_id: CircleId, arc_id: ArcId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain a circle and an arc to have equal radius."""
        return ConstraintTag(self._solver.equal_radius_ca(circle_id, arc_id, driving))

    def equal_radius_aa(
        self, a1_id: ArcId, a2_id: ArcId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain two arcs to have equal radius."""
        return ConstraintTag(self._solver.equal_radius_aa(a1_id, a2_id, driving))

    def equal_radii_ee(
        self, e1_id: EllipseId, e2_id: EllipseId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain two ellipses to have equal major radii."""
        return ConstraintTag(self._solver.equal_radii_ee(e1_id, e2_id, driving))

    def equal_radii_hh(
        self, h1_id: ArcOfHyperbolaId, h2_id: ArcOfHyperbolaId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain two arcs of hyperbola to have equal major radii."""
        return ConstraintTag(self._solver.equal_radii_hh(h1_id, h2_id, driving))

    def equal_focus_pp(
        self, p1_id: ArcOfParabolaId, p2_id: ArcOfParabolaId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain two arcs of parabola to have equal focal distance."""
        return ConstraintTag(self._solver.equal_focus_pp(p1_id, p2_id, driving))

    def l2l_angle(
        self, l1_id: LineId, l2_id: LineId, angle_id: ParamId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain angle between two lines using a parameter.

        For a simpler API that takes a float directly, see :meth:`set_l2l_angle`.
        """
        self._mark_driven(angle_id, driving)
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

    def point_on_arc(
        self, pt_id: PointId, arc_id: ArcId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain point to lie on arc."""
        return ConstraintTag(self._solver.point_on_arc(pt_id, arc_id, driving))

    def point_on_ellipse(
        self, pt_id: PointId, ellipse_id: EllipseId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain point to lie on ellipse."""
        return ConstraintTag(self._solver.point_on_ellipse(pt_id, ellipse_id, driving))

    def point_on_hyperbolic_arc(
        self, pt_id: PointId, arc_id: ArcOfHyperbolaId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain point to lie on an arc of hyperbola."""
        return ConstraintTag(self._solver.point_on_hyperbolic_arc(pt_id, arc_id, driving))

    def point_on_parabolic_arc(
        self, pt_id: PointId, arc_id: ArcOfParabolaId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain point to lie on an arc of parabola."""
        return ConstraintTag(self._solver.point_on_parabolic_arc(pt_id, arc_id, driving))

    def point_on_bspline(
        self, pt_id: PointId, bspline_id: BSplineId, u_id: ParamId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain point to lie on a B-spline at parameter *u*."""
        return ConstraintTag(self._solver.point_on_bspline(pt_id, bspline_id, u_id, driving))

    def circle_radius(
        self, circle_id: CircleId, radius_id: ParamId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain circle radius using a parameter.

        For a simpler API that takes a float directly, see :meth:`set_circle_radius`.
        """
        self._mark_driven(radius_id, driving)
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

    def circle_diameter(
        self, circle_id: CircleId, diameter_id: ParamId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain circle diameter using a parameter.

        For a simpler API that takes a float directly, see :meth:`set_circle_diameter`.
        """
        self._mark_driven(diameter_id, driving)
        return ConstraintTag(self._solver.circle_diameter(circle_id, diameter_id, driving))

    def set_circle_diameter(
        self, circle_id: CircleId, diameter: float, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain circle diameter to a value.

        Convenience method that creates the parameter internally.
        """
        d = self.add_param(diameter, fixed=True)
        return self.circle_diameter(circle_id, d, driving=driving)

    def arc_radius(
        self, arc_id: ArcId, radius_id: ParamId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain arc radius using a parameter.

        For a simpler API that takes a float directly, see :meth:`set_arc_radius`.
        """
        self._mark_driven(radius_id, driving)
        return ConstraintTag(self._solver.arc_radius(arc_id, radius_id, driving))

    def set_arc_radius(
        self, arc_id: ArcId, radius: float, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain arc radius to a value.

        Convenience method that creates the parameter internally.
        """
        r = self.add_param(radius, fixed=True)
        return self.arc_radius(arc_id, r, driving=driving)

    def arc_diameter(
        self, arc_id: ArcId, diameter_id: ParamId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain arc diameter using a parameter.

        For a simpler API that takes a float directly, see :meth:`set_arc_diameter`.
        """
        self._mark_driven(diameter_id, driving)
        return ConstraintTag(self._solver.arc_diameter(arc_id, diameter_id, driving))

    def set_arc_diameter(
        self, arc_id: ArcId, diameter: float, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain arc diameter to a value.

        Convenience method that creates the parameter internally.
        """
        d = self.add_param(diameter, fixed=True)
        return self.arc_diameter(arc_id, d, driving=driving)

    def arc_angle(
        self, arc_id: ArcId, angle_id: ParamId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain the angular sweep of an arc using a parameter.

        The sweep is ``end_angle - start_angle``: positive for CCW arcs,
        negative for CW arcs.  Internally this uses an L2LAngle
        (line-to-line angle) constraint on the two radii of the arc,
        the same approach FreeCAD's Sketcher uses.

        For a simpler API that takes a float directly, see :meth:`set_arc_angle`.
        """
        self._mark_driven(angle_id, driving)
        return ConstraintTag(self._solver.arc_angle(arc_id, angle_id, driving))

    def set_arc_angle(self, arc_id: ArcId, angle: float, *, driving: bool = True) -> ConstraintTag:
        """Constrain the angular sweep of an arc to a value (in radians).

        Positive values constrain a CCW sweep, negative values a CW sweep.

        Convenience method that creates the parameter internally.
        To use an explicit parameter (e.g. to read back the solved value
        or share it between constraints), use :meth:`arc_angle` with
        :meth:`add_param`.
        """
        a = self.add_param(angle, fixed=True)
        return self.arc_angle(arc_id, a, driving=driving)

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

    def tangent_line_ellipse(
        self, line_id: LineId, ellipse_id: EllipseId, *, driving: bool = True
    ) -> ConstraintTag:
        """Line tangent to ellipse."""
        return ConstraintTag(self._solver.tangent_line_ellipse(line_id, ellipse_id, driving))

    def tangent_arc_arc(
        self, a1_id: ArcId, a2_id: ArcId, *, driving: bool = True
    ) -> ConstraintTag:
        """Arc tangent to arc."""
        return ConstraintTag(self._solver.tangent_arc_arc(a1_id, a2_id, driving))

    def tangent_circle_arc(
        self, circle_id: CircleId, arc_id: ArcId, *, driving: bool = True
    ) -> ConstraintTag:
        """Circle tangent to arc."""
        return ConstraintTag(self._solver.tangent_circle_arc(circle_id, arc_id, driving))

    def tangent_circumf(
        self,
        p1_id: PointId,
        p2_id: PointId,
        rd1_id: ParamId,
        rd2_id: ParamId,
        *,
        internal: bool = False,
        driving: bool = True,
    ) -> ConstraintTag:
        """Tangent circumference constraint."""
        return ConstraintTag(
            self._solver.tangent_circumf(p1_id, p2_id, rd1_id, rd2_id, internal, driving)
        )

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

    def p2c_distance(
        self,
        pt_id: PointId,
        circle_id: CircleId,
        distance_id: ParamId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain point-to-circle distance using a parameter.

        For a simpler API that takes a float directly, see :meth:`set_p2c_distance`.
        """
        self._mark_driven(distance_id, driving)
        return ConstraintTag(self._solver.p2c_distance(pt_id, circle_id, distance_id, driving))

    def set_p2c_distance(
        self,
        pt_id: PointId,
        circle_id: CircleId,
        distance: float,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain point-to-circle distance to a value.

        Convenience method that creates the parameter internally.
        """
        d = self.add_param(distance, fixed=True)
        return self.p2c_distance(pt_id, circle_id, d, driving=driving)

    def c2c_distance(
        self,
        c1_id: CircleId,
        c2_id: CircleId,
        dist_id: ParamId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain circle-to-circle distance using a parameter.

        For a simpler API that takes a float directly, see :meth:`set_c2c_distance`.
        """
        self._mark_driven(dist_id, driving)
        return ConstraintTag(self._solver.c2c_distance(c1_id, c2_id, dist_id, driving))

    def set_c2c_distance(
        self,
        c1_id: CircleId,
        c2_id: CircleId,
        distance: float,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain circle-to-circle distance to a value.

        Convenience method that creates the parameter internally.
        """
        d = self.add_param(distance, fixed=True)
        return self.c2c_distance(c1_id, c2_id, d, driving=driving)

    def c2l_distance(
        self,
        circle_id: CircleId,
        line_id: LineId,
        dist_id: ParamId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain circle-to-line distance using a parameter.

        For a simpler API that takes a float directly, see :meth:`set_c2l_distance`.
        """
        self._mark_driven(dist_id, driving)
        return ConstraintTag(self._solver.c2l_distance(circle_id, line_id, dist_id, driving))

    def set_c2l_distance(
        self,
        circle_id: CircleId,
        line_id: LineId,
        distance: float,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain circle-to-line distance to a value.

        Convenience method that creates the parameter internally.
        """
        d = self.add_param(distance, fixed=True)
        return self.c2l_distance(circle_id, line_id, d, driving=driving)

    def p2a_distance(
        self,
        pt_id: PointId,
        arc_id: ArcId,
        distance_id: ParamId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain point-to-arc distance using a parameter.

        This measures the shortest distance from the point to the arc's
        underlying circle (center and radius).  It is the arc analogue of
        :meth:`p2c_distance`.

        For a simpler API that takes a float directly, see
        :meth:`set_p2a_distance`.
        """
        self._mark_driven(distance_id, driving)
        return ConstraintTag(self._solver.p2a_distance(pt_id, arc_id, distance_id, driving))

    def set_p2a_distance(
        self,
        pt_id: PointId,
        arc_id: ArcId,
        distance: float,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain point-to-arc distance to a value.

        Convenience method that creates the parameter internally.
        """
        d = self.add_param(distance, fixed=True)
        return self.p2a_distance(pt_id, arc_id, d, driving=driving)

    def a2l_distance(
        self,
        arc_id: ArcId,
        line_id: LineId,
        dist_id: ParamId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain arc-to-line distance using a parameter.

        This measures the distance between the arc's underlying circle
        and the line.  It is the arc analogue of :meth:`c2l_distance`.

        For a simpler API that takes a float directly, see
        :meth:`set_a2l_distance`.
        """
        self._mark_driven(dist_id, driving)
        return ConstraintTag(self._solver.a2l_distance(arc_id, line_id, dist_id, driving))

    def set_a2l_distance(
        self,
        arc_id: ArcId,
        line_id: LineId,
        distance: float,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain arc-to-line distance to a value.

        Convenience method that creates the parameter internally.
        """
        d = self.add_param(distance, fixed=True)
        return self.a2l_distance(arc_id, line_id, d, driving=driving)

    def c2a_distance(
        self,
        circle_id: CircleId,
        arc_id: ArcId,
        dist_id: ParamId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain circle-to-arc distance using a parameter.

        Measures the distance between the outer edges of the circle and
        the arc's underlying circle.  It is the arc analogue of
        :meth:`c2c_distance`.

        For a simpler API that takes a float directly, see
        :meth:`set_c2a_distance`.
        """
        self._mark_driven(dist_id, driving)
        return ConstraintTag(self._solver.c2a_distance(circle_id, arc_id, dist_id, driving))

    def set_c2a_distance(
        self,
        circle_id: CircleId,
        arc_id: ArcId,
        distance: float,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain circle-to-arc distance to a value.

        Convenience method that creates the parameter internally.
        """
        d = self.add_param(distance, fixed=True)
        return self.c2a_distance(circle_id, arc_id, d, driving=driving)

    def a2a_distance(
        self,
        a1_id: ArcId,
        a2_id: ArcId,
        dist_id: ParamId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain arc-to-arc distance using a parameter.

        Measures the distance between the outer edges of the two arcs'
        underlying circles.  It is the arc analogue of
        :meth:`c2c_distance`.

        For a simpler API that takes a float directly, see
        :meth:`set_a2a_distance`.
        """
        self._mark_driven(dist_id, driving)
        return ConstraintTag(self._solver.a2a_distance(a1_id, a2_id, dist_id, driving))

    def set_a2a_distance(
        self,
        a1_id: ArcId,
        a2_id: ArcId,
        distance: float,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain arc-to-arc distance to a value.

        Convenience method that creates the parameter internally.
        """
        d = self.add_param(distance, fixed=True)
        return self.a2a_distance(a1_id, a2_id, d, driving=driving)

    def arc_length(
        self, arc_id: ArcId, length_id: ParamId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain arc length using a parameter.

        For a simpler API that takes a float directly, see :meth:`set_arc_length`.
        """
        self._mark_driven(length_id, driving)
        return ConstraintTag(self._solver.arc_length(arc_id, length_id, driving))

    def set_arc_length(
        self, arc_id: ArcId, length: float, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain arc length to a value.

        Convenience method that creates the parameter internally.
        """
        p = self.add_param(length, fixed=True)
        return self.arc_length(arc_id, p, driving=driving)

    def arc_rules(self, arc_id: ArcId, *, driving: bool = True) -> ConstraintTag:
        """Add arc rules (start/end points tied to center, radius, angles).

        Arc rules constrain the start and end points to satisfy::

            start = center + radius * (cos(start_angle), sin(start_angle))
            end   = center + radius * (cos(end_angle),   sin(end_angle))

        These are added automatically by :meth:`add_arc`, so you normally
        do not need to call this directly.
        """
        return ConstraintTag(self._solver.arc_rules(arc_id, driving))

    def proportional(
        self,
        param1_id: ParamId,
        param2_id: ParamId,
        ratio: float,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain param1 = ratio * param2."""
        return ConstraintTag(self._solver.proportional(param1_id, param2_id, ratio, driving))

    def difference(
        self,
        param1_id: ParamId,
        param2_id: ParamId,
        diff_id: ParamId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain param2 - param1 = diff.

        All three arguments are parameter IDs (from :meth:`add_param`).
        Use :meth:`get_point_param_ids` to obtain the x/y parameter
        IDs for a point.
        """
        self._mark_driven(diff_id, driving)
        return ConstraintTag(self._solver.difference(param1_id, param2_id, diff_id, driving))

    def internal_alignment_point2ellipse(
        self,
        ellipse_id: EllipseId,
        pt_id: PointId,
        alignment_type: InternalAlignmentType,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Internal alignment: constrain a point relative to an ellipse.

        The *alignment_type* specifies which feature of the ellipse the
        point is aligned to (e.g. major axis endpoint, focus, etc.).
        """
        return ConstraintTag(
            self._solver.internal_alignment_point2ellipse(
                ellipse_id, pt_id, alignment_type, driving
            )
        )

    def internal_alignment_ellipse_major_diameter(
        self,
        ellipse_id: EllipseId,
        p1_id: PointId,
        p2_id: PointId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Internal alignment: tie line endpoints to ellipse major diameter."""
        return ConstraintTag(
            self._solver.internal_alignment_ellipse_major_diameter(
                ellipse_id, p1_id, p2_id, driving
            )
        )

    def internal_alignment_ellipse_minor_diameter(
        self,
        ellipse_id: EllipseId,
        p1_id: PointId,
        p2_id: PointId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Internal alignment: tie line endpoints to ellipse minor diameter."""
        return ConstraintTag(
            self._solver.internal_alignment_ellipse_minor_diameter(
                ellipse_id, p1_id, p2_id, driving
            )
        )

    def internal_alignment_ellipse_focus1(
        self,
        ellipse_id: EllipseId,
        pt_id: PointId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Internal alignment: constrain point to ellipse focus 1."""
        return ConstraintTag(
            self._solver.internal_alignment_ellipse_focus1(ellipse_id, pt_id, driving)
        )

    def internal_alignment_ellipse_focus2(
        self,
        ellipse_id: EllipseId,
        pt_id: PointId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Internal alignment: constrain point to ellipse focus 2."""
        return ConstraintTag(
            self._solver.internal_alignment_ellipse_focus2(ellipse_id, pt_id, driving)
        )

    def internal_alignment_point2hyperbola(
        self,
        hyperbola_id: HyperbolaId,
        pt_id: PointId,
        alignment_type: InternalAlignmentType,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Internal alignment: constrain a point relative to a hyperbola."""
        return ConstraintTag(
            self._solver.internal_alignment_point2hyperbola(
                hyperbola_id, pt_id, alignment_type, driving
            )
        )

    def internal_alignment_hyperbola_major_diameter(
        self,
        hyperbola_id: HyperbolaId,
        p1_id: PointId,
        p2_id: PointId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Internal alignment: tie line endpoints to hyperbola major diameter."""
        return ConstraintTag(
            self._solver.internal_alignment_hyperbola_major_diameter(
                hyperbola_id, p1_id, p2_id, driving
            )
        )

    def internal_alignment_hyperbola_minor_diameter(
        self,
        hyperbola_id: HyperbolaId,
        p1_id: PointId,
        p2_id: PointId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Internal alignment: tie line endpoints to hyperbola minor diameter."""
        return ConstraintTag(
            self._solver.internal_alignment_hyperbola_minor_diameter(
                hyperbola_id, p1_id, p2_id, driving
            )
        )

    def internal_alignment_hyperbola_focus(
        self,
        hyperbola_id: HyperbolaId,
        pt_id: PointId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Internal alignment: constrain point to hyperbola focus."""
        return ConstraintTag(
            self._solver.internal_alignment_hyperbola_focus(hyperbola_id, pt_id, driving)
        )

    def internal_alignment_parabola_focus(
        self,
        parabola_id: ParabolaId,
        pt_id: PointId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Internal alignment: constrain point to parabola focus."""
        return ConstraintTag(
            self._solver.internal_alignment_parabola_focus(parabola_id, pt_id, driving)
        )

    def internal_alignment_bspline_control_point(
        self,
        bspline_id: BSplineId,
        circle_id: CircleId,
        pole_index: int,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Internal alignment: B-spline control point.

        Ties a circle (center = pole, radius = weight) to a control point.
        """
        return ConstraintTag(
            self._solver.internal_alignment_bspline_control_point(
                bspline_id, circle_id, pole_index, driving
            )
        )

    def internal_alignment_knot_point(
        self,
        bspline_id: BSplineId,
        pt_id: PointId,
        knot_index: int,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Internal alignment: constrain point to B-spline knot."""
        return ConstraintTag(
            self._solver.internal_alignment_knot_point(bspline_id, pt_id, knot_index, driving)
        )

    def tangent_at_bspline_knot(
        self,
        bspline_id: BSplineId,
        line_id: LineId,
        knot_index: int,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain a line to be tangent to a B-spline at a knot."""
        return ConstraintTag(
            self._solver.tangent_at_bspline_knot(bspline_id, line_id, knot_index, driving)
        )

    def midpoint_on_line(
        self, l1_id: LineId, l2_id: LineId, *, driving: bool = True
    ) -> ConstraintTag:
        """Constrain midpoint of l1 to lie on l2."""
        return ConstraintTag(self._solver.midpoint_on_line(l1_id, l2_id, driving))

    # ── Angle-via-point constraints ────────────────────────────────

    def angle_via_point(
        self,
        crv1_id: CurveId,
        crv2_id: CurveId,
        pt_id: PointId,
        angle_id: ParamId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain angle between two curves at a shared point.

        The angle is measured between the tangent directions of the two
        curves at the given point. This is the general-purpose angle
        constraint used by FreeCAD's Sketcher for curve–curve angles.

        Args:
            crv1_id: First curve (any geometry ID: line, circle, arc, ellipse, …).
            crv2_id: Second curve.
            pt_id: Point where the curves meet.
            angle_id: Parameter ID for the angle value (radians).
            driving: Whether this is a driving constraint.

        Returns:
            Constraint tag.
        """
        self._mark_driven(angle_id, driving)
        return ConstraintTag(
            self._solver.angle_via_point(crv1_id, crv2_id, pt_id, angle_id, driving)
        )

    def set_angle_via_point(
        self,
        crv1_id: CurveId,
        crv2_id: CurveId,
        pt_id: PointId,
        angle: float,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain angle between two curves at a point to a value (radians).

        Convenience method that creates the angle parameter internally.
        """
        a = self.add_param(angle, fixed=True)
        return self.angle_via_point(crv1_id, crv2_id, pt_id, a, driving=driving)

    def angle_via_two_points(
        self,
        crv1_id: CurveId,
        crv2_id: CurveId,
        pt1_id: PointId,
        pt2_id: PointId,
        angle_id: ParamId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain angle between two curves via two points.

        Used when each curve passes through a different point.

        Args:
            crv1_id: First curve.
            crv2_id: Second curve.
            pt1_id: Point on the first curve.
            pt2_id: Point on the second curve.
            angle_id: Parameter ID for the angle value (radians).
            driving: Whether this is a driving constraint.

        Returns:
            Constraint tag.
        """
        self._mark_driven(angle_id, driving)
        return ConstraintTag(
            self._solver.angle_via_two_points(crv1_id, crv2_id, pt1_id, pt2_id, angle_id, driving)
        )

    def set_angle_via_two_points(
        self,
        crv1_id: CurveId,
        crv2_id: CurveId,
        pt1_id: PointId,
        pt2_id: PointId,
        angle: float,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain angle between two curves via two points to a value (radians).

        Convenience method that creates the angle parameter internally.
        """
        a = self.add_param(angle, fixed=True)
        return self.angle_via_two_points(crv1_id, crv2_id, pt1_id, pt2_id, a, driving=driving)

    def angle_via_point_and_param(
        self,
        crv1_id: CurveId,
        crv2_id: CurveId,
        pt_id: PointId,
        cparam_id: ParamId,
        angle_id: ParamId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain angle between two curves at a point with a curve parameter.

        Args:
            crv1_id: First curve.
            crv2_id: Second curve.
            pt_id: Point where the curves meet.
            cparam_id: Curve parameter for the second curve.
            angle_id: Parameter ID for the angle value (radians).
            driving: Whether this is a driving constraint.

        Returns:
            Constraint tag.
        """
        self._mark_driven(angle_id, driving)
        return ConstraintTag(
            self._solver.angle_via_point_and_param(
                crv1_id, crv2_id, pt_id, cparam_id, angle_id, driving
            )
        )

    def angle_via_point_and_two_params(
        self,
        crv1_id: CurveId,
        crv2_id: CurveId,
        pt_id: PointId,
        cparam1_id: ParamId,
        cparam2_id: ParamId,
        angle_id: ParamId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain angle between two curves at a point with two curve parameters.

        Args:
            crv1_id: First curve.
            crv2_id: Second curve.
            pt_id: Point where the curves meet.
            cparam1_id: Curve parameter for the first curve.
            cparam2_id: Curve parameter for the second curve.
            angle_id: Parameter ID for the angle value (radians).
            driving: Whether this is a driving constraint.

        Returns:
            Constraint tag.
        """
        self._mark_driven(angle_id, driving)
        return ConstraintTag(
            self._solver.angle_via_point_and_two_params(
                crv1_id, crv2_id, pt_id, cparam1_id, cparam2_id, angle_id, driving
            )
        )

    def curve_value(
        self,
        pt_id: PointId,
        curve_id: CurveId,
        u_id: ParamId,
        *,
        driving: bool = True,
    ) -> ConstraintTag:
        """Constrain a point to lie on a curve at parameter *u*.

        Args:
            pt_id: Point to constrain.
            curve_id: Curve the point must lie on.
            u_id: Parameter ID for the curve parameter *u*.
            driving: Whether this is a driving constraint.

        Returns:
            Constraint tag.
        """
        return ConstraintTag(self._solver.curve_value(pt_id, curve_id, u_id, driving))

    def snells_law(
        self,
        ray1_id: CurveId,
        ray2_id: CurveId,
        boundary_id: CurveId,
        pt_id: PointId,
        n1_id: ParamId,
        n2_id: ParamId,
        *,
        flipn1: bool = False,
        flipn2: bool = False,
        driving: bool = True,
    ) -> ConstraintTag:
        """Add Snell's law refraction constraint.

        Constrains the angles of *ray1* and *ray2* relative to the
        *boundary* curve at point *pt* to satisfy Snell's law with
        refractive indices *n1* and *n2*.

        Args:
            ray1_id: Incoming ray curve.
            ray2_id: Outgoing ray curve.
            boundary_id: Boundary curve.
            pt_id: Refraction point.
            n1_id: Parameter for refractive index of first medium.
            n2_id: Parameter for refractive index of second medium.
            flipn1: Flip normal direction for ray1.
            flipn2: Flip normal direction for ray2.
            driving: Whether this is a driving constraint.

        Returns:
            Constraint tag.
        """
        return ConstraintTag(
            self._solver.snells_law(
                ray1_id,
                ray2_id,
                boundary_id,
                pt_id,
                n1_id,
                n2_id,
                flipn1,
                flipn2,
                driving,
            )
        )

    def calculate_angle_via_point(
        self,
        crv1_id: CurveId,
        crv2_id: CurveId,
        pt_id: PointId,
    ) -> float:
        """Calculate the current angle between two curves at a point.

        This is a query, not a constraint — it returns the angle
        between the tangent directions without adding any constraint.

        Args:
            crv1_id: First curve.
            crv2_id: Second curve.
            pt_id: Point where the angle is measured.

        Returns:
            Angle in radians.
        """
        return self._solver.calculate_angle_via_point(crv1_id, crv2_id, pt_id)

    def calculate_angle_via_two_points(
        self,
        crv1_id: CurveId,
        crv2_id: CurveId,
        pt1_id: PointId,
        pt2_id: PointId,
    ) -> float:
        """Calculate the current angle between two curves via two points.

        Args:
            crv1_id: First curve.
            crv2_id: Second curve.
            pt1_id: Point on the first curve.
            pt2_id: Point on the second curve.

        Returns:
            Angle in radians.
        """
        return self._solver.calculate_angle_via_two_points(crv1_id, crv2_id, pt1_id, pt2_id)

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
        conflicting_tags = [ConstraintTag(t) for t in r.conflicting]
        redundant_tags = [ConstraintTag(t) for t in r.redundant]
        partially_redundant_tags = [ConstraintTag(t) for t in r.partially_redundant]
        return Diagnosis(
            dof=r.dof,
            conflicting=conflicting_tags,
            redundant=redundant_tags,
            partially_redundant=partially_redundant_tags,
            conflicting_info=[
                self._constraints[t] for t in conflicting_tags if t in self._constraints
            ],
            redundant_info=[
                self._constraints[t] for t in redundant_tags if t in self._constraints
            ],
            partially_redundant_info=[
                self._constraints[t] for t in partially_redundant_tags if t in self._constraints
            ],
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
        self._constraints.clear()
        self._entity_types.clear()

    def clear_by_tag(self, tag: ConstraintTag) -> None:
        """Remove all constraints with the given tag."""
        self._solver.clear_by_tag(tag)
        self._constraints.pop(tag, None)

    def constraint_error(self, tag: ConstraintTag) -> float:
        """Calculate the RMS error of all constraints with the given tag."""
        return self._solver.constraint_error(tag)

    def to_image(
        self,
        *,
        width: int | None = None,
        height: int | None = None,
        scale: float | None = None,
        padding: int = 40,
        background: str = "white",
        line_color: str = "black",
        circle_color: str = "blue",
        arc_color: str = "red",
        ellipse_color: str = "green",
        line_width: int = 2,
        point_radius: int = 3,
        point_color: str = "gray",
    ) -> object:
        """Render the sketch geometry to a Pillow image.

        This is a convenience wrapper around
        :func:`planegcs.graphics.sketch_to_image`.

        Requires the ``graphics`` extra::

            pip install planegcs[graphics]

        All keyword arguments are forwarded to
        :func:`~planegcs.graphics.sketch_to_image`.

        Returns:
            A :class:`PIL.Image.Image` showing the current sketch geometry.
        """
        from planegcs.graphics import sketch_to_image

        return sketch_to_image(
            self,
            width=width,
            height=height,
            scale=scale,
            padding=padding,
            background=background,
            line_color=line_color,
            circle_color=circle_color,
            arc_color=arc_color,
            ellipse_color=ellipse_color,
            line_width=line_width,
            point_radius=point_radius,
            point_color=point_color,
        )


# Slightly hacky method of getting hold of SketchSolver methods that create
# constraints, based on the docstring which includes a full type signature. If
# this fails we could use an explicit list.
SKETCH_SOLVER_CONSTRAINT_METHODS = [
    n
    for n in dir(SketchSolver)
    if not n.startswith("__")
    and callable(m := getattr(SketchSolver, n))
    and isinstance(m.__doc__, str)
    and "driving: bool" in m.__doc__  # All constraint methods have this.
]


class RecordingSketchSolver(SketchSolver):
    """
    SketchSolver subclass that tracks calls to constraint methods and saves them on a Sketch.
    """

    # This exists so that we can populate Sketch._constraints (mostly for debugging
    # purposes).

    # We really just want to proxy some method calls to a wrapped SketchSolver,
    # rather than use inheritance, but to satisfy type checkers without a lot of
    # boilerplate, RecordingSketchSolver inherits from SketchSolver, and then we
    # use introspection to add wrappers that intercept some method calls.

    def __init__(self, sketch: Sketch) -> None:
        super().__init__()
        self._sketch = sketch


def _make_recording_wrapper(solver_method: FunctionType) -> Callable:
    @functools.wraps(solver_method)
    def wrapper(self: RecordingSketchSolver, *args, **kwargs):
        # solver_method is an unbound method here, so requires self to be passed
        # explicitly.
        retval = solver_method(self, *args, **kwargs)
        assert isinstance(retval, int)
        ct = ConstraintTag(retval)
        # `driving` is always the last argument.
        self._sketch._constraints[ct] = ConstraintInfo(
            tag=ct,
            type_name=solver_method.__name__,
            entities=tuple(list(args[0:-1])),
            driving=args[-1],
        )
        return retval

    return wrapper


for attr in SKETCH_SOLVER_CONSTRAINT_METHODS:
    setattr(RecordingSketchSolver, attr, _make_recording_wrapper(getattr(SketchSolver, attr)))
