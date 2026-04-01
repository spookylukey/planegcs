# Contributing to planegcs


- The underlying C++ solver from FreeCAD should not be modified, except to
  update to the latest version from FreeCAD. The wrapper code can be modified:

  - `src/wrapper.h` - the C++ wrapper
  - `src/bindings.cpp` - the bindings for the C++ code for Python
  - `python/*` - the Python wrapper
    - The `_planegcs.pyi` should only be updated by running `update_stubs.sh`

- All code needs to be 100% covered by unit tests.
- We use pyright for static type checks, with zero errors allowed.
