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
    target_dir: Path
    placeholders_replaced: int
    files_renamed: int
    git_initialized: bool


@dataclass(frozen=True)
class BootstrapRequest:
    """Validated request for creating a project from a workspace template."""

    name: str
    description: str
    template_source: Path
    target_dir: Path
    template: TemplateConfig
    defaults: EcosystemDefaults
    initialize_git: bool = True
    dry_run: bool = False


@dataclass(frozen=True)
class WorkspaceBootstrapRequest:
    """High-level request for bootstrapping a project within a workspace."""

    manifest_dir: Path
    name: str
    description: str
    template: TemplateConfig
    defaults: EcosystemDefaults
    discovery_scan_dirs: tuple[str, ...]
    initialize_git: bool = True
    dry_run: bool = False


@dataclass(frozen=True)
class BootstrapServices:
    """Injected infrastructure for the project bootstrap workflow."""

    read_git_identity: Callable[[], tuple[str, str]]
    copy_template: Callable[[Path, Path], None]
    substitute_directory: Callable[[Path, dict[str, str], tuple[str, ...]], int]
    rename_paths: Callable[[Path, dict[str, str], dict[str, str]], int]
    init_repository: Callable[[Path], None]


def plan_bootstrap_request(request: WorkspaceBootstrapRequest) -> BootstrapRequest:
    """Resolve manifest-relative bootstrap paths into an executable request."""
    if not request.discovery_scan_dirs:
        raise BootstrapError("Manifest discovery.scan_dirs must contain at least one scan directory.")
    scan_dir = (request.manifest_dir / request.discovery_scan_dirs[0]).resolve()
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
) -> dict[str, str]:
    """Build the placeholder-to-value mapping for template substitution.

    Parameters
    ----------
    name
        Project name (used as package_name, repo_name, env_name, project_name).
    description
        One-line project description.
    defaults
        Ecosystem-level defaults from the manifest.
    author_name
        Author full name (typically from git config).
    author_email
        Author email (typically from git config).
    """
    bindings = {
        "{{ package_name }}": name,
        "{{ repo_name }}": name,
        "{{ project_name }}": name,
        "{{ env_name }}": name,
        "{{ description }}": description,
        "{{ github_user }}": defaults.github_user,
        "{{ channel_name }}": defaults.channel_name,
        "{{ license }}": defaults.license,
    }
    if author_name:
        bindings["{{ author_name }}"] = author_name
        first = author_name.split()[0] if author_name.split() else ""
        last = author_name.split()[-1] if author_name.split() else ""
        bindings["{{ first_name }}"] = first
        bindings["{{ last_name }}"] = last
    if author_email:
        bindings["{{ email }}"] = author_email
        bindings["{{ contact@example.com }}"] = author_email
    return bindings


def bootstrap_project(
    request: BootstrapRequest,
    services: BootstrapServices,
) -> BootstrapResult:
    """Bootstrap a new project from the template via injected infrastructure."""
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
        bindings,
        request.template.exclude_patterns,
    )
    renamed = services.rename_paths(
        request.target_dir,
        request.template.renames,
        bindings,
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
    """Bootstrap a new project from a workspace-scoped request."""
    return bootstrap_project(plan_bootstrap_request(request), services)
