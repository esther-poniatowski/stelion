"""Parse .gitmodules files to detect git submodule dependency edges."""

from __future__ import annotations

import configparser
from pathlib import Path

from ..domain.dependency import DependencyEdge, DependencyMechanism


def scan_gitmodules(project_dir: Path, all_project_names: set[str]) -> list[DependencyEdge]:
    """Scan a project's .gitmodules for ecosystem-internal submodule dependencies.

    Only submodules whose name matches a known ecosystem project are returned.
    """
    gitmodules_path = project_dir / ".gitmodules"
    if not gitmodules_path.exists():
        return []

    parser = configparser.ConfigParser()
    parser.read(gitmodules_path)

    edges: list[DependencyEdge] = []
    for section in parser.sections():
        submodule_path = parser.get(section, "path", fallback="")
        # Extract the bare project name from the submodule path (e.g. "vendor/scholia" -> "scholia")
        dep_name = Path(submodule_path).name if submodule_path else ""

        if dep_name in all_project_names:
            edges.append(DependencyEdge(
                dependent=project_dir.name,
                dependency=dep_name,
                mechanism=DependencyMechanism.GIT_SUBMODULE,
                detail=submodule_path,
            ))

    return edges
