Examples
========

Equilateral Triangle with Rounded Corners
-----------------------------------------

This example builds an equilateral triangle whose sharp corners are
replaced by circular arcs of a given radius.  It demonstrates:

* :meth:`~planegcs.Sketch.add_arc_from_start_end` — creating arcs from
  endpoint geometry instead of center/angle parameters.
* :meth:`~planegcs.Sketch.tangent_line_arc` — constraining an arc to be
  tangent to a line, ensuring smooth transitions at each corner.
* Combining positional, dimensional, and geometric constraints to fully
  define a shape.

The shape consists of **three straight line segments** (the trimmed edges of
the triangle) and **three circular arcs** (one at each corner).  Each arc is
tangent to its two adjacent line segments.

.. code-block:: python

    import math
    from planegcs import Sketch, SolveStatus

    # ── Parameters ──────────────────────────────────────────────
    side = 10.0          # side length of the underlying triangle
    r = 1.5              # corner arc radius
    h = side * math.sqrt(3) / 2   # triangle height

    # Tangent length from each vertex to the tangent point.
    # For an interior angle of 60°: t = r / tan(30°) = r * √3
    t = r * math.sqrt(3)

    # ── Compute initial guesses ─────────────────────────────────
    # Triangle vertices
    v1, v2, v3 = (0.0, 0.0), (side, 0.0), (side / 2, h)

    # Unit edge directions
    d_r = ((v3[0] - v2[0]) / side, (v3[1] - v2[1]) / side)
    d_l = ((v1[0] - v3[0]) / side, (v1[1] - v3[1]) / side)

    # Tangent points (where arcs meet lines)
    bs = (v1[0] + t, v1[1])                            # bottom start
    be = (v2[0] - t, v2[1])                            # bottom end
    rs = (v2[0] + t * d_r[0], v2[1] + t * d_r[1])     # right start
    re = (v3[0] - t * d_r[0], v3[1] - t * d_r[1])     # right end
    ls = (v3[0] + t * d_l[0], v3[1] + t * d_l[1])     # left start
    le = (v1[0] - t * d_l[0], v1[1] - t * d_l[1])     # left end

    # ── Build the sketch ────────────────────────────────────────
    s = Sketch()

    # Six tangent-point vertices
    p_bs = s.add_point(*bs)
    p_be = s.add_point(*be)
    p_rs = s.add_point(*rs)
    p_re = s.add_point(*re)
    p_ls = s.add_point(*ls)
    p_le = s.add_point(*le)

    # Three straight edges
    line_b = s.add_line(p_bs, p_be)   # bottom
    line_r = s.add_line(p_rs, p_re)   # right
    line_l = s.add_line(p_ls, p_le)   # left

    # Radius parameter – fixed by default, shared by all three arcs
    rad = s.add_param(r)

    # Three corner arcs
    arc_bl  = s.add_arc_from_start_end(p_le, p_bs, rad)   # bottom-left
    arc_br  = s.add_arc_from_start_end(p_be, p_rs, rad)   # bottom-right
    arc_top = s.add_arc_from_start_end(p_re, p_ls, rad)   # top

    # ── Tangency constraints ────────────────────────────────────
    # Each arc must be tangent to its two adjacent lines.
    s.tangent_line_arc(line_b, arc_bl)
    s.tangent_line_arc(line_b, arc_br)
    s.tangent_line_arc(line_r, arc_br)
    s.tangent_line_arc(line_r, arc_top)
    s.tangent_line_arc(line_l, arc_top)
    s.tangent_line_arc(line_l, arc_bl)

    # ── Equilateral constraint ──────────────────────────────────
    s.equal_length(line_b, line_r)
    s.equal_length(line_r, line_l)

    # ── Positioning and sizing ──────────────────────────────────
    s.fix_point(p_bs, *bs)                          # anchor one point
    s.horizontal(line_b)                             # bottom is horizontal
    s.set_p2p_distance(p_bs, p_be, side - 2 * t)    # set edge length

    # ── Solve ───────────────────────────────────────────────────
    status = s.solve()
    assert status == SolveStatus.Success

    # ── Read results ────────────────────────────────────────────
    for name, pid in [("bs", p_bs), ("be", p_be),
                      ("rs", p_rs), ("re", p_re),
                      ("ls", p_ls), ("le", p_le)]:
        x, y = s.get_point(pid)
        print(f"{name}: ({x:.4f}, {y:.4f})")

Running this prints::

    bs: (2.5981, 0.0000)
    be: (7.4019, 0.0000)
    rs: (8.7010, 2.2500)
    re: (6.2990, 6.4103)
    ls: (3.7010, 6.4103)
    le: (1.2990, 2.2500)

.. note::

   **Initial guesses matter.** The constraint solver is iterative. When the
   geometry has multiple valid configurations (e.g., arcs can bulge inward
   or outward), providing good initial point positions steers the solver to
   the intended solution.  In this example the exact tangent-point
   coordinates are computed up front and used as initial guesses.

Key API methods used
~~~~~~~~~~~~~~~~~~~~

:meth:`~planegcs.Sketch.add_arc_from_start_end`
    Creates an arc that passes through two existing points with a given
    radius parameter.  The radius is supplied as a :class:`~planegcs.ParamId`
    created via :meth:`~planegcs.Sketch.add_param`, giving you explicit
    control over whether it is fixed or free.  Internally this computes the
    arc center and angles, adds ``arc_rules`` constraints (so the arc's
    start/end points stay consistent with center + radius + angles), and adds
    ``coincident`` constraints tying the arc endpoints to the supplied points.
    Multiple arcs can share the same radius parameter.

:meth:`~planegcs.Sketch.tangent_line_arc`
    Constrains a line to be tangent to an arc.  Under the hood this is a
    point-to-line distance constraint: the arc's center is kept at
    exactly one radius away from the line.
