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
from .protocols import EnvironmentReader


def build_dependency_graph(
    manifest: WorkspaceManifest,
    inventory: ProjectInventory,
    env_reader: EnvironmentReader,
) -> DependencyGraph:
    """Build the full dependency graph from auto-detection and manifest data.

    Scans each project for editable pip installs in ``environment.yml``
    and git submodule relationships, then merges with manually declared
    edges from the manifest.
    """
    from ..infrastructure.gitmodules_parser import scan_gitmodules

    all_names = {p.name for p in inventory.projects}
    detected: list[DependencyEdge] = []

    # Collect all directories to scan: inventory projects + extra_scan_dirs
    scan_dirs: list[tuple[str, Path]] = [(p.name, p.path) for p in inventory.projects]
    for extra_dir_str in manifest.dependencies.extra_scan_dirs:
        extra_dir = (manifest.manifest_dir / extra_dir_str).resolve()
        if extra_dir.is_dir():
            scan_dirs.append((extra_dir.name, extra_dir))

    for project_name, project_path in scan_dirs:
        # Detect editable pip installs in environment.yml
        env = env_reader.read(project_path)
        if env:
            for pip_dep in env.pip_dependencies:
                stripped = pip_dep.strip()
                if stripped.startswith("-e"):
                    dep_name = _extract_pip_dep_name(stripped)
                    if dep_name and dep_name in all_names and dep_name != project_name:
                        detected.append(DependencyEdge(
                            dependent=project_name,
                            dependency=dep_name,
                            mechanism=DependencyMechanism.EDITABLE_PIP,
                            detail="environment.yml",
                        ))

        # Detect git submodules
        detected.extend(scan_gitmodules(project_path, all_names))

    manual = tuple(
        manual_edge_to_dependency_edge(e) for e in manifest.dependencies.manual_edges
    )

    return DependencyGraph(
        detected=tuple(detected),
        manual=manual,
    )


def _extract_pip_dep_name(pip_line: str) -> str | None:
    """Extract a package name from an editable pip install line.

    Examples::

        -e /path/to/morpha[dev]  ->  morpha
        -e ../../projects/eikon  ->  eikon
    """
    path_str = pip_line.replace("-e", "").strip()
    if "[" in path_str:
        path_str = path_str[:path_str.index("[")]
    return Path(path_str).name or None
