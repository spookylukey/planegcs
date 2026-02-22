Quick Start
===========

Basic Usage
-----------

Create a sketch, add geometry and constraints, then solve:

.. code-block:: python

   from planegcs import Sketch, SolveStatus

   s = Sketch()

   # Add three points
   p1 = s.add_fixed_point(0, 0)
   p2 = s.add_point(5, 0)
   p3 = s.add_point(2.5, 4)

   # Connect with lines
   l1 = s.add_line(p1, p2)
   l2 = s.add_line(p2, p3)
   l3 = s.add_line(p3, p1)

   # Constraints: equilateral triangle
   s.equal_length(l1, l2)
   s.equal_length(l2, l3)
   s.horizontal(l1)

   # Fix side length
   s.set_p2p_distance(p1, p2, 5.0)

   # Solve
   status = s.solve()
   assert status == SolveStatus.Success

   # Read results
   print(s.get_point(p1))  # (0.0, 0.0)
   print(s.get_point(p2))  # (5.0, 0.0)
   print(s.get_point(p3))  # (~2.5, ~4.33)

Key Concepts
------------

**IDs**: Every geometry element and parameter is identified by an integer ID
returned by ``add_*`` methods.

**Typed IDs**: Each ``add_*`` method returns a typed ID (``PointId``,
``LineId``, ``ParamId``, etc.). These are ``NewType`` wrappers around
``int`` — no runtime cost, but static type checkers will catch mix-ups.

**Parameters**: Standalone doubles used as constraint values (distances, angles,
radii) or as free unknowns.

- ``add_param(value)`` creates a **free** parameter the solver may adjust.
- ``add_fixed_param(value)`` (or ``add_param(value, fixed=True)``) creates a
  **driving** parameter the solver will not change.

For driving constraint values, prefer ``add_fixed_param``:
``d = add_fixed_param(5.0); p2p_distance(p1, p2, d)``.

Many constraints also have ``set_*`` convenience methods that accept a
float directly and create a fixed parameter internally (e.g.
``set_p2p_distance(p1, p2, 5.0)``).

.. note::

   Point coordinates created by ``add_point()`` are always free.
   ``add_fixed_point()`` is a convenience that creates a point and
   then fixes both coordinates.

**Constraints**: Return a ``ConstraintTag`` that can be used to query errors
or remove the constraint.

**Solving**: Call ``solve()`` to find a solution. Returns a
:class:`~planegcs.SolveStatus` enum.

Circles and Arcs
----------------

.. code-block:: python

   s = Sketch()

   center = s.add_fixed_point(0, 0)

   c = s.add_circle(center, 5.0)

   # Constrain radius
   s.set_circle_radius(c, 5.0)

   # Put a point on the circle
   pt = s.add_point(5, 0)
   s.point_on_circle(pt, c)

   status = s.solve()
   assert status == SolveStatus.Success

Low-Level API
-------------

For advanced use, access the :class:`~planegcs.SketchSolver` directly:

.. code-block:: python

   from planegcs import SketchSolver, SolveStatus

   solver = SketchSolver()
   p1 = solver.add_point(0, 0)
   p2 = solver.add_point(5, 3)
   d = solver.add_param(10.0, fixed=True)
   solver.p2p_distance(p1, p2, d)
   status = solver.solve()
