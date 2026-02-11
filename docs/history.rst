
====================
 History/change log
====================

* 0.3 (2026-02-11)

  - **Breaking:** renamed ``add_arc`` to ``add_arc_from_center``;
    ``add_arc_from_start_end`` radius parameter now takes a ``ParamId``
    instead of a ``float``; ``ArcInfo`` changed from ``NamedTuple`` to
    frozen dataclass.
  - Added typed IDs (``PointId``, ``LineId``, etc. via ``NewType``) and
    convenience methods to the ``Sketch`` API.
  - Added ``add_arc_from_start_end`` and ``tangent_line_arc`` constraint.
  - Added arc property getters: ``get_arc``, ``get_arc_center``,
    ``get_arc_radius``, angle and endpoint accessors.
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
