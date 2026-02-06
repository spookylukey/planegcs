# WRAPPER_PLAN.md — Python wrapper for planegcs

## Goal
PyPI-installable Python package wrapping FreeCAD's PlaneGCS 2D geometric
constraint solver via pybind11. Build with scikit-build-core + CMake.
Manage with uv. Docs via Sphinx. Tests via pytest.

## Architecture

### Layer 1: C++ Wrapper (`src/wrapper.h`)
A `SketchSolver` class that:
- Owns a `GCS::System`
- Owns all `double` storage via `std::deque<double>` (pointer-stable)
- Stores geometry objects (Point, Line, Circle, Arc, Ellipse, etc.) by integer ID
- Exposes a flat, ID-based API:
  - `add_point(x, y) -> int`
  - `add_line(p1_id, p2_id) -> int`
  - `add_circle(center_id, radius) -> int`
  - `add_arc(center_id, radius, start_angle, end_angle) -> int`
  - `add_ellipse(center_id, focus1_id, radmin) -> int`
  - etc.
- All `addConstraint*` methods wrapped, taking geometry IDs + values
- `solve()` returns SolveStatus enum
- `get_point(id) -> (x, y)`, `get_param(id) -> double` for reading results
- `clear()` to reset

### Layer 2: pybind11 Bindings (`src/bindings.cpp`)
- Binds `SketchSolver` class
- Binds enums: `SolveStatus`, `Algorithm`, `InternalAlignmentType`, `DebugMode`
- Module name: `_planegcs` (C extension)

### Layer 3: Python API (`python/planegcs/`)
- `planegcs.Sketch` — high-level Pythonic class
- Re-exports enums
- Convenience methods with keyword arguments

## File Structure
```
planegcs-py/
├── WRAPPER_PLAN.md
├── PLAN.md
├── pyproject.toml            # scikit-build-core + pybind11
├── CMakeLists.txt            # builds _planegcs extension
├── README.md
├── LICENSE                   # LGPL-2.1
├── src/
│   ├── planegcs/             # GCS solver C++ sources (existing)
│   ├── wrapper.h             # C++ SketchSolver class
│   └── bindings.cpp          # pybind11 module definition
├── python/
│   └── planegcs/
│       ├── __init__.py       # re-exports Sketch, enums
│       └── sketch.py         # High-level Sketch class
├── tests/
│   ├── test_basic.py         # basic point/line/solve
│   ├── test_triangle.py      # equilateral triangle constraint solving
│   ├── test_circle.py        # circle/arc constraints
│   └── test_constraints.py   # broad constraint coverage
└── docs/
    ├── conf.py
    ├── index.rst
    ├── quickstart.rst
    └── api.rst
```

## Steps

- [x] 1. Create WRAPPER_PLAN.md
- [ ] 2. Create project skeleton: pyproject.toml, CMakeLists.txt, LICENSE, README
- [ ] 3. Write C++ wrapper class (src/wrapper.h)
- [ ] 4. Write pybind11 bindings (src/bindings.cpp)
- [ ] 5. Write Python Sketch class (python/planegcs/sketch.py + __init__.py)
- [ ] 6. Build and verify `import planegcs` works
- [ ] 7. Write tests
- [ ] 8. Write Sphinx docs
- [ ] 9. Initialize git, commit

## Geometry IDs
Every geometry added returns an integer ID. Internally:
- Points stored in `std::map<int, GCS::Point>`
- Lines stored in `std::map<int, GCS::Line>`
- Circles in `std::map<int, GCS::Circle>`
- Arcs in `std::map<int, GCS::Arc>`
- etc.
All doubles owned by `std::deque<double>` for pointer stability.

Constraints reference geometry by ID. The wrapper looks up the GCS objects.

## Param IDs
Some constraints need standalone double* parameters (e.g., distance, angle).
The wrapper provides `add_param(value) -> int` which allocates a double in
the deque and returns its ID. These can be read back with `get_param(id)`.
