# planegcs — Python bindings for FreeCAD's PlaneGCS constraint solver

## Goal
PyPI-installable Python package wrapping FreeCAD's PlaneGCS 2D geometric
constraint solver via pybind11. Supports all constraint types.

## Architecture

### Layers
1. **planegcs C++ sources** — copied from FreeCAD, with shim headers replacing
   framework dependencies (Base::Console, FCGlobal, etc.)
2. **C++ wrapper (`src/wrapper.h`)** — a `SketchSolver` class that:
   - Owns a `GCS::System`
   - Owns all `double` storage via `std::deque<double>` (pointer-stable)
   - Stores geometry objects (Points, Lines, Circles, Arcs, Ellipses, etc.) by ID
   - Exposes a flat, ID-based API: `add_point(x,y)->int`, `add_line(p1,p2)->int`, etc.
   - All `addConstraint*` methods wrapped, taking IDs + values
3. **pybind11 bindings (`src/bindings.cpp`)** — binds SketchSolver + enums
4. **Python API (`python/planegcs/`)** — thin Pythonic layer with `Sketch` class

### Key design: pointer ownership
GCS uses `double*` everywhere. The wrapper allocates doubles in a
`std::deque<double>` (stable addresses) and maps IDs to geometry objects
that reference those doubles.

## Package structure
```
planegcs-py/
├── PLAN.md
├── pyproject.toml          # scikit-build-core + pybind11
├── CMakeLists.txt           # builds the extension module
├── README.md
├── LICENSE                  # LGPL-2.1 (matching FreeCAD)
├── src/
│   ├── planegcs/            # copied GCS solver sources + shims
│   ├── wrapper.h            # C++ SketchSolver wrapper
│   └── bindings.cpp         # pybind11 module
├── python/
│   └── planegcs/
│       ├── __init__.py      # re-exports
│       └── sketch.py        # High-level Sketch class
├── tests/
│   ├── test_triangle.py     # equilateral triangle
│   ├── test_tangent.py      # tangent circles/lines
│   └── test_constraints.py  # broad constraint coverage
└── docs/
    ├── conf.py
    ├── index.rst
    ├── quickstart.rst
    └── api.rst
```

## Steps

- [ ] 1. Create project skeleton (pyproject.toml, CMakeLists, dirs)
- [ ] 2. Copy planegcs sources + shims from sketch-solver project
- [ ] 3. Write C++ wrapper class (SketchSolver) with full API
- [ ] 4. Write pybind11 bindings
- [ ] 5. Write Python Sketch class
- [ ] 6. Build and verify import works
- [ ] 7. Write tests (triangle, tangent, broad constraints)
- [ ] 8. Write Sphinx docs
- [ ] 9. Final integration test, git commit

## Geometry types to wrap
- Point
- Line
- Circle
- Arc
- Ellipse, ArcOfEllipse
- Hyperbola, ArcOfHyperbola
- Parabola, ArcOfParabola
- BSpline

## Constraints to wrap (~60 methods)
See GCS.h for the full list. Key categories:
- **Basic**: Equal, Proportional, Difference
- **Distance**: P2P, P2L, P2C, C2C, C2L
- **Position**: CoordinateX/Y, Coincident, PointOnLine/Circle/Ellipse/Arc/BSpline
- **Angle**: P2PAngle, L2LAngle, AngleViaPoint
- **Direction**: Horizontal, Vertical, Parallel, Perpendicular
- **Tangent**: Line-Circle, Line-Arc, Circle-Circle, Arc-Arc, Line-Ellipse, etc.
- **Size**: CircleRadius/Diameter, ArcRadius/Diameter/Length, EqualLength, EqualRadius
- **Symmetry**: P2PSymmetric
- **Midpoint**: MidpointOnLine
- **Internal alignment**: Ellipse/Hyperbola/Parabola/BSpline alignment
- **Other**: SnellsLaw, TangentCircumf, CurveValue

## Tools
- **Build**: scikit-build-core + CMake + pybind11
- **Package manager**: uv
- **Docs**: Sphinx with autodoc
- **Testing**: pytest
