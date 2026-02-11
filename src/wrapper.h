#ifndef PLANEGCS_WRAPPER_H
#define PLANEGCS_WRAPPER_H

#include "planegcs/GCS.h"
#include "planegcs/Geo.h"
#include "planegcs/Constraints.h"

#include <deque>
#include <map>
#include <stdexcept>
#include <vector>
#include <variant>
#include <cmath>

class SketchSolver {
public:
    SketchSolver() = default;
    ~SketchSolver() = default;

    // ── Parameter allocation ──────────────────────────────────────────
    // Every double* the GCS needs is allocated here for pointer stability.
    // fixed=false: geometry params (unknowns, adjusted by solver)
    // fixed=true:  constraint value params (driving values, not adjusted)
    int add_param(double value, bool fixed = false) {
        int id = next_param_id_++;
        params_.push_back(value);
        size_t idx = params_.size() - 1;
        param_index_[id] = idx;
        param_fixed_[id] = fixed;
        return id;
    }

    double get_param(int id) const {
        return params_[param_index_.at(id)];
    }

    void set_param(int id, double value) {
        params_[param_index_.at(id)] = value;
    }

    bool is_param_fixed(int id) const {
        auto it = param_fixed_.find(id);
        return it != param_fixed_.end() && it->second;
    }

    void set_param_fixed(int id, bool fixed) {
        param_fixed_[id] = fixed;
    }

    double* param_ptr(int id) {
        return &params_[param_index_.at(id)];
    }

    // ── Geometry: Points ──────────────────────────────────────────────
    int add_point(double x, double y) {
        int px = add_param(x);
        int py = add_param(y);
        int id = next_geo_id_++;
        GCS::Point p;
        p.x = param_ptr(px);
        p.y = param_ptr(py);
        points_[id] = p;
        point_param_ids_[id] = {px, py};
        return id;
    }

    std::pair<double, double> get_point(int id) const {
        auto& p = points_.at(id);
        return {*p.x, *p.y};
    }

    // ── Geometry: Lines ──────────────────────────────────────────────
    int add_line(int p1_id, int p2_id) {
        int id = next_geo_id_++;
        GCS::Line l;
        l.p1 = points_.at(p1_id);
        l.p2 = points_.at(p2_id);
        lines_[id] = l;
        return id;
    }

    // Convenience: add_line with coordinates
    int add_line(double x1, double y1, double x2, double y2) {
        int p1 = add_point(x1, y1);
        int p2 = add_point(x2, y2);
        return add_line(p1, p2);
    }

    // ── Geometry: Circles ────────────────────────────────────────────
    int add_circle(int center_id, double radius) {
        int rad_id = add_param(radius);
        int id = next_geo_id_++;
        GCS::Circle c;
        c.center = points_.at(center_id);
        c.rad = param_ptr(rad_id);
        circles_[id] = c;
        circle_rad_param_[id] = rad_id;
        return id;
    }

    // ── Geometry: Arcs ──────────────────────────────────────────────
    int add_arc_from_center(int center_id, double radius, double start_angle, double end_angle) {
        int rad_id = add_param(radius);
        int sa_id = add_param(start_angle);
        int ea_id = add_param(end_angle);
        // start/end points (computed by arc rules)
        double cx = *points_.at(center_id).x;
        double cy = *points_.at(center_id).y;
        int sp = add_point(cx + radius * cos(start_angle), cy + radius * sin(start_angle));
        int ep = add_point(cx + radius * cos(end_angle), cy + radius * sin(end_angle));

        int id = next_geo_id_++;
        GCS::Arc a;
        a.center = points_.at(center_id);
        a.rad = param_ptr(rad_id);
        a.startAngle = param_ptr(sa_id);
        a.endAngle = param_ptr(ea_id);
        a.start = points_.at(sp);
        a.end = points_.at(ep);
        arcs_[id] = a;
        return id;
    }

    int add_arc_from_start_end(int start_id, int end_id, int radius_id) {
        // get start/end coords
        double sx = *points_.at(start_id).x;
        double sy = *points_.at(start_id).y;
        double ex = *points_.at(end_id).x;
        double ey = *points_.at(end_id).y;

        double dx = ex - sx;
        double dy = ey - sy;
        double half_chord = std::sqrt(dx*dx + dy*dy) / 2.0;

        // Read radius from the user-provided parameter
        double r = std::abs(*param_ptr(radius_id));
        if (r < half_chord) r = half_chord;

        double h = std::sqrt(r*r - half_chord*half_chord);

        // Midpoint
        double mx = (sx + ex) / 2.0;
        double my = (sy + ey) / 2.0;

        // Perpendicular direction (normalized), choosing left side for CCW
        double perp_x = -dy / (2.0 * half_chord);
        double perp_y =  dx / (2.0 * half_chord);

        // Center
        double cx = mx + h * perp_x;
        double cy = my + h * perp_y;

        int center = add_point(cx, cy);

        double start_angle = std::atan2(sy - cy, sx - cx);
        double end_angle = std::atan2(ey - cy, ex - cx);

        int rad_id = radius_id;
        int sa_id = add_param(start_angle);
        int ea_id = add_param(end_angle);

        // Create arc start/end points (these are the arc's internal computed points)
        int sp = add_point(sx, sy);
        int ep = add_point(ex, ey);

        int id = next_geo_id_++;
        GCS::Arc a;
        a.center = points_.at(center);
        a.rad = param_ptr(rad_id);
        a.startAngle = param_ptr(sa_id);
        a.endAngle = param_ptr(ea_id);
        a.start = points_.at(sp);
        a.end = points_.at(ep);
        arcs_[id] = a;

        // Add arc rules so start/end are computed from center+radius+angles
        arc_rules(id);

        // Coincident: arc's start/end match the user-provided points
        coincident(sp, start_id);
        coincident(ep, end_id);

        return id;
    }

    // ── Geometry: Arc accessors ───────────────────────────────────────
    std::pair<double, double> get_arc_center(int arc_id) const {
        auto& a = arcs_.at(arc_id);
        return {*a.center.x, *a.center.y};
    }

    double get_arc_radius(int arc_id) const {
        return *arcs_.at(arc_id).rad;
    }

    double get_arc_start_angle(int arc_id) const {
        return *arcs_.at(arc_id).startAngle;
    }

    double get_arc_end_angle(int arc_id) const {
        return *arcs_.at(arc_id).endAngle;
    }

    std::pair<double, double> get_arc_start_point(int arc_id) const {
        auto& a = arcs_.at(arc_id);
        return {*a.start.x, *a.start.y};
    }

    std::pair<double, double> get_arc_end_point(int arc_id) const {
        auto& a = arcs_.at(arc_id);
        return {*a.end.x, *a.end.y};
    }

    // ── Geometry: Ellipses ───────────────────────────────────────────
    int add_ellipse(int center_id, int focus1_id, double radmin) {
        int rm_id = add_param(radmin);
        int id = next_geo_id_++;
        GCS::Ellipse e;
        e.center = points_.at(center_id);
        e.focus1 = points_.at(focus1_id);
        e.radmin = param_ptr(rm_id);
        ellipses_[id] = e;
        return id;
    }

    // ── Geometry: ArcOfEllipse ───────────────────────────────────────
    int add_arc_of_ellipse(int center_id, int focus1_id, double radmin,
                           double start_angle, double end_angle,
                           int start_id, int end_id) {
        int rm_id = add_param(radmin);
        int sa_id = add_param(start_angle);
        int ea_id = add_param(end_angle);
        int id = next_geo_id_++;
        GCS::ArcOfEllipse ae;
        ae.center = points_.at(center_id);
        ae.focus1 = points_.at(focus1_id);
        ae.radmin = param_ptr(rm_id);
        ae.startAngle = param_ptr(sa_id);
        ae.endAngle = param_ptr(ea_id);
        ae.start = points_.at(start_id);
        ae.end = points_.at(end_id);
        arcs_of_ellipse_[id] = ae;
        return id;
    }

    // ── Geometry: Hyperbola ──────────────────────────────────────────
    int add_hyperbola(int center_id, int focus1_id, double radmin) {
        int rm_id = add_param(radmin);
        int id = next_geo_id_++;
        GCS::Hyperbola h;
        h.center = points_.at(center_id);
        h.focus1 = points_.at(focus1_id);
        h.radmin = param_ptr(rm_id);
        hyperbolas_[id] = h;
        return id;
    }

    // ── Geometry: ArcOfHyperbola ─────────────────────────────────────
    int add_arc_of_hyperbola(int center_id, int focus1_id, double radmin,
                             double start_angle, double end_angle,
                             int start_id, int end_id) {
        int rm_id = add_param(radmin);
        int sa_id = add_param(start_angle);
        int ea_id = add_param(end_angle);
        int id = next_geo_id_++;
        GCS::ArcOfHyperbola ah;
        ah.center = points_.at(center_id);
        ah.focus1 = points_.at(focus1_id);
        ah.radmin = param_ptr(rm_id);
        ah.startAngle = param_ptr(sa_id);
        ah.endAngle = param_ptr(ea_id);
        ah.start = points_.at(start_id);
        ah.end = points_.at(end_id);
        arcs_of_hyperbola_[id] = ah;
        return id;
    }

    // ── Geometry: Parabola ───────────────────────────────────────────
    int add_parabola(int vertex_id, int focus1_id) {
        int id = next_geo_id_++;
        GCS::Parabola p;
        p.vertex = points_.at(vertex_id);
        p.focus1 = points_.at(focus1_id);
        parabolas_[id] = p;
        return id;
    }

    // ── Geometry: ArcOfParabola ──────────────────────────────────────
    int add_arc_of_parabola(int vertex_id, int focus1_id,
                            double start_angle, double end_angle,
                            int start_id, int end_id) {
        int sa_id = add_param(start_angle);
        int ea_id = add_param(end_angle);
        int id = next_geo_id_++;
        GCS::ArcOfParabola ap;
        ap.vertex = points_.at(vertex_id);
        ap.focus1 = points_.at(focus1_id);
        ap.startAngle = param_ptr(sa_id);
        ap.endAngle = param_ptr(ea_id);
        ap.start = points_.at(start_id);
        ap.end = points_.at(end_id);
        arcs_of_parabola_[id] = ap;
        return id;
    }

    // ── Solving ─────────────────────────────────────────────────────
    void declare_unknowns() {
        GCS::VEC_pD params;
        // Only non-fixed params are unknowns
        for (auto& [id, idx] : param_index_) {
            if (!is_param_fixed(id)) {
                params.push_back(&params_[idx]);
            }
        }
        system_.declareUnknowns(params);
    }

    void init_solution(GCS::Algorithm alg = GCS::DogLeg) {
        system_.initSolution(alg);
    }

    GCS::SolveStatus solve(GCS::Algorithm alg = GCS::DogLeg) {
        declare_unknowns();
        init_solution(alg);
        int status = system_.solve(true, alg);
        if (status == GCS::Success || status == GCS::Converged) {
            system_.applySolution();
        }
        return static_cast<GCS::SolveStatus>(status);
    }

    void apply_solution() {
        system_.applySolution();
    }

    struct DiagnosisResult {
        int dof;                          // degrees of freedom (0 = fully constrained)
        std::vector<int> conflicting;     // tags of conflicting (over-constraining) constraints
        std::vector<int> redundant;       // tags of redundant constraints
        std::vector<int> partially_redundant; // tags of partially redundant constraints
    };

    int dof() {
        declare_unknowns();
        init_solution();
        system_.diagnose();
        return system_.dofsNumber();
    }

    DiagnosisResult diagnose(GCS::Algorithm alg = GCS::DogLeg) {
        declare_unknowns();
        init_solution(alg);
        system_.diagnose(alg);

        DiagnosisResult result;
        result.dof = system_.dofsNumber();

        GCS::VEC_I tags;
        system_.getConflicting(tags);
        result.conflicting.assign(tags.begin(), tags.end());

        system_.getRedundant(tags);
        result.redundant.assign(tags.begin(), tags.end());

        system_.getPartiallyRedundant(tags);
        result.partially_redundant.assign(tags.begin(), tags.end());

        return result;
    }

    void clear() {
        system_.clear();
        params_.clear();
        param_index_.clear();
        param_fixed_.clear();
        points_.clear();
        point_param_ids_.clear();
        lines_.clear();
        circles_.clear();
        circle_rad_param_.clear();
        arcs_.clear();
        ellipses_.clear();
        arcs_of_ellipse_.clear();
        hyperbolas_.clear();
        arcs_of_hyperbola_.clear();
        parabolas_.clear();
        arcs_of_parabola_.clear();
        next_param_id_ = 0;
        next_geo_id_ = 0;
        next_constraint_tag_ = 1;
    }

    // ── Constraints ─────────────────────────────────────────────────
    // Each returns the tag assigned to this constraint.

    int coincident(int pt1_id, int pt2_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintP2PCoincident(
            points_.at(pt1_id), points_.at(pt2_id), tag, driving);
        return tag;
    }

    int equal(int param1_id, int param2_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintEqual(
            param_ptr(param1_id), param_ptr(param2_id), tag, driving);
        return tag;
    }

    int proportional(int param1_id, int param2_id, double ratio, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintProportional(
            param_ptr(param1_id), param_ptr(param2_id), ratio, tag, driving);
        return tag;
    }

    int difference(int param1_id, int param2_id, int diff_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintDifference(
            param_ptr(param1_id), param_ptr(param2_id), param_ptr(diff_id), tag, driving);
        return tag;
    }

    int p2p_distance(int pt1_id, int pt2_id, int distance_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintP2PDistance(
            points_.at(pt1_id), points_.at(pt2_id), param_ptr(distance_id), tag, driving);
        return tag;
    }

    int p2p_angle(int pt1_id, int pt2_id, int angle_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintP2PAngle(
            points_.at(pt1_id), points_.at(pt2_id), param_ptr(angle_id), tag, driving);
        return tag;
    }

    int p2p_angle_incr(int pt1_id, int pt2_id, int angle_id, double incr_angle, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintP2PAngle(
            points_.at(pt1_id), points_.at(pt2_id), param_ptr(angle_id), incr_angle, tag, driving);
        return tag;
    }

    int p2l_distance(int pt_id, int line_id, int distance_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintP2LDistance(
            points_.at(pt_id), lines_.at(line_id), param_ptr(distance_id), tag, driving);
        return tag;
    }

    int point_on_line(int pt_id, int line_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintPointOnLine(
            points_.at(pt_id), lines_.at(line_id), tag, driving);
        return tag;
    }

    int point_on_line_2pts(int pt_id, int lp1_id, int lp2_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintPointOnLine(
            points_.at(pt_id), points_.at(lp1_id), points_.at(lp2_id), tag, driving);
        return tag;
    }

    int point_on_perp_bisector(int pt_id, int line_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintPointOnPerpBisector(
            points_.at(pt_id), lines_.at(line_id), tag, driving);
        return tag;
    }

    int parallel(int l1_id, int l2_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintParallel(
            lines_.at(l1_id), lines_.at(l2_id), tag, driving);
        return tag;
    }

    int perpendicular(int l1_id, int l2_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintPerpendicular(
            lines_.at(l1_id), lines_.at(l2_id), tag, driving);
        return tag;
    }

    int l2l_angle(int l1_id, int l2_id, int angle_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintL2LAngle(
            lines_.at(l1_id), lines_.at(l2_id), param_ptr(angle_id), tag, driving);
        return tag;
    }

    int midpoint_on_line(int l1_id, int l2_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintMidpointOnLine(
            lines_.at(l1_id), lines_.at(l2_id), tag, driving);
        return tag;
    }

    int horizontal_line(int line_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintHorizontal(lines_.at(line_id), tag, driving);
        return tag;
    }

    int horizontal_points(int p1_id, int p2_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintHorizontal(
            points_.at(p1_id), points_.at(p2_id), tag, driving);
        return tag;
    }

    int vertical_line(int line_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintVertical(lines_.at(line_id), tag, driving);
        return tag;
    }

    int vertical_points(int p1_id, int p2_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintVertical(
            points_.at(p1_id), points_.at(p2_id), tag, driving);
        return tag;
    }

    int coordinate_x(int pt_id, int x_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintCoordinateX(
            points_.at(pt_id), param_ptr(x_id), tag, driving);
        return tag;
    }

    int coordinate_y(int pt_id, int y_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintCoordinateY(
            points_.at(pt_id), param_ptr(y_id), tag, driving);
        return tag;
    }

    int point_on_circle(int pt_id, int circle_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintPointOnCircle(
            points_.at(pt_id), circles_.at(circle_id), tag, driving);
        return tag;
    }

    int point_on_ellipse(int pt_id, int ellipse_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintPointOnEllipse(
            points_.at(pt_id), ellipses_.at(ellipse_id), tag, driving);
        return tag;
    }

    int point_on_arc(int pt_id, int arc_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintPointOnArc(
            points_.at(pt_id), arcs_.at(arc_id), tag, driving);
        return tag;
    }

    int arc_rules(int arc_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintArcRules(arcs_.at(arc_id), tag, driving);
        return tag;
    }

    int arc_of_ellipse_rules(int aoe_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintArcOfEllipseRules(arcs_of_ellipse_.at(aoe_id), tag, driving);
        return tag;
    }

    int arc_of_hyperbola_rules(int aoh_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintArcOfHyperbolaRules(arcs_of_hyperbola_.at(aoh_id), tag, driving);
        return tag;
    }

    int arc_of_parabola_rules(int aop_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintArcOfParabolaRules(arcs_of_parabola_.at(aop_id), tag, driving);
        return tag;
    }

    int tangent_line_circle(int line_id, int circle_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintTangent(
            lines_.at(line_id), circles_.at(circle_id), tag, driving);
        return tag;
    }

    int tangent_line_ellipse(int line_id, int ellipse_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintTangent(
            lines_.at(line_id), ellipses_.at(ellipse_id), tag, driving);
        return tag;
    }

    int tangent_line_arc(int line_id, int arc_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintTangent(
            lines_.at(line_id), arcs_.at(arc_id), tag, driving);
        return tag;
    }

    int tangent_circle_circle(int c1_id, int c2_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintTangent(
            circles_.at(c1_id), circles_.at(c2_id), tag, driving);
        return tag;
    }

    int tangent_arc_arc(int a1_id, int a2_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintTangent(
            arcs_.at(a1_id), arcs_.at(a2_id), tag, driving);
        return tag;
    }

    int tangent_circle_arc(int circle_id, int arc_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintTangent(
            circles_.at(circle_id), arcs_.at(arc_id), tag, driving);
        return tag;
    }

    int circle_radius(int circle_id, int radius_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintCircleRadius(
            circles_.at(circle_id), param_ptr(radius_id), tag, driving);
        return tag;
    }

    int arc_radius(int arc_id, int radius_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintArcRadius(
            arcs_.at(arc_id), param_ptr(radius_id), tag, driving);
        return tag;
    }

    int circle_diameter(int circle_id, int diameter_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintCircleDiameter(
            circles_.at(circle_id), param_ptr(diameter_id), tag, driving);
        return tag;
    }

    int arc_diameter(int arc_id, int diameter_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintArcDiameter(
            arcs_.at(arc_id), param_ptr(diameter_id), tag, driving);
        return tag;
    }

    int equal_length(int l1_id, int l2_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintEqualLength(
            lines_.at(l1_id), lines_.at(l2_id), tag, driving);
        return tag;
    }

    int equal_radius_cc(int c1_id, int c2_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintEqualRadius(
            circles_.at(c1_id), circles_.at(c2_id), tag, driving);
        return tag;
    }

    int equal_radius_ca(int circle_id, int arc_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintEqualRadius(
            circles_.at(circle_id), arcs_.at(arc_id), tag, driving);
        return tag;
    }

    int equal_radius_aa(int a1_id, int a2_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintEqualRadius(
            arcs_.at(a1_id), arcs_.at(a2_id), tag, driving);
        return tag;
    }

    int symmetric_points_line(int p1_id, int p2_id, int line_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintP2PSymmetric(
            points_.at(p1_id), points_.at(p2_id), lines_.at(line_id), tag, driving);
        return tag;
    }

    int symmetric_points_point(int p1_id, int p2_id, int center_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintP2PSymmetric(
            points_.at(p1_id), points_.at(p2_id), points_.at(center_id), tag, driving);
        return tag;
    }

    int p2p_coincident(int p1_id, int p2_id, bool driving = true) {
        return coincident(p1_id, p2_id, driving);
    }

    int p2c_distance(int pt_id, int circle_id, int distance_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintP2CDistance(
            points_.at(pt_id), circles_.at(circle_id), param_ptr(distance_id), tag, driving);
        return tag;
    }

    int c2c_distance(int c1_id, int c2_id, int dist_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintC2CDistance(
            circles_.at(c1_id), circles_.at(c2_id), param_ptr(dist_id), tag, driving);
        return tag;
    }

    int c2l_distance(int circle_id, int line_id, int dist_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintC2LDistance(
            circles_.at(circle_id), lines_.at(line_id), param_ptr(dist_id), tag, driving);
        return tag;
    }

    int arc_length(int arc_id, int dist_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintArcLength(
            arcs_.at(arc_id), param_ptr(dist_id), tag, driving);
        return tag;
    }

    // Internal alignment constraints
    int internal_alignment_point2ellipse(int ellipse_id, int pt_id,
                                         GCS::InternalAlignmentType alignmentType,
                                         bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintInternalAlignmentPoint2Ellipse(
            ellipses_.at(ellipse_id), points_.at(pt_id), alignmentType, tag, driving);
        return tag;
    }

    int internal_alignment_ellipse_major_diameter(int ellipse_id, int p1_id, int p2_id,
                                                   bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintInternalAlignmentEllipseMajorDiameter(
            ellipses_.at(ellipse_id), points_.at(p1_id), points_.at(p2_id), tag, driving);
        return tag;
    }

    int internal_alignment_ellipse_minor_diameter(int ellipse_id, int p1_id, int p2_id,
                                                   bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintInternalAlignmentEllipseMinorDiameter(
            ellipses_.at(ellipse_id), points_.at(p1_id), points_.at(p2_id), tag, driving);
        return tag;
    }

    int internal_alignment_ellipse_focus1(int ellipse_id, int pt_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintInternalAlignmentEllipseFocus1(
            ellipses_.at(ellipse_id), points_.at(pt_id), tag, driving);
        return tag;
    }

    int internal_alignment_ellipse_focus2(int ellipse_id, int pt_id, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintInternalAlignmentEllipseFocus2(
            ellipses_.at(ellipse_id), points_.at(pt_id), tag, driving);
        return tag;
    }

    // Tangent circumference
    int tangent_circumf(int p1_id, int p2_id, int rd1_id, int rd2_id,
                        bool internal = false, bool driving = true) {
        int tag = next_constraint_tag_++;
        system_.addConstraintTangentCircumf(
            points_.at(p1_id), points_.at(p2_id),
            param_ptr(rd1_id), param_ptr(rd2_id),
            internal, tag, driving);
        return tag;
    }

    // Clear constraints by tag
    void clear_by_tag(int tag) {
        system_.clearByTag(tag);
    }

    // Constraint error
    double constraint_error(int tag) {
        return system_.calculateConstraintErrorByTag(tag);
    }

    // Access the GCS system for advanced use
    GCS::System& system() { return system_; }

private:
    GCS::System system_;
    std::deque<double> params_;  // pointer-stable storage
    std::map<int, size_t> param_index_;  // param_id -> index in params_
    std::map<int, bool> param_fixed_;  // param_id -> is fixed (not an unknown)
    std::map<int, GCS::Point> points_;
    std::map<int, std::pair<int,int>> point_param_ids_;  // point_id -> (px_id, py_id)
    std::map<int, GCS::Line> lines_;
    std::map<int, GCS::Circle> circles_;
    std::map<int, int> circle_rad_param_;
    std::map<int, GCS::Arc> arcs_;
    std::map<int, GCS::Ellipse> ellipses_;
    std::map<int, GCS::ArcOfEllipse> arcs_of_ellipse_;
    std::map<int, GCS::Hyperbola> hyperbolas_;
    std::map<int, GCS::ArcOfHyperbola> arcs_of_hyperbola_;
    std::map<int, GCS::Parabola> parabolas_;
    std::map<int, GCS::ArcOfParabola> arcs_of_parabola_;
    int next_param_id_ = 0;
    int next_geo_id_ = 0;
    int next_constraint_tag_ = 1;
};

#endif // PLANEGCS_WRAPPER_H
