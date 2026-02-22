"""Tests for Sketch.add_point_from_params()."""

from planegcs import Sketch, SolveStatus


def test_basic_round_trip():
    """Create params, build a point from them, read back the coordinates."""
    s = Sketch()
    px = s.add_param(3.0, fixed=True)
    py = s.add_param(7.0, fixed=True)
    pt = s.add_point_from_params(px, py)

    assert s.get_point(pt) == (3.0, 7.0)


def test_get_point_param_ids_consistent():
    """get_point_param_ids returns the same IDs we passed in."""
    s = Sketch()
    px = s.add_param(1.0)
    py = s.add_param(2.0)
    pt = s.add_point_from_params(px, py)

    assert s.get_point_param_ids(pt) == (px, py)


def test_shared_param_between_points():
    """Two points sharing an x-parameter move together."""
    s = Sketch()
    shared_x = s.add_param(0.0, fixed=False)
    py1 = s.add_param(0.0, fixed=True)
    py2 = s.add_param(5.0, fixed=True)

    p1 = s.add_point_from_params(shared_x, py1)
    p2 = s.add_point_from_params(shared_x, py2)

    # Fix x via a coordinate constraint to 4.0
    x_val = s.add_fixed_param(4.0)
    s.coordinate_x(p1, x_val)

    status = s.solve()
    assert status == SolveStatus.Success

    # Both points should have x == 4
    assert abs(s.get_point(p1)[0] - 4.0) < 1e-9
    assert abs(s.get_point(p2)[0] - 4.0) < 1e-9


def test_difference_without_get_point_param_ids():
    """Using add_point_from_params the caller already owns the param IDs,
    so difference can be applied without needing get_point_param_ids."""
    s = Sketch()

    # Build two points from explicit params.
    x1 = s.add_param(0.0, fixed=True)
    y1 = s.add_param(0.0, fixed=True)
    _p1 = s.add_point_from_params(x1, y1)

    x2 = s.add_param(8.0, fixed=False)
    y2 = s.add_param(0.0, fixed=True)
    p2 = s.add_point_from_params(x2, y2)

    # Constrain x2 - x1 = 10
    diff = s.add_fixed_param(10.0)
    s.difference(x1, x2, diff)

    status = s.solve()
    assert status == SolveStatus.Success
    assert abs(s.get_point(p2)[0] - 10.0) < 1e-9


def test_line_from_param_points():
    """Points built from params work normally with lines and constraints."""
    s = Sketch()
    px1 = s.add_param(0.0, fixed=True)
    py1 = s.add_param(0.0, fixed=True)
    p1 = s.add_point_from_params(px1, py1)

    px2 = s.add_param(5.0, fixed=False)
    py2 = s.add_param(5.0, fixed=False)
    p2 = s.add_point_from_params(px2, py2)

    line = s.add_line(p1, p2)
    s.horizontal(line)
    s.set_p2p_distance(p1, p2, 3.0)

    status = s.solve()
    assert status == SolveStatus.Success

    pt2 = s.get_point(p2)
    assert abs(pt2[0] - 3.0) < 1e-9
    assert abs(pt2[1] - 0.0) < 1e-9
