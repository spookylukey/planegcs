# Standalone Sketch Solver — Extracted from FreeCAD PlaneGCS

## Goal
Build a standalone C++ executable that uses FreeCAD's PlaneGCS constraint solver
to create a triangle sketch, constrain it, solve it, and print point coordinates.

## Steps

- [x] 1. Explore FreeCAD source: locate planegcs solver, tests, dependencies
- [x] 2. Install build dependencies (Eigen3, Boost graph/math)
- [x] 3. Copy planegcs source files into standalone project
- [x] 4. Create shim headers to replace FreeCAD framework deps (FCGlobal.h, Base/Console.h, SketcherGlobal.h)
- [x] 5. Write CMakeLists.txt to compile planegcs as a static library
- [x] 6. Write main.cpp: equilateral triangle (one fixed side, two equal-length constraints)
- [x] 7. Build and test - solver finds C = (5, 8.660254) correctly
- [x] 8. Done!

## Architecture

The planegcs solver files (in `src/Mod/Sketcher/App/planegcs/`) are:
- GCS.cpp/h — main System class with solve(), addConstraint*() methods
- Constraints.cpp/h — constraint types
- Geo.cpp/h — geometric primitives (Point, Line, Circle, Arc, etc.)
- SubSystem.cpp/h — internal partitioning
- qp_eq.cpp/h — QP solver
- Util.h — type aliases

External deps:
- Eigen3 (linear algebra)
- Boost.Graph (constraint partitioning)
- Boost.Math (constants)
- Base::Console (logging — will stub out)
- FCGlobal.h / SketcherGlobal.h (export macros — will stub out)
- FCConfig.h (config — will stub out)
- boost_graph_adjacency_list.hpp (workaround header — will copy)

## Triangle Sketch Plan

Three points: A(0,0), B(10,0), C(?,?)
- Fix A at origin
- Fix B on x-axis at distance 10
- Constrain |AC| == |AB| (equal length)
- Constrain |BC| == |AB| (equal length)
- Solver should find C at (5, 8.66...) — equilateral triangle
