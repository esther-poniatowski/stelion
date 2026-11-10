"""New project bootstrapping use-case.

Copies a template project, substitutes placeholders, renames directories
and files, and optionally initializes a git repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Callable

from ..domain.manifest import TemplateConfig, EcosystemDefaults
from ..exceptions import BootstrapError


@dataclass(frozen=True)
class BootstrapResult:
    """Outcome of bootstrapping a new project."""

    name: str
    """Project name."""
    target_dir: Path
    """Absolute path to the created project directory."""
    placeholders_replaced: int
    """Number of placeholder substitutions performed."""
    files_renamed: int
    """Number of files and directories renamed."""
    git_initialized: bool
    """Whether a git repository was initialized."""


@dataclass(frozen=True)
class BootstrapRequest:
    """Validated request for creating a project from a workspace template."""

    name: str
    """Project name."""
    description: str
    """One-line project description."""
    template_source: Path
    """Absolute path to the template directory."""
    target_dir: Path
    """Absolute path to the target directory."""
    template: TemplateConfig
    """Template configuration from the manifest."""
    defaults: EcosystemDefaults
    """Ecosystem-level defaults from the manifest."""
    initialize_git: bool = True
    """Whether to initialize a git repository."""
    dry_run: bool = False
    """Whether to skip side effects."""


@dataclass(frozen=True)
class WorkspaceBootstrapRequest:
    """High-level request for bootstrapping a project within a workspace."""

    manifest_dir: Path
    """Absolute root of the workspace, against which the paths of the manifest are resolved."""
    name: str
    """Project name."""
    description: str
    """One-line project description."""
    template: TemplateConfig
    """Template configuration from the manifest."""
    defaults: EcosystemDefaults
    """Ecosystem-level defaults from the manifest."""
    discovery_scan_dirs: tuple[str, ...]
    """Scan directories declared in the manifest discovery section."""
    parent_dir: Path | None = None
    """Folder that receives the new project; one of the scan directories. Defaults to the first."""
    initialize_git: bool = True
    """Whether to initialize a git repository."""
    dry_run: bool = False
    """Whether to skip side effects."""


@dataclass(frozen=True)
class PlaceholderBindings:
    """Resolved template placeholder bindings."""

    mappings: dict[str, str]
    """Placeholder-to-value mapping."""

    def as_dict(self) -> dict[str, str]:
        """Return a plain dict copy of the bindings.

        Returns
        -------
        dict[str, str]
            Shallow copy of the placeholder-to-value mapping.
        """
        return dict(self.mappings)

    def __getitem__(self, key: str) -> str:
        return self.mappings[key]

    def __contains__(self, key: object) -> bool:
        return key in self.mappings

    def __iter__(self):
        return iter(self.mappings)

    def __len__(self) -> int:
        return len(self.mappings)


@dataclass(frozen=True)
class BootstrapServices:
    """Injected infrastructure for the project bootstrap workflow."""

    read_git_identity: Callable[[], tuple[str, str]]
    """Read the git user name and email."""
    copy_template: Callable[[Path, Path], None]
    """Copy a template directory to a target directory."""
    substitute_directory: Callable[
        [Path, dict[str, str], tuple[str, str], tuple[str, ...]], int
    ]
    """Substitute placeholders in all files under a directory."""
    rename_paths: Callable[[Path, dict[str, str], dict[str, str], tuple[str, str]], int]
    """Rename files and directories using the bindings."""
    init_repository: Callable[[Path], None]
    """Initialize a git repository in the given directory."""


def plan_bootstrap_request(request: WorkspaceBootstrapRequest) -> BootstrapRequest:
    """Resolve manifest-relative bootstrap paths into an executable request.

    Parameters
    ----------
    request : WorkspaceBootstrapRequest
        High-level workspace-scoped bootstrap request.

    Returns
    -------
    BootstrapRequest
        Executable bootstrap request with resolved paths.
    """
    if not request.discovery_scan_dirs:
        raise BootstrapError(
            "Manifest discovery.scan_dirs must contain at least one scan directory."
        )
    if not request.template.source:
        raise BootstrapError(
            "Manifest template.source must name the project template directory."
        )
    scan_dirs = tuple(
        (request.manifest_dir / scan_dir).resolve() for scan_dir in request.discovery_scan_dirs
    )
    if request.parent_dir is None:
        scan_dir = scan_dirs[0]
    else:
        scan_dir = request.parent_dir.resolve()
        if scan_dir not in scan_dirs:
            choices = ", ".join(str(path) for path in scan_dirs)
            raise BootstrapError(
                f"The parent folder {scan_dir} is not a discovery scan directory of the manifest; "
                f"expected one of: {choices}."
            )
    target_dir = scan_dir / request.name
    template_source = (request.manifest_dir / request.template.source).resolve()
    return BootstrapRequest(
        name=request.name,
        description=request.description,
        template_source=template_source,
        target_dir=target_dir,
        template=request.template,
        defaults=request.defaults,
        initialize_git=request.initialize_git,
        dry_run=request.dry_run,
    )


def build_placeholder_bindings(
    name: str,
    description: str,
    defaults: EcosystemDefaults,
    author_name: str = "",
    author_email: str = "",
) -> PlaceholderBindings:
    """Build the placeholder-to-value mapping for template substitution.

    Parameters
    ----------
    name : str
        Project name (used as package_name, repo_name, env_name, project_name).
    description : str
        One-line project description.
    defaults : EcosystemDefaults
        Ecosystem-level defaults from the manifest.
    author_name : str
        Author full name (typically from git config).
    author_email : str
        Author email (typically from git config).

    Returns
    -------
    PlaceholderBindings
        Resolved placeholder bindings for template substitution.
    """
    bindings: dict[str, str] = {
        "package_name": name,
        "repo_name": name,
        "project_name": name,
        "env_name": name,
        "description": description,
        "github_user": defaults.github_user,
        "channel_name": defaults.channel_name,
        "license": defaults.license,
    }
    if author_name:
        bindings["author_name"] = author_name
        first = author_name.split()[0] if author_name.split() else ""
        last = author_name.split()[-1] if author_name.split() else ""
        bindings["first_name"] = first
        bindings["last_name"] = last
    if author_email:
        bindings["email"] = author_email
        bindings["contact@example.com"] = author_email
    return PlaceholderBindings(mappings=bindings)


def bootstrap_project(
    request: BootstrapRequest,
    services: BootstrapServices,
) -> BootstrapResult:
    """Bootstrap a new project from the template via injected infrastructure.

    Parameters
    ----------
    request : BootstrapRequest
        Validated bootstrap parameters.
    services : BootstrapServices
        Injected infrastructure collaborators.

    Returns
    -------
    BootstrapResult
        Outcome of the bootstrap operation.
    """
    if not re.match(r"^[a-z][a-z0-9_]*$", request.name):
        raise BootstrapError(
            "Name must start with a lowercase letter and contain only lowercase letters, digits, and underscores."
        )
    if not request.template_source.is_dir():
        raise BootstrapError(f"Template source not found: {request.template_source}")
    if request.target_dir.exists():
        raise BootstrapError(f"Directory already exists: {request.target_dir}")
    if request.dry_run:
        return BootstrapResult(
            name=request.name,
            target_dir=request.target_dir,
            placeholders_replaced=0,
            files_renamed=0,
            git_initialized=False,
        )

    author_name, author_email = services.read_git_identity()
    bindings = build_placeholder_bindings(
        request.name,
        request.description,
        request.defaults,
        author_name,
        author_email,
    )
    services.copy_template(request.template_source, request.target_dir)
    replaced = services.substitute_directory(
        request.target_dir,
        bindings.as_dict(),
        request.template.delimiters,
        request.template.exclude_patterns,
    )
    renamed = services.rename_paths(
        request.target_dir,
        request.template.renames,
        bindings.as_dict(),
        request.template.delimiters,
    )
    git_initialized = False
    if request.initialize_git:
        services.init_repository(request.target_dir)
        git_initialized = True
    return BootstrapResult(
        name=request.name,
        target_dir=request.target_dir,
        placeholders_replaced=replaced,
        files_renamed=renamed,
        git_initialized=git_initialized,
    )


def bootstrap_workspace_project(
    request: WorkspaceBootstrapRequest,
    services: BootstrapServices,
) -> BootstrapResult:
    """Bootstrap a new project from a workspace-scoped request.

    Parameters
    ----------
    request : WorkspaceBootstrapRequest
        High-level workspace-scoped bootstrap request.
    services : BootstrapServices
        Injected infrastructure collaborators.

    Returns
    -------
    BootstrapResult
        Outcome of the bootstrap operation.
    """
    return bootstrap_project(plan_bootstrap_request(request), services)
