"""Parse stelion.yml into a WorkspaceManifest."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import yaml

from ..domain.manifest import WorkspaceManifest
from ..exceptions import ManifestValidationError
from .manifest_codec import parse_workspace_manifest


def load_manifest_mapping(
    path: Path, *, label: str = "Manifest"
) -> Mapping[str, object]:
    """Load a YAML mapping used as a manifest or manifest overlay.

    Parameters
    ----------
    path : Path
        YAML file to load.
    label : str
        Object name used in validation errors.

    Returns
    -------
    Mapping[str, object]
        Parsed top-level mapping.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    ManifestValidationError
        If the YAML is invalid or its top level is not a mapping.
    """
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(f"{label} not found: {path}")

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ManifestValidationError(
            f"Invalid {label.lower()} YAML in {path}: {exc}"
        ) from exc
    if not isinstance(raw, Mapping):
        raise ManifestValidationError(f"{label} must contain a YAML mapping: {path}")
    return raw


def load_manifest(path: Path, root: Path | None = None) -> WorkspaceManifest:
    """Load and validate a workspace manifest from a YAML file.

    Parameters
    ----------
    path : Path
        Absolute or relative path to ``stelion.yml``.
    root : Path | None
        Root of the workspace, against which the paths written in the manifest are resolved.
        Defaults to the folder of the manifest, for a manifest placed at the root.

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
    raw = load_manifest_mapping(path)
    manifest_dir = root.resolve() if root is not None else path.parent
    return parse_workspace_manifest(raw, manifest_dir)
