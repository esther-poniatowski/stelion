"""Composition root: constructs infrastructure and wires use-cases.

All infrastructure objects are built here and injected into application
use-cases.  CLI commands import this module instead of constructing
infrastructure themselves.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .application.bootstrap import BootstrapServices
from .application.discovery import discover_projects
from .application.environment import build_shared_environment
from .application.generation import GenerationResult, compute_drift, generate_all
from .application.graph import build_dependency_graph
from .application.sync import execute_sync, plan_sync, resolve_submodule_targets
from .application.protocols import (
    DependencyScanner,
    DependencyYamlRenderer,
    EnvironmentReader,
    EnvironmentRenderer,
    FileHasher,
    FileReader,
    FileWriter,
    MetadataExtractor,
    ProjectsYamlRenderer,
    WorkspaceFileRenderer,
)
from .domain.dependency import DependencyGraph
from .domain.environment import EnvironmentSpec
from .domain.manifest import WorkspaceManifest
from .domain.project import ProjectInventory
from .domain.status import DriftReport
from .domain.sync import SyncOrigin, SyncResult
from .infrastructure.environment_parser import CondaEnvironmentReader
from .infrastructure.bootstrap_git import init_repository, read_git_identity
from .infrastructure.dependency_scanners import (
    EditablePipDependencyScanner,
    GitmodulesDependencyScanner,
)
from .infrastructure.file_ops import LocalFileReader, LocalFileWriter, SHA256Hasher
from .infrastructure.git_operations import SubprocessGitOperations
from .infrastructure.manifest_loader import load_manifest
from .infrastructure.pyproject_parser import PyprojectExtractor
from .infrastructure.renderers.vscode import render_workspace_file
from .infrastructure.template_engine import copy_template, rename_paths, substitute_in_directory
from .infrastructure.renderers.yaml import (
    render_dependency_yaml,
    render_environment,
    render_projects_yaml,
)


@dataclass(frozen=True)
class WorkspaceServices:
    """Container holding all wired infrastructure implementations."""

    extractor: MetadataExtractor
    env_reader: EnvironmentReader
    dependency_scanners: tuple[DependencyScanner, ...]
    writer: FileWriter
    reader: FileReader
    hasher: FileHasher
    render_workspace_file: WorkspaceFileRenderer
    render_projects_yaml: ProjectsYamlRenderer
    render_dependency_yaml: DependencyYamlRenderer
    render_environment: EnvironmentRenderer


def create_services() -> WorkspaceServices:
    """Build and return the full set of workspace infrastructure services."""
    return WorkspaceServices(
        extractor=PyprojectExtractor(),
        env_reader=CondaEnvironmentReader(),
        dependency_scanners=(
            EditablePipDependencyScanner(CondaEnvironmentReader()),
            GitmodulesDependencyScanner(),
        ),
        writer=LocalFileWriter(),
        reader=LocalFileReader(),
        hasher=SHA256Hasher(),
        render_workspace_file=render_workspace_file,
        render_projects_yaml=render_projects_yaml,
        render_dependency_yaml=render_dependency_yaml,
        render_environment=render_environment,
    )


def create_bootstrap_services() -> BootstrapServices:
    """Build the injected services for workspace project bootstrapping."""
    return BootstrapServices(
        read_git_identity=read_git_identity,
        copy_template=copy_template,
        substitute_directory=lambda root, bindings, patterns: substitute_in_directory(
            root,
            bindings,
            patterns,
        ),
        rename_paths=rename_paths,
        init_repository=init_repository,
    )


def resolve_manifest(manifest_path: Path) -> WorkspaceManifest:
    """Load and return a validated workspace manifest."""
    return load_manifest(manifest_path.resolve())


@dataclass(frozen=True)
class WorkspaceContext:
    """Fully resolved workspace state: manifest + discovered data."""

    manifest: WorkspaceManifest
    inventory: ProjectInventory
    graph: DependencyGraph
    environment: EnvironmentSpec


def build_workspace_context(
    manifest: WorkspaceManifest,
    services: WorkspaceServices,
) -> WorkspaceContext:
    """Discover projects, build the dependency graph, and merge environments."""
    inventory = discover_projects(
        manifest.discovery, services.extractor, manifest.manifest_dir,
    )
    graph = build_dependency_graph(manifest, inventory, services.dependency_scanners)
    environment = build_shared_environment(manifest, inventory, services.env_reader)
    return WorkspaceContext(
        manifest=manifest,
        inventory=inventory,
        graph=graph,
        environment=environment,
    )


def run_generate(
    ctx: WorkspaceContext,
    services: WorkspaceServices,
    force: bool = False,
) -> list[GenerationResult]:
    """Generate all workspace artifacts."""
    return generate_all(
        manifest=ctx.manifest,
        inventory=ctx.inventory,
        graph=ctx.graph,
        environment=ctx.environment,
        render_workspace_file=services.render_workspace_file,
        render_projects_yaml=services.render_projects_yaml,
        render_dependency_yaml=services.render_dependency_yaml,
        render_environment=services.render_environment,
        writer=services.writer,
        reader=services.reader,
        hasher=services.hasher,
        force=force,
    )


def run_drift_check(
    ctx: WorkspaceContext,
    services: WorkspaceServices,
) -> DriftReport:
    """Compute drift without writing any files."""
    return compute_drift(
        manifest=ctx.manifest,
        inventory=ctx.inventory,
        graph=ctx.graph,
        environment=ctx.environment,
        render_workspace_file=services.render_workspace_file,
        render_projects_yaml=services.render_projects_yaml,
        render_dependency_yaml=services.render_dependency_yaml,
        render_environment=services.render_environment,
        reader=services.reader,
        hasher=services.hasher,
    )


def target_paths(manifest: WorkspaceManifest) -> list[Path]:
    """List all generation target output paths."""
    return [
        manifest.manifest_dir / manifest.generate.workspace_file.output,
        manifest.manifest_dir / manifest.generate.projects_registry.output,
        manifest.manifest_dir / manifest.generate.dependency_graph.output,
        manifest.manifest_dir / manifest.generate.shared_environment.output,
    ]


# --- Submodule synchronization -----------------------------------------------


def create_git_operations() -> SubprocessGitOperations:
    """Build the git operations infrastructure for submodule sync."""
    return SubprocessGitOperations()


def run_submodule_sync(
    ctx: WorkspaceContext,
    dependency: str,
    origin: SyncOrigin,
    *,
    source_superproject: str | None = None,
    remote: str = "origin",
    branch: str = "main",
    commit: bool = True,
    dry_run: bool = False,
) -> SyncResult:
    """Resolve, plan, and execute a submodule sync for a dependency."""
    git = create_git_operations()

    targets = resolve_submodule_targets(dependency, ctx.graph, ctx.manifest)

    plan = plan_sync(
        dependency=dependency,
        targets=targets,
        inventory=ctx.inventory,
        origin=origin,
        git=git,
        source_superproject=source_superproject,
        remote=remote,
        branch=branch,
    )

    return execute_sync(plan, git, commit=commit, dry_run=dry_run)
