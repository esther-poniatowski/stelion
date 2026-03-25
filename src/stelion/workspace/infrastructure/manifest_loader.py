"""Parse stelion.yml into a WorkspaceManifest."""

from __future__ import annotations

from pathlib import Path

import yaml

from ..domain.manifest import WorkspaceManifest


def load_manifest(path: Path) -> WorkspaceManifest:
    """Load and validate a workspace manifest from a YAML file.

    Parameters
    ----------
    path
        Absolute or relative path to ``stelion.yml``.

    Returns
    -------
    WorkspaceManifest
        Fully parsed and typed manifest.

    Raises
    ------
    FileNotFoundError
        If the manifest file does not exist.
    ValueError
        If required fields are missing or invalid.
    """
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")

    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    manifest_dir = path.parent
    return WorkspaceManifest.from_dict(raw, manifest_dir)
