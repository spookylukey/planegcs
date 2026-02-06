Quick Start
===========

Basic Usage
-----------

Create a sketch, add geometry and constraints, then solve:

.. code-block:: python

   from planegcs import Sketch, SolveStatus

   s = Sketch()

   # Add three points
   p1 = s.add_point(0, 0)
   p2 = s.add_point(5, 0)
   p3 = s.add_point(2.5, 4)

   # Connect with lines
   l1 = s.add_line(p1, p2)
   l2 = s.add_line(p2, p3)
   l3 = s.add_line(p3, p1)

   # Constraints: equilateral triangle
   s.equal_length(l1, l2)
   s.equal_length(l2, l3)
   s.fix_point(p1, 0, 0)
   s.horizontal(l1)

   # Fix side length
   d = s.add_param(5.0)
   s.p2p_distance(p1, p2, d)

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

**Parameters**: Standalone doubles used as constraint values (distances, angles,
radii). Created with ``add_param(value, fixed=True)``.

- ``fixed=True`` (default): The solver will not change this value
  (driving constraint).
- ``fixed=False``: The solver may adjust this value.

**Constraints**: Return a tag (integer) that can be used to query errors
or remove the constraint.

**Solving**: Call ``solve()`` to find a solution. Returns a
:class:`~planegcs.SolveStatus` enum.

Circles and Arcs
----------------

.. code-block:: python

   s = Sketch()

   center = s.add_point(0, 0)
   s.fix_point(center, 0, 0)

   c = s.add_circle(center, 5.0)

   # Constrain radius
   r = s.add_param(5.0)
   s.circle_radius(c, r)

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
