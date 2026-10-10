===============================
 Reproducibility of the solver
===============================

Solving the same sketch twice with planegcs gives the same answer, bit for
bit, in this library.  That is not true of PlaneGCS in general, and keeping it
true takes a little work in the wrapper; this page explains why.

The underlying problem
======================

PlaneGCS orders several of its internal containers by the *memory address* of
each parameter (``std::set<double*>``, ``std::map<double*, ...>``, and a
``std::sort`` over a vector of ``double*``).  Those orderings decide:

* the column order of the Jacobian,
* the order in which gradient contributions are accumulated, and
* after an exact-equality reduction, which of two merged parameters seeds the
  shared unknown (last write wins, and "last" means "highest address").

The first two only change floating-point rounding, but in a Newton/dogleg
iteration that is enough to converge on a *different* (equally valid) solution
of an under-constrained sketch.  The third is a genuine semantic ambiguity
resolved by the allocator.

So the solution PlaneGCS finds can depend on where in memory the parameters
happen to live - which depends on the process's allocation history, not on the
sketch.  In FreeCAD, where every parameter is a separate ``new double``, this
produces a different answer on almost every rebuild; the full investigation is
in ``docs/freecad_nondeterminism.md``.

The work-around
===============

Rather than patch the vendored solver, this library removes the ambiguity on
the input side.  :file:`src/param_arena.h` implements ``ParamArena``: a bump
allocator over a large reservation of *address space* (64 MiB by default, i.e.
about 8.4 million parameters; nothing is committed until it is used).  Every
parameter the solver sees comes from that arena, so

* parameter addresses increase strictly with declaration order, and therefore
* every address-ordered container inside PlaneGCS is in declaration order,
  which is deterministic and independent of the heap.

Pointers are never invalidated (the arena never moves anything), allocation is
O(1), and parameters are only ever added - ``Sketch.clear()`` resets the whole
arena, and individual parameters are never freed - so a bump allocator is all
that is needed.

If the arena ever has to grow beyond its reservation, it asks the operating
system for a region *above* the existing one, probing upwards for a free gap.
In the vanishingly unlikely event that no such region can be obtained, the
arena falls back to whatever the OS gives it and
:attr:`~planegcs.Sketch.results_are_reproducible` becomes ``False``::

    sketch = Sketch()
    ...
    assert sketch.results_are_reproducible

What this does *not* cover
==========================

The guarantee is "same inputs, same outputs, on the same machine and build".
Results can still differ:

* between platforms, compilers or optimisation levels (different
  floating-point code generation),
* if the sketch itself is built in a different order - declaration order is
  now part of the input, and a different order is a different problem,
* for constraint-level diagnostics that iterate containers keyed by
  ``Constraint*`` inside the solver.  In testing these have been stable, since
  constraint objects are allocated in creation order, but unlike the
  parameters they are not under the wrapper's control.

Checking it yourself
====================

``tools/determinism/`` contains the harness used to develop and verify this:

.. code-block:: bash

   ./tools/determinism/run_checks.sh 20     # solve/diagnose, many configurations
   ./tools/determinism/run_arena_test.sh    # unit test for the arena itself

``run_checks.sh`` builds a deliberately ordering-sensitive sketch (a large,
under-constrained equal-length polygon) repeatedly, with unrelated allocations
in between, and reports how many distinct answers came out.  Before the arena
was introduced it reported up to 10 distinct solutions out of 12 runs, with
coordinates differing by tens of units; it now reports exactly one everywhere.
The same checks run as part of the test suite in ``tests/test_determinism.py``.
