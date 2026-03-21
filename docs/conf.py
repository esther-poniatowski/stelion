# ==================================================================================================
# Sphinx Configuration for stelion
#
# Uses MyST-Parser for Markdown support alongside reStructuredText.
#
# See Also
# --------
# - Sphinx: https://www.sphinx-doc.org/
# - MyST-Parser: https://myst-parser.readthedocs.io/
# ==================================================================================================

project = "stelion"
author = "Esther Poniatowski"
copyright = "2025, Esther Poniatowski"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "_templates"]

# --- HTML Output ---------------------------------------------------------------------------------

html_theme = "sphinx_rtd_theme"

# --- MyST-Parser Configuration ------------------------------------------------------------------

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# --- Napoleon (Docstring Style) ------------------------------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = True
