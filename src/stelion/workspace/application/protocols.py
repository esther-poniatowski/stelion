"""Protocol interfaces for workspace infrastructure capabilities.

Classes
-------
MetadataExtractor
    Extract project metadata from a directory.
DependencyScanner
    Scan a project directory for inter-project dependency edges.
EnvironmentReader
    Read a Conda environment spec from a project directory.
FileReader
    Read file content from disk.
FileWriter
    Write file content to disk.
FileHasher
    Compute a content hash for drift detection.
PackageDataLoader
    Load bundled package data resources.
WorkspaceFileRenderer
    Render a VS Code .code-workspace file.
ProjectsYamlRenderer
    Render the projects registry YAML.
DependencyYamlRenderer
    Render the dependency graph YAML.
EnvironmentRenderer
    Render the shared Conda environment YAML.
GenerationServices
    Bundled infrastructure services for workspace artifact generation.
GitOperations
    Git operations needed for submodule synchronization.
CommandResult
    Captured output from a subprocess execution.
CommandRunner
    Run a command in a working directory and capture its output.
BulkOperation
    Operation executable on a single project within a bulk run.
TreeScanner
    Scan a project directory and return its file-tree snapshot.
StructuredParser
    Parse structured text content into a nested dict.
SpecLoader
    Load a comparison instruction file into a typed specification.
"""

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

    def extract(self, project_dir: Path) -> ProjectMetadata:
        """Extract metadata from the given project directory.

        Parameters
        ----------
        project_dir : Path
            Root directory of the project.
        """
        ...


class DependencyScanner(Protocol):
    """Scan a project directory for inter-project dependency edges."""

    def scan(
        self,
        project_name: str,
        project_dir: Path,
        all_project_names: set[str],
    ) -> list[DependencyEdge]:
        """Scan the project directory for dependency edges.

        Parameters
        ----------
        project_name : str
            Name of the project being scanned.
        project_dir : Path
            Root directory of the project.
        all_project_names : set[str]
            Names of all known projects in the workspace.
        """
        ...


class EnvironmentReader(Protocol):
    """Read a Conda environment spec from a project directory."""

    def read(self, project_dir: Path) -> EnvironmentSpec | None:
        """Read the Conda environment spec from the project directory.

        Parameters
        ----------
        project_dir : Path
            Root directory of the project.
        """
        ...


class FileReader(Protocol):
    """Read file content from disk."""

    def read(self, path: Path) -> str:
        """Read and return the text content of the file at *path*.

        Parameters
        ----------
        path : Path
            File to read.
        """
        ...


class FileWriter(Protocol):
    """Write file content to disk."""

    def write(self, path: Path, content: str) -> None:
        """Write *content* to the file at *path*.

        Parameters
        ----------
        path : Path
            Destination file path.
        content : str
            Text content to write.
        """
        ...


class FileHasher(Protocol):
    """Compute a content hash for drift detection."""

    def hash_content(self, content: str) -> str:
        """Return a hash string for the given content.

        Parameters
        ----------
        content : str
            Text content to hash.
        """
        ...


class PackageDataLoader(Protocol):
    """Load bundled package data resources."""

    def load_text(self, resource_path: str) -> str:
        """Load a bundled text resource.

        Parameters
        ----------
        resource_path : str
            Package-relative path to the resource.
        """
        ...

    def load_json(self, resource_path: str) -> Any:
        """Load a bundled JSON resource and return the parsed object.

        Parameters
        ----------
        resource_path : str
            Package-relative path to the JSON resource.
        """
        ...


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


@dataclass(frozen=True)
class GenerationServices:
    """Bundled infrastructure services for workspace artifact generation.

    Attributes
    ----------
    render_workspace_file : WorkspaceFileRenderer
        Renderer for the VS Code workspace file.
    render_projects_yaml : ProjectsYamlRenderer
        Renderer for the projects registry YAML.
    render_dependency_yaml : DependencyYamlRenderer
        Renderer for the dependency graph YAML.
    render_environment : EnvironmentRenderer
        Renderer for the shared Conda environment YAML.
    writer : FileWriter
        File writer for generated artifacts.
    reader : FileReader
        File reader for existing artifacts.
    hasher : FileHasher
        Content hasher for drift detection.
    """

    render_workspace_file: WorkspaceFileRenderer
    render_projects_yaml: ProjectsYamlRenderer
    render_dependency_yaml: DependencyYamlRenderer
    render_environment: EnvironmentRenderer
    writer: FileWriter
    reader: FileReader
    hasher: FileHasher


# --- Git operations -----------------------------------------------------------


class GitOperations(Protocol):
    """Git operations needed for submodule synchronization."""

    def head_commit(self, repo_dir: Path) -> str:
        """Return the HEAD commit hash of the repository.

        Parameters
        ----------
        repo_dir : Path
            Path to the git repository.
        """
        ...

    def submodule_commit(self, superproject_dir: Path, submodule_path: str) -> str:
        """Return the commit hash the superproject records for the submodule.

        Parameters
        ----------
        superproject_dir : Path
            Root directory of the superproject.
        submodule_path : str
            Relative path to the submodule within the superproject.
        """
        ...

    def fetch_remote(self, repo_dir: Path) -> None:
        """Fetch from the default remote.

        Parameters
        ----------
        repo_dir : Path
            Path to the git repository.
        """
        ...

    def remote_head(self, repo_dir: Path, remote: str, branch: str) -> str:
        """Return the HEAD commit hash of the remote tracking branch.

        Parameters
        ----------
        repo_dir : Path
            Path to the git repository.
        remote : str
            Remote name.
        branch : str
            Branch name on the remote.
        """
        ...

    def update_submodule_pointer(
        self, superproject_dir: Path, submodule_path: str, commit: str,
    ) -> None:
        """Update the superproject's submodule pointer to the given commit.

        Parameters
        ----------
        superproject_dir : Path
            Root directory of the superproject.
        submodule_path : str
            Relative path to the submodule within the superproject.
        commit : str
            Commit hash to set the pointer to.
        """
        ...

    def commit_submodule_update(
        self, superproject_dir: Path, submodule_path: str,
        dependency: str, commit_short: str,
    ) -> None:
        """Commit the submodule pointer update in the superproject.

        Parameters
        ----------
        superproject_dir : Path
            Root directory of the superproject.
        submodule_path : str
            Relative path to the submodule within the superproject.
        dependency : str
            Name of the dependency project.
        commit_short : str
            Short commit hash for the commit message.
        """
        ...

    def is_clean(self, repo_dir: Path) -> bool:
        """Return True if the working tree has no uncommitted changes.

        Parameters
        ----------
        repo_dir : Path
            Path to the git repository.
        """
        ...

    def update_local_clone(self, repo_dir: Path, commit: str) -> str:
        """Check out the given commit in the local clone.

        Parameters
        ----------
        repo_dir : Path
            Path to the local clone.
        commit : str
            Commit hash to check out.
        """
        ...

    def push_to_remote(self, repo_dir: Path, remote: str, branch: str) -> None:
        """Push the local branch to the remote.

        Parameters
        ----------
        repo_dir : Path
            Path to the git repository.
        remote : str
            Remote name.
        branch : str
            Branch name to push.
        """
        ...


# --- Bulk operations ----------------------------------------------------------


@dataclass(frozen=True)
class CommandResult:
    """Captured output from a subprocess execution.

    Attributes
    ----------
    return_code : int
        Process exit code.
    stdout : str
        Captured standard output.
    stderr : str
        Captured standard error.
    """

    return_code: int
    stdout: str
    stderr: str


class CommandRunner(Protocol):
    """Run a command in a working directory and capture its output."""

    def run(self, args: tuple[str, ...], cwd: Path) -> CommandResult:
        """Run a command with the given arguments in the working directory.

        Parameters
        ----------
        args : tuple[str, ...]
            Command and arguments to execute.
        cwd : Path
            Working directory for the subprocess.
        """
        ...


class BulkOperation(Protocol):
    """Operation executable on a single project within a bulk run."""

    @property
    def label(self) -> str:
        """Human-readable label for the operation."""
        ...

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
    ) -> TreeSnapshot:
        """Scan the project directory and return a file-tree snapshot.

        Parameters
        ----------
        project_dir : Path
            Root directory of the project.
        subtree : str | None
            Optional subdirectory to restrict the scan to.
        include : tuple[str, ...]
            Glob patterns for files to include.
        exclude : tuple[str, ...]
            Glob patterns for files to exclude.
        project_name : str | None
            Optional project name for labelling the snapshot.
        """
        ...


class StructuredParser(Protocol):
    """Parse structured text content into a nested dict.

    Implementations consume **text**, not file paths — the application
    layer reads files via :class:`FileReader` and hands the content here.
    """

    def parse(
        self, content: str, *, extension: str = "", hint: str | None = None,
    ) -> dict[str, Any]:
        """Parse structured text content into a nested dict.

        Parameters
        ----------
        content : str
            Raw text content to parse.
        extension : str
            File extension hint for format detection.
        hint : str | None
            Additional format hint.
        """
        ...


class SpecLoader(Protocol):
    """Load a comparison instruction file into a typed specification."""

    def load(self, path: Path) -> ComparisonSpec:
        """Load the comparison spec from the given file path.

        Parameters
        ----------
        path : Path
            Path to the comparison instruction file.
        """
        ...
