#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "wrapper.h"

namespace py = pybind11;

PYBIND11_MODULE(_planegcs, m) {
    m.doc() = "Python bindings for FreeCAD's PlaneGCS 2D geometric constraint solver";

    // Enums
    py::enum_<GCS::SolveStatus>(m, "SolveStatus")
        .value("Success", GCS::Success)
        .value("Converged", GCS::Converged)
        .value("Failed", GCS::Failed)
        .value("SuccessfulSolutionInvalid", GCS::SuccessfulSolutionInvalid)
        .export_values();

    py::enum_<GCS::Algorithm>(m, "Algorithm")
        .value("BFGS", GCS::BFGS)
        .value("LevenbergMarquardt", GCS::LevenbergMarquardt)
        .value("DogLeg", GCS::DogLeg)
        .export_values();

    py::enum_<GCS::DebugMode>(m, "DebugMode")
        .value("NoDebug", GCS::NoDebug)
        .value("Minimal", GCS::Minimal)
        .value("IterationLevel", GCS::IterationLevel)
        .export_values();

    py::enum_<GCS::InternalAlignmentType>(m, "InternalAlignmentType")
        .value("EllipsePositiveMajorX", GCS::EllipsePositiveMajorX)
        .value("EllipsePositiveMajorY", GCS::EllipsePositiveMajorY)
        .value("EllipseNegativeMajorX", GCS::EllipseNegativeMajorX)
        .value("EllipseNegativeMajorY", GCS::EllipseNegativeMajorY)
        .value("EllipsePositiveMinorX", GCS::EllipsePositiveMinorX)
        .value("EllipsePositiveMinorY", GCS::EllipsePositiveMinorY)
        .value("EllipseNegativeMinorX", GCS::EllipseNegativeMinorX)
        .value("EllipseNegativeMinorY", GCS::EllipseNegativeMinorY)
        .value("EllipseFocus2X", GCS::EllipseFocus2X)
        .value("EllipseFocus2Y", GCS::EllipseFocus2Y)
        .value("HyperbolaPositiveMajorX", GCS::HyperbolaPositiveMajorX)
        .value("HyperbolaPositiveMajorY", GCS::HyperbolaPositiveMajorY)
        .value("HyperbolaNegativeMajorX", GCS::HyperbolaNegativeMajorX)
        .value("HyperbolaNegativeMajorY", GCS::HyperbolaNegativeMajorY)
        .value("HyperbolaPositiveMinorX", GCS::HyperbolaPositiveMinorX)
        .value("HyperbolaPositiveMinorY", GCS::HyperbolaPositiveMinorY)
        .value("HyperbolaNegativeMinorX", GCS::HyperbolaNegativeMinorX)
        .value("HyperbolaNegativeMinorY", GCS::HyperbolaNegativeMinorY)
        .export_values();

    py::class_<SketchSolver::DiagnosisResult>(m, "DiagnosisResult")
        .def_readonly("dof", &SketchSolver::DiagnosisResult::dof,
                      "Degrees of freedom. 0 = fully constrained, >0 = under-constrained.")
        .def_readonly("conflicting", &SketchSolver::DiagnosisResult::conflicting,
                      "Tags of conflicting (over-constraining) constraints.")
        .def_readonly("redundant", &SketchSolver::DiagnosisResult::redundant,
                      "Tags of redundant constraints.")
        .def_readonly("partially_redundant", &SketchSolver::DiagnosisResult::partially_redundant,
                      "Tags of partially redundant constraints.")
    ;

    // SketchSolver class
    py::class_<SketchSolver>(m, "SketchSolver")
        .def(py::init<>())

        // Parameters
        .def("add_param", &SketchSolver::add_param, py::arg("value") = 0.0, py::arg("fixed") = false,
             "Allocate a parameter. fixed=True for driving constraint values. Returns param ID.")
        .def("is_param_fixed", &SketchSolver::is_param_fixed, py::arg("param_id"),
             "Check if a parameter is fixed (not an unknown).")
        .def("set_param_fixed", &SketchSolver::set_param_fixed, py::arg("param_id"), py::arg("fixed"),
             "Set whether a parameter is fixed.")
        .def("get_param", &SketchSolver::get_param, py::arg("param_id"),
             "Get the current value of a parameter.")
        .def("set_param", &SketchSolver::set_param, py::arg("param_id"), py::arg("value"),
             "Set the value of a parameter.")

        // Geometry: Points
        .def("add_point", &SketchSolver::add_point, py::arg("x"), py::arg("y"),
             "Add a point. Returns point ID.")
        .def("get_point", &SketchSolver::get_point, py::arg("point_id"),
             "Get the (x, y) of a point.")

        // Geometry: Lines
        .def("add_line", py::overload_cast<int, int>(&SketchSolver::add_line),
             py::arg("p1_id"), py::arg("p2_id"),
             "Add a line between two existing points. Returns line ID.")
        .def("add_line", py::overload_cast<double, double, double, double>(&SketchSolver::add_line),
             py::arg("x1"), py::arg("y1"), py::arg("x2"), py::arg("y2"),
             "Add a line with endpoint coordinates. Returns line ID.")

        // Geometry: Line accessors
        .def("get_line_p1", &SketchSolver::get_line_p1, py::arg("line_id"))
        .def("get_line_p2", &SketchSolver::get_line_p2, py::arg("line_id"))

        // Geometry: Circles
        .def("add_circle", &SketchSolver::add_circle,
             py::arg("center_id"), py::arg("radius"),
             "Add a circle. Returns circle ID.")

        // Geometry: Circle accessors
        .def("get_circle_center", &SketchSolver::get_circle_center, py::arg("circle_id"))
        .def("get_circle_radius", &SketchSolver::get_circle_radius, py::arg("circle_id"))

        // Geometry: Arcs
        .def("add_arc_from_center", &SketchSolver::add_arc_from_center,
             py::arg("center_id"), py::arg("radius"),
             py::arg("start_angle"), py::arg("end_angle"),
             "Add an arc from center point, radius and angles. Returns arc ID.")
        .def("add_arc_from_start_end", &SketchSolver::add_arc_from_start_end,
             py::arg("start_id"), py::arg("end_id"), py::arg("radius_id"),
             "Add an arc from start/end points and a radius parameter. Automatically adds arc rules and coincident constraints. Returns arc ID.")

        // Geometry: Arc accessors (used internally by Sketch.get_arc())
        .def("get_arc_center", &SketchSolver::get_arc_center, py::arg("arc_id"))
        .def("get_arc_radius", &SketchSolver::get_arc_radius, py::arg("arc_id"))
        .def("get_arc_start_angle", &SketchSolver::get_arc_start_angle, py::arg("arc_id"))
        .def("get_arc_end_angle", &SketchSolver::get_arc_end_angle, py::arg("arc_id"))
        .def("get_arc_start_point", &SketchSolver::get_arc_start_point, py::arg("arc_id"))
        .def("get_arc_end_point", &SketchSolver::get_arc_end_point, py::arg("arc_id"))

        // Geometry: Ellipses
        .def("add_ellipse", &SketchSolver::add_ellipse,
             py::arg("center_id"), py::arg("focus1_id"), py::arg("radmin"),
             "Add an ellipse. Returns ellipse ID.")

        // Geometry: Ellipse accessors
        .def("get_ellipse_center", &SketchSolver::get_ellipse_center, py::arg("ellipse_id"))
        .def("get_ellipse_focus1", &SketchSolver::get_ellipse_focus1, py::arg("ellipse_id"))
        .def("get_ellipse_radmin", &SketchSolver::get_ellipse_radmin, py::arg("ellipse_id"))

        // Geometry: ArcOfEllipse
        .def("add_arc_of_ellipse", &SketchSolver::add_arc_of_ellipse,
             py::arg("center_id"), py::arg("focus1_id"), py::arg("radmin"),
             py::arg("start_angle"), py::arg("end_angle"),
             py::arg("start_id"), py::arg("end_id"),
             "Add an arc of ellipse. Returns ID.")

        // Geometry: Hyperbola
        .def("add_hyperbola", &SketchSolver::add_hyperbola,
             py::arg("center_id"), py::arg("focus1_id"), py::arg("radmin"),
             "Add a hyperbola. Returns ID.")

        // Geometry: ArcOfHyperbola
        .def("add_arc_of_hyperbola", &SketchSolver::add_arc_of_hyperbola,
             py::arg("center_id"), py::arg("focus1_id"), py::arg("radmin"),
             py::arg("start_angle"), py::arg("end_angle"),
             py::arg("start_id"), py::arg("end_id"),
             "Add an arc of hyperbola. Returns ID.")

        // Geometry: Parabola
        .def("add_parabola", &SketchSolver::add_parabola,
             py::arg("vertex_id"), py::arg("focus1_id"),
             "Add a parabola. Returns ID.")

        // Geometry: ArcOfParabola
        .def("add_arc_of_parabola", &SketchSolver::add_arc_of_parabola,
             py::arg("vertex_id"), py::arg("focus1_id"),
             py::arg("start_angle"), py::arg("end_angle"),
             py::arg("start_id"), py::arg("end_id"),
             "Add an arc of parabola. Returns ID.")

        // Solving
        .def("solve", &SketchSolver::solve,
             py::arg("algorithm") = GCS::DogLeg,
             "Solve the system. Returns SolveStatus.")
        .def("dof", &SketchSolver::dof,
             "Return degrees of freedom after running diagnosis. 0 = fully constrained, >0 = under-constrained.")
        .def("diagnose", &SketchSolver::diagnose,
             py::arg("algorithm") = GCS::DogLeg,
             "Run full diagnosis. Returns DiagnosisResult with dof, conflicting, redundant, and partially_redundant constraint tags.")
        .def("clear", &SketchSolver::clear,
             "Clear all geometry, constraints, and parameters.")

        // Constraints
        .def("coincident", &SketchSolver::coincident,
             py::arg("pt1_id"), py::arg("pt2_id"), py::arg("driving") = true,
             "Add coincident constraint between two points.")
        .def("equal", &SketchSolver::equal,
             py::arg("param1_id"), py::arg("param2_id"), py::arg("driving") = true,
             "Add equality constraint between two parameters.")
        .def("proportional", &SketchSolver::proportional,
             py::arg("param1_id"), py::arg("param2_id"), py::arg("ratio"),
             py::arg("driving") = true,
             "Add proportional constraint.")
        .def("difference", &SketchSolver::difference,
             py::arg("param1_id"), py::arg("param2_id"), py::arg("diff_id"),
             py::arg("driving") = true,
             "Add difference constraint.")
        .def("p2p_distance", &SketchSolver::p2p_distance,
             py::arg("pt1_id"), py::arg("pt2_id"), py::arg("distance_id"),
             py::arg("driving") = true,
             "Add point-to-point distance constraint.")
        .def("p2p_angle", &SketchSolver::p2p_angle,
             py::arg("pt1_id"), py::arg("pt2_id"), py::arg("angle_id"),
             py::arg("driving") = true,
             "Add point-to-point angle constraint.")
        .def("p2l_distance", &SketchSolver::p2l_distance,
             py::arg("pt_id"), py::arg("line_id"), py::arg("distance_id"),
             py::arg("driving") = true,
             "Add point-to-line distance constraint.")
        .def("point_on_line", &SketchSolver::point_on_line,
             py::arg("pt_id"), py::arg("line_id"), py::arg("driving") = true,
             "Constrain point to lie on line.")
        .def("point_on_perp_bisector", &SketchSolver::point_on_perp_bisector,
             py::arg("pt_id"), py::arg("line_id"), py::arg("driving") = true,
             "Constrain point to lie on perpendicular bisector of line.")
        .def("parallel", &SketchSolver::parallel,
             py::arg("l1_id"), py::arg("l2_id"), py::arg("driving") = true,
             "Add parallel constraint.")
        .def("perpendicular", &SketchSolver::perpendicular,
             py::arg("l1_id"), py::arg("l2_id"), py::arg("driving") = true,
             "Add perpendicular constraint.")
        .def("l2l_angle", &SketchSolver::l2l_angle,
             py::arg("l1_id"), py::arg("l2_id"), py::arg("angle_id"),
             py::arg("driving") = true,
             "Add line-to-line angle constraint.")
        .def("midpoint_on_line", &SketchSolver::midpoint_on_line,
             py::arg("l1_id"), py::arg("l2_id"), py::arg("driving") = true,
             "Constrain midpoint of l1 to lie on l2.")
        .def("horizontal_line", &SketchSolver::horizontal_line,
             py::arg("line_id"), py::arg("driving") = true,
             "Constrain line to be horizontal.")
        .def("horizontal_points", &SketchSolver::horizontal_points,
             py::arg("p1_id"), py::arg("p2_id"), py::arg("driving") = true,
             "Constrain two points to have same Y.")
        .def("vertical_line", &SketchSolver::vertical_line,
             py::arg("line_id"), py::arg("driving") = true,
             "Constrain line to be vertical.")
        .def("vertical_points", &SketchSolver::vertical_points,
             py::arg("p1_id"), py::arg("p2_id"), py::arg("driving") = true,
             "Constrain two points to have same X.")
        .def("coordinate_x", &SketchSolver::coordinate_x,
             py::arg("pt_id"), py::arg("x_id"), py::arg("driving") = true,
             "Fix the X coordinate of a point.")
        .def("coordinate_y", &SketchSolver::coordinate_y,
             py::arg("pt_id"), py::arg("y_id"), py::arg("driving") = true,
             "Fix the Y coordinate of a point.")
        .def("point_on_circle", &SketchSolver::point_on_circle,
             py::arg("pt_id"), py::arg("circle_id"), py::arg("driving") = true,
             "Constrain point to lie on circle.")
        .def("point_on_ellipse", &SketchSolver::point_on_ellipse,
             py::arg("pt_id"), py::arg("ellipse_id"), py::arg("driving") = true,
             "Constrain point to lie on ellipse.")
        .def("point_on_arc", &SketchSolver::point_on_arc,
             py::arg("pt_id"), py::arg("arc_id"), py::arg("driving") = true,
             "Constrain point to lie on arc.")
        .def("arc_rules", &SketchSolver::arc_rules,
             py::arg("arc_id"), py::arg("driving") = true,
             "Add arc rules constraint (start/end computed from center+radius+angles).")
        .def("tangent_line_circle", &SketchSolver::tangent_line_circle,
             py::arg("line_id"), py::arg("circle_id"), py::arg("driving") = true,
             "Add line-circle tangent constraint.")
        .def("tangent_line_ellipse", &SketchSolver::tangent_line_ellipse,
             py::arg("line_id"), py::arg("ellipse_id"), py::arg("driving") = true,
             "Add line-ellipse tangent constraint.")
        .def("tangent_line_arc", &SketchSolver::tangent_line_arc,
             py::arg("line_id"), py::arg("arc_id"), py::arg("driving") = true,
             "Add line-arc tangent constraint.")
        .def("tangent_circle_circle", &SketchSolver::tangent_circle_circle,
             py::arg("c1_id"), py::arg("c2_id"), py::arg("driving") = true,
             "Add circle-circle tangent constraint.")
        .def("tangent_arc_arc", &SketchSolver::tangent_arc_arc,
             py::arg("a1_id"), py::arg("a2_id"), py::arg("driving") = true,
             "Add arc-arc tangent constraint.")
        .def("tangent_circle_arc", &SketchSolver::tangent_circle_arc,
             py::arg("circle_id"), py::arg("arc_id"), py::arg("driving") = true,
             "Add circle-arc tangent constraint.")
        .def("circle_radius", &SketchSolver::circle_radius,
             py::arg("circle_id"), py::arg("radius_id"), py::arg("driving") = true,
             "Set circle radius.")
        .def("arc_radius", &SketchSolver::arc_radius,
             py::arg("arc_id"), py::arg("radius_id"), py::arg("driving") = true,
             "Set arc radius.")
        .def("circle_diameter", &SketchSolver::circle_diameter,
             py::arg("circle_id"), py::arg("diameter_id"), py::arg("driving") = true,
             "Set circle diameter.")
        .def("arc_diameter", &SketchSolver::arc_diameter,
             py::arg("arc_id"), py::arg("diameter_id"), py::arg("driving") = true,
             "Set arc diameter.")
        .def("equal_length", &SketchSolver::equal_length,
             py::arg("l1_id"), py::arg("l2_id"), py::arg("driving") = true,
             "Constrain two lines to have equal length.")
        .def("equal_radius_cc", &SketchSolver::equal_radius_cc,
             py::arg("c1_id"), py::arg("c2_id"), py::arg("driving") = true,
             "Constrain two circles to have equal radius.")
        .def("equal_radius_ca", &SketchSolver::equal_radius_ca,
             py::arg("circle_id"), py::arg("arc_id"), py::arg("driving") = true,
             "Constrain circle and arc to have equal radius.")
        .def("equal_radius_aa", &SketchSolver::equal_radius_aa,
             py::arg("a1_id"), py::arg("a2_id"), py::arg("driving") = true,
             "Constrain two arcs to have equal radius.")
        .def("symmetric_points_line", &SketchSolver::symmetric_points_line,
             py::arg("p1_id"), py::arg("p2_id"), py::arg("line_id"),
             py::arg("driving") = true,
             "Constrain points symmetric about a line.")
        .def("symmetric_points_point", &SketchSolver::symmetric_points_point,
             py::arg("p1_id"), py::arg("p2_id"), py::arg("center_id"),
             py::arg("driving") = true,
             "Constrain points symmetric about a center point.")
        .def("p2c_distance", &SketchSolver::p2c_distance,
             py::arg("pt_id"), py::arg("circle_id"), py::arg("distance_id"),
             py::arg("driving") = true,
             "Add point-to-circle distance constraint.")
        .def("c2c_distance", &SketchSolver::c2c_distance,
             py::arg("c1_id"), py::arg("c2_id"), py::arg("dist_id"),
             py::arg("driving") = true,
             "Add circle-to-circle distance constraint.")
        .def("c2l_distance", &SketchSolver::c2l_distance,
             py::arg("circle_id"), py::arg("line_id"), py::arg("dist_id"),
             py::arg("driving") = true,
             "Add circle-to-line distance constraint.")
        .def("arc_length", &SketchSolver::arc_length,
             py::arg("arc_id"), py::arg("dist_id"), py::arg("driving") = true,
             "Constrain arc length.")
        .def("internal_alignment_point2ellipse", &SketchSolver::internal_alignment_point2ellipse,
             py::arg("ellipse_id"), py::arg("pt_id"), py::arg("alignment_type"),
             py::arg("driving") = true,
             "Internal alignment: point to ellipse.")
        .def("tangent_circumf", &SketchSolver::tangent_circumf,
             py::arg("p1_id"), py::arg("p2_id"),
             py::arg("rd1_id"), py::arg("rd2_id"),
             py::arg("internal") = false, py::arg("driving") = true,
             "Tangent circumference constraint.")
        .def("clear_by_tag", &SketchSolver::clear_by_tag, py::arg("tag"),
             "Clear all constraints with the given tag.")
        .def("constraint_error", &SketchSolver::constraint_error, py::arg("tag"),
             "Calculate RMS error of all constraints with given tag.")
    ;
}
