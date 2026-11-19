"""
The check of the layout of a repository against a layout that its consumer declares.

A layout, of format `stelion:layout@1`, declares the areas of a repository, its kinds of folder and
of file, the roles admitted in each area, the link directions forbidden between areas, its retired
paths and the rules of its tree. Stelion imposes no layout; it ships default layouts that a layout
may extend by name.
"""

from .declaration import Layout, LayoutError, load_layout
from .report import sarif_log, text_lines
from .rules import RULES, Finding, Reader, Rule, check_layout

__all__ = [
    "RULES",
    "Finding",
    "Layout",
    "LayoutError",
    "Reader",
    "Rule",
    "check_layout",
    "load_layout",
    "sarif_log",
    "text_lines",
]
