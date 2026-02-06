"""Basic tests for planegcs: import, points, lines, simple solving."""

import math
import pytest
from planegcs import Sketch, SketchSolver, SolveStatus, Algorithm


def test_import():
    """Module imports correctly."""
    from planegcs import _planegcs
    assert hasattr(_planegcs, "SketchSolver")
    assert hasattr(_planegcs, "SolveStatus")


def test_solver_direct():
    """Low-level SketchSolver API works."""
    solver = SketchSolver()
    p1 = solver.add_point(0, 0)
    p2 = solver.add_point(10, 0)
    assert solver.get_point(p1) == (0.0, 0.0)
    assert solver.get_point(p2) == (10.0, 0.0)


def test_param():
    """Parameter allocation and retrieval."""
    solver = SketchSolver()
    pid = solver.add_param(42.0)
    assert solver.get_param(pid) == 42.0
    solver.set_param(pid, 99.0)
    assert solver.get_param(pid) == 99.0


def test_sketch_fix_point():
    """Fix a point to a specific location."""
    s = Sketch()
    p = s.add_point(10, 20)
    s.fix_point(p, 3.0, 4.0)
    status = s.solve()
    assert status == SolveStatus.Success
    x, y = s.get_point(p)
    assert abs(x - 3.0) < 1e-8
    assert abs(y - 4.0) < 1e-8


def test_horizontal_line():
    """Horizontal constraint makes y-coords equal."""
    s = Sketch()
    p1 = s.add_point(0, 0)
    p2 = s.add_point(5, 3)
    l = s.add_line(p1, p2)
    s.fix_point(p1, 0, 0)
    s.horizontal(l)
    status = s.solve()
    assert status == SolveStatus.Success
    _, y1 = s.get_point(p1)
    _, y2 = s.get_point(p2)
    assert abs(y1 - y2) < 1e-8


def test_vertical_line():
    """Vertical constraint makes x-coords equal."""
    s = Sketch()
    p1 = s.add_point(0, 0)
    p2 = s.add_point(3, 5)
    l = s.add_line(p1, p2)
    s.fix_point(p1, 0, 0)
    s.vertical(l)
    status = s.solve()
    assert status == SolveStatus.Success
    x1, _ = s.get_point(p1)
    x2, _ = s.get_point(p2)
    assert abs(x1 - x2) < 1e-8


def test_coincident():
    """Two points made coincident end up at the same location."""
    s = Sketch()
    p1 = s.add_point(0, 0)
    p2 = s.add_point(5, 5)
    s.fix_point(p1, 1, 2)
    s.coincident(p1, p2)
    status = s.solve()
    assert status == SolveStatus.Success
    x1, y1 = s.get_point(p1)
    x2, y2 = s.get_point(p2)
    assert abs(x1 - x2) < 1e-8
    assert abs(y1 - y2) < 1e-8


def test_point_on_line():
    """Point constrained to lie on a line."""
    s = Sketch()
    p1 = s.add_point(0, 0)
    p2 = s.add_point(10, 0)
    l = s.add_line(p1, p2)
    s.fix_point(p1, 0, 0)
    s.horizontal(l)

    p3 = s.add_point(5, 5)  # starts off-line
    s.point_on_line(p3, l)
    status = s.solve()
    assert status == SolveStatus.Success
    _, y3 = s.get_point(p3)
    assert abs(y3) < 1e-8  # should be on the horizontal line y=0


def test_distance_constraint():
    """Point-to-point distance."""
    s = Sketch()
    p1 = s.add_point(0, 0)
    p2 = s.add_point(1, 0)
    s.fix_point(p1, 0, 0)
    s.horizontal_points(p1, p2)

    d = s.add_param(7.0)
    s.p2p_distance(p1, p2, d)
    status = s.solve()
    assert status == SolveStatus.Success
    x2, y2 = s.get_point(p2)
    dist = math.sqrt(x2**2 + y2**2)
    assert abs(dist - 7.0) < 1e-8


def test_clear():
    """Clear resets the solver."""
    s = Sketch()
    p = s.add_point(1, 2)
    s.clear()
    # After clear, old IDs are invalid; adding a new point should work
    p2 = s.add_point(3, 4)
    assert s.get_point(p2) == (3.0, 4.0)


def test_algorithms():
    """Solving works with different algorithms."""
    for alg in [Algorithm.DogLeg, Algorithm.BFGS, Algorithm.LevenbergMarquardt]:
        s = Sketch()
        p1 = s.add_point(0, 0)
        p2 = s.add_point(5, 3)
        s.fix_point(p1, 0, 0)
        s.fix_point(p2, 3, 4)
        status = s.solve(alg)
        assert status == SolveStatus.Success
        assert abs(s.get_point(p2)[0] - 3.0) < 1e-6
        assert abs(s.get_point(p2)[1] - 4.0) < 1e-6
