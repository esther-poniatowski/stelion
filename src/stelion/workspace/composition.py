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
    compute_artifact_specs,
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
    GenerationServices,
    MetadataExtractor,
    ProjectsYamlRenderer,
    SpecLoader,
    StructuredParser,
    TreeScanner,
    WorkspaceFileRenderer,
)
from .application.registration import execute_registration
from .application.sync import execute_sync, plan_sync, resolve_submodule_targets
from .domain.bulk import BulkResult, ProjectFilter
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
    reader = LocalFileReader()
    return WorkspaceServices(
        extractor=extractor,
        env_reader=env_reader,
        dependency_scanners=(
            EditablePipDependencyScanner(env_reader),
            GitmodulesDependencyScanner(),
        ),
        writer=LocalFileWriter(),
        reader=reader,
        hasher=SHA256Hasher(),
        render_workspace_file=VSCodeWorkspaceFileRenderer(data_loader, reader=reader),
        render_projects_yaml=render_projects_yaml,
        render_dependency_yaml=render_dependency_yaml,
        render_environment=render_environment,
    )


def _make_generation_services(services: WorkspaceServices) -> GenerationServices:
    """Assemble a ``GenerationServices`` bundle from ``WorkspaceServices``."""
    return GenerationServices(
        render_workspace_file=services.render_workspace_file,
        render_projects_yaml=services.render_projects_yaml,
        render_dependency_yaml=services.render_dependency_yaml,
        render_environment=services.render_environment,
        writer=services.writer,
        reader=services.reader,
        hasher=services.hasher,
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
    """Discover projects, build the dependency graph, and merge environments.

    Pre-reads each project's environment spec exactly once and shares those
    specs with the dependency-graph builder and the shared-environment merger.
    """
    inventory = discover_projects(
        manifest.discovery, services.extractor, manifest.manifest_dir,
    )

    # Pre-read environment specs once; pass to both subsystems.
    env_specs: dict[str, EnvironmentSpec | None] = {}
    for project in inventory.projects:
        try:
            env_specs[project.name] = services.env_reader.read(project.path)
        except Exception:
            env_specs[project.name] = None

    graph = build_dependency_graph(manifest, inventory, services.dependency_scanners)
    environment = build_shared_environment(
        manifest, inventory, services.env_reader, env_specs=env_specs,
    )
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
    generation_services: GenerationServices | None = None,
) -> list[GenerationResult]:
    """Generate all or a selected subset of workspace artifacts."""
    gen_services = generation_services or _make_generation_services(services)
    return generate_all(
        manifest=ctx.manifest,
        inventory=ctx.inventory,
        graph=ctx.graph,
        environment=ctx.environment,
        services=gen_services,
        force=force,
        selected_targets=selected_targets,
    )


def run_drift_check(
    ctx: WorkspaceContext,
    services: WorkspaceServices,
    selected_targets: tuple[GenerationArtifact, ...] = (),
    generation_services: GenerationServices | None = None,
) -> DriftReport:
    """Compute drift without writing any files."""
    gen_services = generation_services or _make_generation_services(services)
    return compute_drift(
        manifest=ctx.manifest,
        inventory=ctx.inventory,
        graph=ctx.graph,
        environment=ctx.environment,
        services=gen_services,
        selected_targets=selected_targets,
    )


def target_output_paths(
    manifest: WorkspaceManifest,
    selected_targets: tuple[GenerationArtifact, ...] = (),
) -> list[Path]:
    """List generation target output paths using ``compute_artifact_specs``."""
    specs = compute_artifact_specs(manifest)
    if not selected_targets:
        return [spec.output_path for spec in specs.values()]
    wanted = set(selected_targets)
    return [spec.output_path for artifact, spec in specs.items() if artifact in wanted]


def target_paths(
    manifest: WorkspaceManifest,
    selected_targets: tuple[GenerationArtifact, ...] = (),
) -> list[Path]:
    """List generation target output paths (backward-compatible alias)."""
    return target_output_paths(manifest, selected_targets)


def register_workspace_project(
    manifest_path: Path,
    project_dir: Path,
    services: WorkspaceServices,
) -> WorkspaceRegistrationResult:
    """Register a project, persist manifest updates, and regenerate artifacts.

    Thin wiring function that delegates orchestration to
    ``application.registration.execute_registration``. Provides the
    infrastructure callbacks (discovery, context build + generate,
    manifest persistence).
    """
    manifest_path = manifest_path.resolve()
    manifest = resolve_manifest(manifest_path)

    def _discover(m: WorkspaceManifest) -> ProjectInventory:
        return discover_projects(
            m.discovery, services.extractor, m.manifest_dir,
        )

    def _build_and_generate(
        m: WorkspaceManifest,
    ) -> tuple[ProjectInventory, tuple[GenerationResult, ...]]:
        ctx = build_workspace_context(m, services)
        generated = tuple(run_generate(ctx, services))
        return ctx.inventory, generated

    def _persist(path: Path, m: WorkspaceManifest) -> None:
        services.writer.write(path, render_manifest(m))

    result = execute_registration(
        manifest_path=manifest_path,
        project_dir=project_dir,
        manifest=manifest,
        extractor=services.extractor,
        discover=_discover,
        build_context_and_generate=_build_and_generate,
        persist_manifest=_persist,
    )
    return WorkspaceRegistrationResult(
        manifest=result.manifest,
        project=result.project,
        manifest_updated=result.manifest_updated,
        generated=result.generated,
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
    targets = resolve_submodule_targets(
        dependency, ctx.graph, ctx.manifest, inventory=ctx.inventory,
    )
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
    filter_: ProjectFilter | None = None,
    dry_run: bool = False,
) -> BulkResult:
    """Select projects and run an arbitrary shell command on each."""
    runner = create_command_runner()
    return _run_bulk(
        ctx,
        ShellOperation(command, runner),
        filter_=filter_ or ProjectFilter(),
        dry_run=dry_run,
    )


def run_bulk_commit(
    ctx: WorkspaceContext,
    message: str,
    *,
    filter_: ProjectFilter | None = None,
    dry_run: bool = False,
) -> BulkResult:
    """Select projects and commit tracked changes on each."""
    runner = create_command_runner()
    return _run_bulk(
        ctx,
        GitCommitOperation(message, runner),
        filter_=filter_ or ProjectFilter(),
        dry_run=dry_run,
    )


def run_bulk_push(
    ctx: WorkspaceContext,
    *,
    remote: str = "origin",
    branch: str = "main",
    filter_: ProjectFilter | None = None,
    dry_run: bool = False,
) -> BulkResult:
    """Select projects and push to remote on each."""
    runner = create_command_runner()
    return _run_bulk(
        ctx,
        GitPushOperation(remote, branch, runner),
        filter_=filter_ or ProjectFilter(),
        dry_run=dry_run,
    )


def _run_bulk(
    ctx: WorkspaceContext,
    operation: BulkOperation,
    *,
    filter_: ProjectFilter,
    dry_run: bool,
) -> BulkResult:
    """Resolve the target project set and execute a bulk operation."""
    projects = select_projects(ctx.inventory, filter_=filter_)
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
    filter_: ProjectFilter | None = None,
) -> TreeReport:
    """Select projects and compare their directory structures."""
    projects = _select_comparison_projects(ctx, filter_ or ProjectFilter())
    return compare_trees(projects, target, services.scanner)


def run_compare_files(
    ctx: WorkspaceContext,
    services: ComparisonServices,
    target: FileTarget,
    *,
    filter_: ProjectFilter | None = None,
) -> FileReport:
    """Select projects and compare specific files across them."""
    projects = _select_comparison_projects(ctx, filter_ or ProjectFilter())
    return compare_files(projects, target, services.reader, services.parser)


def _select_comparison_projects(
    ctx: WorkspaceContext,
    filter_: ProjectFilter,
) -> tuple[ProjectMetadata, ...]:
    """Select and validate that at least 2 projects are available."""
    projects = select_projects(ctx.inventory, filter_=filter_)
    if len(projects) < 2:
        raise WorkspaceError("Comparison requires at least 2 projects.")
    return projects
