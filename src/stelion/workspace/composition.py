"""Composition root: constructs infrastructure and wires use-cases.

Classes
-------
WorkspaceServices
    Container holding all wired infrastructure implementations.
WorkspaceContext
    Fully resolved workspace state: manifest + discovered data.
WorkspaceRegistrationResult
    Result of registering a project into the workspace and regenerating artifacts.
ComparisonServices
    Container for cross-project comparison infrastructure.

Functions
---------
create_services
    Build and return the full set of workspace infrastructure services.
create_bootstrap_services
    Build the injected services for workspace project bootstrapping.
create_manifest_init_services
    Build the collaborators for initializing a workspace manifest.
resolve_manifest
    Load and return a validated workspace manifest.
build_workspace_context
    Discover projects, build the dependency graph, and merge environments.
initialize_workspace_manifest
    Create and optionally write a default manifest for a new workspace.
run_generate
    Generate all or a selected subset of workspace artifacts.
run_drift_check
    Compute drift without writing any files.
target_output_paths
    List generation target output paths using ``compute_artifact_specs``.
target_paths
    List generation target output paths (backward-compatible alias).
register_workspace_project
    Register a project, persist manifest updates, and regenerate artifacts.
create_git_operations
    Build the git operations infrastructure for submodule sync.
run_submodule_sync
    Resolve, plan, and execute a submodule sync for a dependency.
create_command_runner
    Build the command runner infrastructure for bulk operations.
run_bulk_exec
    Select projects and run an arbitrary shell command on each.
run_bulk_commit
    Select projects and commit tracked changes on each.
run_bulk_push
    Select projects and push to remote on each.
run_compare_trees
    Select projects and compare their directory structures.
run_compare_files
    Select projects and compare specific files across them.
create_comparison_services
    Build the infrastructure services for comparison operations.
"""

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
    """Container holding all wired infrastructure implementations.

    Attributes
    ----------
    extractor : MetadataExtractor
        Extracts project metadata from project directories.
    env_reader : EnvironmentReader
        Reads Conda environment specs from project directories.
    dependency_scanners : tuple[DependencyScanner, ...]
        Scanners that detect inter-project dependency edges.
    writer : FileWriter
        Writes file content to disk.
    reader : FileReader
        Reads file content from disk.
    hasher : FileHasher
        Computes content hashes for drift detection.
    render_workspace_file : WorkspaceFileRenderer
        Renders the VS Code ``.code-workspace`` file.
    render_projects_yaml : ProjectsYamlRenderer
        Renders the projects registry YAML.
    render_dependency_yaml : DependencyYamlRenderer
        Renders the dependency graph YAML.
    render_environment : EnvironmentRenderer
        Renders the shared Conda environment YAML.
    """

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
    """Fully resolved workspace state: manifest + discovered data.

    Attributes
    ----------
    manifest : WorkspaceManifest
        The loaded workspace manifest.
    inventory : ProjectInventory
        Discovered projects in the workspace.
    graph : DependencyGraph
        Inter-project dependency graph.
    environment : EnvironmentSpec
        Merged shared environment specification.
    """

    manifest: WorkspaceManifest
    inventory: ProjectInventory
    graph: DependencyGraph
    environment: EnvironmentSpec


@dataclass(frozen=True)
class WorkspaceRegistrationResult:
    """Result of registering a project into the workspace and regenerating artifacts.

    Attributes
    ----------
    manifest : WorkspaceManifest
        The workspace manifest after registration.
    project : ProjectMetadata
        Metadata of the newly registered project.
    manifest_updated : bool
        Whether the manifest was modified during registration.
    generated : tuple[GenerationResult, ...]
        Artifacts regenerated after registration.
    """

    manifest: WorkspaceManifest
    project: ProjectMetadata
    manifest_updated: bool
    generated: tuple[GenerationResult, ...]


def create_services() -> WorkspaceServices:
    """Build and return the full set of workspace infrastructure services.

    Returns
    -------
    WorkspaceServices
        Fully wired infrastructure service container.
    """
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
    """Assemble a ``GenerationServices`` bundle from ``WorkspaceServices``.

    Parameters
    ----------
    services : WorkspaceServices
        The workspace infrastructure services to extract renderers from.

    Returns
    -------
    GenerationServices
        Bundle of generation-specific services.
    """
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
    """Build the injected services for workspace project bootstrapping.

    Returns
    -------
    BootstrapServices
        Wired bootstrap infrastructure callbacks.
    """
    return BootstrapServices(
        read_git_identity=read_git_identity,
        copy_template=copy_template,
        substitute_directory=substitute_in_directory,
        rename_paths=rename_template_paths,
        init_repository=init_repository,
    )


def create_manifest_init_services(writer: FileWriter) -> ManifestInitServices:
    """Build the collaborators for initializing a workspace manifest.

    Parameters
    ----------
    writer : FileWriter
        File writer used to persist the manifest.

    Returns
    -------
    ManifestInitServices
        Wired manifest initialization collaborators.
    """
    return ManifestInitServices(
        read_git_identity=read_git_identity,
        build_default_manifest=default_workspace_manifest,
        render_manifest=render_manifest,
        write_manifest=writer.write,
    )


def resolve_manifest(manifest_path: Path) -> WorkspaceManifest:
    """Load and return a validated workspace manifest.

    Parameters
    ----------
    manifest_path : Path
        Path to the workspace manifest file.

    Returns
    -------
    WorkspaceManifest
        The parsed and validated manifest.
    """
    return load_manifest(manifest_path.resolve())


def build_workspace_context(
    manifest: WorkspaceManifest,
    services: WorkspaceServices,
) -> WorkspaceContext:
    """Discover projects, build the dependency graph, and merge environments.

    Pre-reads each project's environment spec exactly once and shares those
    specs with the dependency-graph builder and the shared-environment merger.

    Parameters
    ----------
    manifest : WorkspaceManifest
        The workspace manifest defining discovery rules.
    services : WorkspaceServices
        Infrastructure services for project discovery and scanning.

    Returns
    -------
    WorkspaceContext
        Fully resolved workspace state with inventory, graph, and environment.
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
    """Create and optionally write a default manifest for a new workspace.

    Parameters
    ----------
    manifest_path : Path
        Destination path for the new manifest file.
    services : WorkspaceServices
        Infrastructure services providing the file writer.
    dry_run : bool
        If True, build the manifest without writing to disk.

    Returns
    -------
    ManifestInitResult
        The generated manifest, discovered inventory, and write status.
    """
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
    """Generate all or a selected subset of workspace artifacts.

    Parameters
    ----------
    ctx : WorkspaceContext
        Resolved workspace state.
    services : WorkspaceServices
        Infrastructure services for generation.
    force : bool
        If True, regenerate even when content is unchanged.
    selected_targets : tuple[GenerationArtifact, ...]
        Subset of artifacts to generate; empty means all.
    generation_services : GenerationServices | None
        Pre-built generation services; built from *services* if None.

    Returns
    -------
    list[GenerationResult]
        Results for each generated artifact.
    """
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
    """Compute drift without writing any files.

    Parameters
    ----------
    ctx : WorkspaceContext
        Resolved workspace state.
    services : WorkspaceServices
        Infrastructure services for generation.
    selected_targets : tuple[GenerationArtifact, ...]
        Subset of artifacts to check; empty means all.
    generation_services : GenerationServices | None
        Pre-built generation services; built from *services* if None.

    Returns
    -------
    DriftReport
        Report describing which artifacts have drifted.
    """
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
    """List generation target output paths using ``compute_artifact_specs``.

    Parameters
    ----------
    manifest : WorkspaceManifest
        The workspace manifest defining artifact output locations.
    selected_targets : tuple[GenerationArtifact, ...]
        Subset of artifacts to include; empty means all.

    Returns
    -------
    list[Path]
        Output paths for the selected (or all) generation targets.
    """
    specs = compute_artifact_specs(manifest)
    if not selected_targets:
        return [spec.output_path for spec in specs.values()]
    wanted = set(selected_targets)
    return [spec.output_path for artifact, spec in specs.items() if artifact in wanted]


def target_paths(
    manifest: WorkspaceManifest,
    selected_targets: tuple[GenerationArtifact, ...] = (),
) -> list[Path]:
    """List generation target output paths (backward-compatible alias).

    Parameters
    ----------
    manifest : WorkspaceManifest
        The workspace manifest defining artifact output locations.
    selected_targets : tuple[GenerationArtifact, ...]
        Subset of artifacts to include; empty means all.

    Returns
    -------
    list[Path]
        Output paths for the selected (or all) generation targets.
    """
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

    Parameters
    ----------
    manifest_path : Path
        Path to the workspace manifest file.
    project_dir : Path
        Directory of the project to register.
    services : WorkspaceServices
        Infrastructure services for discovery, generation, and persistence.

    Returns
    -------
    WorkspaceRegistrationResult
        Registration outcome including manifest, project, and generated artifacts.
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
    """Build the git operations infrastructure for submodule sync.

    Returns
    -------
    SubprocessGitOperations
        Git operations implemented via subprocess calls.
    """
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
    """Resolve, plan, and execute a submodule sync for a dependency.

    Parameters
    ----------
    ctx : WorkspaceContext
        Resolved workspace state.
    dependency : str
        Name of the dependency project to sync.
    origin : SyncOrigin
        Source of the target commit (local HEAD or remote).
    source_superproject : str | None
        Name of the superproject supplying the source commit.
    remote : str
        Git remote name to fetch from.
    branch : str
        Git branch name to resolve the remote HEAD.
    commit : bool
        If True, commit submodule pointer updates.
    dry_run : bool
        If True, plan without executing filesystem changes.

    Returns
    -------
    SyncResult
        Outcome of the sync operation.
    """
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
    """Build the command runner infrastructure for bulk operations.

    Returns
    -------
    SubprocessCommandRunner
        Command runner implemented via subprocess calls.
    """
    return SubprocessCommandRunner()


def run_bulk_exec(
    ctx: WorkspaceContext,
    command: str,
    *,
    filter_: ProjectFilter | None = None,
    dry_run: bool = False,
) -> BulkResult:
    """Select projects and run an arbitrary shell command on each.

    Parameters
    ----------
    ctx : WorkspaceContext
        Resolved workspace state.
    command : str
        Shell command to execute in each project directory.
    filter_ : ProjectFilter | None
        Optional filter to narrow the target project set.
    dry_run : bool
        If True, select projects without executing the command.

    Returns
    -------
    BulkResult
        Aggregated outcomes from all targeted projects.
    """
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
    """Select projects and commit tracked changes on each.

    Parameters
    ----------
    ctx : WorkspaceContext
        Resolved workspace state.
    message : str
        Commit message to use for each project.
    filter_ : ProjectFilter | None
        Optional filter to narrow the target project set.
    dry_run : bool
        If True, select projects without committing.

    Returns
    -------
    BulkResult
        Aggregated outcomes from all targeted projects.
    """
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
    """Select projects and push to remote on each.

    Parameters
    ----------
    ctx : WorkspaceContext
        Resolved workspace state.
    remote : str
        Git remote name to push to.
    branch : str
        Git branch name to push.
    filter_ : ProjectFilter | None
        Optional filter to narrow the target project set.
    dry_run : bool
        If True, select projects without pushing.

    Returns
    -------
    BulkResult
        Aggregated outcomes from all targeted projects.
    """
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
    """Resolve the target project set and execute a bulk operation.

    Parameters
    ----------
    ctx : WorkspaceContext
        Resolved workspace state.
    operation : BulkOperation
        Operation to execute on each selected project.
    filter_ : ProjectFilter
        Filter to narrow the target project set.
    dry_run : bool
        If True, select projects without executing the operation.

    Returns
    -------
    BulkResult
        Aggregated outcomes from all targeted projects.
    """
    projects = select_projects(ctx.inventory, filter_=filter_)
    return execute_bulk(projects, operation, dry_run=dry_run)


# --- Comparison ---------------------------------------------------------------


@dataclass(frozen=True)
class ComparisonServices:
    """Container for cross-project comparison infrastructure.

    Attributes
    ----------
    scanner : TreeScanner
        Scans project directories for file-tree snapshots.
    parser : StructuredParser
        Parses structured file content into nested dicts.
    spec_loader : SpecLoader
        Loads comparison instruction files into typed specifications.
    reader : FileReader
        Reads file content from disk.
    """

    scanner: TreeScanner
    parser: StructuredParser
    spec_loader: SpecLoader
    reader: FileReader


def create_comparison_services() -> ComparisonServices:
    """Build the infrastructure services for comparison operations.

    Returns
    -------
    ComparisonServices
        Wired comparison infrastructure container.
    """
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
    """Select projects and compare their directory structures.

    Parameters
    ----------
    ctx : WorkspaceContext
        Resolved workspace state.
    services : ComparisonServices
        Infrastructure services for tree scanning.
    target : TreeTarget
        Specification of the tree comparison to perform.
    filter_ : ProjectFilter | None
        Optional filter to narrow the target project set.

    Returns
    -------
    TreeReport
        Cross-project tree comparison report.
    """
    projects = _select_comparison_projects(ctx, filter_ or ProjectFilter())
    return compare_trees(projects, target, services.scanner)


def run_compare_files(
    ctx: WorkspaceContext,
    services: ComparisonServices,
    target: FileTarget,
    *,
    filter_: ProjectFilter | None = None,
) -> FileReport:
    """Select projects and compare specific files across them.

    Parameters
    ----------
    ctx : WorkspaceContext
        Resolved workspace state.
    services : ComparisonServices
        Infrastructure services for file reading and parsing.
    target : FileTarget
        Specification of the file comparison to perform.
    filter_ : ProjectFilter | None
        Optional filter to narrow the target project set.

    Returns
    -------
    FileReport
        Cross-project file comparison report.
    """
    projects = _select_comparison_projects(ctx, filter_ or ProjectFilter())
    return compare_files(projects, target, services.reader, services.parser)


def _select_comparison_projects(
    ctx: WorkspaceContext,
    filter_: ProjectFilter,
) -> tuple[ProjectMetadata, ...]:
    """Select and validate that at least 2 projects are available.

    Parameters
    ----------
    ctx : WorkspaceContext
        Resolved workspace state.
    filter_ : ProjectFilter
        Filter to narrow the target project set.

    Returns
    -------
    tuple[ProjectMetadata, ...]
        Selected projects (guaranteed at least 2).
    """
    projects = select_projects(ctx.inventory, filter_=filter_)
    if len(projects) < 2:
        raise WorkspaceError("Comparison requires at least 2 projects.")
    return projects
