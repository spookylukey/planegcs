"""Test the difference constraint using get_point_param_ids."""

from planegcs import Sketch, SolveStatus


def test_difference_horizontal_distance():
    """Use difference to constrain x2 - x1 = 10.

    The GCS difference constraint enforces param2 - param1 = diff,
    so we pass (p1x, p2x, diff) to get p2x - p1x = 10.
    """
    s = Sketch()

    # Two points; fix the first one at the origin.
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(12, 3)  # initial guess

    # Get the underlying x-parameter IDs.
    p1x, _p1y = s.get_point_param_ids(p1)
    p2x, _p2y = s.get_point_param_ids(p2)

    # Create a fixed parameter for the desired difference.
    diff = s.add_param(10.0, fixed=True)

    # Constrain p2.x - p1.x = 10  (GCS semantics: param2 - param1 = diff)
    s.difference(p1x, p2x, diff)

    # Also pin the y-coordinate of p2 so the system is fully constrained.
    y_val = s.add_param(5.0, fixed=True)
    s.coordinate_y(p2, y_val)

    status = s.solve()
    assert status == SolveStatus.Success

    x1, _ = s.get_point(p1)
    x2, y2 = s.get_point(p2)

    assert abs(x1 - 0.0) < 1e-9
    assert abs(x2 - 10.0) < 1e-9
    assert abs(y2 - 5.0) < 1e-9
