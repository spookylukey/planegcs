"""Verify that _planegcs.pyi stays in sync with the compiled C extension.

Run ``pybind11-stubgen`` against the live module and compare the output
to the committed stub file.  If this test fails, regenerate with::

    python -m pybind11_stubgen planegcs._planegcs \
        --enum-class-locations 'Algorithm:planegcs._planegcs' \
        -o python
    ruff check --fix python/planegcs/_planegcs.pyi
    ruff format python/planegcs/_planegcs.pyi
"""

import importlib.util
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
STUB_PATH = ROOT / "python" / "planegcs" / "_planegcs.pyi"

REGEN_CMD = textwrap.dedent("""\
    python -m pybind11_stubgen planegcs._planegcs \\
        --enum-class-locations 'Algorithm:planegcs._planegcs' \\
        -o python
    ruff check --fix python/planegcs/_planegcs.pyi
    ruff format python/planegcs/_planegcs.pyi""")


def _stubgen_available() -> bool:
    return importlib.util.find_spec("pybind11_stubgen") is not None


@pytest.mark.skipif(not _stubgen_available(), reason="pybind11-stubgen not installed")
def test_stubs_up_to_date(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pybind11_stubgen",
            "planegcs._planegcs",
            "--enum-class-locations",
            "Algorithm:planegcs._planegcs",
            "-o",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"pybind11-stubgen failed:\n{result.stderr}"

    generated_path = tmp_path / "planegcs" / "_planegcs.pyi"

    # Apply the same ruff check --fix and ruff format that the pre-commit
    # hooks would apply, so formatting differences don't cause false positives.
    ruff = shutil.which("ruff") or shutil.which("ruff", path=str(Path(sys.executable).parent))
    if ruff:
        config = str(ROOT / "pyproject.toml")
        subprocess.run(
            [
                ruff,
                "check",
                "--fix",
                "--unsafe-fixes",
                "--config",
                config,
                "--per-file-ignores",
                f"{generated_path}:E501",
                str(generated_path),
            ],
            capture_output=True,
        )
        subprocess.run(
            [ruff, "format", "--config", config, str(generated_path)],
            capture_output=True,
        )

    generated = generated_path.read_text()
    committed = STUB_PATH.read_text()

    if generated != committed:
        import difflib

        diff = difflib.unified_diff(
            committed.splitlines(keepends=True),
            generated.splitlines(keepends=True),
            fromfile="committed  python/planegcs/_planegcs.pyi",
            tofile="generated  (pybind11-stubgen output)",
        )
        diff_text = "".join(diff)
        pytest.fail(
            f"_planegcs.pyi is out of date. Regenerate with:\n\n"
            f"    {REGEN_CMD}\n\n"
            f"Diff:\n{diff_text}"
        )
