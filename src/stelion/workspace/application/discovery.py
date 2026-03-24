"""Project discovery use-case."""

from __future__ import annotations

from pathlib import Path

from ..domain.manifest import DiscoveryConfig
from ..domain.project import ProjectInventory, ProjectMetadata
from .protocols import MetadataExtractor


def discover_projects(
    config: DiscoveryConfig,
    categories: dict[str, list[str]],
    extractor: MetadataExtractor,
    manifest_dir: Path,
) -> ProjectInventory:
    """Scan directories for projects and extract metadata.

    Parameters
    ----------
    config
        Discovery rules from the workspace manifest.
    categories
        Category-to-project-names mapping from the manifest.
    extractor
        Infrastructure implementation that reads pyproject.toml.
    manifest_dir
        Absolute path to the directory containing stelion.yml.

    Returns
    -------
    ProjectInventory
        All discovered projects with their metadata and category assignments.
    """
    projects: list[ProjectMetadata] = []

    for scan_dir_str in config.scan_dirs:
        scan_dir = (manifest_dir / scan_dir_str).resolve()
        if not scan_dir.is_dir():
            continue
        for child in sorted(scan_dir.iterdir()):
            if not child.is_dir():
                continue
            if child.name in config.exclude:
                continue
            if child.name.startswith("."):
                continue
            if not _has_marker(child, config.markers):
                continue
            metadata = extractor.extract(child)
            projects.append(metadata)

    return ProjectInventory(projects=projects, categories=categories)


def _has_marker(directory: Path, markers: list[str]) -> bool:
    """Check whether a directory contains at least one marker file."""
    try:
        return any((directory / marker).exists() for marker in markers)
    except PermissionError:
        return False
