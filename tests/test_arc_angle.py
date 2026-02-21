"""Test constraining the angular span (sweep) of an arc."""

import math

from planegcs import Sketch, SolveStatus


def test_arc_angle_45_degrees():
    """Create an arc and constrain its angular span to 45 degrees.

    Setup:
      - Center fixed at origin (0, 0).
      - Arc with initial radius 5, start_angle=0, end_angle=pi/2 (90°).
      - Constrain the arc angle (sweep) to 45° (pi/4 radians).
      - The solver should adjust end_angle so that end_angle - start_angle = pi/4.
    """
    s = Sketch()

    s.add_fixed_point(0, 0)
    arc = s.add_arc3p((0, 0), 5.0, 0.0, math.pi / 2)

    # Constrain the sweep to 45 degrees
    target_angle = math.pi / 4
    s.set_arc_angle(arc, target_angle)

    status = s.solve()
    assert status == SolveStatus.Success

    info = s.get_arc(arc)
    sweep = info.end_angle - info.start_angle
    assert abs(sweep - target_angle) < 1e-6, (
        f"Expected sweep ~{target_angle:.4f} rad but got {sweep:.4f} rad"
    )


def test_arc_angle_large_sweep():
    """Arc constrained to a large sweep (270° = 3π/2).

    Setup:
      - Center at origin, radius 4, initial sweep of 90°.
      - Constrain sweep to 270° (3*pi/2 radians).
    """
    s = Sketch()

    s.add_fixed_point(0, 0)
    arc = s.add_arc3p((0, 0), 4.0, 0.0, math.pi / 2)

    target_angle = 3 * math.pi / 2
    s.set_arc_angle(arc, target_angle)

    status = s.solve()
    assert status == SolveStatus.Success

    info = s.get_arc(arc)
    sweep = info.end_angle - info.start_angle
    assert abs(sweep - target_angle) < 1e-4, (
        f"Expected sweep ~{target_angle:.4f} rad but got {sweep:.4f}"
    )


def test_arc_angle_param_version():
    """Test the parameter-based arc_angle (not the set_ convenience)."""
    s = Sketch()

    s.add_fixed_point(0, 0)
    arc = s.add_arc3p((0, 0), 3.0, 0.0, math.pi)

    angle_param = s.add_param(math.pi / 6, fixed=True)  # 30 degrees
    s.arc_angle(arc, angle_param)

    status = s.solve()
    assert status == SolveStatus.Success

    info = s.get_arc(arc)
    sweep = info.end_angle - info.start_angle
    assert abs(sweep - math.pi / 6) < 1e-6, (
        f"Expected sweep ~{math.pi / 6:.4f} rad (30°) but got {sweep:.4f} rad"
    )
