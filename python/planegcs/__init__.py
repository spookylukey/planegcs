"""planegcs — Python bindings for FreeCAD's PlaneGCS 2D geometric constraint solver."""

from planegcs._planegcs import (
    SketchSolver,
    SolveStatus,
    Algorithm,
    DebugMode,
    InternalAlignmentType,
)
from planegcs.sketch import Sketch

__all__ = [
    "SketchSolver",
    "Sketch",
    "SolveStatus",
    "Algorithm",
    "DebugMode",
    "InternalAlignmentType",
]

__version__ = "0.1.1"
