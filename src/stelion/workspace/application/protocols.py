"""Protocol interfaces for workspace infrastructure capabilities."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ..domain.dependency import DependencyEdge, DependencyGraph
from ..domain.environment import EnvironmentSpec
from ..domain.manifest import WorkspaceManifest
from ..domain.project import ProjectInventory, ProjectMetadata


class MetadataExtractor(Protocol):
    """Extract project metadata from a directory."""

    def extract(self, project_dir: Path) -> ProjectMetadata: ...


class DependencyScanner(Protocol):
    """Scan a project directory for inter-project dependency edges."""

    def scan(
        self,
        project_name: str,
        project_dir: Path,
        all_project_names: set[str],
    ) -> list[DependencyEdge]: ...


class EnvironmentReader(Protocol):
    """Read a Conda environment spec from a project directory."""

    def read(self, project_dir: Path) -> EnvironmentSpec | None: ...


class FileReader(Protocol):
    """Read file content from disk."""

    def read(self, path: Path) -> str: ...


class FileWriter(Protocol):
    """Write file content to disk."""

    def write(self, path: Path, content: str) -> None: ...


class FileHasher(Protocol):
    """Compute a content hash for drift detection."""

    def hash_content(self, content: str) -> str: ...


class PackageDataLoader(Protocol):
    """Load bundled package data resources."""

    def load_text(self, resource_path: str) -> str: ...

    def load_json(self, resource_path: str) -> dict: ...


# --- Renderer protocols ------------------------------------------------------


class WorkspaceFileRenderer(Protocol):
    """Render a VS Code .code-workspace file."""

    def __call__(self, manifest: WorkspaceManifest, inventory: ProjectInventory) -> str: ...


class ProjectsYamlRenderer(Protocol):
    """Render the projects registry YAML."""

    def __call__(self, inventory: ProjectInventory, manifest_dir: Path) -> str: ...


class DependencyYamlRenderer(Protocol):
    """Render the dependency graph YAML."""

    def __call__(self, graph: DependencyGraph) -> str: ...


class EnvironmentRenderer(Protocol):
    """Render the shared Conda environment YAML."""

    def __call__(self, environment: EnvironmentSpec) -> str: ...
