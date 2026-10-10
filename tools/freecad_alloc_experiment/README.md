# FreeCAD allocation-pattern experiment

Does planegcs' habit of ordering parameters by pointer value matter in
FreeCAD, or only in this Python wrapper?

This harness answers that by driving the vendored planegcs solver from C++
while allocating parameters the way `FreeCAD/src/Mod/Sketcher/App/Sketch.cpp`
does (one `new double` each, freed and reallocated on every rebuild).

Run everything:

    ./run_experiment.sh 20

That builds patch levels 0-4 (`patch_planegcs.py` applies the candidate fixes
to a *copy* of `src/planegcs`; the vendored sources are never modified) and
prints, for each, how many distinct solutions 20 solves of the same sketch
produce.

Individual pieces:

    ./build.sh            # ./experiment    - planegcs as vendored
    ./build.sh 4          # ./experiment-4  - all four fixes applied
    ./experiment 20 freecad solve      # FreeCAD-style allocation
    ./experiment 20 interleaved solve  # ... with interleaved allocations
    ./experiment 20 arena solve        # control: contiguous parameter arena
    ./experiment 20 freecad diagnose   # over-constrained sketch, diagnosis

Findings are written up in `docs/freecad_nondeterminism.md`.
