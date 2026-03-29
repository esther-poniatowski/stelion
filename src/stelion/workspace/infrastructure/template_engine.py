"""Simple placeholder substitution engine for template instantiation.

Replaces ``{{ key }}`` patterns in text files while respecting exclusion
patterns (GitHub Actions ``${{ }}``, Conda Jinja2 ``{{ pyproject.* }}``).

This is a standalone Phase 1 implementation. When stelion's full template
engine is built, this module can be replaced via the protocol interface.
"""

from __future__ import annotations

import re
import shutil
from collections.abc import Sequence
from pathlib import Path

BINARY_EXTENSIONS: set[str] = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".ico",
    ".woff", ".woff2", ".ttf", ".eot",
    ".zip", ".tar", ".gz", ".bz2",
    ".pyc", ".pyo", ".so", ".dylib",
}


def substitute_in_file(
    path: Path,
    bindings: dict[str, str],
    delimiters: tuple[str, str] = ("{{ ", " }}"),
    exclude_patterns: Sequence[str] | None = None,
) -> int:
    """Replace placeholder strings in a single file.

    Parameters
    ----------
    path
        File to process.
    bindings
        Mapping from placeholder string (including delimiters) to value.
    delimiters
        Opening and closing placeholder delimiters.
    exclude_patterns
        Regex patterns whose matches should be protected from substitution.

    Returns
    -------
    int
        Number of replacements made.
    """
    if path.suffix in BINARY_EXTENSIONS:
        return 0
    if not path.is_file():
        return 0

    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return 0

    protected: dict[str, str] = {}
    if exclude_patterns:
        for idx, pattern in enumerate(exclude_patterns):
            for match_index, match in enumerate(re.finditer(pattern, content)):
                token = f"__STELION_PROTECTED_{idx}_{match_index}__"
                protected[token] = match.group(0)
                content = content.replace(match.group(0), token, 1)

    count = 0
    placeholders = _materialize_bindings(bindings, delimiters)
    for placeholder, value in placeholders.items():
        occurrences = content.count(placeholder)
        if occurrences > 0:
            content = content.replace(placeholder, value)
            count += occurrences

    for token, original in protected.items():
        content = content.replace(token, original)

    if count > 0:
        path.write_text(content, encoding="utf-8")

    return count


def substitute_in_directory(
    root: Path,
    bindings: dict[str, str],
    delimiters: tuple[str, str] = ("{{ ", " }}"),
    exclude_patterns: Sequence[str] | None = None,
) -> int:
    """Replace placeholders in all text files under a directory.

    Returns the total number of replacements across all files.
    """
    total = 0
    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            total += substitute_in_file(path, bindings, delimiters, exclude_patterns)
    return total


def copy_template(source: Path, target: Path) -> None:
    """Copy a template directory, excluding .git."""
    if target.exists():
        raise FileExistsError(f"Target directory already exists: {target}")

    shutil.copytree(source, target, ignore=shutil.ignore_patterns(".git"))


def rename_paths(
    root: Path,
    renames: dict[str, str],
    bindings: dict[str, str],
    delimiters: tuple[str, str] = ("{{ ", " }}"),
) -> int:
    """Rename directories and files according to the rename mapping.

    The rename values may contain placeholder references that are resolved
    against ``bindings``.

    Returns the number of renames performed.
    """
    count = 0
    placeholders = _materialize_bindings(bindings, delimiters)
    for old_rel, new_template in renames.items():
        # Resolve placeholders in the new name
        new_rel = new_template
        for placeholder, value in placeholders.items():
            new_rel = new_rel.replace(placeholder, value)

        old_path = root / old_rel
        new_path = root / new_rel
        if old_path.exists() and old_path != new_path:
            old_path.rename(new_path)
            count += 1

    return count


def _materialize_bindings(
    bindings: dict[str, str],
    delimiters: tuple[str, str],
) -> dict[str, str]:
    """Expand logical binding names into concrete placeholder tokens."""
    start, end = delimiters
    return {f"{start}{name}{end}": value for name, value in bindings.items()}
