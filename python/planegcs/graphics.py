"""Render a :class:`~planegcs.sketch.Sketch` to a Pillow (PIL) image.

This module provides a single public function, :func:`sketch_to_image`,
that draws 2D geometry (points, lines, circles, arcs, ellipses) from a
:class:`~planegcs.sketch.Sketch` into a :class:`PIL.Image.Image`.

Pillow is **not** a hard dependency of *planegcs*.  It is imported lazily
inside :func:`sketch_to_image` so that the rest of the library works
without it.  If Pillow is not installed, an :exc:`ImportError` is raised
with a helpful message when the function is called.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image as ImageModule

    from planegcs.sketch import Sketch


def sketch_to_image(
    sketch: Sketch,
    *,
    width: int | None = None,
    height: int | None = None,
    scale: float | None = None,
    padding: int = 40,
    background: str = "white",
    line_color: str = "black",
    circle_color: str = "blue",
    arc_color: str = "red",
    ellipse_color: str = "green",
    line_width: int = 2,
    point_radius: int = 3,
    point_color: str = "gray",
) -> ImageModule.Image:
    """Render *sketch* geometry into a PIL :class:`~PIL.Image.Image`.

    Parameters
    ----------
    sketch:
        The sketch whose geometry will be drawn.
    width, height:
        Desired image dimensions in pixels.  If only one is given the
        other is computed from the bounding-box aspect ratio.  Ignored
        when *scale* is provided.
    scale:
        Pixels per sketch unit.  Overrides *width* / *height*.
    padding:
        Blank border (in pixels) around the geometry on all sides.
    background:
        Background colour (any PIL colour string).
    line_color, circle_color, arc_color, ellipse_color, point_color:
        Stroke / fill colours for each entity type.
    line_width:
        Stroke width in pixels for lines, circles, arcs, and ellipses.
    point_radius:
        Radius of the filled dot drawn for each point entity.

    Returns
    -------
    PIL.Image.Image
        The rendered image.

    Raises
    ------
    ImportError
        If Pillow is not installed.
    """
    # Lazy import so the rest of planegcs works without Pillow.
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Pillow is required for sketch_to_image().  Install it with:  pip install Pillow"
        ) from exc

    from planegcs.sketch import (
        ArcId,
        ArcInfo,
        CircleId,
        CircleInfo,
        EllipseId,
        EllipseInfo,
        LineId,
        LineInfo,
        PointId,
    )

    # ------------------------------------------------------------------
    # 1. Collect entities by type
    # ------------------------------------------------------------------
    points: list[tuple[float, float]] = []
    lines: list[LineInfo] = []
    circles: list[CircleInfo] = []
    arcs: list[ArcInfo] = []
    ellipses: list[EllipseInfo] = []

    for entity_id, etype in sketch._entity_types.items():
        if etype == "point":
            points.append(sketch.get_point(PointId(entity_id)))
        elif etype == "line":
            lines.append(sketch.get_line(LineId(entity_id)))
        elif etype == "circle":
            circles.append(sketch.get_circle(CircleId(entity_id)))
        elif etype == "arc":
            arcs.append(sketch.get_arc(ArcId(entity_id)))
        elif etype == "ellipse":
            ellipses.append(sketch.get_ellipse(EllipseId(entity_id)))

    # ------------------------------------------------------------------
    # 2. Compute bounding box of all geometry
    # ------------------------------------------------------------------
    xs: list[float] = []
    ys: list[float] = []

    for px, py in points:
        xs.append(px)
        ys.append(py)

    for ln in lines:
        x1, y1 = ln.p1
        x2, y2 = ln.p2
        xs.extend([x1, x2])
        ys.extend([y1, y2])

    for circ in circles:
        cx, cy = circ.center
        r = circ.radius
        xs.extend([cx - r, cx + r])
        ys.extend([cy - r, cy + r])

    for arc_info in arcs:
        cx, cy = arc_info.center
        r = arc_info.radius
        # Conservative: use full circle bounding box
        xs.extend([cx - r, cx + r])
        ys.extend([cy - r, cy + r])

    for ell in ellipses:
        cx, cy = ell.center
        fx, fy = ell.focus1
        # Semi-major axis: a = sqrt(c^2 + b^2) where c = dist(center, focus),
        # b = radmin (semi-minor).
        c_dist = math.hypot(fx - cx, fy - cy)
        semi_major = math.sqrt(c_dist**2 + ell.radmin**2) if c_dist > 0 else ell.radmin
        # Conservative: axis-aligned bounding box using semi-major
        xs.extend([cx - semi_major, cx + semi_major])
        ys.extend([cy - semi_major, cy + semi_major])

    # Handle empty sketch
    if not xs:
        img_w = width or 200
        img_h = height or 200
        return Image.new("RGB", (img_w, img_h), background)

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # Handle degenerate bounding box (all geometry at the same location)
    if max_x - min_x < 1e-9:
        min_x -= 1.0
        max_x += 1.0
    if max_y - min_y < 1e-9:
        min_y -= 1.0
        max_y += 1.0

    bbox_w = max_x - min_x
    bbox_h = max_y - min_y

    # ------------------------------------------------------------------
    # 3. Determine image size and scale
    # ------------------------------------------------------------------
    if scale is not None:
        img_w = int(math.ceil(bbox_w * scale)) + 2 * padding
        img_h = int(math.ceil(bbox_h * scale)) + 2 * padding
    elif width is not None and height is not None:
        img_w = width
        img_h = height
        # Fit bounding box into the given size respecting padding
        usable_w = max(img_w - 2 * padding, 1)
        usable_h = max(img_h - 2 * padding, 1)
        scale = min(usable_w / bbox_w, usable_h / bbox_h)
    elif width is not None:
        img_w = width
        usable_w = max(img_w - 2 * padding, 1)
        scale = usable_w / bbox_w
        img_h = int(math.ceil(bbox_h * scale)) + 2 * padding
    elif height is not None:
        img_h = height
        usable_h = max(img_h - 2 * padding, 1)
        scale = usable_h / bbox_h
        img_w = int(math.ceil(bbox_w * scale)) + 2 * padding
    else:
        # Default: longest axis → ~800 px
        default_size = 800 - 2 * padding
        scale = default_size / max(bbox_w, bbox_h)
        img_w = int(math.ceil(bbox_w * scale)) + 2 * padding
        img_h = int(math.ceil(bbox_h * scale)) + 2 * padding

    # ------------------------------------------------------------------
    # 4. Coordinate transform: sketch → pixel
    #    Sketch Y points up; pixel Y points down → flip Y.
    #    Map bounding-box center to image center.
    # ------------------------------------------------------------------
    bbox_cx = (min_x + max_x) / 2.0
    bbox_cy = (min_y + max_y) / 2.0
    img_cx = img_w / 2.0
    img_cy = img_h / 2.0

    def to_pixel(sx: float, sy: float) -> tuple[float, float]:
        """Convert sketch coordinates to pixel coordinates."""
        px = img_cx + (sx - bbox_cx) * scale
        py = img_cy - (sy - bbox_cy) * scale  # flip Y
        return (px, py)

    # ------------------------------------------------------------------
    # 5. Create image and draw
    # ------------------------------------------------------------------
    image = Image.new("RGB", (img_w, img_h), background)
    draw = ImageDraw.Draw(image)

    # --- Circles ---
    for circ in circles:
        cx, cy = circ.center
        r = circ.radius
        # Bounding box corners in sketch coords
        x0, y0 = to_pixel(cx - r, cy + r)  # top-left in sketch → top-left in pixel
        x1, y1 = to_pixel(cx + r, cy - r)  # bottom-right in sketch → bottom-right in pixel
        draw.ellipse([x0, y0, x1, y1], outline=circle_color, width=line_width)

    # --- Arcs ---
    for arc_info in arcs:
        cx, cy = arc_info.center
        r = arc_info.radius
        # Bounding box of the full circle containing the arc
        x0, y0 = to_pixel(cx - r, cy + r)
        x1, y1 = to_pixel(cx + r, cy - r)
        # PIL arc angles: since we flip Y, negate the angles and swap start/end.
        # In math coords the arc goes CCW from start_angle to end_angle.
        # With Y flipped, CCW becomes CW.  PIL's arc() draws CCW in screen
        # coords.  So we supply start = -end_angle, end = -start_angle
        # (in degrees) to make PIL trace the equivalent path.
        start_deg = -math.degrees(arc_info.end_angle)
        end_deg = -math.degrees(arc_info.start_angle)
        draw.arc([x0, y0, x1, y1], start=start_deg, end=end_deg, fill=arc_color, width=line_width)

    # --- Ellipses (polyline approximation) ---
    for ell in ellipses:
        cx, cy = ell.center
        fx, fy = ell.focus1
        b = ell.radmin  # semi-minor axis
        c_dist = math.hypot(fx - cx, fy - cy)
        a = math.sqrt(c_dist**2 + b**2) if c_dist > 0 else b  # semi-major axis

        # Tilt angle of the major axis (from center to focus1)
        tilt = math.atan2(fy - cy, fx - cx) if c_dist > 1e-12 else 0.0

        cos_t = math.cos(tilt)
        sin_t = math.sin(tilt)

        # Parametric ellipse: ~100 segments
        n_segments = 100
        pixel_pts: list[tuple[float, float]] = []
        for i in range(n_segments + 1):
            theta = 2.0 * math.pi * i / n_segments
            # Point on axis-aligned ellipse then rotate by tilt
            ex = a * math.cos(theta)
            ey = b * math.sin(theta)
            sx = cx + ex * cos_t - ey * sin_t
            sy = cy + ex * sin_t + ey * cos_t
            pixel_pts.append(to_pixel(sx, sy))

        # Draw as connected line segments
        for i in range(len(pixel_pts) - 1):
            draw.line([pixel_pts[i], pixel_pts[i + 1]], fill=ellipse_color, width=line_width)

    # --- Lines ---
    for ln in lines:
        p1 = to_pixel(*ln.p1)
        p2 = to_pixel(*ln.p2)
        draw.line([p1, p2], fill=line_color, width=line_width)

    # --- Points (drawn last so they appear on top) ---
    for px, py in points:
        cx_px, cy_px = to_pixel(px, py)
        r = point_radius
        draw.ellipse(
            [cx_px - r, cy_px - r, cx_px + r, cy_px + r],
            fill=point_color,
        )

    return image
