"""Dependency graph construction use-case."""

from __future__ import annotations

from pathlib import Path

from ..domain.dependency import (
    DependencyEdge,
    DependencyGraph,
    DependencyMechanism,
    manual_edge_to_dependency_edge,
)
from ..domain.manifest import WorkspaceManifest
from ..domain.project import ProjectInventory
from .protocols import DependencyScanner


def build_dependency_graph(
    manifest: WorkspaceManifest,
    inventory: ProjectInventory,
    scanners: tuple[DependencyScanner, ...],
) -> DependencyGraph:
    """Build the full dependency graph from auto-detection and manifest data.

    Scans each project for editable pip installs in ``environment.yml``
    and git submodule relationships, then merges with manually declared
    edges from the manifest.

    Parameters
    ----------
    manifest : WorkspaceManifest
        Workspace manifest with dependency configuration.
    inventory : ProjectInventory
        All discovered projects.
    scanners : tuple[DependencyScanner, ...]
        Infrastructure scanners for detecting dependency edges.

    Returns
    -------
    DependencyGraph
        Combined graph of detected and manual dependency edges.
    """
    all_names = {p.name for p in inventory.projects}
    detected: list[DependencyEdge] = []

    # Collect all directories to scan: inventory projects + configured extra scan paths.
    scan_dirs: list[tuple[str, Path]] = [(p.name, p.path) for p in inventory.projects]
    for extra_dir_str in manifest.dependencies.scan_paths:
        extra_dir = (manifest.manifest_dir / extra_dir_str).resolve()
        if extra_dir.is_dir():
            scan_dirs.append((extra_dir.name, extra_dir))

    for project_name, project_path in scan_dirs:
        for scanner in scanners:
            detected.extend(scanner.scan(project_name, project_path, all_names))

    manual = tuple(
        manual_edge_to_dependency_edge(e) for e in manifest.dependencies.manual_edges
    )

    return DependencyGraph(
        detected=tuple(detected),
        manual=manual,
    )
