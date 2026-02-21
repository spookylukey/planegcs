"""Reproduce a FreeCAD Sketch tangent constraint between an arc and a line.

This recreates the following fully-constrained FreeCAD sketch (DOF = 0):

  Geometry:
    Geo 0: Arc   - center (-20,20), R=20, startAngle=0, endAngle=3π/2
                   start point (0,20), end point (-20,0)
    Geo 1: Line  - from (0,0) up to (0,20)           [vertical]
    Geo 2: Line  - from (0,0) left to (-20,0)         [horizontal]

  Constraints:
    [0] Vertical:      Line1
    [1] Coincident:    Line2.start = Line1.start       (origin)
    [2] Horizontal:    Line2
    [3] Coincident:    Arc.end = Line2.end              (-20, 0)
    [4] PointOnObject: Line1.start on Y-axis           (x = 0)
    [5] Equal:         Line1 length = Line2 length
    [6] DistanceY:     |Line1| = 20 mm
    [7] Tangent:       Line1.end ↔ Arc.start           (endpoint-to-endpoint)
    [8] PointOnObject: Arc.end on X-axis               (y = 0)

The tangent constraint (type 5) is stored with Value = -π/2 in FreeCAD.
This is NOT the raw angle -- FreeCAD uses an offset encoding:

    actual_angle = stored_value - angleOffset
    angleOffset  = -π/2   (for Tangent)
    actual_angle = -π/2 - (-π/2) = 0

An actual angle of 0 means the tangent vectors of the two curves are
aligned, i.e. the curves are tangent.

In planegcs the endpoint-to-endpoint tangent becomes:
  1. Share the point (or add a coincident constraint)
  2. set_angle_via_point(crv1, crv2, shared_point, 0.0)
"""

import math

from planegcs import Sketch, SolveStatus


def main() -> None:
    s = Sketch()

    # ── Shared points ──────────────────────────────────────────────
    # FreeCAD coincident constraints collapse to shared points here.
    origin = s.add_point(0.0, 0.0)  # Line1.start = Line2.start
    tangent_pt = s.add_point(0.0, 20.0)  # Line1.end   = Arc.start
    corner_pt = s.add_point(-20.0, 0.0)  # Line2.end   = Arc.end

    # ── Geometry ───────────────────────────────────────────────────
    # Arc: center at (-20, 20), radius 20, from 0 to 3π/2.
    # add_arc takes explicit center/start/end points + params;
    # arc-rules are applied automatically.
    arc_center = s.add_point(-20.0, 20.0)
    arc = s.add_arc_cse(arc_center, tangent_pt, corner_pt, 20.0, 0.0, 3 * math.pi / 2)

    line1 = s.add_line(origin, tangent_pt)
    line2 = s.add_line(origin, corner_pt)

    # ── Constraints ───────────────────────────────────────────────
    s.vertical(line1)  # [0] Line1 is vertical
    s.horizontal(line2)  # [2] Line2 is horizontal
    s.fix_point(origin, 0.0, 0.0)  # [1,4] origin at (0,0)
    s.equal_length(line1, line2)  # [5] same length
    s.set_p2p_distance(origin, tangent_pt, 20.0)  # [6] length = 20

    # [7] Tangent (endpoint-to-endpoint)
    # The coincident part is handled by sharing tangent_pt between
    # the line and arc.  We just need the angle-via-point = 0:
    s.set_angle_via_point(line1, arc, tangent_pt, 0.0)

    # [8] Arc end on X-axis
    y_zero = s.add_param(0.0, fixed=True)
    s.coordinate_y(corner_pt, y_zero)

    # ── Diagnose ──────────────────────────────────────────────────
    diag = s.diagnose()
    print(f"DOF: {diag.dof}")
    assert diag.dof == 0, f"expected DOF=0, got {diag.dof}"
    assert not diag.conflicting, f"conflicting: {diag.conflicting}"

    # ── Solve ─────────────────────────────────────────────────────
    status = s.solve()
    print(f"Solve: {status}")
    assert status in (SolveStatus.Success, SolveStatus.Converged)

    # ── Verify results ────────────────────────────────────────────
    l1 = s.get_line(line1)
    l2 = s.get_line(line2)
    ai = s.get_arc(arc)

    print(f"Line1: ({l1.p1[0]:.1f},{l1.p1[1]:.1f}) → ({l1.p2[0]:.1f},{l1.p2[1]:.1f})")
    print(f"Line2: ({l2.p1[0]:.1f},{l2.p1[1]:.1f}) → ({l2.p2[0]:.1f},{l2.p2[1]:.1f})")
    print(f"Arc:   center=({ai.center[0]:.1f},{ai.center[1]:.1f}) r={ai.radius:.1f}")
    print(
        f"       start=({ai.start_point[0]:.1f},{ai.start_point[1]:.1f})"
        f" end=({ai.end_point[0]:.1f},{ai.end_point[1]:.1f})"
    )

    angle = s.calculate_angle_via_point(line1, arc, tangent_pt)
    print(f"Tangent angle: {angle:.6f} rad (0 = tangent)")

    # Check geometry matches expected values
    assert math.isclose(l1.p1[0], 0.0, abs_tol=1e-6)
    assert math.isclose(l1.p1[1], 0.0, abs_tol=1e-6)
    assert math.isclose(l1.p2[0], 0.0, abs_tol=1e-6)
    assert math.isclose(l1.p2[1], 20.0, abs_tol=1e-6)
    assert math.isclose(l2.p2[0], -20.0, abs_tol=1e-6)
    assert math.isclose(l2.p2[1], 0.0, abs_tol=1e-6)
    assert math.isclose(ai.center[0], -20.0, abs_tol=1e-6)
    assert math.isclose(ai.center[1], 20.0, abs_tol=1e-6)
    assert math.isclose(ai.radius, 20.0, abs_tol=1e-6)
    assert math.isclose(angle, 0.0, abs_tol=1e-6)

    print("\n✓ All assertions passed.")


if __name__ == "__main__":
    main()
