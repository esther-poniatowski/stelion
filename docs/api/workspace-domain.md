<a id="workspace-domain"></a>

# Workspace Domain

Domain models for workspace management.

<a id="module-stelion.workspace.domain.project"></a>

<a id="project"></a>

## Project

Domain models for project metadata and inventory.

<a id="stelion.workspace.domain.project.MetadataStatus"></a>

### *class* stelion.workspace.domain.project.MetadataStatus(\*values)

Bases: [`StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Status of metadata extracted from a project directory.

<a id="stelion.workspace.domain.project.MetadataStatus.CURRENT"></a>

#### CURRENT *= 'current'*

<a id="stelion.workspace.domain.project.MetadataStatus.MISSING_PYPROJECT"></a>

#### MISSING_PYPROJECT *= 'missing_pyproject'*

<a id="stelion.workspace.domain.project.MetadataStatus.INVALID_PYPROJECT"></a>

#### INVALID_PYPROJECT *= 'invalid_pyproject'*

<a id="stelion.workspace.domain.project.GithubSlug"></a>

### *class* stelion.workspace.domain.project.GithubSlug(owner, repo)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A validated GitHub owner/repo identifier.

<a id="stelion.workspace.domain.project.GithubSlug.owner"></a>

#### owner *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

GitHub user or organisation name.

<a id="stelion.workspace.domain.project.GithubSlug.repo"></a>

#### repo *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Repository name.

<a id="stelion.workspace.domain.project.GithubSlug.parse"></a>

#### *classmethod* parse(raw)

Parse an `owner/repo` string.

* **Parameters:**
  **raw** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – String in `owner/repo` format.
* **Returns:**
  Parsed slug with owner and repo populated.
* **Return type:**
  [GithubSlug](#stelion.workspace.domain.project.GithubSlug)
* **Raises:**
  [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the string is not exactly `owner/repo` with non-empty parts.

<a id="stelion.workspace.domain.project.GithubSlug.from_url"></a>

#### *classmethod* from_url(url)

Extract owner/repo from a GitHub URL.

Accepts HTTPS (`https://github.com/owner/repo`) and SSH
(`git@github.com:owner/repo.git`) formats.  Returns `None`
if the URL does not match a GitHub pattern.

* **Parameters:**
  **url** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – GitHub URL in HTTPS or SSH format.
* **Returns:**
  Parsed slug, or `None` if the URL is not a GitHub URL.
* **Return type:**
  [GithubSlug](#stelion.workspace.domain.project.GithubSlug) | None

<a id="stelion.workspace.domain.project.ProjectMetadata"></a>

### *class* stelion.workspace.domain.project.ProjectMetadata(name, path, description='', version='0.0.0', homepage=None, github=None, has_git=False, languages=(), status=MetadataStatus.CURRENT, issue='')

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Metadata extracted from a single project’s pyproject.toml and filesystem.

<a id="stelion.workspace.domain.project.ProjectMetadata.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Project name from pyproject.toml.

<a id="stelion.workspace.domain.project.ProjectMetadata.path"></a>

#### path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

Filesystem path to the project root.

<a id="stelion.workspace.domain.project.ProjectMetadata.description"></a>

#### description *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= ''*

Short project description.

<a id="stelion.workspace.domain.project.ProjectMetadata.version"></a>

#### version *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= '0.0.0'*

Declared version string.

<a id="stelion.workspace.domain.project.ProjectMetadata.homepage"></a>

#### homepage *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Project homepage URL.

<a id="stelion.workspace.domain.project.ProjectMetadata.github"></a>

#### github *: [GithubSlug](#stelion.workspace.domain.project.GithubSlug) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Parsed GitHub owner/repo identifier.

<a id="stelion.workspace.domain.project.ProjectMetadata.has_git"></a>

#### has_git *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= False*

Whether the project directory is a git repository.

<a id="stelion.workspace.domain.project.ProjectMetadata.languages"></a>

#### languages *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Programming languages detected in the project.

<a id="stelion.workspace.domain.project.ProjectMetadata.status"></a>

#### status *: [MetadataStatus](#stelion.workspace.domain.project.MetadataStatus)* *= 'current'*

Parsing status of the metadata extraction.

<a id="stelion.workspace.domain.project.ProjectMetadata.issue"></a>

#### issue *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= ''*

Error or warning message from metadata extraction.

<a id="stelion.workspace.domain.project.ProjectInventory"></a>

### *class* stelion.workspace.domain.project.ProjectInventory(projects=())

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Collection of discovered projects.

<a id="stelion.workspace.domain.project.ProjectInventory.projects"></a>

#### projects *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[ProjectMetadata](#stelion.workspace.domain.project.ProjectMetadata), ...]* *= ()*

Discovered project metadata entries.

<a id="stelion.workspace.domain.project.ProjectInventory.by_name"></a>

#### by_name()

Index projects by name.

* **Returns:**
  Mapping from project name to metadata.
* **Return type:**
  [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [ProjectMetadata](#stelion.workspace.domain.project.ProjectMetadata)]

<a id="stelion.workspace.domain.project.ProjectInventory.by_path"></a>

#### by_path()

Index projects by their resolved filesystem path.

* **Returns:**
  Mapping from resolved path to metadata.
* **Return type:**
  [dict](https://docs.python.org/3/library/stdtypes.html#dict)[Path, [ProjectMetadata](#stelion.workspace.domain.project.ProjectMetadata)]

<a id="module-stelion.workspace.domain.manifest"></a>

<a id="manifest"></a>

## Manifest

Immutable domain models for workspace manifest configuration.

<a id="stelion.workspace.domain.manifest.DiscoveryConfig"></a>

### *class* stelion.workspace.domain.manifest.DiscoveryConfig(scan_dirs, exclude=('dev',), markers=('pyproject.toml',), extra_paths=(), include_self=True, self_name='dev')

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Rules for discovering projects on disk.

<a id="stelion.workspace.domain.manifest.DiscoveryConfig.scan_dirs"></a>

#### scan_dirs *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]*

Directories to scan for projects.

<a id="stelion.workspace.domain.manifest.DiscoveryConfig.exclude"></a>

#### exclude *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ('dev',)*

Directory names to skip during scanning.

<a id="stelion.workspace.domain.manifest.DiscoveryConfig.markers"></a>

#### markers *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ('pyproject.toml',)*

Filenames whose presence identifies a project root.

<a id="stelion.workspace.domain.manifest.DiscoveryConfig.extra_paths"></a>

#### extra_paths *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Additional paths to include as projects unconditionally.

<a id="stelion.workspace.domain.manifest.DiscoveryConfig.include_self"></a>

#### include_self *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= True*

Whether to include the workspace root as a project.

<a id="stelion.workspace.domain.manifest.DiscoveryConfig.self_name"></a>

#### self_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= 'dev'*

Name assigned to the workspace root project.

<a id="stelion.workspace.domain.manifest.TemplateConfig"></a>

### *class* stelion.workspace.domain.manifest.TemplateConfig(source, delimiters=('{{ ', ' }}'), exclude_patterns=(), renames=<factory>)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Template source and substitution rules for bootstrapping new projects.

<a id="stelion.workspace.domain.manifest.TemplateConfig.source"></a>

#### source *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Path or identifier of the template source.

<a id="stelion.workspace.domain.manifest.TemplateConfig.delimiters"></a>

#### delimiters *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), [str](https://docs.python.org/3/library/stdtypes.html#str)]* *= ('{{ ', ' }}')*

Opening and closing delimiter pair for placeholders.

<a id="stelion.workspace.domain.manifest.TemplateConfig.exclude_patterns"></a>

#### exclude_patterns *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Glob patterns for files excluded from template processing.

<a id="stelion.workspace.domain.manifest.TemplateConfig.renames"></a>

#### renames *: [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping)[[str](https://docs.python.org/3/library/stdtypes.html#str), [str](https://docs.python.org/3/library/stdtypes.html#str)]*

Filename substitution rules applied during bootstrapping.

<a id="stelion.workspace.domain.manifest.EcosystemDefaults"></a>

### *class* stelion.workspace.domain.manifest.EcosystemDefaults(github_user='', channel_name='', license='GPL-3.0-or-later')

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Default values for placeholder substitution and project metadata.

<a id="stelion.workspace.domain.manifest.EcosystemDefaults.github_user"></a>

#### github_user *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= ''*

Default GitHub username for new projects.

<a id="stelion.workspace.domain.manifest.EcosystemDefaults.channel_name"></a>

#### channel_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= ''*

Default Conda channel name.

<a id="stelion.workspace.domain.manifest.EcosystemDefaults.license"></a>

#### license *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= 'GPL-3.0-or-later'*

Default SPDX license identifier.

<a id="stelion.workspace.domain.manifest.VSCodeConfig"></a>

### *class* stelion.workspace.domain.manifest.VSCodeConfig(source='defaults', settings_overrides=<factory>, extensions_overrides=())

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

VS Code workspace settings source and overrides.

<a id="stelion.workspace.domain.manifest.VSCodeConfig.source"></a>

#### source *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= 'defaults'*

Settings source identifier (`"defaults"` for bundled defaults).

<a id="stelion.workspace.domain.manifest.VSCodeConfig.settings_overrides"></a>

#### settings_overrides *: [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Any](https://docs.python.org/3/library/typing.html#typing.Any)]*

User overrides merged into VS Code settings.

<a id="stelion.workspace.domain.manifest.VSCodeConfig.extensions_overrides"></a>

#### extensions_overrides *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Additional VS Code extension identifiers to recommend.

<a id="stelion.workspace.domain.manifest.VSCodeConfig.uses_defaults"></a>

#### uses_defaults()

Whether VS Code assets should come from bundled defaults.

* **Returns:**
  True if source is `"defaults"`.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="stelion.workspace.domain.manifest.WorkspaceFileConfig"></a>

### *class* stelion.workspace.domain.manifest.WorkspaceFileConfig(output='dev-repos.code-workspace')

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Generation target for the VS Code .code-workspace file.

<a id="stelion.workspace.domain.manifest.WorkspaceFileConfig.output"></a>

#### output *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= 'dev-repos.code-workspace'*

Filename for the generated .code-workspace file.

<a id="stelion.workspace.domain.manifest.ProjectsRegistryConfig"></a>

### *class* stelion.workspace.domain.manifest.ProjectsRegistryConfig(output='projects.yml')

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Generation target for the projects registry (YAML).

<a id="stelion.workspace.domain.manifest.ProjectsRegistryConfig.output"></a>

#### output *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= 'projects.yml'*

Filename for the generated projects registry.

<a id="stelion.workspace.domain.manifest.DependencyGraphConfig"></a>

### *class* stelion.workspace.domain.manifest.DependencyGraphConfig(output='dependencies.yml')

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Generation target for the dependency graph (YAML).

<a id="stelion.workspace.domain.manifest.DependencyGraphConfig.output"></a>

#### output *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= 'dependencies.yml'*

Filename for the generated dependency graph.

<a id="stelion.workspace.domain.manifest.SharedEnvironmentConfig"></a>

### *class* stelion.workspace.domain.manifest.SharedEnvironmentConfig(output='environment.yml', name='dev')

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Generation target for the shared Conda environment.

<a id="stelion.workspace.domain.manifest.SharedEnvironmentConfig.output"></a>

#### output *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= 'environment.yml'*

Filename for the generated environment file.

<a id="stelion.workspace.domain.manifest.SharedEnvironmentConfig.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= 'dev'*

Conda environment name.

<a id="stelion.workspace.domain.manifest.GenerateConfig"></a>

### *class* stelion.workspace.domain.manifest.GenerateConfig(workspace_file=<factory>, projects_registry=<factory>, dependency_graph=<factory>, shared_environment=<factory>)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

All generation targets.

<a id="stelion.workspace.domain.manifest.GenerateConfig.workspace_file"></a>

#### workspace_file *: [WorkspaceFileConfig](#stelion.workspace.domain.manifest.WorkspaceFileConfig)*

Configuration for the VS Code .code-workspace file.

<a id="stelion.workspace.domain.manifest.GenerateConfig.projects_registry"></a>

#### projects_registry *: [ProjectsRegistryConfig](#stelion.workspace.domain.manifest.ProjectsRegistryConfig)*

Configuration for the projects registry.

<a id="stelion.workspace.domain.manifest.GenerateConfig.dependency_graph"></a>

#### dependency_graph *: [DependencyGraphConfig](#stelion.workspace.domain.manifest.DependencyGraphConfig)*

Configuration for the dependency graph.

<a id="stelion.workspace.domain.manifest.GenerateConfig.shared_environment"></a>

#### shared_environment *: [SharedEnvironmentConfig](#stelion.workspace.domain.manifest.SharedEnvironmentConfig)*

Configuration for the shared Conda environment.

<a id="stelion.workspace.domain.manifest.CanonicalMechanism"></a>

### *class* stelion.workspace.domain.manifest.CanonicalMechanism(type, mechanism)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Integration mechanism assignment for a library.

<a id="stelion.workspace.domain.manifest.CanonicalMechanism.type"></a>

#### type *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Library type identifier.

<a id="stelion.workspace.domain.manifest.CanonicalMechanism.mechanism"></a>

#### mechanism *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Integration mechanism name.

<a id="stelion.workspace.domain.manifest.ReferenceImplementation"></a>

### *class* stelion.workspace.domain.manifest.ReferenceImplementation(module, description)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A reference implementation of the integration module pattern.

<a id="stelion.workspace.domain.manifest.ReferenceImplementation.module"></a>

#### module *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Fully qualified module path.

<a id="stelion.workspace.domain.manifest.ReferenceImplementation.description"></a>

#### description *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Human-readable description of the reference implementation.

<a id="stelion.workspace.domain.manifest.IntegrationsConfig"></a>

### *class* stelion.workspace.domain.manifest.IntegrationsConfig(canonical_mechanisms=<factory>, reference_implementations=())

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Project-specific integration mechanism assignments and references.

<a id="stelion.workspace.domain.manifest.IntegrationsConfig.canonical_mechanisms"></a>

#### canonical_mechanisms *: [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping)[[str](https://docs.python.org/3/library/stdtypes.html#str), [CanonicalMechanism](#stelion.workspace.domain.manifest.CanonicalMechanism)]*

Library-to-mechanism assignments keyed by library name.

<a id="stelion.workspace.domain.manifest.IntegrationsConfig.reference_implementations"></a>

#### reference_implementations *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[ReferenceImplementation](#stelion.workspace.domain.manifest.ReferenceImplementation), ...]* *= ()*

Known reference implementations of the integration pattern.

<a id="stelion.workspace.domain.manifest.ManualEdge"></a>

### *class* stelion.workspace.domain.manifest.ManualEdge(dependent, dependency, mechanism, detail='')

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A manually declared dependency edge.

<a id="stelion.workspace.domain.manifest.ManualEdge.dependent"></a>

#### dependent *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the project that depends on another.

<a id="stelion.workspace.domain.manifest.ManualEdge.dependency"></a>

#### dependency *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the project being depended upon.

<a id="stelion.workspace.domain.manifest.ManualEdge.mechanism"></a>

#### mechanism *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

How the dependency is consumed (e.g. submodule, editable install).

<a id="stelion.workspace.domain.manifest.ManualEdge.detail"></a>

#### detail *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= ''*

Optional additional detail about the dependency.

<a id="stelion.workspace.domain.manifest.DependenciesConfig"></a>

### *class* stelion.workspace.domain.manifest.DependenciesConfig(manual_edges=(), scan_paths=(), superproject_paths=())

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Manual dependency declarations and supplemental repository paths.

<a id="stelion.workspace.domain.manifest.DependenciesConfig.manual_edges"></a>

#### manual_edges *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[ManualEdge](#stelion.workspace.domain.manifest.ManualEdge), ...]* *= ()*

Explicitly declared dependency edges.

<a id="stelion.workspace.domain.manifest.DependenciesConfig.scan_paths"></a>

#### scan_paths *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Directories scanned for dependency *edges* (editable pip installs,
gitmodules). Used by `build_dependency_graph`.

<a id="stelion.workspace.domain.manifest.DependenciesConfig.superproject_paths"></a>

#### superproject_paths *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Directories resolved as superproject *locations* for submodule sync.
Used by `resolve_submodule_targets` to find superproject directories
by name.

<a id="stelion.workspace.domain.manifest.ReferencesConfig"></a>

### *class* stelion.workspace.domain.manifest.ReferencesConfig(expected=())

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Expected reference documents in the workspace.

<a id="stelion.workspace.domain.manifest.ReferencesConfig.expected"></a>

#### expected *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Filenames of reference documents that should be present.

<a id="stelion.workspace.domain.manifest.WorkspaceManifest"></a>

### *class* stelion.workspace.domain.manifest.WorkspaceManifest(discovery, template, defaults, vscode, generate, integrations, names_in_use, dependencies, references, manifest_dir)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Complete workspace manifest parsed from stelion.yml.

<a id="stelion.workspace.domain.manifest.WorkspaceManifest.discovery"></a>

#### discovery *: [DiscoveryConfig](#stelion.workspace.domain.manifest.DiscoveryConfig)*

Project discovery rules.

<a id="stelion.workspace.domain.manifest.WorkspaceManifest.template"></a>

#### template *: [TemplateConfig](#stelion.workspace.domain.manifest.TemplateConfig)*

Template bootstrapping configuration.

<a id="stelion.workspace.domain.manifest.WorkspaceManifest.defaults"></a>

#### defaults *: [EcosystemDefaults](#stelion.workspace.domain.manifest.EcosystemDefaults)*

Default placeholder values.

<a id="stelion.workspace.domain.manifest.WorkspaceManifest.vscode"></a>

#### vscode *: [VSCodeConfig](#stelion.workspace.domain.manifest.VSCodeConfig)*

VS Code workspace settings.

<a id="stelion.workspace.domain.manifest.WorkspaceManifest.generate"></a>

#### generate *: [GenerateConfig](#stelion.workspace.domain.manifest.GenerateConfig)*

All generation target configurations.

<a id="stelion.workspace.domain.manifest.WorkspaceManifest.integrations"></a>

#### integrations *: [IntegrationsConfig](#stelion.workspace.domain.manifest.IntegrationsConfig)*

Integration mechanism assignments and references.

<a id="stelion.workspace.domain.manifest.WorkspaceManifest.names_in_use"></a>

#### names_in_use *: [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping)[[str](https://docs.python.org/3/library/stdtypes.html#str), [str](https://docs.python.org/3/library/stdtypes.html#str)]*

Reserved project names mapped to their descriptions.

<a id="stelion.workspace.domain.manifest.WorkspaceManifest.dependencies"></a>

#### dependencies *: [DependenciesConfig](#stelion.workspace.domain.manifest.DependenciesConfig)*

Manual dependency declarations and scan paths.

<a id="stelion.workspace.domain.manifest.WorkspaceManifest.references"></a>

#### references *: [ReferencesConfig](#stelion.workspace.domain.manifest.ReferencesConfig)*

Expected reference documents in the workspace.

<a id="stelion.workspace.domain.manifest.WorkspaceManifest.manifest_dir"></a>

#### manifest_dir *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

Directory containing the manifest file.

<a id="stelion.workspace.domain.manifest.WorkspaceManifest.with_added_extra_path"></a>

#### with_added_extra_path(extra_path)

Return a manifest that explicitly discovers *extra_path*.

* **Parameters:**
  **extra_path** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Additional path to include in project discovery.
* **Returns:**
  Updated manifest (or self if the path is already present).
* **Return type:**
  [WorkspaceManifest](#stelion.workspace.domain.manifest.WorkspaceManifest)

<a id="module-stelion.workspace.domain.environment"></a>

<a id="environment"></a>

## Environment

Domain models and logic for Conda environment specifications.

<a id="stelion.workspace.domain.environment.EnvironmentSpec"></a>

### *class* stelion.workspace.domain.environment.EnvironmentSpec(name='', channels=(), dependencies=(), pip_dependencies=(), issues=())

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Parsed content of a Conda environment.yml file.

<a id="stelion.workspace.domain.environment.EnvironmentSpec.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= ''*

Environment name.

<a id="stelion.workspace.domain.environment.EnvironmentSpec.channels"></a>

#### channels *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Conda channels in priority order.

<a id="stelion.workspace.domain.environment.EnvironmentSpec.dependencies"></a>

#### dependencies *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Conda package specifications.

<a id="stelion.workspace.domain.environment.EnvironmentSpec.pip_dependencies"></a>

#### pip_dependencies *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Pip package specifications.

<a id="stelion.workspace.domain.environment.EnvironmentSpec.issues"></a>

#### issues *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Parsing warnings or errors encountered during extraction.

<a id="stelion.workspace.domain.environment.merge_environments"></a>

### stelion.workspace.domain.environment.merge_environments(specs, name)

Merge multiple environment specs into one, de-duplicating entries.

Channels and dependencies are unioned in encounter order. Pip editable
installs (lines starting with `-e`) are excluded from the shared
environment since they contain machine-specific paths.

* **Parameters:**
  * **specs** ([*list*](https://docs.python.org/3/library/stdtypes.html#list) *[*[*EnvironmentSpec*](#stelion.workspace.domain.environment.EnvironmentSpec) *]*) – Individual environment specifications to merge.
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name for the merged environment.
* **Returns:**
  Combined specification with de-duplicated channels and dependencies.
* **Return type:**
  [EnvironmentSpec](#stelion.workspace.domain.environment.EnvironmentSpec)

<a id="module-stelion.workspace.domain.dependency"></a>

<a id="dependency"></a>

## Dependency

Domain models for inter-project dependency tracking.

<a id="stelion.workspace.domain.dependency.DependencyMechanism"></a>

### *class* stelion.workspace.domain.dependency.DependencyMechanism(\*values)

Bases: [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)

How one project depends on another.

<a id="stelion.workspace.domain.dependency.DependencyMechanism.EDITABLE_PIP"></a>

#### EDITABLE_PIP *= 'editable pip install'*

<a id="stelion.workspace.domain.dependency.DependencyMechanism.CONDA"></a>

#### CONDA *= 'conda'*

<a id="stelion.workspace.domain.dependency.DependencyMechanism.GIT_SUBMODULE"></a>

#### GIT_SUBMODULE *= 'git submodule'*

<a id="stelion.workspace.domain.dependency.DependencyEdge"></a>

### *class* stelion.workspace.domain.dependency.DependencyEdge(dependent, dependency, mechanism, detail='')

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A resolved dependency between two projects.

<a id="stelion.workspace.domain.dependency.DependencyEdge.dependent"></a>

#### dependent *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the downstream project.

<a id="stelion.workspace.domain.dependency.DependencyEdge.dependency"></a>

#### dependency *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the upstream project.

<a id="stelion.workspace.domain.dependency.DependencyEdge.mechanism"></a>

#### mechanism *: [DependencyMechanism](#stelion.workspace.domain.dependency.DependencyMechanism)*

How the dependency is realized.

<a id="stelion.workspace.domain.dependency.DependencyEdge.detail"></a>

#### detail *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= ''*

Additional context about the edge.

<a id="stelion.workspace.domain.dependency.DependencyGraph"></a>

### *class* stelion.workspace.domain.dependency.DependencyGraph(detected=(), manual=())

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Complete dependency graph: auto-detected and manual edges.

<a id="stelion.workspace.domain.dependency.DependencyGraph.detected"></a>

#### detected *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[DependencyEdge](#stelion.workspace.domain.dependency.DependencyEdge), ...]* *= ()*

Edges discovered automatically from project configuration files.

<a id="stelion.workspace.domain.dependency.DependencyGraph.manual"></a>

#### manual *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[DependencyEdge](#stelion.workspace.domain.dependency.DependencyEdge), ...]* *= ()*

Edges declared explicitly in the workspace manifest.

<a id="stelion.workspace.domain.dependency.DependencyGraph.all_edges"></a>

#### *property* all_edges *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[DependencyEdge](#stelion.workspace.domain.dependency.DependencyEdge), ...]*

All resolved edges (detected + manual).

* **Returns:**
  Concatenation of detected and manual edges.
* **Return type:**
  [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[DependencyEdge](#stelion.workspace.domain.dependency.DependencyEdge), …]

<a id="stelion.workspace.domain.dependency.DependencyGraph.by_dependent"></a>

#### by_dependent()

Group edges by their dependent project.

* **Returns:**
  Mapping from dependent project name to its edges.
* **Return type:**
  [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [list](https://docs.python.org/3/library/stdtypes.html#list)[[DependencyEdge](#stelion.workspace.domain.dependency.DependencyEdge)]]

<a id="stelion.workspace.domain.dependency.DependencyGraph.by_dependency"></a>

#### by_dependency()

Group edges by their dependency (upstream) project.

* **Returns:**
  Mapping from dependency project name to its edges.
* **Return type:**
  [dict](https://docs.python.org/3/library/stdtypes.html#dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [list](https://docs.python.org/3/library/stdtypes.html#list)[[DependencyEdge](#stelion.workspace.domain.dependency.DependencyEdge)]]

<a id="stelion.workspace.domain.dependency.DependencyGraph.dependents_of"></a>

#### dependents_of(name)

Project names that directly depend on the given project.

* **Parameters:**
  **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Upstream project name.
* **Returns:**
  Names of projects that depend on *name*.
* **Return type:**
  [list](https://docs.python.org/3/library/stdtypes.html#list)[[str](https://docs.python.org/3/library/stdtypes.html#str)]

<a id="stelion.workspace.domain.dependency.DependencyGraph.dependencies_of"></a>

#### dependencies_of(name)

Project names that the given project directly depends on.

* **Parameters:**
  **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Downstream project name.
* **Returns:**
  Names of upstream projects that *name* depends on.
* **Return type:**
  [list](https://docs.python.org/3/library/stdtypes.html#list)[[str](https://docs.python.org/3/library/stdtypes.html#str)]

<a id="stelion.workspace.domain.dependency.DependencyGraph.affected_projects"></a>

#### affected_projects(name)

All project names connected to the given project by any edge.

* **Parameters:**
  **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Project name to look up.
* **Returns:**
  Union of dependents and dependencies of *name*.
* **Return type:**
  [set](https://docs.python.org/3/library/stdtypes.html#set)[[str](https://docs.python.org/3/library/stdtypes.html#str)]

<a id="stelion.workspace.domain.dependency.DependencyGraph.edges_involving"></a>

#### edges_involving(name)

All dependency edges that reference the given project.

* **Parameters:**
  **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Project name to look up.
* **Returns:**
  Edges where *name* appears as dependent or dependency.
* **Return type:**
  [list](https://docs.python.org/3/library/stdtypes.html#list)[[DependencyEdge](#stelion.workspace.domain.dependency.DependencyEdge)]

<a id="stelion.workspace.domain.dependency.manual_edge_to_dependency_edge"></a>

### stelion.workspace.domain.dependency.manual_edge_to_dependency_edge(edge)

Convert a manifest ManualEdge to a resolved DependencyEdge.

* **Parameters:**
  **edge** ([*ManualEdge*](#stelion.workspace.domain.manifest.ManualEdge)) – Manually declared edge from the workspace manifest.
* **Returns:**
  Resolved edge with a validated mechanism.
* **Return type:**
  [DependencyEdge](#stelion.workspace.domain.dependency.DependencyEdge)
* **Raises:**
  [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the mechanism string does not match a known `DependencyMechanism`.

<a id="module-stelion.workspace.domain.bulk"></a>

<a id="bulk"></a>

## Bulk

Domain models for bulk operations across projects.

<a id="stelion.workspace.domain.bulk.ProjectFilter"></a>

### *class* stelion.workspace.domain.bulk.ProjectFilter(names=(), pattern=None, git_only=False, exclude=())

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Criteria for selecting a subset of projects.

<a id="stelion.workspace.domain.bulk.ProjectFilter.names"></a>

#### names *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Explicit project names to include.

<a id="stelion.workspace.domain.bulk.ProjectFilter.pattern"></a>

#### pattern *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Glob pattern for matching project names.

<a id="stelion.workspace.domain.bulk.ProjectFilter.git_only"></a>

#### git_only *: [bool](https://docs.python.org/3/library/functions.html#bool)* *= False*

If true, restrict to projects with a git repository.

<a id="stelion.workspace.domain.bulk.ProjectFilter.exclude"></a>

#### exclude *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Project names to exclude from selection.

<a id="stelion.workspace.domain.bulk.OutcomeStatus"></a>

### *class* stelion.workspace.domain.bulk.OutcomeStatus(\*values)

Bases: [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)

Result status for a single project within a bulk operation.

<a id="stelion.workspace.domain.bulk.OutcomeStatus.SUCCESS"></a>

#### SUCCESS *= 'success'*

<a id="stelion.workspace.domain.bulk.OutcomeStatus.SKIPPED"></a>

#### SKIPPED *= 'skipped'*

<a id="stelion.workspace.domain.bulk.OutcomeStatus.FAILED"></a>

#### FAILED *= 'failed'*

<a id="stelion.workspace.domain.bulk.ProjectOutcome"></a>

### *class* stelion.workspace.domain.bulk.ProjectOutcome(project, path, status, detail, error='')

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Outcome of executing a bulk operation on a single project.

<a id="stelion.workspace.domain.bulk.ProjectOutcome.project"></a>

#### project *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the project.

<a id="stelion.workspace.domain.bulk.ProjectOutcome.path"></a>

#### path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

Filesystem path to the project directory.

<a id="stelion.workspace.domain.bulk.ProjectOutcome.status"></a>

#### status *: [OutcomeStatus](#stelion.workspace.domain.bulk.OutcomeStatus)*

Result status of the operation.

<a id="stelion.workspace.domain.bulk.ProjectOutcome.detail"></a>

#### detail *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Human-readable description of the outcome.

<a id="stelion.workspace.domain.bulk.ProjectOutcome.error"></a>

#### error *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= ''*

Error message, empty if the operation succeeded.

<a id="stelion.workspace.domain.bulk.BulkResult"></a>

### *class* stelion.workspace.domain.bulk.BulkResult(label, outcomes=())

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Aggregated outcomes from a bulk operation across projects.

<a id="stelion.workspace.domain.bulk.BulkResult.label"></a>

#### label *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Human-readable label describing the bulk operation.

<a id="stelion.workspace.domain.bulk.BulkResult.outcomes"></a>

#### outcomes *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[ProjectOutcome](#stelion.workspace.domain.bulk.ProjectOutcome), ...]* *= ()*

Per-project outcomes in execution order.

<a id="stelion.workspace.domain.bulk.BulkResult.success_count"></a>

#### *property* success_count *: [int](https://docs.python.org/3/library/functions.html#int)*

Number of projects where the operation succeeded.

* **Returns:**
  Count of outcomes with `SUCCESS` status.
* **Return type:**
  [int](https://docs.python.org/3/library/functions.html#int)

<a id="stelion.workspace.domain.bulk.BulkResult.has_errors"></a>

#### *property* has_errors *: [bool](https://docs.python.org/3/library/functions.html#bool)*

True if any project operation failed.

* **Returns:**
  Whether at least one outcome has `FAILED` status.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="module-stelion.workspace.domain.comparison"></a>

<a id="comparison"></a>

## Comparison

Immutable domain models and pure functions for cross-project comparison.

<a id="stelion.workspace.domain.comparison.MatchMethod"></a>

### *class* stelion.workspace.domain.comparison.MatchMethod(\*values)

Bases: [`StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

How correspondence between nodes was established.

<a id="stelion.workspace.domain.comparison.MatchMethod.EXACT"></a>

#### EXACT *= 'exact'*

<a id="stelion.workspace.domain.comparison.MatchMethod.CASE_INSENSITIVE"></a>

#### CASE_INSENSITIVE *= 'case-insensitive'*

<a id="stelion.workspace.domain.comparison.MatchMethod.FUZZY"></a>

#### FUZZY *= 'fuzzy'*

<a id="stelion.workspace.domain.comparison.ContentKind"></a>

### *class* stelion.workspace.domain.comparison.ContentKind(\*values)

Bases: [`StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Dispatches the comparison strategy for file content.

<a id="stelion.workspace.domain.comparison.ContentKind.STRUCTURED"></a>

#### STRUCTURED *= 'structured'*

<a id="stelion.workspace.domain.comparison.ContentKind.UNSTRUCTURED"></a>

#### UNSTRUCTURED *= 'unstructured'*

<a id="stelion.workspace.domain.comparison.FileGranularity"></a>

### *class* stelion.workspace.domain.comparison.FileGranularity(\*values)

Bases: [`StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Level of detail for file content comparison.

<a id="stelion.workspace.domain.comparison.FileGranularity.SURVEY"></a>

#### SURVEY *= 'survey'*

<a id="stelion.workspace.domain.comparison.FileGranularity.DETAIL"></a>

#### DETAIL *= 'detail'*

<a id="stelion.workspace.domain.comparison.TreeTarget"></a>

### *class* stelion.workspace.domain.comparison.TreeTarget(subtree=None, include_patterns=(), exclude_patterns=())

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Target specification for architecture (tree) comparison.

<a id="stelion.workspace.domain.comparison.TreeTarget.subtree"></a>

#### subtree *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Relative path prefix to restrict the comparison scope.

<a id="stelion.workspace.domain.comparison.TreeTarget.include_patterns"></a>

#### include_patterns *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Glob patterns for paths to include.

<a id="stelion.workspace.domain.comparison.TreeTarget.exclude_patterns"></a>

#### exclude_patterns *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Glob patterns for paths to exclude.

<a id="stelion.workspace.domain.comparison.FileTargetEntry"></a>

### *class* stelion.workspace.domain.comparison.FileTargetEntry(canonical, overrides=<factory>, selectors=(), parser_hint=None)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

One logical file to compare across projects.

<a id="stelion.workspace.domain.comparison.FileTargetEntry.canonical"></a>

#### canonical *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

The standard relative path (e.g. `pyproject.toml`).

<a id="stelion.workspace.domain.comparison.FileTargetEntry.overrides"></a>

#### overrides *: [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping)[[str](https://docs.python.org/3/library/stdtypes.html#str), [str](https://docs.python.org/3/library/stdtypes.html#str)]*

Project-specific path remappings as `{project_name: actual_path}`.

<a id="stelion.workspace.domain.comparison.FileTargetEntry.selectors"></a>

#### selectors *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]* *= ()*

Dotted field paths to compare for structured files (empty = all).

<a id="stelion.workspace.domain.comparison.FileTargetEntry.parser_hint"></a>

#### parser_hint *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Force a parser regardless of extension (e.g. `"toml"`).

<a id="stelion.workspace.domain.comparison.FileTarget"></a>

### *class* stelion.workspace.domain.comparison.FileTarget(entries, granularity=FileGranularity.SURVEY, reference_project=None)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Target specification for file content comparison.

<a id="stelion.workspace.domain.comparison.FileTarget.entries"></a>

#### entries *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[FileTargetEntry](#stelion.workspace.domain.comparison.FileTargetEntry), ...]*

Logical files to compare.

<a id="stelion.workspace.domain.comparison.FileTarget.granularity"></a>

#### granularity *: [FileGranularity](#stelion.workspace.domain.comparison.FileGranularity)* *= 'survey'*

Level of detail for the comparison.

<a id="stelion.workspace.domain.comparison.FileTarget.reference_project"></a>

#### reference_project *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Project used as the baseline for detail-level diffs.

<a id="stelion.workspace.domain.comparison.ComparisonSpec"></a>

### *class* stelion.workspace.domain.comparison.ComparisonSpec(project_names, target)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Full declarative specification for a comparison operation.

Constructed from an instruction file or from CLI arguments.
`target` is either a [`TreeTarget`](#stelion.workspace.domain.comparison.TreeTarget) or a [`FileTarget`](#stelion.workspace.domain.comparison.FileTarget)
— the tagged union makes invalid states unrepresentable.

<a id="stelion.workspace.domain.comparison.ComparisonSpec.project_names"></a>

#### project_names *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]*

Names of projects to compare.

<a id="stelion.workspace.domain.comparison.ComparisonSpec.target"></a>

#### target *: [TreeTarget](#stelion.workspace.domain.comparison.TreeTarget) | [FileTarget](#stelion.workspace.domain.comparison.FileTarget)*

What to compare (architecture tree or file contents).

<a id="stelion.workspace.domain.comparison.TreeEntry"></a>

### *class* stelion.workspace.domain.comparison.TreeEntry(relative_path, project, is_directory)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A single node within a project’s file tree.

<a id="stelion.workspace.domain.comparison.TreeEntry.relative_path"></a>

#### relative_path *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Forward-slash path relative to the project root.

<a id="stelion.workspace.domain.comparison.TreeEntry.project"></a>

#### project *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the project this entry belongs to.

<a id="stelion.workspace.domain.comparison.TreeEntry.is_directory"></a>

#### is_directory *: [bool](https://docs.python.org/3/library/functions.html#bool)*

Whether the node is a directory.

<a id="stelion.workspace.domain.comparison.TreeSnapshot"></a>

### *class* stelion.workspace.domain.comparison.TreeSnapshot(project, root, entries)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Complete file-tree scan for one project.

<a id="stelion.workspace.domain.comparison.TreeSnapshot.project"></a>

#### project *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Project name.

<a id="stelion.workspace.domain.comparison.TreeSnapshot.root"></a>

#### root *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Filesystem root used for the scan.

<a id="stelion.workspace.domain.comparison.TreeSnapshot.entries"></a>

#### entries *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[TreeEntry](#stelion.workspace.domain.comparison.TreeEntry), ...]*

All nodes discovered in the tree.

<a id="stelion.workspace.domain.comparison.NodeMatch"></a>

### *class* stelion.workspace.domain.comparison.NodeMatch(canonical_path, resolved, present_in, absent_from, method, similarity, is_directory, children=())

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

An N-way mapping of one logical node across projects.

Presence is explicit: `present_in` lists projects that contain this
node, `absent_from` lists selected projects that do not.

<a id="stelion.workspace.domain.comparison.NodeMatch.canonical_path"></a>

#### canonical_path *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Normalized path used as the canonical key.

<a id="stelion.workspace.domain.comparison.NodeMatch.resolved"></a>

#### resolved *: [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping)[[str](https://docs.python.org/3/library/stdtypes.html#str), [str](https://docs.python.org/3/library/stdtypes.html#str)]*

Mapping from project name to actual relative path.

<a id="stelion.workspace.domain.comparison.NodeMatch.present_in"></a>

#### present_in *: [frozenset](https://docs.python.org/3/library/stdtypes.html#frozenset)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Projects that contain this node.

<a id="stelion.workspace.domain.comparison.NodeMatch.absent_from"></a>

#### absent_from *: [frozenset](https://docs.python.org/3/library/stdtypes.html#frozenset)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Selected projects that lack this node.

<a id="stelion.workspace.domain.comparison.NodeMatch.method"></a>

#### method *: [MatchMethod](#stelion.workspace.domain.comparison.MatchMethod)*

How correspondence was established.

<a id="stelion.workspace.domain.comparison.NodeMatch.similarity"></a>

#### similarity *: [float](https://docs.python.org/3/library/functions.html#float)*

Match confidence score (1.0 for exact).

<a id="stelion.workspace.domain.comparison.NodeMatch.is_directory"></a>

#### is_directory *: [bool](https://docs.python.org/3/library/functions.html#bool)*

Whether the node is a directory.

<a id="stelion.workspace.domain.comparison.NodeMatch.children"></a>

#### children *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[NodeMatch](#stelion.workspace.domain.comparison.NodeMatch), ...]* *= ()*

Recursively matched child nodes (directories only).

<a id="stelion.workspace.domain.comparison.TreeSummary"></a>

### *class* stelion.workspace.domain.comparison.TreeSummary(total_nodes, in_all, in_some, in_one, directories_matched, files_matched)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Aggregate counts for a tree comparison.

<a id="stelion.workspace.domain.comparison.TreeSummary.total_nodes"></a>

#### total_nodes *: [int](https://docs.python.org/3/library/functions.html#int)*

Total number of matched logical nodes.

<a id="stelion.workspace.domain.comparison.TreeSummary.in_all"></a>

#### in_all *: [int](https://docs.python.org/3/library/functions.html#int)*

Nodes present in every compared project.

<a id="stelion.workspace.domain.comparison.TreeSummary.in_some"></a>

#### in_some *: [int](https://docs.python.org/3/library/functions.html#int)*

Nodes present in more than one but not all projects.

<a id="stelion.workspace.domain.comparison.TreeSummary.in_one"></a>

#### in_one *: [int](https://docs.python.org/3/library/functions.html#int)*

Nodes unique to a single project.

<a id="stelion.workspace.domain.comparison.TreeSummary.directories_matched"></a>

#### directories_matched *: [int](https://docs.python.org/3/library/functions.html#int)*

Number of directory nodes.

<a id="stelion.workspace.domain.comparison.TreeSummary.files_matched"></a>

#### files_matched *: [int](https://docs.python.org/3/library/functions.html#int)*

Number of file nodes.

<a id="stelion.workspace.domain.comparison.TreeReport"></a>

### *class* stelion.workspace.domain.comparison.TreeReport(projects, subtree, matches, summary)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Full architecture comparison result.

<a id="stelion.workspace.domain.comparison.TreeReport.projects"></a>

#### projects *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]*

Names of the compared projects.

<a id="stelion.workspace.domain.comparison.TreeReport.subtree"></a>

#### subtree *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)*

Subtree prefix that was compared, or `None` for the full tree.

<a id="stelion.workspace.domain.comparison.TreeReport.matches"></a>

#### matches *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[NodeMatch](#stelion.workspace.domain.comparison.NodeMatch), ...]*

Top-level matched nodes.

<a id="stelion.workspace.domain.comparison.TreeReport.summary"></a>

#### summary *: [TreeSummary](#stelion.workspace.domain.comparison.TreeSummary)*

Aggregate counts.

<a id="stelion.workspace.domain.comparison.FieldDiff"></a>

### *class* stelion.workspace.domain.comparison.FieldDiff(path, values)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

One structured field compared across N projects.

Status is derived from the values: all equal means identical, some
`None` means partial presence, all different means diverged.

<a id="stelion.workspace.domain.comparison.FieldDiff.path"></a>

#### path *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Dotted field path within the structured document.

<a id="stelion.workspace.domain.comparison.FieldDiff.values"></a>

#### values *: [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping)[[str](https://docs.python.org/3/library/stdtypes.html#str), [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)]*

Per-project stringified values (`None` if absent).

<a id="stelion.workspace.domain.comparison.FieldDiff.is_identical"></a>

#### *property* is_identical *: [bool](https://docs.python.org/3/library/functions.html#bool)*

All projects have the same non-None value.

* **Returns:**
  True when every project has the field and all values are equal.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="stelion.workspace.domain.comparison.FieldDiff.is_partial"></a>

#### *property* is_partial *: [bool](https://docs.python.org/3/library/functions.html#bool)*

The field is absent in at least one project.

* **Returns:**
  True when at least one project lacks this field.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="stelion.workspace.domain.comparison.VariantGroup"></a>

### *class* stelion.workspace.domain.comparison.VariantGroup(projects, digest, line_count)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Projects with identical content for an unstructured file.

<a id="stelion.workspace.domain.comparison.VariantGroup.projects"></a>

#### projects *: [frozenset](https://docs.python.org/3/library/stdtypes.html#frozenset)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Project names sharing the same content.

<a id="stelion.workspace.domain.comparison.VariantGroup.digest"></a>

#### digest *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Truncated SHA-256 hex digest of the content.

<a id="stelion.workspace.domain.comparison.VariantGroup.line_count"></a>

#### line_count *: [int](https://docs.python.org/3/library/functions.html#int)*

Number of lines in the content.

<a id="stelion.workspace.domain.comparison.PairwiseSimilarity"></a>

### *class* stelion.workspace.domain.comparison.PairwiseSimilarity(project_a, project_b, score)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Similarity score between two projects for an unstructured file.

<a id="stelion.workspace.domain.comparison.PairwiseSimilarity.project_a"></a>

#### project_a *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

First project name.

<a id="stelion.workspace.domain.comparison.PairwiseSimilarity.project_b"></a>

#### project_b *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Second project name.

<a id="stelion.workspace.domain.comparison.PairwiseSimilarity.score"></a>

#### score *: [float](https://docs.python.org/3/library/functions.html#float)*

SequenceMatcher ratio between the two files.

<a id="stelion.workspace.domain.comparison.ReferenceDiff"></a>

### *class* stelion.workspace.domain.comparison.ReferenceDiff(project, diff_lines)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Unified diff against the reference project for one compared file.

<a id="stelion.workspace.domain.comparison.ReferenceDiff.project"></a>

#### project *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the project being compared to the reference.

<a id="stelion.workspace.domain.comparison.ReferenceDiff.diff_lines"></a>

#### diff_lines *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]*

Lines of the unified diff output.

<a id="stelion.workspace.domain.comparison.FileDiffResult"></a>

### *class* stelion.workspace.domain.comparison.FileDiffResult(canonical_path, actual_paths, present_in, absent_from, content_kind, field_diffs=(), variants=(), similarities=(), reference_project=None, reference_diffs=(), issue='')

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Comparison result for one logical file across projects.

<a id="stelion.workspace.domain.comparison.FileDiffResult.canonical_path"></a>

#### canonical_path *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Normalized file path used as the comparison key.

<a id="stelion.workspace.domain.comparison.FileDiffResult.actual_paths"></a>

#### actual_paths *: [Mapping](https://docs.python.org/3/library/typing.html#typing.Mapping)[[str](https://docs.python.org/3/library/stdtypes.html#str), [str](https://docs.python.org/3/library/stdtypes.html#str)]*

Per-project resolved file paths.

<a id="stelion.workspace.domain.comparison.FileDiffResult.present_in"></a>

#### present_in *: [frozenset](https://docs.python.org/3/library/stdtypes.html#frozenset)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Projects where the file exists.

<a id="stelion.workspace.domain.comparison.FileDiffResult.absent_from"></a>

#### absent_from *: [frozenset](https://docs.python.org/3/library/stdtypes.html#frozenset)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Projects where the file is missing.

<a id="stelion.workspace.domain.comparison.FileDiffResult.content_kind"></a>

#### content_kind *: [ContentKind](#stelion.workspace.domain.comparison.ContentKind)*

Whether the file was compared as structured or unstructured.

<a id="stelion.workspace.domain.comparison.FileDiffResult.field_diffs"></a>

#### field_diffs *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[FieldDiff](#stelion.workspace.domain.comparison.FieldDiff), ...]* *= ()*

Per-field diffs (structured files only).

<a id="stelion.workspace.domain.comparison.FileDiffResult.variants"></a>

#### variants *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[VariantGroup](#stelion.workspace.domain.comparison.VariantGroup), ...]* *= ()*

Content groups (unstructured files only).

<a id="stelion.workspace.domain.comparison.FileDiffResult.similarities"></a>

#### similarities *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[PairwiseSimilarity](#stelion.workspace.domain.comparison.PairwiseSimilarity), ...]* *= ()*

Pairwise similarity scores (unstructured files only).

<a id="stelion.workspace.domain.comparison.FileDiffResult.reference_project"></a>

#### reference_project *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Baseline project for detail-level diffs.

<a id="stelion.workspace.domain.comparison.FileDiffResult.reference_diffs"></a>

#### reference_diffs *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[ReferenceDiff](#stelion.workspace.domain.comparison.ReferenceDiff), ...]* *= ()*

Unified diffs against the reference project.

<a id="stelion.workspace.domain.comparison.FileDiffResult.issue"></a>

#### issue *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= ''*

Error message if comparison failed for this file.

<a id="stelion.workspace.domain.comparison.FileDiffResult.is_identical"></a>

#### *property* is_identical *: [bool](https://docs.python.org/3/library/functions.html#bool)*

All projects have identical content (no absent, no differences).

* **Returns:**
  True when no project is missing the file and all content matches.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="stelion.workspace.domain.comparison.FileSummary"></a>

### *class* stelion.workspace.domain.comparison.FileSummary(files_compared, fully_identical, with_differences, with_errors)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Aggregate counts for a file comparison.

<a id="stelion.workspace.domain.comparison.FileSummary.files_compared"></a>

#### files_compared *: [int](https://docs.python.org/3/library/functions.html#int)*

Total number of logical files compared.

<a id="stelion.workspace.domain.comparison.FileSummary.fully_identical"></a>

#### fully_identical *: [int](https://docs.python.org/3/library/functions.html#int)*

Files identical across all projects.

<a id="stelion.workspace.domain.comparison.FileSummary.with_differences"></a>

#### with_differences *: [int](https://docs.python.org/3/library/functions.html#int)*

Files with at least one difference.

<a id="stelion.workspace.domain.comparison.FileSummary.with_errors"></a>

#### with_errors *: [int](https://docs.python.org/3/library/functions.html#int)*

Files that could not be compared due to errors.

<a id="stelion.workspace.domain.comparison.FileReport"></a>

### *class* stelion.workspace.domain.comparison.FileReport(projects, results, summary)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Full file comparison result.

<a id="stelion.workspace.domain.comparison.FileReport.projects"></a>

#### projects *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]*

Names of the compared projects.

<a id="stelion.workspace.domain.comparison.FileReport.results"></a>

#### results *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[FileDiffResult](#stelion.workspace.domain.comparison.FileDiffResult), ...]*

Per-file comparison results.

<a id="stelion.workspace.domain.comparison.FileReport.summary"></a>

#### summary *: [FileSummary](#stelion.workspace.domain.comparison.FileSummary)*

Aggregate counts.

<a id="stelion.workspace.domain.comparison.match_tree_nodes"></a>

### stelion.workspace.domain.comparison.match_tree_nodes(snapshots, all_projects)

Match file-tree nodes across projects hierarchically.

Directories are matched first at each depth level, then files within
matched directories.  Each level uses a three-pass strategy: exact
name, case-insensitive, then fuzzy (above `_FUZZY_THRESHOLD`).

* **Parameters:**
  * **snapshots** ([*tuple*](https://docs.python.org/3/library/stdtypes.html#tuple) *[*[*TreeSnapshot*](#stelion.workspace.domain.comparison.TreeSnapshot) *,*  *...* *]*) – Per-project file-tree scans.
  * **all_projects** ([*frozenset*](https://docs.python.org/3/library/stdtypes.html#frozenset) *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Complete set of project names being compared.
* **Returns:**
  Hierarchically matched nodes sorted by canonical path.
* **Return type:**
  [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[NodeMatch](#stelion.workspace.domain.comparison.NodeMatch), …]

<a id="stelion.workspace.domain.comparison.diff_structured"></a>

### stelion.workspace.domain.comparison.diff_structured(contents, selectors=())

Compare parsed structured data field by field across projects.

* **Parameters:**
  * **contents** (*Mapping* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* [*dict*](https://docs.python.org/3/library/stdtypes.html#dict) *]*) – `{project_name: parsed_dict}` for each project that has this file.
  * **selectors** ([*tuple*](https://docs.python.org/3/library/stdtypes.html#tuple) *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,*  *...* *]*) – Dotted field paths to limit the comparison. Empty means compare all.
* **Returns:**
  Per-field comparison results.
* **Return type:**
  [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[FieldDiff](#stelion.workspace.domain.comparison.FieldDiff), …]

<a id="stelion.workspace.domain.comparison.group_variants"></a>

### stelion.workspace.domain.comparison.group_variants(contents)

Group projects by identical content.

Returns groups sorted by descending size (largest group first).

* **Parameters:**
  **contents** (*Mapping* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* [*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Per-project raw file content.
* **Returns:**
  Groups sorted by descending member count.
* **Return type:**
  [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[VariantGroup](#stelion.workspace.domain.comparison.VariantGroup), …]

<a id="stelion.workspace.domain.comparison.compute_pairwise_similarity"></a>

### stelion.workspace.domain.comparison.compute_pairwise_similarity(contents)

Compute SequenceMatcher ratio for every pair of projects.

* **Parameters:**
  **contents** (*Mapping* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* [*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Per-project raw file content.
* **Returns:**
  Similarity scores for all unique project pairs.
* **Return type:**
  [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[PairwiseSimilarity](#stelion.workspace.domain.comparison.PairwiseSimilarity), …]

<a id="stelion.workspace.domain.comparison.compute_reference_diffs"></a>

### stelion.workspace.domain.comparison.compute_reference_diffs(contents, reference_project)

Compute unified diffs from the reference project to every other project.

* **Parameters:**
  * **contents** (*Mapping* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* [*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Per-project raw file content.
  * **reference_project** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Project name used as the diff baseline.
* **Returns:**
  Unified diffs for each non-reference project.
* **Return type:**
  [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[ReferenceDiff](#stelion.workspace.domain.comparison.ReferenceDiff), …]

<a id="stelion.workspace.domain.comparison.compute_tree_summary"></a>

### stelion.workspace.domain.comparison.compute_tree_summary(matches, all_projects)

Derive aggregate counts from matched nodes.

* **Parameters:**
  * **matches** ([*tuple*](https://docs.python.org/3/library/stdtypes.html#tuple) *[*[*NodeMatch*](#stelion.workspace.domain.comparison.NodeMatch) *,*  *...* *]*) – Top-level matched nodes (children are counted recursively).
  * **all_projects** ([*frozenset*](https://docs.python.org/3/library/stdtypes.html#frozenset) *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Complete set of project names being compared.
* **Returns:**
  Aggregate presence and type counts.
* **Return type:**
  [TreeSummary](#stelion.workspace.domain.comparison.TreeSummary)

<a id="stelion.workspace.domain.comparison.compute_file_summary"></a>

### stelion.workspace.domain.comparison.compute_file_summary(results)

Derive aggregate counts from file comparison results.

* **Parameters:**
  **results** ([*tuple*](https://docs.python.org/3/library/stdtypes.html#tuple) *[*[*FileDiffResult*](#stelion.workspace.domain.comparison.FileDiffResult) *,*  *...* *]*) – Per-file comparison results.
* **Returns:**
  Counts of identical, different, and errored files.
* **Return type:**
  [FileSummary](#stelion.workspace.domain.comparison.FileSummary)

<a id="module-stelion.workspace.domain.status"></a>

<a id="status"></a>

## Status

Domain models for workspace drift detection.

<a id="stelion.workspace.domain.status.FileStatus"></a>

### *class* stelion.workspace.domain.status.FileStatus(\*values)

Bases: [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)

Status of a generated file relative to its expected content.

<a id="stelion.workspace.domain.status.FileStatus.CURRENT"></a>

#### CURRENT *= 'current'*

<a id="stelion.workspace.domain.status.FileStatus.STALE"></a>

#### STALE *= 'stale'*

<a id="stelion.workspace.domain.status.FileStatus.MISSING"></a>

#### MISSING *= 'missing'*

<a id="stelion.workspace.domain.status.DriftEntry"></a>

### *class* stelion.workspace.domain.status.DriftEntry(path, status, detail='')

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Drift status for a single generated file.

<a id="stelion.workspace.domain.status.DriftEntry.path"></a>

#### path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

Filesystem path of the generated file.

<a id="stelion.workspace.domain.status.DriftEntry.status"></a>

#### status *: [FileStatus](#stelion.workspace.domain.status.FileStatus)*

Whether the file is current, stale, or missing.

<a id="stelion.workspace.domain.status.DriftEntry.detail"></a>

#### detail *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= ''*

Human-readable explanation of the drift.

<a id="stelion.workspace.domain.status.DriftReport"></a>

### *class* stelion.workspace.domain.status.DriftReport(entries=())

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Aggregated drift report for all generated workspace files.

<a id="stelion.workspace.domain.status.DriftReport.entries"></a>

#### entries *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[DriftEntry](#stelion.workspace.domain.status.DriftEntry), ...]* *= ()*

Individual drift entries for each generated file.

<a id="stelion.workspace.domain.status.DriftReport.has_drift"></a>

#### *property* has_drift *: [bool](https://docs.python.org/3/library/functions.html#bool)*

True if any file is stale or missing.

* **Returns:**
  Whether any entry has a non-current status.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="module-stelion.workspace.domain.sync"></a>

<a id="sync"></a>

## Sync

Domain models for submodule synchronization.

<a id="stelion.workspace.domain.sync.SyncOrigin"></a>

### *class* stelion.workspace.domain.sync.SyncOrigin(\*values)

Bases: [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)

How the source commit for synchronization is determined.

<a id="stelion.workspace.domain.sync.SyncOrigin.LOCAL"></a>

#### LOCAL *= 'local'*

<a id="stelion.workspace.domain.sync.SyncOrigin.SUPERPROJECT"></a>

#### SUPERPROJECT *= 'superproject'*

<a id="stelion.workspace.domain.sync.SyncOrigin.REMOTE"></a>

#### REMOTE *= 'remote'*

<a id="stelion.workspace.domain.sync.Superproject"></a>

### *class* stelion.workspace.domain.sync.Superproject(name, path)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A project that consumes dependencies as git submodules.

<a id="stelion.workspace.domain.sync.Superproject.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Project name.

<a id="stelion.workspace.domain.sync.Superproject.path"></a>

#### path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

Filesystem path to the superproject root.

<a id="stelion.workspace.domain.sync.SubmoduleTarget"></a>

### *class* stelion.workspace.domain.sync.SubmoduleTarget(superproject_name, superproject_dir, submodule_path)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

A superproject containing a submodule that should be updated.

<a id="stelion.workspace.domain.sync.SubmoduleTarget.superproject_name"></a>

#### superproject_name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the superproject.

<a id="stelion.workspace.domain.sync.SubmoduleTarget.superproject_dir"></a>

#### superproject_dir *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

Filesystem path to the superproject root.

<a id="stelion.workspace.domain.sync.SubmoduleTarget.submodule_path"></a>

#### submodule_path *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Relative path of the submodule within the superproject.

<a id="stelion.workspace.domain.sync.PushSpec"></a>

### *class* stelion.workspace.domain.sync.PushSpec(repo_dir, remote, branch)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Remote push parameters.

<a id="stelion.workspace.domain.sync.PushSpec.repo_dir"></a>

#### repo_dir *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

Filesystem path to the repository.

<a id="stelion.workspace.domain.sync.PushSpec.remote"></a>

#### remote *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the git remote.

<a id="stelion.workspace.domain.sync.PushSpec.branch"></a>

#### branch *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Branch to push.

<a id="stelion.workspace.domain.sync.SyncPlan"></a>

### *class* stelion.workspace.domain.sync.SyncPlan(dependency, origin, source_label, target_commit, submodule_targets, local_dir=None, push_spec=None)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Resolved plan for propagating a commit across all replicas of a dependency.

<a id="stelion.workspace.domain.sync.SyncPlan.dependency"></a>

#### dependency *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the dependency being synchronized.

<a id="stelion.workspace.domain.sync.SyncPlan.origin"></a>

#### origin *: [SyncOrigin](#stelion.workspace.domain.sync.SyncOrigin)*

How the source commit was determined.

<a id="stelion.workspace.domain.sync.SyncPlan.source_label"></a>

#### source_label *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Human-readable description of the commit source.

<a id="stelion.workspace.domain.sync.SyncPlan.target_commit"></a>

#### target_commit *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Git commit hash to propagate.

<a id="stelion.workspace.domain.sync.SyncPlan.submodule_targets"></a>

#### submodule_targets *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[SubmoduleTarget](#stelion.workspace.domain.sync.SubmoduleTarget), ...]*

Superprojects whose submodule pointers should be updated.

<a id="stelion.workspace.domain.sync.SyncPlan.local_dir"></a>

#### local_dir *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Local clone directory, if the dependency has one.

<a id="stelion.workspace.domain.sync.SyncPlan.push_spec"></a>

#### push_spec *: [PushSpec](#stelion.workspace.domain.sync.PushSpec) | [None](https://docs.python.org/3/library/constants.html#None)* *= None*

Remote push parameters, if a push is planned.

<a id="stelion.workspace.domain.sync.OutcomeKind"></a>

### *class* stelion.workspace.domain.sync.OutcomeKind(\*values)

Bases: [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)

Which replica kind a sync outcome refers to.

<a id="stelion.workspace.domain.sync.OutcomeKind.SUBMODULE"></a>

#### SUBMODULE *= 'submodule'*

<a id="stelion.workspace.domain.sync.OutcomeKind.LOCAL"></a>

#### LOCAL *= 'local'*

<a id="stelion.workspace.domain.sync.OutcomeKind.REMOTE"></a>

#### REMOTE *= 'remote'*

<a id="stelion.workspace.domain.sync.SyncOutcome"></a>

### *class* stelion.workspace.domain.sync.SyncOutcome(kind, label, old_ref, new_ref, applied, error='')

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Result of a single synchronization action.

<a id="stelion.workspace.domain.sync.SyncOutcome.kind"></a>

#### kind *: [OutcomeKind](#stelion.workspace.domain.sync.OutcomeKind)*

Which replica kind was targeted.

<a id="stelion.workspace.domain.sync.SyncOutcome.label"></a>

#### label *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Human-readable identifier for the target.

<a id="stelion.workspace.domain.sync.SyncOutcome.old_ref"></a>

#### old_ref *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Git ref before the sync action.

<a id="stelion.workspace.domain.sync.SyncOutcome.new_ref"></a>

#### new_ref *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Git ref after the sync action.

<a id="stelion.workspace.domain.sync.SyncOutcome.applied"></a>

#### applied *: [bool](https://docs.python.org/3/library/functions.html#bool)*

Whether the action actually changed the replica.

<a id="stelion.workspace.domain.sync.SyncOutcome.error"></a>

#### error *: [str](https://docs.python.org/3/library/stdtypes.html#str)* *= ''*

Error message, empty on success.

<a id="stelion.workspace.domain.sync.SyncResult"></a>

### *class* stelion.workspace.domain.sync.SyncResult(dependency, target_commit, outcomes=())

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Aggregated outcomes from executing a sync plan.

<a id="stelion.workspace.domain.sync.SyncResult.dependency"></a>

#### dependency *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Name of the dependency that was synchronized.

<a id="stelion.workspace.domain.sync.SyncResult.target_commit"></a>

#### target_commit *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

Git commit hash that was propagated.

<a id="stelion.workspace.domain.sync.SyncResult.outcomes"></a>

#### outcomes *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[SyncOutcome](#stelion.workspace.domain.sync.SyncOutcome), ...]* *= ()*

Per-replica outcomes in execution order.

<a id="stelion.workspace.domain.sync.SyncResult.applied_count"></a>

#### *property* applied_count *: [int](https://docs.python.org/3/library/functions.html#int)*

Number of replicas that were actually changed.

* **Returns:**
  Count of outcomes where `applied` is true.
* **Return type:**
  [int](https://docs.python.org/3/library/functions.html#int)

<a id="stelion.workspace.domain.sync.SyncResult.has_errors"></a>

#### *property* has_errors *: [bool](https://docs.python.org/3/library/functions.html#bool)*

True if any action failed.

* **Returns:**
  Whether any outcome has a non-empty error message.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)
