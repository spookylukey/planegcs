"""Tests for constraint system diagnosis."""

from planegcs import Sketch, SolveStatus


def test_fully_constrained():
    """A fully constrained system has dof=0 and no conflicts."""
    s = Sketch()
    p1 = s.add_point(0, 0)
    p2 = s.add_point(5, 0)
    s.add_line(p1, p2)

    s.fix_point(p1, 0, 0)
    s.fix_point(p2, 5, 0)

    diag = s.diagnose()
    assert diag.dof == 0
    assert diag.is_fully_constrained
    assert not diag.is_under_constrained
    assert not diag.is_over_constrained
    assert diag.conflicting == []
    assert diag.redundant == []


def test_under_constrained():
    """A system with free degrees of freedom."""
    s = Sketch()
    p1 = s.add_point(0, 0)
    p2 = s.add_point(5, 0)
    s.add_line(p1, p2)

    s.fix_point(p1, 0, 0)
    # p2 is free -> 2 dof remaining

    diag = s.diagnose()
    assert diag.dof > 0
    assert diag.is_under_constrained
    assert not diag.is_fully_constrained


def test_over_constrained():
    """A system with conflicting constraints."""
    s = Sketch()
    p1 = s.add_point(0, 0)
    p2 = s.add_point(5, 0)
    s.add_line(p1, p2)

    s.fix_point(p1, 0, 0)
    s.fix_point(p2, 5, 0)
    # Now also constrain distance to something different
    s.set_p2p_distance(p1, p2, 10.0)

    diag = s.diagnose()
    assert diag.is_over_constrained
    assert len(diag.conflicting) > 0


def test_redundant_constraint():
    """A system with redundant constraints."""
    s = Sketch()
    p1 = s.add_point(0, 0)
    p2 = s.add_point(5, 0)
    s.add_line(p1, p2)

    s.fix_point(p1, 0, 0)
    s.fix_point(p2, 5, 0)
    # Adding a consistent distance constraint (redundant with fixed points)
    s.set_p2p_distance(p1, p2, 5.0)

    diag = s.diagnose()
    assert diag.dof == 0
    assert len(diag.redundant) > 0 or len(diag.partially_redundant) > 0


def test_dof_shorthand():
    """Sketch.dof() returns same as diagnose().dof."""
    s = Sketch()
    p1 = s.add_point(0, 0)
    _p2 = s.add_point(5, 0)
    s.fix_point(p1, 0, 0)

    assert s.dof() == s.diagnose().dof


def test_dof_triangle_example():
    """Equilateral triangle from README is fully constrained."""
    s = Sketch()
    p1 = s.add_point(0, 0)
    p2 = s.add_point(5, 0)
    p3 = s.add_point(2.5, 4)

    l1 = s.add_line(p1, p2)
    l2 = s.add_line(p2, p3)
    l3 = s.add_line(p3, p1)

    s.equal_length(l1, l2)
    s.equal_length(l2, l3)
    s.fix_point(p1, 0, 0)
    s.horizontal(l1)
    s.set_p2p_distance(p1, p2, 5.0)

    status = s.solve()
    assert status == SolveStatus.Success

    diag = s.diagnose()
    assert diag.dof == 0
    assert diag.is_fully_constrained
