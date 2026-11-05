<a id="module-stelion.workspace.composition"></a>

<a id="workspace-composition-root"></a>

# Workspace Composition Root

Composition root: constructs infrastructure and wires use-cases.

<a id="stelion.workspace.composition.WorkspaceServices"></a>

### *class* stelion.workspace.composition.WorkspaceServices(extractor, env_reader, dependency_scanners, writer, reader, hasher, render_workspace_file, render_projects_yaml, render_dependency_yaml, render_environment)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Container holding all wired infrastructure implementations.

<a id="stelion.workspace.composition.WorkspaceServices.extractor"></a>

#### extractor *: [MetadataExtractor](workspace-application.md#stelion.workspace.application.protocols.MetadataExtractor)*

Extracts project metadata from project directories.

<a id="stelion.workspace.composition.WorkspaceServices.env_reader"></a>

#### env_reader *: [EnvironmentReader](workspace-application.md#stelion.workspace.application.protocols.EnvironmentReader)*

Reads Conda environment specs from project directories.

<a id="stelion.workspace.composition.WorkspaceServices.dependency_scanners"></a>

#### dependency_scanners *: [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[DependencyScanner](workspace-application.md#stelion.workspace.application.protocols.DependencyScanner), ...]*

Scanners that detect inter-project dependency edges.

<a id="stelion.workspace.composition.WorkspaceServices.writer"></a>

#### writer *: [FileWriter](workspace-application.md#stelion.workspace.application.protocols.FileWriter)*

Writes file content to disk.

<a id="stelion.workspace.composition.WorkspaceServices.reader"></a>

#### reader *: [FileReader](workspace-application.md#stelion.workspace.application.protocols.FileReader)*

Reads file content from disk.

<a id="stelion.workspace.composition.WorkspaceServices.hasher"></a>

#### hasher *: [FileHasher](workspace-application.md#stelion.workspace.application.protocols.FileHasher)*

Computes content hashes for drift detection.

<a id="stelion.workspace.composition.WorkspaceServices.render_workspace_file"></a>

#### render_workspace_file *: [WorkspaceFileRenderer](workspace-application.md#stelion.workspace.application.protocols.WorkspaceFileRenderer)*

Renders the VS Code `.code-workspace` file.

<a id="stelion.workspace.composition.WorkspaceServices.render_projects_yaml"></a>

#### render_projects_yaml *: [ProjectsYamlRenderer](workspace-application.md#stelion.workspace.application.protocols.ProjectsYamlRenderer)*

Renders the projects registry YAML.

<a id="stelion.workspace.composition.WorkspaceServices.render_dependency_yaml"></a>

#### render_dependency_yaml *: [DependencyYamlRenderer](workspace-application.md#stelion.workspace.application.protocols.DependencyYamlRenderer)*

Renders the dependency graph YAML.

<a id="stelion.workspace.composition.WorkspaceServices.render_environment"></a>

#### render_environment *: [EnvironmentRenderer](workspace-application.md#stelion.workspace.application.protocols.EnvironmentRenderer)*

Renders the shared Conda environment YAML.

<a id="stelion.workspace.composition.WorkspaceContext"></a>

### *class* stelion.workspace.composition.WorkspaceContext(manifest, inventory, graph, environment)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Fully resolved workspace state: manifest + discovered data.

<a id="stelion.workspace.composition.WorkspaceContext.manifest"></a>

#### manifest *: [WorkspaceManifest](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)*

The loaded workspace manifest.

<a id="stelion.workspace.composition.WorkspaceContext.inventory"></a>

#### inventory *: [ProjectInventory](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory)*

Discovered projects in the workspace.

<a id="stelion.workspace.composition.WorkspaceContext.graph"></a>

#### graph *: [DependencyGraph](workspace-domain.md#stelion.workspace.domain.dependency.DependencyGraph)*

Inter-project dependency graph.

<a id="stelion.workspace.composition.WorkspaceContext.environment"></a>

#### environment *: [EnvironmentSpec](workspace-domain.md#stelion.workspace.domain.environment.EnvironmentSpec)*

Merged shared environment specification.

<a id="stelion.workspace.composition.WorkspaceRegistrationResult"></a>

### *class* stelion.workspace.composition.WorkspaceRegistrationResult(manifest, project, manifest_updated, generated)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Result of registering a project into the workspace and regenerating artifacts.

<a id="stelion.workspace.composition.WorkspaceRegistrationResult.manifest"></a>

#### manifest *: [WorkspaceManifest](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)*

The workspace manifest after registration.

<a id="stelion.workspace.composition.WorkspaceRegistrationResult.project"></a>

#### project *: [ProjectMetadata](workspace-domain.md#stelion.workspace.domain.project.ProjectMetadata)*

Metadata of the newly registered project.

<a id="stelion.workspace.composition.WorkspaceRegistrationResult.manifest_updated"></a>

#### manifest_updated *: [bool](https://docs.python.org/3/builtins/functions.html#bool)*

Whether the manifest was modified during registration.

<a id="stelion.workspace.composition.WorkspaceRegistrationResult.generated"></a>

#### generated *: [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[GenerationResult](workspace-application.md#stelion.workspace.application.generation.GenerationResult), ...]*

Artifacts regenerated after registration.

<a id="stelion.workspace.composition.create_services"></a>

### stelion.workspace.composition.create_services()

Build and return the full set of workspace infrastructure services.

* **Returns:**
  Fully wired infrastructure service container.
* **Return type:**
  [WorkspaceServices](#stelion.workspace.composition.WorkspaceServices)

<a id="stelion.workspace.composition.create_bootstrap_services"></a>

### stelion.workspace.composition.create_bootstrap_services()

Build the injected services for workspace project bootstrapping.

* **Returns:**
  Wired bootstrap infrastructure callbacks.
* **Return type:**
  [BootstrapServices](workspace-application.md#stelion.workspace.application.bootstrap.BootstrapServices)

<a id="stelion.workspace.composition.create_manifest_init_services"></a>

### stelion.workspace.composition.create_manifest_init_services(writer)

Build the collaborators for initializing a workspace manifest.

* **Parameters:**
  **writer** ([*FileWriter*](workspace-application.md#stelion.workspace.application.protocols.FileWriter)) – File writer used to persist the manifest.
* **Returns:**
  Wired manifest initialization collaborators.
* **Return type:**
  [ManifestInitServices](workspace-application.md#stelion.workspace.application.manifest_init.ManifestInitServices)

<a id="stelion.workspace.composition.resolve_manifest"></a>

### stelion.workspace.composition.resolve_manifest(manifest_path)

Load and return a validated workspace manifest.

* **Parameters:**
  **manifest_path** (*Path*) – Path to the workspace manifest file.
* **Returns:**
  The parsed and validated manifest.
* **Return type:**
  [WorkspaceManifest](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)

<a id="stelion.workspace.composition.compose_workspace_manifest"></a>

### stelion.workspace.composition.compose_workspace_manifest(overlay_path, manifest_path)

Compose and validate a consumer overlay against canonical defaults.

The destination path determines path-sensitive defaults such as the workspace
name. The overlay remains independent of Stelion’s complete manifest shape.

* **Parameters:**
  * **overlay_path** (*Path*) – YAML mapping containing consumer-specific manifest values.
  * **manifest_path** (*Path*) – Destination of the complete rendered manifest.
* **Returns:**
  Complete typed manifest after default composition and validation.
* **Return type:**
  [WorkspaceManifest](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)

<a id="stelion.workspace.composition.render_workspace_manifest"></a>

### stelion.workspace.composition.render_workspace_manifest(overlay_path, manifest_path)

Render a validated complete manifest from a consumer overlay.

* **Parameters:**
  * **overlay_path** (*Path*) – YAML mapping containing consumer-specific manifest values.
  * **manifest_path** (*Path*) – Destination path used to resolve path-sensitive defaults.
* **Returns:**
  Complete canonical YAML manifest.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)

<a id="stelion.workspace.composition.build_workspace_context"></a>

### stelion.workspace.composition.build_workspace_context(manifest, services)

Discover projects, build the dependency graph, and merge environments.

Pre-reads each project’s environment spec exactly once and shares those
specs with the dependency-graph builder and the shared-environment merger.

* **Parameters:**
  * **manifest** ([*WorkspaceManifest*](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)) – The workspace manifest defining discovery rules.
  * **services** ([*WorkspaceServices*](#stelion.workspace.composition.WorkspaceServices)) – Infrastructure services for project discovery and scanning.
* **Returns:**
  Fully resolved workspace state with inventory, graph, and environment.
* **Return type:**
  [WorkspaceContext](#stelion.workspace.composition.WorkspaceContext)

<a id="stelion.workspace.composition.initialize_workspace_manifest"></a>

### stelion.workspace.composition.initialize_workspace_manifest(manifest_path, services, \*, dry_run=False)

Create and optionally write a default manifest for a new workspace.

* **Parameters:**
  * **manifest_path** (*Path*) – Destination path for the new manifest file.
  * **services** ([*WorkspaceServices*](#stelion.workspace.composition.WorkspaceServices)) – Infrastructure services providing the file writer.
  * **dry_run** ([*bool*](https://docs.python.org/3/builtins/functions.html#bool)) – If True, build the manifest without writing to disk.
* **Returns:**
  The generated manifest, discovered inventory, and write status.
* **Return type:**
  [ManifestInitResult](workspace-application.md#stelion.workspace.application.manifest_init.ManifestInitResult)

<a id="stelion.workspace.composition.run_generate"></a>

### stelion.workspace.composition.run_generate(ctx, services, force=False, selected_targets=(), generation_services=None)

Generate all or a selected subset of workspace artifacts.

* **Parameters:**
  * **ctx** ([*WorkspaceContext*](#stelion.workspace.composition.WorkspaceContext)) – Resolved workspace state.
  * **services** ([*WorkspaceServices*](#stelion.workspace.composition.WorkspaceServices)) – Infrastructure services for generation.
  * **force** ([*bool*](https://docs.python.org/3/builtins/functions.html#bool)) – If True, regenerate even when content is unchanged.
  * **selected_targets** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*GenerationArtifact*](workspace-application.md#stelion.workspace.application.generation.GenerationArtifact) *,*  *...* *]*) – Subset of artifacts to generate; empty means all.
  * **generation_services** ([*GenerationServices*](workspace-application.md#stelion.workspace.application.protocols.GenerationServices) *|* *None*) – Pre-built generation services; built from *services* if None.
* **Returns:**
  Results for each generated artifact.
* **Return type:**
  [list](https://docs.python.org/3/builtins/stdtypes.html#list)[[GenerationResult](workspace-application.md#stelion.workspace.application.generation.GenerationResult)]

<a id="stelion.workspace.composition.run_drift_check"></a>

### stelion.workspace.composition.run_drift_check(ctx, services, selected_targets=(), generation_services=None)

Compute drift without writing any files.

* **Parameters:**
  * **ctx** ([*WorkspaceContext*](#stelion.workspace.composition.WorkspaceContext)) – Resolved workspace state.
  * **services** ([*WorkspaceServices*](#stelion.workspace.composition.WorkspaceServices)) – Infrastructure services for generation.
  * **selected_targets** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*GenerationArtifact*](workspace-application.md#stelion.workspace.application.generation.GenerationArtifact) *,*  *...* *]*) – Subset of artifacts to check; empty means all.
  * **generation_services** ([*GenerationServices*](workspace-application.md#stelion.workspace.application.protocols.GenerationServices) *|* *None*) – Pre-built generation services; built from *services* if None.
* **Returns:**
  Report describing which artifacts have drifted.
* **Return type:**
  [DriftReport](workspace-domain.md#stelion.workspace.domain.status.DriftReport)

<a id="stelion.workspace.composition.target_output_paths"></a>

### stelion.workspace.composition.target_output_paths(manifest, selected_targets=())

List generation target output paths using `compute_artifact_specs`.

* **Parameters:**
  * **manifest** ([*WorkspaceManifest*](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)) – The workspace manifest defining artifact output locations.
  * **selected_targets** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*GenerationArtifact*](workspace-application.md#stelion.workspace.application.generation.GenerationArtifact) *,*  *...* *]*) – Subset of artifacts to include; empty means all.
* **Returns:**
  Output paths for the selected (or all) generation targets.
* **Return type:**
  [list](https://docs.python.org/3/builtins/stdtypes.html#list)[Path]

<a id="stelion.workspace.composition.target_paths"></a>

### stelion.workspace.composition.target_paths(manifest, selected_targets=())

List generation target output paths (backward-compatible alias).

* **Parameters:**
  * **manifest** ([*WorkspaceManifest*](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)) – The workspace manifest defining artifact output locations.
  * **selected_targets** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*GenerationArtifact*](workspace-application.md#stelion.workspace.application.generation.GenerationArtifact) *,*  *...* *]*) – Subset of artifacts to include; empty means all.
* **Returns:**
  Output paths for the selected (or all) generation targets.
* **Return type:**
  [list](https://docs.python.org/3/builtins/stdtypes.html#list)[Path]

<a id="stelion.workspace.composition.register_workspace_project"></a>

### stelion.workspace.composition.register_workspace_project(manifest_path, project_dir, services)

Register a project, persist manifest updates, and regenerate artifacts.

Thin wiring function that delegates orchestration to
`application.registration.execute_registration`. Provides the
infrastructure callbacks (discovery, context build + generate,
manifest persistence).

* **Parameters:**
  * **manifest_path** (*Path*) – Path to the workspace manifest file.
  * **project_dir** (*Path*) – Directory of the project to register.
  * **services** ([*WorkspaceServices*](#stelion.workspace.composition.WorkspaceServices)) – Infrastructure services for discovery, generation, and persistence.
* **Returns:**
  Registration outcome including manifest, project, and generated artifacts.
* **Return type:**
  [WorkspaceRegistrationResult](#stelion.workspace.composition.WorkspaceRegistrationResult)

<a id="stelion.workspace.composition.create_git_operations"></a>

### stelion.workspace.composition.create_git_operations()

Build the git operations infrastructure for submodule sync.

* **Returns:**
  Git operations implemented via subprocess calls.
* **Return type:**
  [SubprocessGitOperations](workspace-infrastructure.md#stelion.workspace.infrastructure.git_operations.SubprocessGitOperations)

<a id="stelion.workspace.composition.run_submodule_sync"></a>

### stelion.workspace.composition.run_submodule_sync(ctx, dependency, origin, \*, source_superproject=None, remote='origin', branch='main', commit=True, dry_run=False)

Resolve, plan, and execute a submodule sync for a dependency.

* **Parameters:**
  * **ctx** ([*WorkspaceContext*](#stelion.workspace.composition.WorkspaceContext)) – Resolved workspace state.
  * **dependency** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the dependency project to sync.
  * **origin** ([*SyncOrigin*](workspace-domain.md#stelion.workspace.domain.sync.SyncOrigin)) – Source of the target commit (local HEAD or remote).
  * **source_superproject** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *|* *None*) – Name of the superproject supplying the source commit.
  * **remote** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Git remote name to fetch from.
  * **branch** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Git branch name to resolve the remote HEAD.
  * **commit** ([*bool*](https://docs.python.org/3/builtins/functions.html#bool)) – If True, commit submodule pointer updates.
  * **dry_run** ([*bool*](https://docs.python.org/3/builtins/functions.html#bool)) – If True, plan without executing filesystem changes.
* **Returns:**
  Outcome of the sync operation.
* **Return type:**
  [SyncResult](workspace-domain.md#stelion.workspace.domain.sync.SyncResult)

<a id="stelion.workspace.composition.create_command_runner"></a>

### stelion.workspace.composition.create_command_runner()

Build the command runner infrastructure for bulk operations.

* **Returns:**
  Command runner implemented via subprocess calls.
* **Return type:**
  [SubprocessCommandRunner](workspace-infrastructure.md#stelion.workspace.infrastructure.command_runner.SubprocessCommandRunner)

<a id="stelion.workspace.composition.run_bulk_exec"></a>

### stelion.workspace.composition.run_bulk_exec(ctx, command, \*, filter_=None, dry_run=False)

Select projects and run an arbitrary shell command on each.

* **Parameters:**
  * **ctx** ([*WorkspaceContext*](#stelion.workspace.composition.WorkspaceContext)) – Resolved workspace state.
  * **command** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Shell command to execute in each project directory.
  * **filter** ([*ProjectFilter*](workspace-domain.md#stelion.workspace.domain.bulk.ProjectFilter) *|* *None*) – Optional filter to narrow the target project set.
  * **dry_run** ([*bool*](https://docs.python.org/3/builtins/functions.html#bool)) – If True, select projects without executing the command.
* **Returns:**
  Aggregated outcomes from all targeted projects.
* **Return type:**
  [BulkResult](workspace-domain.md#stelion.workspace.domain.bulk.BulkResult)

<a id="stelion.workspace.composition.run_bulk_commit"></a>

### stelion.workspace.composition.run_bulk_commit(ctx, message, \*, filter_=None, dry_run=False)

Select projects and commit tracked changes on each.

* **Parameters:**
  * **ctx** ([*WorkspaceContext*](#stelion.workspace.composition.WorkspaceContext)) – Resolved workspace state.
  * **message** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Commit message to use for each project.
  * **filter** ([*ProjectFilter*](workspace-domain.md#stelion.workspace.domain.bulk.ProjectFilter) *|* *None*) – Optional filter to narrow the target project set.
  * **dry_run** ([*bool*](https://docs.python.org/3/builtins/functions.html#bool)) – If True, select projects without committing.
* **Returns:**
  Aggregated outcomes from all targeted projects.
* **Return type:**
  [BulkResult](workspace-domain.md#stelion.workspace.domain.bulk.BulkResult)

<a id="stelion.workspace.composition.run_bulk_push"></a>

### stelion.workspace.composition.run_bulk_push(ctx, \*, remote='origin', branch='main', filter_=None, dry_run=False)

Select projects and push to remote on each.

* **Parameters:**
  * **ctx** ([*WorkspaceContext*](#stelion.workspace.composition.WorkspaceContext)) – Resolved workspace state.
  * **remote** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Git remote name to push to.
  * **branch** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Git branch name to push.
  * **filter** ([*ProjectFilter*](workspace-domain.md#stelion.workspace.domain.bulk.ProjectFilter) *|* *None*) – Optional filter to narrow the target project set.
  * **dry_run** ([*bool*](https://docs.python.org/3/builtins/functions.html#bool)) – If True, select projects without pushing.
* **Returns:**
  Aggregated outcomes from all targeted projects.
* **Return type:**
  [BulkResult](workspace-domain.md#stelion.workspace.domain.bulk.BulkResult)

<a id="stelion.workspace.composition.ComparisonServices"></a>

### *class* stelion.workspace.composition.ComparisonServices(scanner, parser, spec_loader, reader)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Container for cross-project comparison infrastructure.

<a id="stelion.workspace.composition.ComparisonServices.scanner"></a>

#### scanner *: [TreeScanner](workspace-application.md#stelion.workspace.application.protocols.TreeScanner)*

Scans project directories for file-tree snapshots.

<a id="stelion.workspace.composition.ComparisonServices.parser"></a>

#### parser *: [StructuredParser](workspace-application.md#stelion.workspace.application.protocols.StructuredParser)*

Parses structured file content into nested dicts.

<a id="stelion.workspace.composition.ComparisonServices.spec_loader"></a>

#### spec_loader *: [SpecLoader](workspace-application.md#stelion.workspace.application.protocols.SpecLoader)*

Loads comparison instruction files into typed specifications.

<a id="stelion.workspace.composition.ComparisonServices.reader"></a>

#### reader *: [FileReader](workspace-application.md#stelion.workspace.application.protocols.FileReader)*

Reads file content from disk.

<a id="stelion.workspace.composition.create_comparison_services"></a>

### stelion.workspace.composition.create_comparison_services()

Build the infrastructure services for comparison operations.

* **Returns:**
  Wired comparison infrastructure container.
* **Return type:**
  [ComparisonServices](#stelion.workspace.composition.ComparisonServices)

<a id="stelion.workspace.composition.run_compare_trees"></a>

### stelion.workspace.composition.run_compare_trees(ctx, services, target, \*, filter_=None)

Select projects and compare their directory structures.

* **Parameters:**
  * **ctx** ([*WorkspaceContext*](#stelion.workspace.composition.WorkspaceContext)) – Resolved workspace state.
  * **services** ([*ComparisonServices*](#stelion.workspace.composition.ComparisonServices)) – Infrastructure services for tree scanning.
  * **target** ([*TreeTarget*](workspace-domain.md#stelion.workspace.domain.comparison.TreeTarget)) – Specification of the tree comparison to perform.
  * **filter** ([*ProjectFilter*](workspace-domain.md#stelion.workspace.domain.bulk.ProjectFilter) *|* *None*) – Optional filter to narrow the target project set.
* **Returns:**
  Cross-project tree comparison report.
* **Return type:**
  [TreeReport](workspace-domain.md#stelion.workspace.domain.comparison.TreeReport)

<a id="stelion.workspace.composition.run_compare_files"></a>

### stelion.workspace.composition.run_compare_files(ctx, services, target, \*, filter_=None)

Select projects and compare specific files across them.

* **Parameters:**
  * **ctx** ([*WorkspaceContext*](#stelion.workspace.composition.WorkspaceContext)) – Resolved workspace state.
  * **services** ([*ComparisonServices*](#stelion.workspace.composition.ComparisonServices)) – Infrastructure services for file reading and parsing.
  * **target** ([*FileTarget*](workspace-domain.md#stelion.workspace.domain.comparison.FileTarget)) – Specification of the file comparison to perform.
  * **filter** ([*ProjectFilter*](workspace-domain.md#stelion.workspace.domain.bulk.ProjectFilter) *|* *None*) – Optional filter to narrow the target project set.
* **Returns:**
  Cross-project file comparison report.
* **Return type:**
  [FileReport](workspace-domain.md#stelion.workspace.domain.comparison.FileReport)
