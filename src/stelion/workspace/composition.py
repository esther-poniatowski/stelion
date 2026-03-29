"""Composition root: constructs infrastructure and wires use-cases."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .application.bootstrap import BootstrapServices
from .application.bulk import execute_bulk, select_projects
from .application.comparison import compare_files, compare_trees
from .application.discovery import discover_projects
from .application.environment import build_shared_environment
from .application.generation import (
    GenerationArtifact,
    GenerationResult,
    compute_drift,
    generate_all,
)
from .application.graph import build_dependency_graph
from .application.manifest_init import (
    ManifestInitResult,
    ManifestInitServices,
    initialize_default_manifest,
)
from .application.protocols import (
    BulkOperation,
    DependencyScanner,
    DependencyYamlRenderer,
    EnvironmentReader,
    EnvironmentRenderer,
    FileHasher,
    FileReader,
    FileWriter,
    MetadataExtractor,
    ProjectsYamlRenderer,
    SpecLoader,
    StructuredParser,
    TreeScanner,
    WorkspaceFileRenderer,
)
from .application.registration import apply_registration, register_project
from .application.sync import execute_sync, plan_sync, resolve_submodule_targets
from .domain.bulk import BulkResult
from .domain.comparison import FileReport, FileTarget, TreeReport, TreeTarget
from .domain.dependency import DependencyGraph
from .domain.environment import EnvironmentSpec
from .domain.manifest import WorkspaceManifest
from .domain.project import ProjectInventory, ProjectMetadata
from .domain.status import DriftReport
from .domain.sync import SyncOrigin, SyncResult
from .exceptions import WorkspaceError
from .infrastructure.bootstrap_git import init_repository, read_git_identity
from .infrastructure.bulk_operations import GitCommitOperation, GitPushOperation, ShellOperation
from .infrastructure.command_runner import SubprocessCommandRunner
from .infrastructure.data_loader import StelionDataLoader
from .infrastructure.dependency_scanners import (
    EditablePipDependencyScanner,
    GitmodulesDependencyScanner,
)
from .infrastructure.environment_parser import CondaEnvironmentReader
from .infrastructure.file_ops import LocalFileReader, LocalFileWriter, SHA256Hasher
from .infrastructure.git_operations import SubprocessGitOperations
from .infrastructure.manifest_codec import default_workspace_manifest, render_manifest
from .infrastructure.manifest_loader import load_manifest
from .infrastructure.pyproject_parser import PyprojectExtractor
from .infrastructure.renderers.vscode import VSCodeWorkspaceFileRenderer
from .infrastructure.renderers.yaml import (
    render_dependency_yaml,
    render_environment,
    render_projects_yaml,
)
from .infrastructure.spec_loader import YamlSpecLoader
from .infrastructure.structured_parsers import (
    DispatchingParser,
    JsonParser,
    MarkdownSectionParser,
    TomlParser,
    YamlParser,
)
from .infrastructure.template_engine import (
    copy_template,
    rename_paths as rename_template_paths,
    substitute_in_directory,
)
from .infrastructure.tree_scanner import LocalTreeScanner


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


@dataclass(frozen=True)
class WorkspaceContext:
    """Fully resolved workspace state: manifest + discovered data."""

    manifest: WorkspaceManifest
    inventory: ProjectInventory
    graph: DependencyGraph
    environment: EnvironmentSpec


@dataclass(frozen=True)
class WorkspaceRegistrationResult:
    """Result of registering a project into the workspace and regenerating artifacts."""

    manifest: WorkspaceManifest
    project: ProjectMetadata
    manifest_updated: bool
    generated: tuple[GenerationResult, ...]


def create_services() -> WorkspaceServices:
    """Build and return the full set of workspace infrastructure services."""
    extractor = PyprojectExtractor()
    env_reader = CondaEnvironmentReader()
    data_loader = StelionDataLoader()
    return WorkspaceServices(
        extractor=extractor,
        env_reader=env_reader,
        dependency_scanners=(
            EditablePipDependencyScanner(env_reader),
            GitmodulesDependencyScanner(),
        ),
        writer=LocalFileWriter(),
        reader=LocalFileReader(),
        hasher=SHA256Hasher(),
        render_workspace_file=VSCodeWorkspaceFileRenderer(data_loader),
        render_projects_yaml=render_projects_yaml,
        render_dependency_yaml=render_dependency_yaml,
        render_environment=render_environment,
    )


def create_bootstrap_services() -> BootstrapServices:
    """Build the injected services for workspace project bootstrapping."""
    return BootstrapServices(
        read_git_identity=read_git_identity,
        copy_template=copy_template,
        substitute_directory=substitute_in_directory,
        rename_paths=rename_template_paths,
        init_repository=init_repository,
    )


def create_manifest_init_services(writer: FileWriter) -> ManifestInitServices:
    """Build the collaborators for initializing a workspace manifest."""
    return ManifestInitServices(
        read_git_identity=read_git_identity,
        build_default_manifest=default_workspace_manifest,
        render_manifest=render_manifest,
        write_manifest=writer.write,
    )


def resolve_manifest(manifest_path: Path) -> WorkspaceManifest:
    """Load and return a validated workspace manifest."""
    return load_manifest(manifest_path.resolve())


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


def initialize_workspace_manifest(
    manifest_path: Path,
    services: WorkspaceServices,
    *,
    dry_run: bool = False,
) -> ManifestInitResult:
    """Create and optionally write a default manifest for a new workspace."""
    manifest_services = create_manifest_init_services(services.writer)
    return initialize_default_manifest(
        manifest_path,
        services.extractor,
        manifest_services,
        dry_run=dry_run,
    )


def run_generate(
    ctx: WorkspaceContext,
    services: WorkspaceServices,
    force: bool = False,
    selected_targets: tuple[GenerationArtifact, ...] = (),
) -> list[GenerationResult]:
    """Generate all or a selected subset of workspace artifacts."""
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
        selected_targets=selected_targets,
    )


def run_drift_check(
    ctx: WorkspaceContext,
    services: WorkspaceServices,
    selected_targets: tuple[GenerationArtifact, ...] = (),
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
        selected_targets=selected_targets,
    )


def target_paths(
    manifest: WorkspaceManifest,
    selected_targets: tuple[GenerationArtifact, ...] = (),
) -> list[Path]:
    """List generation target output paths."""
    all_targets = {
        GenerationArtifact.WORKSPACE_FILE: manifest.manifest_dir / manifest.generate.workspace_file.output,
        GenerationArtifact.PROJECTS: manifest.manifest_dir / manifest.generate.projects_registry.output,
        GenerationArtifact.DEPENDENCIES: manifest.manifest_dir / manifest.generate.dependency_graph.output,
        GenerationArtifact.ENVIRONMENT: manifest.manifest_dir / manifest.generate.shared_environment.output,
    }
    if not selected_targets:
        return list(all_targets.values())
    wanted = set(selected_targets)
    return [path for artifact, path in all_targets.items() if artifact in wanted]


def register_workspace_project(
    manifest_path: Path,
    project_dir: Path,
    services: WorkspaceServices,
) -> WorkspaceRegistrationResult:
    """Register a project, persist manifest updates, and regenerate artifacts."""
    manifest_path = manifest_path.resolve()
    manifest = resolve_manifest(manifest_path)
    ctx = build_workspace_context(manifest, services)
    project = register_project(project_dir.resolve(), services.extractor)
    registration = apply_registration(manifest, ctx.inventory, project)

    effective_manifest = registration.manifest
    if registration.manifest_updated:
        services.writer.write(manifest_path, render_manifest(effective_manifest))

    updated_ctx = build_workspace_context(effective_manifest, services)
    if project.path.resolve() not in updated_ctx.inventory.by_path():
        raise WorkspaceError(
            f"Registered project at {project.path} is still not discoverable after updating the manifest."
        )

    generated = tuple(run_generate(updated_ctx, services))
    return WorkspaceRegistrationResult(
        manifest=effective_manifest,
        project=registration.project,
        manifest_updated=registration.manifest_updated,
        generated=generated,
    )


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


def create_command_runner() -> SubprocessCommandRunner:
    """Build the command runner infrastructure for bulk operations."""
    return SubprocessCommandRunner()


def run_bulk_exec(
    ctx: WorkspaceContext,
    command: str,
    *,
    names: tuple[str, ...] = (),
    pattern: str | None = None,
    git_only: bool = False,
    exclude: tuple[str, ...] = (),
    dry_run: bool = False,
) -> BulkResult:
    """Select projects and run an arbitrary shell command on each."""
    runner = create_command_runner()
    return _run_bulk(
        ctx,
        ShellOperation(command, runner),
        names=names,
        pattern=pattern,
        git_only=git_only,
        exclude=exclude,
        dry_run=dry_run,
    )


def run_bulk_commit(
    ctx: WorkspaceContext,
    message: str,
    *,
    names: tuple[str, ...] = (),
    pattern: str | None = None,
    git_only: bool = False,
    exclude: tuple[str, ...] = (),
    dry_run: bool = False,
) -> BulkResult:
    """Select projects and commit tracked changes on each."""
    runner = create_command_runner()
    return _run_bulk(
        ctx,
        GitCommitOperation(message, runner),
        names=names,
        pattern=pattern,
        git_only=git_only,
        exclude=exclude,
        dry_run=dry_run,
    )


def run_bulk_push(
    ctx: WorkspaceContext,
    *,
    remote: str = "origin",
    branch: str = "main",
    names: tuple[str, ...] = (),
    pattern: str | None = None,
    git_only: bool = False,
    exclude: tuple[str, ...] = (),
    dry_run: bool = False,
) -> BulkResult:
    """Select projects and push to remote on each."""
    runner = create_command_runner()
    return _run_bulk(
        ctx,
        GitPushOperation(remote, branch, runner),
        names=names,
        pattern=pattern,
        git_only=git_only,
        exclude=exclude,
        dry_run=dry_run,
    )


def _run_bulk(
    ctx: WorkspaceContext,
    operation: BulkOperation,
    *,
    names: tuple[str, ...],
    pattern: str | None,
    git_only: bool,
    exclude: tuple[str, ...],
    dry_run: bool,
) -> BulkResult:
    """Resolve the target project set and execute a bulk operation."""
    projects = select_projects(
        ctx.inventory,
        names=names,
        pattern=pattern,
        git_only=git_only,
        exclude=exclude,
    )
    return execute_bulk(projects, operation, dry_run=dry_run)


# --- Comparison ---------------------------------------------------------------


@dataclass(frozen=True)
class ComparisonServices:
    """Container for cross-project comparison infrastructure."""

    scanner: TreeScanner
    parser: StructuredParser
    spec_loader: SpecLoader
    reader: FileReader


def create_comparison_services() -> ComparisonServices:
    """Build the infrastructure services for comparison operations."""
    return ComparisonServices(
        scanner=LocalTreeScanner(),
        parser=DispatchingParser({
            ".toml": TomlParser(),
            ".yaml": YamlParser(),
            ".yml": YamlParser(),
            ".json": JsonParser(),
            ".md": MarkdownSectionParser(),
        }),
        spec_loader=YamlSpecLoader(),
        reader=LocalFileReader(),
    )


def run_compare_trees(
    ctx: WorkspaceContext,
    services: ComparisonServices,
    target: TreeTarget,
    *,
    names: tuple[str, ...] = (),
    pattern: str | None = None,
    git_only: bool = False,
    exclude: tuple[str, ...] = (),
) -> TreeReport:
    """Select projects and compare their directory structures."""
    projects = _select_comparison_projects(
        ctx, names=names, pattern=pattern, git_only=git_only, exclude=exclude,
    )
    return compare_trees(projects, target, services.scanner)


def run_compare_files(
    ctx: WorkspaceContext,
    services: ComparisonServices,
    target: FileTarget,
    *,
    names: tuple[str, ...] = (),
    pattern: str | None = None,
    git_only: bool = False,
    exclude: tuple[str, ...] = (),
) -> FileReport:
    """Select projects and compare specific files across them."""
    projects = _select_comparison_projects(
        ctx, names=names, pattern=pattern, git_only=git_only, exclude=exclude,
    )
    return compare_files(projects, target, services.reader, services.parser)


def _select_comparison_projects(
    ctx: WorkspaceContext,
    *,
    names: tuple[str, ...],
    pattern: str | None,
    git_only: bool,
    exclude: tuple[str, ...],
) -> tuple[ProjectMetadata, ...]:
    """Select and validate that at least 2 projects are available."""
    projects = select_projects(
        ctx.inventory, names=names, pattern=pattern, git_only=git_only, exclude=exclude,
    )
    if len(projects) < 2:
        raise WorkspaceError("Comparison requires at least 2 projects.")
    return projects
