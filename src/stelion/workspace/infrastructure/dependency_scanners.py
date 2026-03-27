"""Concrete dependency scanners used by the workspace graph builder."""

from __future__ import annotations

from pathlib import Path

from ..application.protocols import DependencyScanner, EnvironmentReader
from ..domain.dependency import DependencyEdge, DependencyMechanism
from .gitmodules_parser import scan_gitmodules


class EditablePipDependencyScanner:
    """Detect editable pip dependencies from environment.yml files."""

    def __init__(self, env_reader: EnvironmentReader) -> None:
        self._env_reader = env_reader

    def scan(
        self,
        project_name: str,
        project_dir: Path,
        all_project_names: set[str],
    ) -> list[DependencyEdge]:
        env = self._env_reader.read(project_dir)
        if env is None:
            return []
        edges: list[DependencyEdge] = []
        for pip_dep in env.pip_dependencies:
            stripped = pip_dep.strip()
            if stripped.startswith("-e"):
                dep_name = Path(stripped.replace("-e", "").strip().split("[", 1)[0]).name
                if dep_name and dep_name in all_project_names and dep_name != project_name:
                    edges.append(
                        DependencyEdge(
                            dependent=project_name,
                            dependency=dep_name,
                            mechanism=DependencyMechanism.EDITABLE_PIP,
                            detail="environment.yml",
                        )
                    )
        return edges


class GitmodulesDependencyScanner:
    """Detect git submodule dependencies."""

    def scan(
        self,
        project_name: str,
        project_dir: Path,
        all_project_names: set[str],
    ) -> list[DependencyEdge]:
        edges = scan_gitmodules(project_dir, all_project_names)
        return [
            DependencyEdge(
                dependent=project_name,
                dependency=edge.dependency,
                mechanism=edge.mechanism,
                detail=edge.detail,
            )
            for edge in edges
        ]
