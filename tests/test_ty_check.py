"""Run ty type checker as part of the test suite."""

import subprocess
import sys
from pathlib import Path


def test_ty_check():
    """Ensure the codebase passes ``ty check`` with no errors."""
    project_root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "ty", "check"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"ty check failed (exit {result.returncode}):\n{result.stderr or result.stdout}"
    )
