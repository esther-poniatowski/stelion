"""Default manifest generation use-case."""

from __future__ import annotations

from pathlib import Path

import yaml

from ..domain.manifest import default_workspace_manifest, manifest_to_dict
from ..domain.project import ProjectInventory
from .discovery import discover_projects
from .protocols import MetadataExtractor


def generate_default_manifest_content(
    manifest_dir: Path,
    extractor: MetadataExtractor,
    github_user: str = "",
) -> tuple[str, ProjectInventory]:
    """Build the text content for a new stelion.yml with auto-discovered projects.

    Parameters
    ----------
    manifest_dir
        Directory that will contain the new manifest.
    extractor
        Infrastructure component for reading pyproject.toml metadata.
    github_user
        GitHub username for template defaults (e.g. from git config).

    Returns
    -------
    tuple[str, ProjectInventory]
        The YAML content string and the discovered project inventory.
    """
    manifest = default_workspace_manifest(manifest_dir, github_user=github_user)
    inventory = discover_projects(manifest.discovery, extractor, manifest_dir)
    content = yaml.safe_dump(manifest_to_dict(manifest), sort_keys=False)
    return content, inventory
