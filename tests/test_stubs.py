"""Verify that _planegcs.pyi stays in sync with the compiled C extension.

Run ``pybind11-stubgen`` against the live module and compare the output
to the committed stub file.  If this test fails, regenerate with::

  ./update_stubs.sh
"""

import importlib.util
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
STUB_PATH = ROOT / "python" / "planegcs" / "_planegcs.pyi"

REGEN_CMD = textwrap.dedent("./update_stubs.sh")

# Regex to strip ``# value = ...`` comments that some pybind11-stubgen
# versions emit on ClassVar and module-level enum aliases.
_VALUE_COMMENT_RE = re.compile(r"\s*# value = .+$", re.MULTILINE)


def _stubgen_available() -> bool:
    return importlib.util.find_spec("pybind11_stubgen") is not None


def _normalize_stubs(text: str) -> str:
    """Normalize stub text so that cosmetic differences between
    pybind11-stubgen versions don't cause false positives.

    Handles:
    * ``# value = <...>`` comments on ClassVar / module-level aliases
    * Ordering of top-level definitions (classes + trailing assignments)
    * Parenthesised vs non-parenthesised type annotations on module-level
      aliases, e.g.::

          Foo: (\n    Bar  # ...\n)   ->   Foo: Bar
    """
    # 1. Strip value comments.
    text = _VALUE_COMMENT_RE.sub("", text)

    # 2. Collapse multi-line parenthesised module-level annotations back to
    #    a single line.  After stripping value comments these look like:
    #        Name: (
    #            Type
    #        )
    #    We normalise to:  Name: Type
    text = re.sub(
        r"^([A-Za-z_]\w*): \(\n\s+([A-Za-z_]\w*(?:\[[^\]]*\])?)\s*\n\)",
        r"\1: \2",
        text,
        flags=re.MULTILINE,
    )

    # 3. Split into a preamble (imports / __all__) and top-level blocks
    #    (classes, standalone assignments).  Re-sort the blocks so that
    #    ordering differences between stubgen versions are ignored.
    lines = text.split("\n")
    preamble: list[str] = []
    blocks: list[list[str]] = []
    current_block: list[str] | None = None

    for line in lines:
        is_toplevel_start = (
            line
            and not line[0].isspace()
            and not line.startswith('"""')
            and not line.startswith("from ")
            and not line.startswith("import ")
            and not line.startswith("__all__")
        )
        if is_toplevel_start and current_block is None and not blocks:
            # We haven't started any block yet — everything so far is preamble.
            # But this line starts the first block.
            current_block = [line]
        elif is_toplevel_start and current_block is not None:
            # Finish previous block, start a new one.
            blocks.append(current_block)
            current_block = [line]
        elif current_block is not None:
            current_block.append(line)
        else:
            preamble.append(line)

    if current_block is not None:
        blocks.append(current_block)

    # Sort blocks by their first non-empty line (the definition name).
    blocks.sort(key=lambda b: b[0])

    # Reassemble.
    result_lines = preamble
    for block in blocks:
        result_lines.extend(block)

    # Strip trailing whitespace on each line and collapse multiple trailing
    # newlines to one.
    normalised = "\n".join(line.rstrip() for line in result_lines).rstrip() + "\n"
    return normalised


@pytest.mark.skipif(not _stubgen_available(), reason="pybind11-stubgen not installed")
@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Fails in cibuildwheel on Windows due to formatting differences.",
)
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

    generated = _normalize_stubs(generated_path.read_text())
    committed = _normalize_stubs(STUB_PATH.read_text())

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
