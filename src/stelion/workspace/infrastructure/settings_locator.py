"""Locate the root of a workspace and the configuration file of Stelion, through Hodegos.

Hodegos resolves both, as its specification states
(https://github.com/esther-poniatowski/hodegos/blob/main/docs/specification.md). The root is the
folder from which Stelion finds its configuration file and resolves the paths written in that
file. It is resolved in this order, which stops at the first answer:

1. the folder given by the option ``--root``;
2. the folder named by the environment variable ``STELION_ROOT``;
3. the nearest folder, from the current folder upward, that holds ``stelion.yml`` at one of its
   places;
4. the current folder.

The places of ``stelion.yml`` in a folder are the folder itself, its subfolder ``.config/``, and
each folder that the declaration ``hodegos.yml`` of the folder lists. When two places hold the
file, the location is ambiguous and :class:`SettingsError` names both files. A configuration file
named explicitly must exist. Without any configuration file, Stelion runs on its built-in defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from hodegos import DiscoveryError, Tool, discover

from ..exceptions import SettingsError

TOOL = Tool("stelion", ("yml",))
"""Convention of Stelion for Hodegos: the file ``stelion.yml`` and the variable ``STELION_ROOT``."""
SETTINGS_FILE_NAME = TOOL.file_names[0]
"""Name of the configuration file of Stelion, written at the root when none exists."""


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


def locate_settings(root: Path | None, config: Path | None, *, cwd: Path) -> SettingsLocation:
    """Resolve the root and the configuration file of a workspace through Hodegos.

    Parameters
    ----------
    root : Path | None
        Folder given by ``--root``, relative to *cwd* when relative; ``None`` to take the root
        from ``STELION_ROOT`` or to search for it.
    config : Path | None
        Configuration file given by ``--config``, relative to *cwd* when relative.
    cwd : Path
        Current folder.

    Returns
    -------
    SettingsLocation
        The root, resolved, and the configuration file: *config* when named, otherwise the single
        place of the root holding ``stelion.yml``, or ``None`` when no place holds it.

    Raises
    ------
    SettingsError
        If the file named by *config* does not exist, if two places of the root hold a
        configuration file, or if a declaration ``hodegos.yml`` met by the search is invalid.
    """
    try:
        found = discover(
            TOOL,
            root=root.expanduser() if root is not None else None,
            config=config.expanduser() if config is not None else None,
            cwd=cwd,
        )
    except DiscoveryError as exc:
        raise SettingsError(str(exc)) from exc
    settings_path = found.configuration.path.resolve() if found.configuration else None
    return SettingsLocation(root=found.root.resolve(), settings_path=settings_path)
