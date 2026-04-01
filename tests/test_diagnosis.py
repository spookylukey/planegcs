"""Tests for constraint system diagnosis."""

from planegcs import ConstraintInfo, Sketch, SolveStatus


def test_fully_constrained():
    """A fully constrained system has dof=0 and no conflicts."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(5, 0)
    s.add_line(p1, p2)

    diag = s.diagnose()
    assert diag.dof == 0
    assert diag.is_fully_constrained
    assert not diag.is_under_constrained
    assert not diag.is_over_constrained
    assert diag.conflicting == []
    assert diag.redundant == []
    assert diag.conflicting_info == []
    assert diag.redundant_info == []
    assert diag.partially_redundant_info == []


def test_under_constrained():
    """A system with free degrees of freedom."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(5, 0)
    s.add_line(p1, p2)

    # p2 is free -> 2 dof remaining

    diag = s.diagnose()
    assert diag.dof > 0
    assert diag.is_under_constrained
    assert not diag.is_fully_constrained


def test_over_constrained():
    """A system with conflicting constraints."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(5, 0)
    s.add_line(p1, p2)

    # Now also constrain distance to something different
    tag_d = s.set_p2p_distance(p1, p2, 10.0)

    diag = s.diagnose()
    assert diag.is_over_constrained
    assert len(diag.conflicting) > 0
    # The conflicting_info should contain rich info about the constraint
    assert len(diag.conflicting_info) > 0
    # The distance constraint should be among the conflicting ones
    conflicting_tags = [ci.tag for ci in diag.conflicting_info]
    assert tag_d in conflicting_tags
    # Verify constraint info fields
    dist_info = next(ci for ci in diag.conflicting_info if ci.tag == tag_d)
    assert dist_info.type_name == "p2p_distance"
    assert p1 in dist_info.entities
    assert p2 in dist_info.entities
    assert dist_info.driving is True


def test_over_constrained_info_types():
    """Conflicting constraints expose their type names."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(5, 0)
    s.add_line(p1, p2)

    # Fix the x-coordinates are already set; also add a contradictory horizontal constraint
    s.set_p2p_distance(p1, p2, 10.0)

    diag = s.diagnose()
    type_names = {ci.type_name for ci in diag.conflicting_info}
    # The fix constraints (coordinate_x/y) and the distance should conflict
    assert len(type_names) >= 1


def test_redundant_constraint():
    """A system with redundant constraints."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(5, 0)
    s.add_line(p1, p2)

    # Adding a consistent distance constraint (redundant with fixed points)
    tag_d = s.set_p2p_distance(p1, p2, 5.0)

    diag = s.diagnose()
    assert diag.dof == 0
    assert len(diag.redundant) > 0 or len(diag.partially_redundant) > 0
    # The distance constraint should appear in redundant info
    all_redundant_tags = [ci.tag for ci in diag.redundant_info + diag.partially_redundant_info]
    assert tag_d in all_redundant_tags


def test_redundant_constraint_info_details():
    """Redundant constraints have full info."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(5, 0)
    line = s.add_line(p1, p2)

    tag_d = s.set_p2p_distance(p1, p2, 5.0)
    tag_h = s.horizontal(line)

    diag = s.diagnose()
    redundant_tags = [ci.tag for ci in diag.redundant_info]
    assert tag_d in redundant_tags
    assert tag_h in redundant_tags

    h_info = next(ci for ci in diag.redundant_info if ci.tag == tag_h)
    assert h_info.type_name == "horizontal_line"
    assert line in h_info.entities


def test_dof_shorthand():
    """Sketch.dof() returns same as diagnose().dof."""
    s = Sketch()
    s.add_fixed_point(0, 0)
    _p2 = s.add_point(5, 0)

    assert s.dof() == s.diagnose().dof


def test_dof_triangle_example():
    """Equilateral triangle from README is fully constrained."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(5, 0)
    p3 = s.add_point(2.5, 4)

    l1 = s.add_line(p1, p2)
    l2 = s.add_line(p2, p3)
    l3 = s.add_line(p3, p1)

    s.equal_length(l1, l2)
    s.equal_length(l2, l3)
    s.horizontal(l1)
    s.set_p2p_distance(p1, p2, 5.0)

    status = s.solve()
    assert status == SolveStatus.Success

    diag = s.diagnose()
    assert diag.dof == 0
    assert diag.is_fully_constrained


def test_constraint_info_repr():
    """ConstraintInfo has a useful repr."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(5, 0)
    line = s.add_line(p1, p2)
    tag = s.horizontal(line)

    info = s.get_constraint_info(tag)
    assert info is not None
    r = repr(info)
    assert "horizontal" in r
    assert str(tag) in r
    assert "driving=True" in r


def test_constraints_property():
    """Sketch.constraints returns all registered constraints."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(5, 0)
    line = s.add_line(p1, p2)
    tag_h = s.horizontal(line)
    tag_d = s.set_p2p_distance(p1, p2, 5.0)

    constraints = s.constraints
    assert tag_h in constraints
    assert tag_d in constraints
    # fix_point creates 2 coordinate constraints per point
    # p1 has 2, so there should be at least 4 constraints total
    assert len(constraints) >= 4


def test_get_constraint_info_missing():
    """get_constraint_info returns None for unknown tags."""
    s = Sketch()
    from planegcs.sketch import ConstraintTag

    assert s.get_constraint_info(ConstraintTag(9999)) is None


def test_clear_removes_constraint_info():
    """Sketch.clear() also clears constraint metadata."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(5, 0)
    line = s.add_line(p1, p2)
    tag = s.horizontal(line)
    assert s.get_constraint_info(tag) is not None

    s.clear()
    assert s.get_constraint_info(tag) is None
    assert len(s.constraints) == 0


def test_clear_by_tag_removes_constraint_info():
    """Sketch.clear_by_tag() also removes the constraint metadata."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(5, 0)
    line = s.add_line(p1, p2)
    tag = s.horizontal(line)
    assert s.get_constraint_info(tag) is not None

    s.clear_by_tag(tag)
    assert s.get_constraint_info(tag) is None


def test_constraint_info_is_frozen():
    """ConstraintInfo is immutable."""
    import pytest

    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(5, 0)
    line = s.add_line(p1, p2)
    tag = s.horizontal(line)
    info = s.get_constraint_info(tag)

    with pytest.raises(AttributeError):
        info.type_name = "something_else"  # type: ignore[invalid-assignment]


def test_diagnosis_info_matches_tags():
    """The *_info lists correspond to the same constraints as the tag lists."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(5, 0)
    line = s.add_line(p1, p2)
    s.set_p2p_distance(p1, p2, 5.0)  # redundant
    s.horizontal(line)  # redundant

    diag = s.diagnose()
    # Every info tag should appear in the corresponding tag list
    for ci in diag.redundant_info:
        assert ci.tag in diag.redundant
    for ci in diag.conflicting_info:
        assert ci.tag in diag.conflicting
    for ci in diag.partially_redundant_info:
        assert ci.tag in diag.partially_redundant


def test_constraint_info_isinstance():
    """ConstraintInfo objects in diagnosis are proper instances."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(5, 0)
    s.add_line(p1, p2)
    s.set_p2p_distance(p1, p2, 5.0)

    diag = s.diagnose()
    for ci in diag.redundant_info:
        assert isinstance(ci, ConstraintInfo)
        assert isinstance(ci.tag, int)
        assert isinstance(ci.type_name, str)
        assert isinstance(ci.entities, tuple)
        assert isinstance(ci.driving, bool)
