
====================
 History/change log
====================

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
