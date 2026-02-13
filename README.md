# planegcs

Python bindings for FreeCAD's PlaneGCS 2D geometric constraint solver.

This project extracts the constraint solver system from
[FreeCAD](https://www.freecad.org/)'s
[Sketcher](https://wiki.freecad.org/Sketcher_Workbench) component, changes the
headers so that it can be used outside FreeCAD, and adds some thin C++ and
Python wrappers so it can be used as a Python library. As per the [FreeCAD
licence requirements](https://wiki.freecad.org/License), the result is licenced
under the LPGL 2.1 or later.

## Installation

```bash
pip install planegcs
```

or:
```bash
uv add planegcs
```

If wheels aren't available, you'll need C++ tools and some development headers:

- eigen3
- boost

## Quick Start

```python
from planegcs import Sketch, SolveStatus

s = Sketch()

# Create three points for a triangle
p1 = s.add_fixed_point(0, 0)
p2 = s.add_point(5, 0)
p3 = s.add_point(2.5, 4)

# Create lines
l1 = s.add_line(p1, p2)
l2 = s.add_line(p2, p3)
l3 = s.add_line(p3, p1)

# Make it equilateral
s.equal_length(l1, l2)
s.equal_length(l2, l3)

# Make base horizontal
s.horizontal(l1)

# Fix the side length to 5
s.set_p2p_distance(p1, p2, 5.0)

# Solve
status = s.solve()
assert status == SolveStatus.Success

# Read results
print(s.get_point(p1))  # (0.0, 0.0)
print(s.get_point(p2))  # (5.0, 0.0)
print(s.get_point(p3))  # (~2.5, ~4.33)
```

## Docs

Full documentation at [readthedocs](https://planegcs.readthedocs.io/en/latest/),
and in the `docs/` folder (requires Sphinx to build).

## License

LGPL-2.1-or-later (same as the FreeCAD source code it wraps).
