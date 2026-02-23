"""Tests for entity lookup and ConstraintInfo.get_entities()."""

import math

from planegcs import (
    ArcInfo,
    CircleInfo,
    EllipseInfo,
    EntityInfo,
    LineInfo,
    Sketch,
    SolveStatus,
)

# ── Sketch.get_entity ──────────────────────────────────────────────


def test_get_entity_point():
    s = Sketch()
    p = s.add_point(3.0, 4.0)
    info = s.get_entity(p)
    assert info is not None
    assert info.id == p
    assert info.type == "point"
    assert info.value == (3.0, 4.0)


def test_get_entity_line():
    s = Sketch()
    p1 = s.add_point(0.0, 0.0)
    p2 = s.add_point(1.0, 2.0)
    line = s.add_line(p1, p2)
    info = s.get_entity(line)
    assert info is not None
    assert info.id == line
    assert info.type == "line"
    assert isinstance(info.value, LineInfo)
    assert info.value.p1 == (0.0, 0.0)
    assert info.value.p2 == (1.0, 2.0)


def test_get_entity_line_xy():
    s = Sketch()
    line = s.add_line_xy(0.0, 0.0, 5.0, 5.0)
    info = s.get_entity(line)
    assert info is not None
    assert info.type == "line"
    assert isinstance(info.value, LineInfo)


def test_get_entity_circle():
    s = Sketch()
    c = s.add_point(0.0, 0.0)
    circle = s.add_circle(c, s.add_param(5.0))
    info = s.get_entity(circle)
    assert info is not None
    assert info.id == circle
    assert info.type == "circle"
    assert isinstance(info.value, CircleInfo)
    assert info.value.radius == 5.0


def test_get_entity_arc():
    s = Sketch()
    arc = s.add_arc3p(
        center=(0.0, 0.0),
        radius=5.0,
        start_angle=0.0,
        end_angle=math.pi / 2,
    )
    info = s.get_entity(arc)
    assert info is not None
    assert info.id == arc
    assert info.type == "arc"
    assert isinstance(info.value, ArcInfo)


def test_get_entity_ellipse():
    s = Sketch()
    center = s.add_point(0.0, 0.0)
    focus = s.add_point(3.0, 0.0)
    ellipse = s.add_ellipse(center, focus, 2.0)
    info = s.get_entity(ellipse)
    assert info is not None
    assert info.id == ellipse
    assert info.type == "ellipse"
    assert isinstance(info.value, EllipseInfo)
    assert info.value.radmin == 2.0


def test_get_entity_param():
    s = Sketch()
    p = s.add_param(42.0)
    info = s.get_entity(p)
    assert info is not None
    assert info.id == p
    assert info.type == "param"
    assert info.value == 42.0


def test_get_entity_fixed_param():
    s = Sketch()
    p = s.add_fixed_param(7.5)
    info = s.get_entity(p)
    assert info is not None
    assert info.type == "param"
    assert info.value == 7.5


def test_get_entity_unknown_id():
    s = Sketch()
    assert s.get_entity(99999) is None


def test_get_entity_reflects_solved_values():
    """After solving, get_entity returns updated values."""
    s = Sketch()
    p1 = s.add_fixed_point(0.0, 0.0)
    p2 = s.add_point(10.0, 10.0)
    s.add_line(p1, p2)
    s.set_p2p_distance(p1, p2, 5.0)
    s.horizontal_points(p1, p2)

    status = s.solve()
    assert status == SolveStatus.Success

    info = s.get_entity(p2)
    assert info is not None
    assert info.type == "point"
    assert isinstance(info.value, tuple)
    assert abs(info.value[0] - 5.0) < 1e-6
    assert abs(info.value[1]) < 1e-6


def test_get_entity_point_from_params():
    s = Sketch()
    px = s.add_param(1.0, fixed=False)
    py = s.add_param(2.0, fixed=False)
    pt = s.add_point_from_params(px, py)
    info = s.get_entity(pt)
    assert info is not None
    assert info.type == "point"
    assert info.value == (1.0, 2.0)


def test_clear_removes_entity_types():
    s = Sketch()
    p = s.add_point(1.0, 2.0)
    assert s.get_entity(p) is not None
    s.clear()
    assert s.get_entity(p) is None


# ── EntityInfo repr ────────────────────────────────────────────────


def test_entity_info_repr():
    s = Sketch()
    p = s.add_point(3.0, 4.0)
    info = s.get_entity(p)
    r = repr(info)
    assert "point" in r
    assert "3.0" in r
    assert "4.0" in r


# ── ConstraintInfo.get_entities ────────────────────────────────────


def test_get_entities_horizontal():
    """horizontal constraint references one line entity."""
    s = Sketch()
    p1 = s.add_point(0.0, 0.0)
    p2 = s.add_point(5.0, 0.0)
    line = s.add_line(p1, p2)
    tag = s.horizontal(line)

    ci = s.get_constraint_info(tag)
    assert ci is not None
    entities = ci.get_entities(s)
    assert len(entities) == 1
    assert entities[0].type == "line"
    assert entities[0].id == line


def test_get_entities_coincident():
    """coincident constraint references two point entities."""
    s = Sketch()
    p1 = s.add_point(0.0, 0.0)
    p2 = s.add_point(1.0, 1.0)
    tag = s.coincident(p1, p2)

    ci = s.get_constraint_info(tag)
    assert ci is not None
    entities = ci.get_entities(s)
    assert len(entities) == 2
    assert entities[0].type == "point"
    assert entities[1].type == "point"


def test_get_entities_p2p_distance():
    """p2p_distance references two points and a param."""
    s = Sketch()
    p1 = s.add_point(0.0, 0.0)
    p2 = s.add_point(5.0, 0.0)
    tag = s.set_p2p_distance(p1, p2, 5.0)

    ci = s.get_constraint_info(tag)
    assert ci is not None
    entities = ci.get_entities(s)
    assert len(entities) == 3
    types = [e.type for e in entities]
    assert types[0] == "point"
    assert types[1] == "point"
    assert types[2] == "param"


def test_get_entities_point_on_circle():
    """point_on_circle references a point and a circle."""
    s = Sketch()
    center = s.add_point(0.0, 0.0)
    circle = s.add_circle(center, s.add_param(5.0))
    pt = s.add_point(5.0, 0.0)
    tag = s.point_on_circle(pt, circle)

    ci = s.get_constraint_info(tag)
    assert ci is not None
    entities = ci.get_entities(s)
    types = [e.type for e in entities]
    assert "point" in types
    assert "circle" in types


def test_get_entities_from_diagnosis():
    """get_entities works on ConstraintInfo from diagnosis results."""
    s = Sketch()
    p1 = s.add_fixed_point(0.0, 0.0)
    p2 = s.add_fixed_point(5.0, 0.0)
    line = s.add_line(p1, p2)
    s.horizontal(line)  # redundant

    diag = s.diagnose()
    assert len(diag.redundant_info) > 0

    for ci in diag.redundant_info:
        entities = ci.get_entities(s)
        # Every entity should resolve
        for e in entities:
            assert isinstance(e, EntityInfo)
            assert e.type in ("point", "line", "circle", "arc", "ellipse", "param")


def test_get_entities_omits_unknown():
    """Entities not in the registry are omitted."""
    from planegcs.sketch import ConstraintInfo, ConstraintTag

    s = Sketch()
    # Manually create a ConstraintInfo with a bogus entity ID
    ci = ConstraintInfo(
        tag=ConstraintTag(1),
        type_name="test",
        entities=(99999,),
        driving=True,
    )
    entities = ci.get_entities(s)
    assert entities == []


def test_get_entities_mixed_known_unknown():
    """Known entities are returned, unknown ones are skipped."""
    from planegcs.sketch import ConstraintInfo, ConstraintTag

    s = Sketch()
    p = s.add_point(1.0, 2.0)
    ci = ConstraintInfo(
        tag=ConstraintTag(1),
        type_name="test",
        entities=(p, 99999),
        driving=True,
    )
    entities = ci.get_entities(s)
    assert len(entities) == 1
    assert entities[0].id == p
