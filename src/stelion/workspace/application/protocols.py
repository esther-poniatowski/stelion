"""Protocol interfaces for workspace infrastructure capabilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, Union

from ..domain.bulk import ProjectOutcome
from ..domain.comparison import ComparisonSpec, TreeSnapshot
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

    def load_json(self, resource_path: str) -> Any: ...


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


# --- Git operations -----------------------------------------------------------


class GitOperations(Protocol):
    """Git operations needed for submodule synchronization."""

    def head_commit(self, repo_dir: Path) -> str: ...

    def submodule_commit(self, superproject_dir: Path, submodule_path: str) -> str: ...

    def fetch_remote(self, repo_dir: Path) -> None: ...

    def remote_head(self, repo_dir: Path, remote: str, branch: str) -> str: ...

    def update_submodule_pointer(
        self, superproject_dir: Path, submodule_path: str, commit: str,
    ) -> None: ...

    def commit_submodule_update(
        self, superproject_dir: Path, submodule_path: str,
        dependency: str, commit_short: str,
    ) -> None: ...

    def is_clean(self, repo_dir: Path) -> bool: ...

    def update_local_clone(self, repo_dir: Path, commit: str) -> str: ...

    def push_to_remote(self, repo_dir: Path, remote: str, branch: str) -> None: ...


# --- Bulk operations ----------------------------------------------------------


@dataclass(frozen=True)
class CommandResult:
    """Captured output from a subprocess execution."""

    return_code: int
    stdout: str
    stderr: str


class CommandRunner(Protocol):
    """Run a command in a working directory and capture its output."""

    def run(self, args: tuple[str, ...], cwd: Path) -> CommandResult: ...


class BulkOperation(Protocol):
    """Operation executable on a single project within a bulk run."""

    @property
    def label(self) -> str: ...

    def __call__(self, project: ProjectMetadata, *, dry_run: bool) -> ProjectOutcome: ...


# --- Comparison operations ----------------------------------------------------


class TreeScanner(Protocol):
    """Scan a project directory and return its file-tree snapshot."""

    def scan(
        self,
        project_dir: Path,
        subtree: str | None,
        include: tuple[str, ...],
        exclude: tuple[str, ...],
        *,
        project_name: str | None = None,
    ) -> TreeSnapshot: ...


class StructuredParser(Protocol):
    """Parse structured text content into a nested dict.

    Implementations consume **text**, not file paths — the application
    layer reads files via :class:`FileReader` and hands the content here.
    """

    def parse(
        self, content: str, *, extension: str = "", hint: str | None = None,
    ) -> dict[str, Any]: ...


class SpecLoader(Protocol):
    """Load a comparison instruction file into a typed specification."""

    def load(self, path: Path) -> ComparisonSpec: ...
