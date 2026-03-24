"""Project discovery use-case."""

from __future__ import annotations

from pathlib import Path

from ..domain.manifest import DiscoveryConfig
from ..domain.project import ProjectInventory, ProjectMetadata
from .protocols import MetadataExtractor


def discover_projects(
    config: DiscoveryConfig,
    extractor: MetadataExtractor,
    manifest_dir: Path,
) -> ProjectInventory:
    """Scan directories for projects and extract metadata.

    Parameters
    ----------
    config
        Discovery rules from the workspace manifest.
    extractor
        Infrastructure implementation that reads pyproject.toml.
    manifest_dir
        Absolute path to the directory containing stelion.yml.

    Returns
    -------
    ProjectInventory
        All discovered projects with their metadata.
    """
    projects: list[ProjectMetadata] = []
    seen: set[Path] = set()

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
            resolved = child.resolve()
            if resolved not in seen:
                seen.add(resolved)
                projects.append(extractor.extract(child))

    for extra_path_str in config.extra_paths:
        extra_path = (manifest_dir / extra_path_str).resolve()
        if extra_path.is_dir() and extra_path not in seen:
            seen.add(extra_path)
            projects.append(extractor.extract(extra_path))

    return ProjectInventory(projects=projects)


def _has_marker(directory: Path, markers: list[str]) -> bool:
    """Check whether a directory contains at least one marker file.

    Markers can be exact filenames (``pyproject.toml``) or glob patterns
    (``*.sty``, ``*.cls``) to match projects without standard Python packaging.
    """
    try:
        for marker in markers:
            if "*" in marker or "?" in marker:
                if next(directory.glob(marker), None) is not None:
                    return True
            elif (directory / marker).exists():
                return True
        return False
    except PermissionError:
        return False
