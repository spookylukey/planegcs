
====================
 History/change log
====================

* 0.5 (2026-02-24)

  **Breaking changes:**

  - Replaced ``add_arc_from_center`` / ``add_arc_from_start_end`` with a
    single unified ``add_arc`` method.
  - Changed ``add_circle`` to take ``radius_id: Param`` instead of
    ``radius: float``, for consistency with other entity constructors.
  - Changed ``add_param()`` default to ``fixed=False`` for consistency.

  **New constraints:**

  - ``difference``, ``proportional``, ``p2p_angle``
  - ``point_on_perp_bisector``, ``point_on_arc``, ``point_on_ellipse``
  - ``circle_diameter``, ``arc_radius``, ``arc_diameter``
  - ``equal_radius_cc``, ``equal_radius_ca``, ``equal_radius_aa``
  - ``tangent_line_ellipse``, ``tangent_arc_arc``, ``tangent_circle_arc``,
    ``tangent_circumf``
  - ``p2c_distance``, ``c2c_distance``, ``c2l_distance``
  - ``p2a_distance``, ``a2l_distance``, ``c2a_distance``, ``a2a_distance``
  - ``arc_length``
  - ``internal_alignment_point2ellipse``
  - ``arc_angle`` / ``set_arc_angle`` for constraining arc sweep angles
  - ``*ViaPoint`` family: ``angle_via_point``, ``curve_value``,
    ``snells_law``, etc.
  - ``coordinate_x``, ``coordinate_y``
  - ``clear_by_tag``, ``constraint_error``

  **New features:**

  - Debugging graphics: ``Sketch.to_image()`` renders the sketch to a
    PIL/Pillow image for visual inspection.
  - Entity lookup API: ``ConstraintInfo.get_entities()`` to inspect which
    geometric entities a constraint references.
  - Rich constraint info in diagnosis results (``diagnose()`` now returns
    ``ConstraintInfo`` objects for conflicting/redundant constraints).
  - ``add_point_from_params()`` to build points from existing param IDs.
  - ``get_point_param_ids()`` to retrieve the underlying param IDs of a
    point.
  - ``arc_size`` property on ``ArcInfo`` (``end_angle - start_angle``).
  - Improved ``CurveId`` type checking.
  - Script to regenerate type stubs (``update_stubs.py``).

  **Documentation:**

  - Documented arc direction conventions in docstrings.
  - Added tangent arc-line example.
  - Added graphics/visualization docs.

* 0.4 (2026-02-13)

  - **Breaking:** removed ``get_arc_center()``, ``get_arc_radius()``,
    ``get_arc_start_angle()``, and ``get_arc_end_angle()`` from the public
    ``Sketch`` API—use ``get_arc()`` instead.
  - Replaced ``add_point`` + ``fix_point`` pairs with ``add_fixed_point``
    throughout docs, examples, and tests.
  - Added ``get_circle()`` returning a ``CircleInfo`` dataclass.
  - Added ``get_line()`` returning a ``LineInfo`` dataclass.
  - Added ``get_ellipse()`` returning an ``EllipseInfo`` dataclass.
  - Added ``PointInfo`` type alias for ``tuple[float, float]``.
  - Added 100% Python code coverage enforcement.
  - Added pytest/ty checks to ``release.sh``.

* 0.3 (2026-02-11)

  - **Breaking:** renamed ``add_arc`` to ``add_arc_from_center``;
    ``add_arc_from_start_end`` radius parameter now takes a ``ParamId``
    instead of a ``float``; ``ArcInfo`` changed from ``NamedTuple`` to
    frozen dataclass.
  - Added typed IDs (``PointId``, ``LineId``, etc. via ``NewType``) and
    convenience methods to the ``Sketch`` API.
  - Added ``add_arc_from_start_end`` and ``tangent_line_arc`` constraint.
  - Added ``get_arc`` property getter returning full ``ArcInfo``.
  - Added constraint-system diagnosis: degrees of freedom, conflicting
    and redundant constraint detection.
  - Added ``add_fixed_param`` convenience method.
  - Added type stubs (``.pyi``) for the ``_planegcs`` C extension module
    with automated freshness checking.

* 0.2 (2026-02-11)

  - Added ``add_fixed_point`` convenience method


* 0.1.2 (2026-02-11)

  - more automated tests, reformatting etc.
  - Python 3.14 wheels added

* 0.1.1 (2026-02-09)

  - build some wheels

* 0.1 (2026-02-09)

  - initial release
