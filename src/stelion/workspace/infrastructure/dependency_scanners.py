"""Concrete dependency scanners used by the workspace graph builder.

Classes
-------
EditablePipDependencyScanner
    Detect editable pip dependencies from environment.yml files.
GitmodulesDependencyScanner
    Detect git submodule dependencies.
"""

from __future__ import annotations

from pathlib import Path

from ..application.protocols import DependencyScanner, EnvironmentReader
from ..domain.dependency import DependencyEdge, DependencyMechanism
from ..domain.environment import EnvironmentSpec
from .gitmodules_parser import scan_gitmodules


def _extract_editable_pip_edges(
    env: EnvironmentSpec,
    project_name: str,
    all_project_names: set[str],
) -> list[DependencyEdge]:
    """Extract editable pip dependency edges from an environment spec.

    Parameters
    ----------
    env : EnvironmentSpec
        Parsed Conda environment specification.
    project_name : str
        Name of the project owning the environment.
    all_project_names : set[str]
        Known project names in the ecosystem.

    Returns
    -------
    list[DependencyEdge]
        Edges for editable pip installs referencing ecosystem projects.
    """
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


class EditablePipDependencyScanner:
    """Detect editable pip dependencies from environment.yml files.

    Parameters
    ----------
    env_reader : EnvironmentReader
        Reader used to load environment specs from disk.

    Attributes
    ----------
    _env_reader : EnvironmentReader
        Reader used to load environment specs from disk.
    """

    def __init__(self, env_reader: EnvironmentReader) -> None:
        self._env_reader = env_reader

    def scan(
        self,
        project_name: str,
        project_dir: Path,
        all_project_names: set[str],
    ) -> list[DependencyEdge]:
        """Scan a project directory for editable pip dependency edges.

        Parameters
        ----------
        project_name : str
            Name of the project to scan.
        project_dir : Path
            Root directory of the project.
        all_project_names : set[str]
            Known project names in the ecosystem.

        Returns
        -------
        list[DependencyEdge]
            Detected editable pip dependency edges.
        """
        env = self._env_reader.read(project_dir)
        if env is None:
            return []
        return _extract_editable_pip_edges(env, project_name, all_project_names)

    def scan_with_spec(
        self,
        project_name: str,
        env_spec: EnvironmentSpec | None,
        all_project_names: set[str],
    ) -> list[DependencyEdge]:
        """Scan using a pre-read environment spec instead of reading from disk.

        Parameters
        ----------
        project_name : str
            Name of the project to scan.
        env_spec : EnvironmentSpec | None
            Pre-read environment spec, or ``None`` to skip.
        all_project_names : set[str]
            Known project names in the ecosystem.

        Returns
        -------
        list[DependencyEdge]
            Detected editable pip dependency edges.
        """
        if env_spec is None:
            return []
        return _extract_editable_pip_edges(env_spec, project_name, all_project_names)


class GitmodulesDependencyScanner:
    """Detect git submodule dependencies."""

    def scan(
        self,
        project_name: str,
        project_dir: Path,
        all_project_names: set[str],
    ) -> list[DependencyEdge]:
        """Scan a project for git submodule dependency edges.

        Parameters
        ----------
        project_name : str
            Name of the project to scan.
        project_dir : Path
            Root directory of the project.
        all_project_names : set[str]
            Known project names in the ecosystem.

        Returns
        -------
        list[DependencyEdge]
            Detected submodule dependency edges.
        """
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
