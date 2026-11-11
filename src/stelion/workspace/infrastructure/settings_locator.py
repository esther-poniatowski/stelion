"""Locate the root of a workspace and the configuration file of Stelion.

The root is the folder from which Stelion finds its configuration file and resolves the paths
written in that file. It is resolved in this order, which stops at the first answer:

1. the folder given explicitly (option ``--root``, or the environment variable ``STELION_ROOT``,
   which the command line reads into the same option);
2. the nearest ancestor of the current folder that holds the configuration file, in
   ``config/tools/`` or at its own level;
3. the current folder.

The configuration file is ``config/tools/stelion.yml`` or ``stelion.yml`` below the root. When both
exist, the location is ambiguous and :class:`SettingsError` names both files. A configuration file
named explicitly must exist. Without any configuration file, Stelion runs on its built-in defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..exceptions import SettingsError

SETTINGS_FILE_NAME = "stelion.yml"
"""Name of the configuration file of Stelion."""
SETTINGS_SUBDIRECTORY = Path("config", "tools")
"""Folder below the root that may hold the configuration file."""
ROOT_ENVIRONMENT_VARIABLE = "STELION_ROOT"
"""Environment variable that names the root when the option ``--root`` is absent."""


@dataclass(frozen=True)
class SettingsLocation:
    """Resolved root of a workspace and the configuration file found for it."""

    root: Path
    """Absolute root of the workspace."""
    settings_path: Path | None
    """Absolute path of the configuration file, or ``None`` when Stelion runs on its defaults."""

    @property
    def target_path(self) -> Path:
        """Return the configuration file to write: the existing one, else root ``stelion.yml``."""
        return self.settings_path or self.root / SETTINGS_FILE_NAME


def settings_candidates(folder: Path) -> tuple[Path, Path]:
    """Return the two places of the configuration file below *folder*."""
    return (folder / SETTINGS_SUBDIRECTORY / SETTINGS_FILE_NAME, folder / SETTINGS_FILE_NAME)


def find_settings_file(root: Path) -> Path | None:
    """Return the configuration file below *root*, or ``None`` when there is none.

    Raises
    ------
    SettingsError
        If both places hold a configuration file.
    """
    present = [path for path in settings_candidates(root) if path.is_file()]
    if len(present) > 1:
        raise SettingsError(
            f"Two configuration files compete: {present[0]} and {present[1]}; keep only one."
        )
    return present[0] if present else None


def find_root(start: Path) -> Path | None:
    """Return the nearest folder, from *start* upward, that holds a configuration file."""
    for folder in (start, *start.parents):
        if any(path.is_file() for path in settings_candidates(folder)):
            return folder
    return None


def resolve_root(root: Path | None, *, cwd: Path) -> Path:
    """Resolve the root from an explicit folder, an upward search, or the current folder.

    Parameters
    ----------
    root : Path | None
        Folder given by ``--root`` or ``STELION_ROOT``, relative to *cwd* when relative.
    cwd : Path
        Current folder.
    """
    cwd = cwd.resolve()
    if root is not None:
        return (cwd / root.expanduser()).resolve()
    return find_root(cwd) or cwd


def locate_settings(root: Path | None, config: Path | None, *, cwd: Path) -> SettingsLocation:
    """Resolve the root and the configuration file of a workspace.

    Parameters
    ----------
    root : Path | None
        Folder given by ``--root`` or ``STELION_ROOT``.
    config : Path | None
        Configuration file given by ``--config``, relative to *cwd* when relative.
    cwd : Path
        Current folder.

    Raises
    ------
    SettingsError
        If the file named by *config* does not exist, or if two configuration files compete.
    """
    resolved_root = resolve_root(root, cwd=cwd)
    if config is not None:
        path = (cwd.resolve() / config.expanduser()).resolve()
        if not path.is_file():
            raise SettingsError(f"Configuration file not found: {path}")
        return SettingsLocation(root=resolved_root, settings_path=path)
    return SettingsLocation(root=resolved_root, settings_path=find_settings_file(resolved_root))
