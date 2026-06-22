"""Tests for reference (non-driving) constraints and their DOF behaviour.

A reference (driving=False) constraint is one that *observes* a value
rather than *driving* it.  For example, a non-driving p2p_distance
constraint computes the distance between two points without constraining
the geometry.  The solver fills in the value parameter, which can then
be read back.

Crucially, the value parameter of a non-driving constraint should be
treated as a *driven* output — it should NOT contribute to the
reported degrees of freedom (DOF).  This file tests that behaviour.
"""

import math

from planegcs import Sketch, SolveStatus

# ── Basic DOF tests ────────────────────────────────────────────────


def test_reference_p2p_distance_dof_fixed_points():
    """Reference p2p_distance on two fixed points → dof=0, not dof=1.

    This is the exact scenario from the bug report.
    """
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(5, 0)
    param = s.add_param()
    s.p2p_distance(p1, p2, param, driving=False)

    status = s.solve()
    assert status == SolveStatus.Success

    diag = s.diagnose()
    assert diag.dof == 0, (
        f"Expected dof=0 (fully constrained), got dof={diag.dof}. "
        f"The distance param of a non-driving constraint should not "
        f"count as a degree of freedom."
    )
    assert diag.is_fully_constrained
    assert abs(s.get_param(param) - 5.0) < 1e-8


def test_reference_p2p_distance_dof_one_free_point():
    """Reference p2p_distance with one fixed and one free point.

    The free point has 2 DOF; the reference constraint does not reduce it.
    """
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(5, 0)
    param = s.add_param()
    s.p2p_distance(p1, p2, param, driving=False)

    status = s.solve()
    assert status == SolveStatus.Success

    diag = s.diagnose()
    # p2 has 2 free coordinates → 2 DOF
    # The reference constraint adds no driving equations, so DOF stays at 2.
    assert diag.dof == 2
    assert diag.is_under_constrained


def test_reference_p2p_distance_vs_driving():
    """Driving p2p_distance reduces DOF; reference does not."""
    # Driving version: 1 free point (2 DOF) minus 1 distance constraint = 1 DOF
    s_drive = Sketch()
    p1_d = s_drive.add_fixed_point(0, 0)
    p2_d = s_drive.add_point(5, 0)
    s_drive.set_p2p_distance(p1_d, p2_d, 5.0, driving=True)
    s_drive.solve()
    dof_driving = s_drive.diagnose().dof

    # Reference version: 1 free point (2 DOF), reference adds no constraint
    s_ref = Sketch()
    p1_r = s_ref.add_fixed_point(0, 0)
    p2_r = s_ref.add_point(5, 0)
    param = s_ref.add_param()
    s_ref.p2p_distance(p1_r, p2_r, param, driving=False)
    s_ref.solve()
    dof_reference = s_ref.diagnose().dof

    assert dof_driving == 1  # distance constraint removes 1 DOF
    assert dof_reference == 2  # reference constraint removes 0 DOF


# ── Solving correctness ───────────────────────────────────────────


def test_reference_distance_solves_correctly():
    """Reference constraint computes correct distance."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(3, 4)
    param = s.add_param()
    s.p2p_distance(p1, p2, param, driving=False)

    status = s.solve()
    assert status == SolveStatus.Success
    assert abs(s.get_param(param) - 5.0) < 1e-8


def test_reference_p2l_distance_dof():
    """Reference p2l_distance does not add DOF."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(10, 0)
    line = s.add_line(p1, p2)
    p3 = s.add_fixed_point(5, 3)
    param = s.add_param()
    s.p2l_distance(p3, line, param, driving=False)

    status = s.solve()
    assert status == SolveStatus.Success

    diag = s.diagnose()
    assert diag.dof == 0
    assert abs(s.get_param(param) - 3.0) < 1e-8


def test_reference_l2l_angle_dof():
    """Reference l2l_angle does not add DOF."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(1, 0)
    p3 = s.add_fixed_point(0, 0)
    p4 = s.add_fixed_point(0, 1)
    l1 = s.add_line(p1, p2)  # horizontal
    l2 = s.add_line(p3, p4)  # vertical
    param = s.add_param()
    s.l2l_angle(l1, l2, param, driving=False)

    status = s.solve()
    assert status == SolveStatus.Success

    diag = s.diagnose()
    assert diag.dof == 0
    assert abs(abs(s.get_param(param)) - math.pi / 2) < 1e-8


def test_reference_coordinate_x_dof():
    """Reference coordinate_x does not add DOF."""
    s = Sketch()
    p1 = s.add_fixed_point(7, 3)
    param = s.add_param()
    s.coordinate_x(p1, param, driving=False)

    status = s.solve()
    assert status == SolveStatus.Success

    diag = s.diagnose()
    assert diag.dof == 0
    assert abs(s.get_param(param) - 7.0) < 1e-8


def test_reference_coordinate_y_dof():
    """Reference coordinate_y does not add DOF."""
    s = Sketch()
    p1 = s.add_fixed_point(7, 3)
    param = s.add_param()
    s.coordinate_y(p1, param, driving=False)

    status = s.solve()
    assert status == SolveStatus.Success

    diag = s.diagnose()
    assert diag.dof == 0
    assert abs(s.get_param(param) - 3.0) < 1e-8


# ── Multiple reference constraints ────────────────────────────────


def test_multiple_reference_constraints_dof():
    """Multiple reference constraints don't inflate DOF."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_fixed_point(3, 4)
    p3 = s.add_fixed_point(6, 0)

    d12 = s.add_param()
    d23 = s.add_param()
    d13 = s.add_param()

    s.p2p_distance(p1, p2, d12, driving=False)
    s.p2p_distance(p2, p3, d23, driving=False)
    s.p2p_distance(p1, p3, d13, driving=False)

    status = s.solve()
    assert status == SolveStatus.Success

    diag = s.diagnose()
    assert diag.dof == 0

    assert abs(s.get_param(d12) - 5.0) < 1e-8
    assert abs(s.get_param(d23) - math.sqrt(9 + 16)) < 1e-8
    assert abs(s.get_param(d13) - 6.0) < 1e-8


def test_mixed_driving_and_reference_dof():
    """Mix of driving and reference constraints: DOF only from geometry."""
    s = Sketch()
    p1 = s.add_fixed_point(0, 0)
    p2 = s.add_point(5, 0)
    # Drive: fix horizontal
    line = s.add_line(p1, p2)
    s.horizontal(line)
    # Drive: set distance to 5
    s.set_p2p_distance(p1, p2, 5.0, driving=True)
    # Reference: read angle
    angle_param = s.add_param()
    s.p2p_angle(p1, p2, angle_param, driving=False)

    status = s.solve()
    assert status == SolveStatus.Success

    diag = s.diagnose()
    assert diag.dof == 0  # fully constrained by driving constraints
    assert abs(s.get_param(angle_param) - 0.0) < 1e-8  # horizontal → angle ≈ 0


# ── Circle radius/diameter reference constraints ──────────────────


def test_reference_circle_radius_fixed_param():
    """Reference circle_radius with fixed radius param reads back radius."""
    s = Sketch()
    point = s.add_fixed_point(0, 0)
    radius = s.add_fixed_param(50)
    circle = s.add_circle(point, radius)
    ref = s.add_param()
    s.circle_radius(circle, ref, driving=False)

    assert s.diagnose().dof == 0
    assert s.solve() == SolveStatus.Success
    assert abs(s.get_param(ref) - 50.0) < 1e-8


def test_reference_circle_diameter_fixed_param():
    """Reference circle_diameter with fixed radius param reads back diameter.

    This is a regression test: the solver previously failed due to an
    incorrect gradient in ConstraintEqual when ratio != 1.0.
    """
    s = Sketch()
    point = s.add_fixed_point(0, 0)
    radius = s.add_fixed_param(50)
    circle = s.add_circle(point, radius)
    ref = s.add_param()
    s.circle_diameter(circle, ref, driving=False)

    assert s.diagnose().dof == 0
    assert s.solve() == SolveStatus.Success
    assert abs(s.get_param(ref) - 100.0) < 1e-8


def test_reference_circle_diameter_with_driving_radius():
    """Reference circle_diameter when radius is set via a driving constraint.

    This is a regression test: the parameter reduction step previously
    treated proportional ConstraintEqual (ratio != 1.0) as a simple
    equality, causing the diameter to be reported as the radius value.
    """
    s = Sketch()
    point = s.add_fixed_point(0, 0)
    radius = s.add_param()
    circle = s.add_circle(point, radius)
    s.set_circle_radius(circle, 50)
    ref = s.add_param()
    s.circle_diameter(circle, ref, driving=False)

    assert s.diagnose().dof == 0
    assert s.solve() == SolveStatus.Success
    assert abs(s.get_param(ref) - 100.0) < 1e-8


def test_driving_circle_diameter_sets_radius():
    """Driving circle_diameter correctly sets the radius to half the diameter."""
    s = Sketch()
    point = s.add_fixed_point(0, 0)
    radius = s.add_param(10)
    circle = s.add_circle(point, radius)
    s.set_circle_diameter(circle, 80)

    assert s.solve() == SolveStatus.Success
    assert abs(s.get_param(radius) - 40.0) < 1e-8


def test_reference_arc_diameter():
    """Reference arc_diameter reads back correct diameter."""
    s = Sketch()
    center = s.add_fixed_point(0, 0)
    start = s.add_fixed_point(30, 0)
    end = s.add_fixed_point(0, 30)
    arc = s.add_arc_cse(center, start, end, radius=30, start_angle=0, end_angle=math.pi / 2)
    ref = s.add_param()
    s.arc_diameter(arc, ref, driving=False)

    assert s.solve() == SolveStatus.Success
    assert abs(s.get_param(ref) - 60.0) < 1e-8
