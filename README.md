# planegcs

Python bindings for FreeCAD's PlaneGCS 2D geometric constraint solver.

## Installation

```bash
pip install planegcs
```

## Quick Start

```python
from planegcs import Sketch, SolveStatus

s = Sketch()

# Create three points for a triangle
p1 = s.add_point(0, 0)
p2 = s.add_point(5, 0)
p3 = s.add_point(2.5, 4)

# Create lines
l1 = s.add_line(p1, p2)
l2 = s.add_line(p2, p3)
l3 = s.add_line(p3, p1)

# Make it equilateral
s.equal_length(l1, l2)
s.equal_length(l2, l3)

# Fix first point and make base horizontal
s.fix_point(p1, 0, 0)
s.horizontal(l1)

# Fix the side length to 5
d = s.add_param(5.0)
s.p2p_distance(p1, p2, d)

# Solve
status = s.solve()
assert status == SolveStatus.Success

# Read results
print(s.get_point(p1))  # (0.0, 0.0)
print(s.get_point(p2))  # (5.0, 0.0)
print(s.get_point(p3))  # (~2.5, ~4.33)
```

## License

LGPL-2.1-or-later (same as the FreeCAD source code it wraps).
