"""Sphinx configuration for planegcs documentation."""

from pathlib import Path

import toml

THIS_FILE = Path(__file__).resolve()

pyproject = toml.load(THIS_FILE.parent.parent / "pyproject.toml")


project = "planegcs"
copyright = "2026, planegcs contributors"
author = "planegcs contributors"
release = pyproject["project"]["version"]

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# Intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Autodoc
autodoc_member_order = "bysource"
