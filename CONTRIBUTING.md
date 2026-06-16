# Contributing to planegcs


- The underlying C++ solver from FreeCAD should not be modified, except to
  update to the latest version from FreeCAD. The wrapper code can be modified:

  - `src/wrapper.h` - the C++ wrapper
  - `src/bindings.cpp` - the bindings for the C++ code for Python
  - `python/*` - the Python wrapper
    - The `_planegcs.pyi` should only be updated by running `update_stubs.sh`

- All code needs to be 100% covered by unit tests. Run the test suite with:
  ```bash
  uv run pytest
  ```

- We use pyright for static type checks, with zero errors allowed. Run the type checker with:

  ```bash
  uv run pyright
  ```

- C++ wrapper code is checked with **cppcheck** and **clang-tidy**. Install
  them with:

  ```bash
  sudo apt-get install cppcheck clang-tidy
  ```

  Run both tools:

  ```bash
  ./tools/lint_cpp.sh
  ```

  Or run individually: `./tools/lint_cpp.sh cppcheck` or `./tools/lint_cpp.sh clang-tidy`.

  cppcheck also runs automatically as a pre-commit hook. clang-tidy (which
  requires a CMake build step) runs in CI.
