"""Filesystem tree scanner for cross-project comparison.

Classes
-------
LocalTreeScanner
    Scan a project directory and return a TreeSnapshot.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

from ..domain.comparison import TreeEntry, TreeSnapshot


class LocalTreeScanner:
    """Scan a project directory and return a :class:`TreeSnapshot`.

    Uses :meth:`Path.iterdir` recursively.  Respects include/exclude
    glob patterns via :func:`fnmatch.fnmatch`.  Skips permission errors
    and symlink cycles.
    """

    def scan(
        self,
        project_dir: Path,
        subtree: str | None,
        include: tuple[str, ...],
        exclude: tuple[str, ...],
        *,
        project_name: str | None = None,
    ) -> TreeSnapshot:
        """Scan a project directory and return a tree snapshot.

        Parameters
        ----------
        project_dir : Path
            Root directory of the project.
        subtree : str | None
            Optional subdirectory to restrict the scan to.
        include : tuple[str, ...]
            Glob patterns for files to include (empty means all).
        exclude : tuple[str, ...]
            Glob patterns for entries to skip.
        project_name : str | None
            Override for the project key (defaults to directory name).

        Returns
        -------
        TreeSnapshot
            Snapshot of the scanned file tree.
        """
        project_key = project_name or project_dir.name
        root = project_dir / subtree if subtree else project_dir
        base = root if subtree else project_dir
        entries = list(self._walk(root, base, include, exclude, project_key))
        return TreeSnapshot(
            project=project_key,
            root=str(root.relative_to(project_dir)) if subtree else "",
            entries=tuple(sorted(entries, key=lambda e: e.relative_path)),
        )

    def _walk(
        self,
        current: Path,
        base: Path,
        include: tuple[str, ...],
        exclude: tuple[str, ...],
        project_name: str,
    ) -> list[TreeEntry]:
        entries: list[TreeEntry] = []
        try:
            children = sorted(current.iterdir())
        except PermissionError:
            return entries
        except OSError:
            return entries

        for child in children:
            if child.is_symlink() and not child.exists():
                continue
            try:
                rel = str(child.relative_to(base))
            except ValueError:
                continue
            name = child.name
            if _matches_any(name, exclude):
                continue
            if child.is_dir():
                entries.append(TreeEntry(relative_path=rel, project=project_name, is_directory=True))
                entries.extend(self._walk(child, base, include, exclude, project_name))
            elif child.is_file():
                if include and not _matches_any(name, include):
                    continue
                entries.append(TreeEntry(relative_path=rel, project=project_name, is_directory=False))
        return entries


def _matches_any(name: str, patterns: tuple[str, ...]) -> bool:
    """True if *name* matches any of the given glob patterns.

    Parameters
    ----------
    name : str
        File or directory name to test.
    patterns : tuple[str, ...]
        Glob patterns to match against.

    Returns
    -------
    bool
        ``True`` if *name* matches at least one pattern.
    """
    return any(fnmatch.fnmatch(name, p) for p in patterns)
