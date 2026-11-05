<a id="workspace-application"></a>

# Workspace Application

Application use-cases coordinating domain models and infrastructure services.

<a id="module-stelion.workspace.application.protocols"></a>

<a id="protocols"></a>

## Protocols

Protocol interfaces for workspace infrastructure capabilities.

<a id="stelion.workspace.application.protocols.MetadataExtractor"></a>

### *class* stelion.workspace.application.protocols.MetadataExtractor(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Extract project metadata from a directory.

<a id="stelion.workspace.application.protocols.MetadataExtractor.extract"></a>

#### extract(project_dir)

Extract metadata from the given project directory.

* **Parameters:**
  **project_dir** (*Path*) – Root directory of the project.

<a id="stelion.workspace.application.protocols.DependencyScanner"></a>

### *class* stelion.workspace.application.protocols.DependencyScanner(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Scan a project directory for inter-project dependency edges.

<a id="stelion.workspace.application.protocols.DependencyScanner.scan"></a>

#### scan(project_name, project_dir, all_project_names)

Scan the project directory for dependency edges.

* **Parameters:**
  * **project_name** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the project being scanned.
  * **project_dir** (*Path*) – Root directory of the project.
  * **all_project_names** ([*set*](https://docs.python.org/3/builtins/stdtypes.html#set) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *]*) – Names of all known projects in the workspace.

<a id="stelion.workspace.application.protocols.EnvironmentReader"></a>

### *class* stelion.workspace.application.protocols.EnvironmentReader(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Read a Conda environment spec from a project directory.

<a id="stelion.workspace.application.protocols.EnvironmentReader.read"></a>

#### read(project_dir)

Read the Conda environment spec from the project directory.

* **Parameters:**
  **project_dir** (*Path*) – Root directory of the project.

<a id="stelion.workspace.application.protocols.FileReader"></a>

### *class* stelion.workspace.application.protocols.FileReader(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Read file content from disk.

<a id="stelion.workspace.application.protocols.FileReader.read"></a>

#### read(path)

Read and return the text content of the file at *path*.

* **Parameters:**
  **path** (*Path*) – File to read.

<a id="stelion.workspace.application.protocols.FileWriter"></a>

### *class* stelion.workspace.application.protocols.FileWriter(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Write file content to disk.

<a id="stelion.workspace.application.protocols.FileWriter.write"></a>

#### write(path, content)

Write *content* to the file at *path*.

* **Parameters:**
  * **path** (*Path*) – Destination file path.
  * **content** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Text content to write.

<a id="stelion.workspace.application.protocols.FileHasher"></a>

### *class* stelion.workspace.application.protocols.FileHasher(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Compute a content hash for drift detection.

<a id="stelion.workspace.application.protocols.FileHasher.hash_content"></a>

#### hash_content(content)

Return a hash string for the given content.

* **Parameters:**
  **content** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Text content to hash.

<a id="stelion.workspace.application.protocols.PackageDataLoader"></a>

### *class* stelion.workspace.application.protocols.PackageDataLoader(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Load bundled package data resources.

<a id="stelion.workspace.application.protocols.PackageDataLoader.load_text"></a>

#### load_text(resource_path)

Load a bundled text resource.

* **Parameters:**
  **resource_path** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Package-relative path to the resource.

<a id="stelion.workspace.application.protocols.PackageDataLoader.load_json"></a>

#### load_json(resource_path)

Load a bundled JSON resource and return the parsed object.

* **Parameters:**
  **resource_path** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Package-relative path to the JSON resource.

<a id="stelion.workspace.application.protocols.WorkspaceFileRenderer"></a>

### *class* stelion.workspace.application.protocols.WorkspaceFileRenderer(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Render a VS Code .code-workspace file.

<a id="stelion.workspace.application.protocols.ProjectsYamlRenderer"></a>

### *class* stelion.workspace.application.protocols.ProjectsYamlRenderer(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Render the projects registry YAML.

<a id="stelion.workspace.application.protocols.DependencyYamlRenderer"></a>

### *class* stelion.workspace.application.protocols.DependencyYamlRenderer(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Render the dependency graph YAML.

<a id="stelion.workspace.application.protocols.EnvironmentRenderer"></a>

### *class* stelion.workspace.application.protocols.EnvironmentRenderer(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Render the shared Conda environment YAML.

<a id="stelion.workspace.application.protocols.GenerationServices"></a>

### *class* stelion.workspace.application.protocols.GenerationServices(render_workspace_file, render_projects_yaml, render_dependency_yaml, render_environment, writer, reader, hasher)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Bundled infrastructure services for workspace artifact generation.

<a id="stelion.workspace.application.protocols.GenerationServices.render_workspace_file"></a>

#### render_workspace_file *: [WorkspaceFileRenderer](#stelion.workspace.application.protocols.WorkspaceFileRenderer)*

Renderer for the VS Code workspace file.

<a id="stelion.workspace.application.protocols.GenerationServices.render_projects_yaml"></a>

#### render_projects_yaml *: [ProjectsYamlRenderer](#stelion.workspace.application.protocols.ProjectsYamlRenderer)*

Renderer for the projects registry YAML.

<a id="stelion.workspace.application.protocols.GenerationServices.render_dependency_yaml"></a>

#### render_dependency_yaml *: [DependencyYamlRenderer](#stelion.workspace.application.protocols.DependencyYamlRenderer)*

Renderer for the dependency graph YAML.

<a id="stelion.workspace.application.protocols.GenerationServices.render_environment"></a>

#### render_environment *: [EnvironmentRenderer](#stelion.workspace.application.protocols.EnvironmentRenderer)*

Renderer for the shared Conda environment YAML.

<a id="stelion.workspace.application.protocols.GenerationServices.writer"></a>

#### writer *: [FileWriter](#stelion.workspace.application.protocols.FileWriter)*

File writer for generated artifacts.

<a id="stelion.workspace.application.protocols.GenerationServices.reader"></a>

#### reader *: [FileReader](#stelion.workspace.application.protocols.FileReader)*

File reader for existing artifacts.

<a id="stelion.workspace.application.protocols.GenerationServices.hasher"></a>

#### hasher *: [FileHasher](#stelion.workspace.application.protocols.FileHasher)*

Content hasher for drift detection.

<a id="stelion.workspace.application.protocols.GitOperations"></a>

### *class* stelion.workspace.application.protocols.GitOperations(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Git operations needed for submodule synchronization.

<a id="stelion.workspace.application.protocols.GitOperations.head_commit"></a>

#### head_commit(repo_dir)

Return the HEAD commit hash of the repository.

* **Parameters:**
  **repo_dir** (*Path*) – Path to the git repository.

<a id="stelion.workspace.application.protocols.GitOperations.submodule_commit"></a>

#### submodule_commit(superproject_dir, submodule_path)

Return the commit hash the superproject records for the submodule.

* **Parameters:**
  * **superproject_dir** (*Path*) – Root directory of the superproject.
  * **submodule_path** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Relative path to the submodule within the superproject.

<a id="stelion.workspace.application.protocols.GitOperations.fetch_remote"></a>

#### fetch_remote(repo_dir)

Fetch from the default remote.

* **Parameters:**
  **repo_dir** (*Path*) – Path to the git repository.

<a id="stelion.workspace.application.protocols.GitOperations.remote_head"></a>

#### remote_head(repo_dir, remote, branch)

Return the HEAD commit hash of the remote tracking branch.

* **Parameters:**
  * **repo_dir** (*Path*) – Path to the git repository.
  * **remote** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Remote name.
  * **branch** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Branch name on the remote.

<a id="stelion.workspace.application.protocols.GitOperations.update_submodule_pointer"></a>

#### update_submodule_pointer(superproject_dir, submodule_path, commit)

Update the superproject’s submodule pointer to the given commit.

* **Parameters:**
  * **superproject_dir** (*Path*) – Root directory of the superproject.
  * **submodule_path** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Relative path to the submodule within the superproject.
  * **commit** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Commit hash to set the pointer to.

<a id="stelion.workspace.application.protocols.GitOperations.commit_submodule_update"></a>

#### commit_submodule_update(superproject_dir, submodule_path, dependency, commit_short)

Commit the submodule pointer update in the superproject.

* **Parameters:**
  * **superproject_dir** (*Path*) – Root directory of the superproject.
  * **submodule_path** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Relative path to the submodule within the superproject.
  * **dependency** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the dependency project.
  * **commit_short** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Short commit hash for the commit message.

<a id="stelion.workspace.application.protocols.GitOperations.is_clean"></a>

#### is_clean(repo_dir)

Return True if the working tree has no uncommitted changes.

* **Parameters:**
  **repo_dir** (*Path*) – Path to the git repository.

<a id="stelion.workspace.application.protocols.GitOperations.update_local_clone"></a>

#### update_local_clone(repo_dir, commit)

Check out the given commit in the local clone.

* **Parameters:**
  * **repo_dir** (*Path*) – Path to the local clone.
  * **commit** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Commit hash to check out.

<a id="stelion.workspace.application.protocols.GitOperations.push_to_remote"></a>

#### push_to_remote(repo_dir, remote, branch)

Push the local branch to the remote.

* **Parameters:**
  * **repo_dir** (*Path*) – Path to the git repository.
  * **remote** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Remote name.
  * **branch** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Branch name to push.

<a id="stelion.workspace.application.protocols.CommandResult"></a>

### *class* stelion.workspace.application.protocols.CommandResult(return_code, stdout, stderr)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Captured output from a subprocess execution.

<a id="stelion.workspace.application.protocols.CommandResult.return_code"></a>

#### return_code *: [int](https://docs.python.org/3/builtins/functions.html#int)*

Process exit code.

<a id="stelion.workspace.application.protocols.CommandResult.stdout"></a>

#### stdout *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)*

Captured standard output.

<a id="stelion.workspace.application.protocols.CommandResult.stderr"></a>

#### stderr *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)*

Captured standard error.

<a id="stelion.workspace.application.protocols.CommandRunner"></a>

### *class* stelion.workspace.application.protocols.CommandRunner(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Run a command in a working directory and capture its output.

<a id="stelion.workspace.application.protocols.CommandRunner.run"></a>

#### run(args, cwd)

Run a command with the given arguments in the working directory.

* **Parameters:**
  * **args** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,*  *...* *]*) – Command and arguments to execute.
  * **cwd** (*Path*) – Working directory for the subprocess.

<a id="stelion.workspace.application.protocols.BulkOperation"></a>

### *class* stelion.workspace.application.protocols.BulkOperation(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Operation executable on a single project within a bulk run.

<a id="stelion.workspace.application.protocols.BulkOperation.label"></a>

#### *property* label *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)*

Human-readable label for the operation.

<a id="stelion.workspace.application.protocols.TreeScanner"></a>

### *class* stelion.workspace.application.protocols.TreeScanner(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Scan a project directory and return its file-tree snapshot.

<a id="stelion.workspace.application.protocols.TreeScanner.scan"></a>

#### scan(project_dir, subtree, include, exclude, \*, project_name=None)

Scan the project directory and return a file-tree snapshot.

* **Parameters:**
  * **project_dir** (*Path*) – Root directory of the project.
  * **subtree** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *|* *None*) – Optional subdirectory to restrict the scan to.
  * **include** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,*  *...* *]*) – Glob patterns for files to include.
  * **exclude** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,*  *...* *]*) – Glob patterns for files to exclude.
  * **project_name** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *|* *None*) – Optional project name for labelling the snapshot.

<a id="stelion.workspace.application.protocols.StructuredParser"></a>

### *class* stelion.workspace.application.protocols.StructuredParser(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Parse structured text content into a nested dict.

Implementations consume **text**, not file paths — the application
layer reads files via [`FileReader`](#stelion.workspace.application.protocols.FileReader) and hands the content here.

<a id="stelion.workspace.application.protocols.StructuredParser.parse"></a>

#### parse(content, \*, extension='', hint=None)

Parse structured text content into a nested dict.

* **Parameters:**
  * **content** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Raw text content to parse.
  * **extension** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – File extension hint for format detection.
  * **hint** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *|* *None*) – Additional format hint.

<a id="stelion.workspace.application.protocols.SpecLoader"></a>

### *class* stelion.workspace.application.protocols.SpecLoader(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Load a comparison instruction file into a typed specification.

<a id="stelion.workspace.application.protocols.SpecLoader.load"></a>

#### load(path)

Load the comparison spec from the given file path.

* **Parameters:**
  **path** (*Path*) – Path to the comparison instruction file.

<a id="module-stelion.workspace.application.bootstrap"></a>

<a id="bootstrap"></a>

## Bootstrap

New project bootstrapping use-case.

Copies a template project, substitutes placeholders, renames directories
and files, and optionally initializes a git repository.

<a id="stelion.workspace.application.bootstrap.BootstrapResult"></a>

### *class* stelion.workspace.application.bootstrap.BootstrapResult(name, target_dir, placeholders_replaced, files_renamed, git_initialized)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Outcome of bootstrapping a new project.

<a id="stelion.workspace.application.bootstrap.BootstrapResult.name"></a>

#### name *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)*

Project name.

<a id="stelion.workspace.application.bootstrap.BootstrapResult.target_dir"></a>

#### target_dir *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

Absolute path to the created project directory.

<a id="stelion.workspace.application.bootstrap.BootstrapResult.placeholders_replaced"></a>

#### placeholders_replaced *: [int](https://docs.python.org/3/builtins/functions.html#int)*

Number of placeholder substitutions performed.

<a id="stelion.workspace.application.bootstrap.BootstrapResult.files_renamed"></a>

#### files_renamed *: [int](https://docs.python.org/3/builtins/functions.html#int)*

Number of files and directories renamed.

<a id="stelion.workspace.application.bootstrap.BootstrapResult.git_initialized"></a>

#### git_initialized *: [bool](https://docs.python.org/3/builtins/functions.html#bool)*

Whether a git repository was initialized.

<a id="stelion.workspace.application.bootstrap.BootstrapRequest"></a>

### *class* stelion.workspace.application.bootstrap.BootstrapRequest(name, description, template_source, target_dir, template, defaults, initialize_git=True, dry_run=False)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Validated request for creating a project from a workspace template.

<a id="stelion.workspace.application.bootstrap.BootstrapRequest.name"></a>

#### name *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)*

Project name.

<a id="stelion.workspace.application.bootstrap.BootstrapRequest.description"></a>

#### description *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)*

One-line project description.

<a id="stelion.workspace.application.bootstrap.BootstrapRequest.template_source"></a>

#### template_source *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

Absolute path to the template directory.

<a id="stelion.workspace.application.bootstrap.BootstrapRequest.target_dir"></a>

#### target_dir *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

Absolute path to the target directory.

<a id="stelion.workspace.application.bootstrap.BootstrapRequest.template"></a>

#### template *: [TemplateConfig](workspace-domain.md#stelion.workspace.domain.manifest.TemplateConfig)*

Template configuration from the manifest.

<a id="stelion.workspace.application.bootstrap.BootstrapRequest.defaults"></a>

#### defaults *: [EcosystemDefaults](workspace-domain.md#stelion.workspace.domain.manifest.EcosystemDefaults)*

Ecosystem-level defaults from the manifest.

<a id="stelion.workspace.application.bootstrap.BootstrapRequest.initialize_git"></a>

#### initialize_git *: [bool](https://docs.python.org/3/builtins/functions.html#bool)* *= True*

Whether to initialize a git repository.

<a id="stelion.workspace.application.bootstrap.BootstrapRequest.dry_run"></a>

#### dry_run *: [bool](https://docs.python.org/3/builtins/functions.html#bool)* *= False*

Whether to skip side effects.

<a id="stelion.workspace.application.bootstrap.WorkspaceBootstrapRequest"></a>

### *class* stelion.workspace.application.bootstrap.WorkspaceBootstrapRequest(manifest_dir, name, description, template, defaults, discovery_scan_dirs, destination_root=None, initialize_git=True, dry_run=False)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

High-level request for bootstrapping a project within a workspace.

<a id="stelion.workspace.application.bootstrap.WorkspaceBootstrapRequest.manifest_dir"></a>

#### manifest_dir *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

Absolute path to the workspace manifest directory.

<a id="stelion.workspace.application.bootstrap.WorkspaceBootstrapRequest.name"></a>

#### name *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)*

Project name.

<a id="stelion.workspace.application.bootstrap.WorkspaceBootstrapRequest.description"></a>

#### description *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)*

One-line project description.

<a id="stelion.workspace.application.bootstrap.WorkspaceBootstrapRequest.template"></a>

#### template *: [TemplateConfig](workspace-domain.md#stelion.workspace.domain.manifest.TemplateConfig)*

Template configuration from the manifest.

<a id="stelion.workspace.application.bootstrap.WorkspaceBootstrapRequest.defaults"></a>

#### defaults *: [EcosystemDefaults](workspace-domain.md#stelion.workspace.domain.manifest.EcosystemDefaults)*

Ecosystem-level defaults from the manifest.

<a id="stelion.workspace.application.bootstrap.WorkspaceBootstrapRequest.discovery_scan_dirs"></a>

#### discovery_scan_dirs *: [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), ...]*

Scan directories declared in the manifest discovery section.

<a id="stelion.workspace.application.bootstrap.WorkspaceBootstrapRequest.destination_root"></a>

#### destination_root *: [str](https://docs.python.org/3/builtins/stdtypes.html#str) | [None](https://docs.python.org/3/builtins/constants.html#None)* *= None*

Override for the destination scan directory.

<a id="stelion.workspace.application.bootstrap.WorkspaceBootstrapRequest.initialize_git"></a>

#### initialize_git *: [bool](https://docs.python.org/3/builtins/functions.html#bool)* *= True*

Whether to initialize a git repository.

<a id="stelion.workspace.application.bootstrap.WorkspaceBootstrapRequest.dry_run"></a>

#### dry_run *: [bool](https://docs.python.org/3/builtins/functions.html#bool)* *= False*

Whether to skip side effects.

<a id="stelion.workspace.application.bootstrap.PlaceholderBindings"></a>

### *class* stelion.workspace.application.bootstrap.PlaceholderBindings(mappings)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Resolved template placeholder bindings.

<a id="stelion.workspace.application.bootstrap.PlaceholderBindings.mappings"></a>

#### mappings *: [dict](https://docs.python.org/3/builtins/stdtypes.html#dict)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), [str](https://docs.python.org/3/builtins/stdtypes.html#str)]*

Placeholder-to-value mapping.

<a id="stelion.workspace.application.bootstrap.PlaceholderBindings.as_dict"></a>

#### as_dict()

Return a plain dict copy of the bindings.

* **Returns:**
  Shallow copy of the placeholder-to-value mapping.
* **Return type:**
  [dict](https://docs.python.org/3/builtins/stdtypes.html#dict)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), [str](https://docs.python.org/3/builtins/stdtypes.html#str)]

<a id="stelion.workspace.application.bootstrap.BootstrapServices"></a>

### *class* stelion.workspace.application.bootstrap.BootstrapServices(read_git_identity, copy_template, substitute_directory, rename_paths, init_repository)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Injected infrastructure for the project bootstrap workflow.

<a id="stelion.workspace.application.bootstrap.BootstrapServices.read_git_identity"></a>

#### read_git_identity *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[], [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), [str](https://docs.python.org/3/builtins/stdtypes.html#str)]]*

Read the git user name and email.

<a id="stelion.workspace.application.bootstrap.BootstrapServices.copy_template"></a>

#### copy_template *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path), [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)], [None](https://docs.python.org/3/builtins/constants.html#None)]*

Copy a template directory to a target directory.

<a id="stelion.workspace.application.bootstrap.BootstrapServices.substitute_directory"></a>

#### substitute_directory *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path), [dict](https://docs.python.org/3/builtins/stdtypes.html#dict)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), [str](https://docs.python.org/3/builtins/stdtypes.html#str)], [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), [str](https://docs.python.org/3/builtins/stdtypes.html#str)], [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), ...]], [int](https://docs.python.org/3/builtins/functions.html#int)]*

Substitute placeholders in all files under a directory.

<a id="stelion.workspace.application.bootstrap.BootstrapServices.rename_paths"></a>

#### rename_paths *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path), [dict](https://docs.python.org/3/builtins/stdtypes.html#dict)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), [str](https://docs.python.org/3/builtins/stdtypes.html#str)], [dict](https://docs.python.org/3/builtins/stdtypes.html#dict)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), [str](https://docs.python.org/3/builtins/stdtypes.html#str)], [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), [str](https://docs.python.org/3/builtins/stdtypes.html#str)]], [int](https://docs.python.org/3/builtins/functions.html#int)]*

Rename files and directories using the bindings.

<a id="stelion.workspace.application.bootstrap.BootstrapServices.init_repository"></a>

#### init_repository *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)], [None](https://docs.python.org/3/builtins/constants.html#None)]*

Initialize a git repository in the given directory.

<a id="stelion.workspace.application.bootstrap.plan_bootstrap_request"></a>

### stelion.workspace.application.bootstrap.plan_bootstrap_request(request)

Resolve manifest-relative bootstrap paths into an executable request.

* **Parameters:**
  **request** ([*WorkspaceBootstrapRequest*](#stelion.workspace.application.bootstrap.WorkspaceBootstrapRequest)) – High-level workspace-scoped bootstrap request.
* **Returns:**
  Executable bootstrap request with resolved paths.
* **Return type:**
  [BootstrapRequest](#stelion.workspace.application.bootstrap.BootstrapRequest)

<a id="stelion.workspace.application.bootstrap.build_placeholder_bindings"></a>

### stelion.workspace.application.bootstrap.build_placeholder_bindings(name, description, defaults, author_name='', author_email='')

Build the placeholder-to-value mapping for template substitution.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Project name (used as package_name, repo_name, env_name, project_name).
  * **description** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – One-line project description.
  * **defaults** ([*EcosystemDefaults*](workspace-domain.md#stelion.workspace.domain.manifest.EcosystemDefaults)) – Ecosystem-level defaults from the manifest.
  * **author_name** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Author full name (typically from git config).
  * **author_email** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Author email (typically from git config).
* **Returns:**
  Resolved placeholder bindings for template substitution.
* **Return type:**
  [PlaceholderBindings](#stelion.workspace.application.bootstrap.PlaceholderBindings)

<a id="stelion.workspace.application.bootstrap.bootstrap_project"></a>

### stelion.workspace.application.bootstrap.bootstrap_project(request, services)

Bootstrap a new project from the template via injected infrastructure.

* **Parameters:**
  * **request** ([*BootstrapRequest*](#stelion.workspace.application.bootstrap.BootstrapRequest)) – Validated bootstrap parameters.
  * **services** ([*BootstrapServices*](#stelion.workspace.application.bootstrap.BootstrapServices)) – Injected infrastructure collaborators.
* **Returns:**
  Outcome of the bootstrap operation.
* **Return type:**
  [BootstrapResult](#stelion.workspace.application.bootstrap.BootstrapResult)

<a id="stelion.workspace.application.bootstrap.bootstrap_workspace_project"></a>

### stelion.workspace.application.bootstrap.bootstrap_workspace_project(request, services)

Bootstrap a new project from a workspace-scoped request.

* **Parameters:**
  * **request** ([*WorkspaceBootstrapRequest*](#stelion.workspace.application.bootstrap.WorkspaceBootstrapRequest)) – High-level workspace-scoped bootstrap request.
  * **services** ([*BootstrapServices*](#stelion.workspace.application.bootstrap.BootstrapServices)) – Injected infrastructure collaborators.
* **Returns:**
  Outcome of the bootstrap operation.
* **Return type:**
  [BootstrapResult](#stelion.workspace.application.bootstrap.BootstrapResult)

<a id="module-stelion.workspace.application.manifest_init"></a>

<a id="manifest-initialization"></a>

## Manifest Initialization

Default manifest generation use-case.

<a id="stelion.workspace.application.manifest_init.ManifestInitServices"></a>

### *class* stelion.workspace.application.manifest_init.ManifestInitServices(read_git_identity, build_default_manifest, render_manifest, write_manifest)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Injected collaborators for initializing a new workspace manifest.

<a id="stelion.workspace.application.manifest_init.ManifestInitServices.read_git_identity"></a>

#### read_git_identity *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[], [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), [str](https://docs.python.org/3/builtins/stdtypes.html#str)]]*

Read the git user name and email.

<a id="stelion.workspace.application.manifest_init.ManifestInitServices.build_default_manifest"></a>

#### build_default_manifest *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path), [str](https://docs.python.org/3/builtins/stdtypes.html#str)], [WorkspaceManifest](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)]*

Build a default manifest for the given directory.

<a id="stelion.workspace.application.manifest_init.ManifestInitServices.render_manifest"></a>

#### render_manifest *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[WorkspaceManifest](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)], [str](https://docs.python.org/3/builtins/stdtypes.html#str)]*

Render a manifest to YAML text.

<a id="stelion.workspace.application.manifest_init.ManifestInitServices.write_manifest"></a>

#### write_manifest *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[[Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path), [str](https://docs.python.org/3/builtins/stdtypes.html#str)], [None](https://docs.python.org/3/builtins/constants.html#None)]*

Write manifest content to disk.

<a id="stelion.workspace.application.manifest_init.ManifestInitResult"></a>

### *class* stelion.workspace.application.manifest_init.ManifestInitResult(manifest_path, manifest, inventory, content, written)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Result of creating a default workspace manifest.

<a id="stelion.workspace.application.manifest_init.ManifestInitResult.manifest_path"></a>

#### manifest_path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

Absolute path to the manifest file.

<a id="stelion.workspace.application.manifest_init.ManifestInitResult.manifest"></a>

#### manifest *: [WorkspaceManifest](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)*

The generated workspace manifest.

<a id="stelion.workspace.application.manifest_init.ManifestInitResult.inventory"></a>

#### inventory *: [ProjectInventory](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory)*

Projects discovered during initialization.

<a id="stelion.workspace.application.manifest_init.ManifestInitResult.content"></a>

#### content *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)*

Rendered YAML content of the manifest.

<a id="stelion.workspace.application.manifest_init.ManifestInitResult.written"></a>

#### written *: [bool](https://docs.python.org/3/builtins/functions.html#bool)*

Whether the manifest was written to disk.

<a id="stelion.workspace.application.manifest_init.ManifestInitResult.project_names"></a>

#### *property* project_names *: [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), ...]*

Alphabetical list of discovered project names.

* **Returns:**
  Sorted project names from the inventory.
* **Return type:**
  [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), …]

<a id="stelion.workspace.application.manifest_init.initialize_default_manifest"></a>

### stelion.workspace.application.manifest_init.initialize_default_manifest(manifest_path, extractor, services, \*, dry_run=False)

Build and optionally persist a default manifest for a new workspace.

* **Parameters:**
  * **manifest_path** (*Path*) – Target path for the manifest file.
  * **extractor** ([*MetadataExtractor*](#stelion.workspace.application.protocols.MetadataExtractor)) – Infrastructure extractor for project metadata.
  * **services** ([*ManifestInitServices*](#stelion.workspace.application.manifest_init.ManifestInitServices)) – Injected collaborators.
  * **dry_run** ([*bool*](https://docs.python.org/3/builtins/functions.html#bool)) – If True, skip writing the manifest to disk.
* **Returns:**
  Result containing the manifest, inventory, and write status.
* **Return type:**
  [ManifestInitResult](#stelion.workspace.application.manifest_init.ManifestInitResult)

<a id="module-stelion.workspace.application.manifest_overlay"></a>

<a id="manifest-overlays"></a>

## Manifest overlays

Pure composition of workspace-manifest defaults and consumer overlays.

<a id="stelion.workspace.application.manifest_overlay.merge_manifest_mappings"></a>

### stelion.workspace.application.manifest_overlay.merge_manifest_mappings(base, overlay)

Merge a consumer overlay into a canonical manifest mapping.

Nonempty nested mappings merge recursively. An empty mapping explicitly
clears a default mapping. Every scalar and sequence replaces its default.
Neither input is mutated.

* **Parameters:**
  * **base** (*Mapping* *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,* [*object*](https://docs.python.org/3/builtins/functions.html#object) *]*) – Canonical manifest values owned by Stelion.
  * **overlay** (*Mapping* *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,* [*object*](https://docs.python.org/3/builtins/functions.html#object) *]*) – Consumer-specific values that differ from the canonical defaults.
* **Returns:**
  Independent mapping containing the composed manifest values.
* **Return type:**
  [dict](https://docs.python.org/3/builtins/stdtypes.html#dict)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), [object](https://docs.python.org/3/builtins/functions.html#object)]

<a id="module-stelion.workspace.application.discovery"></a>

<a id="discovery"></a>

## Discovery

Project discovery use-case.

<a id="stelion.workspace.application.discovery.discover_projects"></a>

### stelion.workspace.application.discovery.discover_projects(config, extractor, manifest_dir)

Scan directories for projects and extract metadata.

* **Parameters:**
  * **config** ([*DiscoveryConfig*](workspace-domain.md#stelion.workspace.domain.manifest.DiscoveryConfig)) – Discovery rules from the workspace manifest.
  * **extractor** ([*MetadataExtractor*](#stelion.workspace.application.protocols.MetadataExtractor)) – Infrastructure implementation that reads pyproject.toml.
  * **manifest_dir** (*Path*) – Absolute path to the directory containing stelion.yml.
* **Returns:**
  All discovered projects with their metadata.
* **Return type:**
  [ProjectInventory](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory)

<a id="module-stelion.workspace.application.registration"></a>

<a id="registration"></a>

## Registration

Project registration use-case.

Registers an existing project into workspace artifacts without regenerating
everything. Used for copy-pasted, imported, or manually created projects.

<a id="stelion.workspace.application.registration.RegistrationResult"></a>

### *class* stelion.workspace.application.registration.RegistrationResult(manifest, project, manifest_updated)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Outcome of registering a project.

<a id="stelion.workspace.application.registration.RegistrationResult.manifest"></a>

#### manifest *: [WorkspaceManifest](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)*

Workspace manifest after registration (may be unchanged).

<a id="stelion.workspace.application.registration.RegistrationResult.project"></a>

#### project *: [ProjectMetadata](workspace-domain.md#stelion.workspace.domain.project.ProjectMetadata)*

Metadata of the registered project.

<a id="stelion.workspace.application.registration.RegistrationResult.manifest_updated"></a>

#### manifest_updated *: [bool](https://docs.python.org/3/builtins/functions.html#bool)*

Whether the manifest was modified to include the project.

<a id="stelion.workspace.application.registration.ExecuteRegistrationResult"></a>

### *class* stelion.workspace.application.registration.ExecuteRegistrationResult(manifest, project, manifest_updated, generated)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Full outcome of registering and regenerating workspace artifacts.

<a id="stelion.workspace.application.registration.ExecuteRegistrationResult.manifest"></a>

#### manifest *: [WorkspaceManifest](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)*

Workspace manifest after registration.

<a id="stelion.workspace.application.registration.ExecuteRegistrationResult.project"></a>

#### project *: [ProjectMetadata](workspace-domain.md#stelion.workspace.domain.project.ProjectMetadata)*

Metadata of the registered project.

<a id="stelion.workspace.application.registration.ExecuteRegistrationResult.manifest_updated"></a>

#### manifest_updated *: [bool](https://docs.python.org/3/builtins/functions.html#bool)*

Whether the manifest was modified to include the project.

<a id="stelion.workspace.application.registration.ExecuteRegistrationResult.generated"></a>

#### generated *: [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[GenerationResult](#stelion.workspace.application.generation.GenerationResult), ...]*

Results of regenerating workspace artifacts.

<a id="stelion.workspace.application.registration.register_project"></a>

### stelion.workspace.application.registration.register_project(project_dir, extractor)

Extract metadata from a project directory for registration.

The caller (CLI adapter) is responsible for updating the workspace file,
projects index, and dependency graph with the returned metadata.

* **Parameters:**
  * **project_dir** (*Path*) – Absolute path to the project directory.
  * **extractor** ([*MetadataExtractor*](#stelion.workspace.application.protocols.MetadataExtractor)) – Infrastructure extractor for project metadata.
* **Returns:**
  Extracted project metadata.
* **Return type:**
  [ProjectMetadata](workspace-domain.md#stelion.workspace.domain.project.ProjectMetadata)

<a id="stelion.workspace.application.registration.apply_registration"></a>

### stelion.workspace.application.registration.apply_registration(manifest, inventory, project)

Return the manifest state needed to include *project* in the workspace.

* **Parameters:**
  * **manifest** ([*WorkspaceManifest*](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)) – Current workspace manifest.
  * **inventory** ([*ProjectInventory*](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory)) – Current project inventory.
  * **project** ([*ProjectMetadata*](workspace-domain.md#stelion.workspace.domain.project.ProjectMetadata)) – Project to register.
* **Returns:**
  Updated manifest and registration status.
* **Return type:**
  [RegistrationResult](#stelion.workspace.application.registration.RegistrationResult)

<a id="stelion.workspace.application.registration.execute_registration"></a>

### stelion.workspace.application.registration.execute_registration(manifest_path, project_dir, manifest, extractor, discover, build_context_and_generate, persist_manifest)

Full registration use-case: inspect, update manifest, regenerate artifacts.

Avoids building the full workspace context twice. If the project is already
registered (its path is in the manifest’s extra_paths), the manifest is
used as-is. Otherwise, a discovery pass determines whether the manifest
needs updating before the single context build.

* **Parameters:**
  * **manifest_path** (*Path*) – Path to the manifest file on disk.
  * **project_dir** (*Path*) – Path to the project directory to register.
  * **manifest** ([*WorkspaceManifest*](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)) – Current workspace manifest.
  * **extractor** ([*MetadataExtractor*](#stelion.workspace.application.protocols.MetadataExtractor)) – Infrastructure extractor for project metadata.
  * **discover** (*Callable* *[* *[*[*WorkspaceManifest*](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest) *]* *,* [*ProjectInventory*](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory) *]*) – Callable to discover projects from a manifest.
  * **build_context_and_generate** (*Callable* *[* *[*[*WorkspaceManifest*](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest) *]* *,* [*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*ProjectInventory*](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory) *,* [*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*GenerationResult*](#stelion.workspace.application.generation.GenerationResult) *,*  *...* *]* *]* *]*) – Callable to build the workspace context and generate artifacts.
  * **persist_manifest** (*Callable* *[* *[**Path* *,* [*WorkspaceManifest*](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest) *]* *,* *None* *]*) – Callable to write the manifest to disk.
* **Returns:**
  Full outcome including manifest update and generated artifacts.
* **Return type:**
  [ExecuteRegistrationResult](#stelion.workspace.application.registration.ExecuteRegistrationResult)

<a id="module-stelion.workspace.application.generation"></a>

<a id="generation"></a>

## Generation

Workspace artifact generation use-cases.

<a id="stelion.workspace.application.generation.GenerationResult"></a>

### *class* stelion.workspace.application.generation.GenerationResult(artifact, path, written, reason)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Outcome of generating a single file.

<a id="stelion.workspace.application.generation.GenerationResult.artifact"></a>

#### artifact *: [GenerationArtifact](#stelion.workspace.application.generation.GenerationArtifact)*

Identifier of the generated artifact.

<a id="stelion.workspace.application.generation.GenerationResult.path"></a>

#### path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

Output path of the generated file.

<a id="stelion.workspace.application.generation.GenerationResult.written"></a>

#### written *: [bool](https://docs.python.org/3/builtins/functions.html#bool)*

Whether the file was actually written to disk.

<a id="stelion.workspace.application.generation.GenerationResult.reason"></a>

#### reason *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)*

Short label describing the outcome (e.g. `"created"`, `"current"`).

<a id="stelion.workspace.application.generation.GenerationArtifact"></a>

### *class* stelion.workspace.application.generation.GenerationArtifact(\*values)

Bases: [`StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Identifier for a generated workspace artifact.

<a id="stelion.workspace.application.generation.GenerationArtifact.WORKSPACE_FILE"></a>

#### WORKSPACE_FILE *= 'workspace-file'*

<a id="stelion.workspace.application.generation.GenerationArtifact.PROJECTS"></a>

#### PROJECTS *= 'projects'*

<a id="stelion.workspace.application.generation.GenerationArtifact.DEPENDENCIES"></a>

#### DEPENDENCIES *= 'dependencies'*

<a id="stelion.workspace.application.generation.GenerationArtifact.ENVIRONMENT"></a>

#### ENVIRONMENT *= 'environment'*

<a id="stelion.workspace.application.generation.ArtifactSpec"></a>

### *class* stelion.workspace.application.generation.ArtifactSpec(artifact, output_path)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Identity and output path of a workspace artifact.

<a id="stelion.workspace.application.generation.ArtifactSpec.artifact"></a>

#### artifact *: [GenerationArtifact](#stelion.workspace.application.generation.GenerationArtifact)*

Artifact identifier.

<a id="stelion.workspace.application.generation.ArtifactSpec.output_path"></a>

#### output_path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

Resolved output path for this artifact.

<a id="stelion.workspace.application.generation.GenerationTarget"></a>

### *class* stelion.workspace.application.generation.GenerationTarget(artifact, path, render)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

A single file to generate: its output path and a renderer callable.

<a id="stelion.workspace.application.generation.GenerationTarget.artifact"></a>

#### artifact *: [GenerationArtifact](#stelion.workspace.application.generation.GenerationArtifact)*

Artifact identifier.

<a id="stelion.workspace.application.generation.GenerationTarget.path"></a>

#### path *: [Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)*

Output path of the file to generate.

<a id="stelion.workspace.application.generation.GenerationTarget.render"></a>

#### render *: [Callable](https://docs.python.org/3/library/typing.html#typing.Callable)[[], [str](https://docs.python.org/3/builtins/stdtypes.html#str)]*

Zero-argument callable that produces the file content.

<a id="stelion.workspace.application.generation.compute_artifact_specs"></a>

### stelion.workspace.application.generation.compute_artifact_specs(manifest)

Compute the output paths for all generation artifacts.

* **Parameters:**
  **manifest** ([*WorkspaceManifest*](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)) – Workspace manifest configuration.
* **Returns:**
  Mapping from artifact identifier to its output spec.
* **Return type:**
  [dict](https://docs.python.org/3/builtins/stdtypes.html#dict)[[GenerationArtifact](#stelion.workspace.application.generation.GenerationArtifact), [ArtifactSpec](#stelion.workspace.application.generation.ArtifactSpec)]

<a id="stelion.workspace.application.generation.generate_all"></a>

### stelion.workspace.application.generation.generate_all(manifest, inventory, graph, environment, services, force=False, selected_targets=())

Generate all enabled workspace artifacts.

Each target is rendered to a string, compared with the existing file via
content hash, and written only if the content differs (or `force` is set).

* **Parameters:**
  * **manifest** ([*WorkspaceManifest*](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)) – Workspace manifest configuration.
  * **inventory** ([*ProjectInventory*](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory)) – All discovered projects.
  * **graph** ([*DependencyGraph*](workspace-domain.md#stelion.workspace.domain.dependency.DependencyGraph)) – Project dependency graph.
  * **environment** ([*EnvironmentSpec*](workspace-domain.md#stelion.workspace.domain.environment.EnvironmentSpec)) – Merged shared environment specification.
  * **services** ([*GenerationServices*](#stelion.workspace.application.protocols.GenerationServices)) – Bundled infrastructure services.
  * **force** ([*bool*](https://docs.python.org/3/builtins/functions.html#bool)) – If True, write all files regardless of content hash.
  * **selected_targets** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*GenerationArtifact*](#stelion.workspace.application.generation.GenerationArtifact) *,*  *...* *]*) – Subset of artifacts to generate; empty means all.
* **Returns:**
  One result per artifact indicating whether it was written.
* **Return type:**
  [list](https://docs.python.org/3/builtins/stdtypes.html#list)[[GenerationResult](#stelion.workspace.application.generation.GenerationResult)]

<a id="stelion.workspace.application.generation.compute_drift"></a>

### stelion.workspace.application.generation.compute_drift(manifest, inventory, graph, environment, services, selected_targets=())

Compare generated content with existing files without writing.

* **Parameters:**
  * **manifest** ([*WorkspaceManifest*](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)) – Workspace manifest configuration.
  * **inventory** ([*ProjectInventory*](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory)) – All discovered projects.
  * **graph** ([*DependencyGraph*](workspace-domain.md#stelion.workspace.domain.dependency.DependencyGraph)) – Project dependency graph.
  * **environment** ([*EnvironmentSpec*](workspace-domain.md#stelion.workspace.domain.environment.EnvironmentSpec)) – Merged shared environment specification.
  * **services** ([*GenerationServices*](#stelion.workspace.application.protocols.GenerationServices)) – Bundled infrastructure services.
  * **selected_targets** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*GenerationArtifact*](#stelion.workspace.application.generation.GenerationArtifact) *,*  *...* *]*) – Subset of artifacts to check; empty means all.
* **Returns:**
  Per-artifact drift status.
* **Return type:**
  [DriftReport](workspace-domain.md#stelion.workspace.domain.status.DriftReport)

<a id="module-stelion.workspace.application.graph"></a>

<a id="graph"></a>

## Graph

Dependency graph construction use-case.

<a id="stelion.workspace.application.graph.build_dependency_graph"></a>

### stelion.workspace.application.graph.build_dependency_graph(manifest, inventory, scanners)

Build the full dependency graph from auto-detection and manifest data.

Scans each project for editable pip installs in `environment.yml`
and git submodule relationships, then merges with manually declared
edges from the manifest.

* **Parameters:**
  * **manifest** ([*WorkspaceManifest*](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)) – Workspace manifest with dependency configuration.
  * **inventory** ([*ProjectInventory*](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory)) – All discovered projects.
  * **scanners** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*DependencyScanner*](#stelion.workspace.application.protocols.DependencyScanner) *,*  *...* *]*) – Infrastructure scanners for detecting dependency edges.
* **Returns:**
  Combined graph of detected and manual dependency edges.
* **Return type:**
  [DependencyGraph](workspace-domain.md#stelion.workspace.domain.dependency.DependencyGraph)

<a id="module-stelion.workspace.application.environment"></a>

<a id="environment"></a>

## Environment

Shared environment construction use-case.

<a id="stelion.workspace.application.environment.build_shared_environment"></a>

### stelion.workspace.application.environment.build_shared_environment(manifest, inventory, env_reader, env_specs=None)

Merge all project environments into a single shared spec.

When *env_specs* is provided, uses pre-read specs instead of calling
*env_reader* per project. Otherwise reads each project’s
`environment.yml` via *env_reader*.

* **Parameters:**
  * **manifest** ([*WorkspaceManifest*](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)) – Workspace manifest with shared environment configuration.
  * **inventory** ([*ProjectInventory*](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory)) – All discovered projects.
  * **env_reader** ([*EnvironmentReader*](#stelion.workspace.application.protocols.EnvironmentReader)) – Infrastructure reader for Conda environment specs.
  * **env_specs** ([*dict*](https://docs.python.org/3/builtins/stdtypes.html#dict) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,* [*EnvironmentSpec*](workspace-domain.md#stelion.workspace.domain.environment.EnvironmentSpec) *|* *None* *]*  *|* *None*) – Pre-read environment specs keyed by project name.
* **Returns:**
  Merged shared environment specification.
* **Return type:**
  [EnvironmentSpec](workspace-domain.md#stelion.workspace.domain.environment.EnvironmentSpec)

<a id="module-stelion.workspace.application.sync"></a>

<a id="sync"></a>

## Sync

Submodule synchronization use-case.

<a id="stelion.workspace.application.sync.SyncOriginResolver"></a>

### *class* stelion.workspace.application.sync.SyncOriginResolver(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Strategy for resolving the source commit in a sync operation.

<a id="stelion.workspace.application.sync.SyncOriginResolver.resolve"></a>

#### resolve(dependency, targets, inventory, git)

Resolve the source commit and build a sync plan.

* **Parameters:**
  * **dependency** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the dependency project.
  * **targets** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*SubmoduleTarget*](workspace-domain.md#stelion.workspace.domain.sync.SubmoduleTarget) *,*  *...* *]*) – Submodule targets to synchronize.
  * **inventory** ([*ProjectInventory*](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory)) – All discovered projects.
  * **git** ([*GitOperations*](#stelion.workspace.application.protocols.GitOperations)) – Git infrastructure operations.

<a id="stelion.workspace.application.sync.LocalOriginResolver"></a>

### *class* stelion.workspace.application.sync.LocalOriginResolver(remote='origin', branch='main')

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Resolve sync origin from the local clone’s HEAD.

* **Parameters:**
  * **remote** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Remote name for the push spec.
  * **branch** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Branch name for the push spec.

<a id="stelion.workspace.application.sync.LocalOriginResolver.resolve"></a>

#### resolve(dependency, targets, inventory, git)

Resolve the source commit from the local clone’s HEAD.

* **Parameters:**
  * **dependency** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the dependency project.
  * **targets** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*SubmoduleTarget*](workspace-domain.md#stelion.workspace.domain.sync.SubmoduleTarget) *,*  *...* *]*) – Submodule targets to synchronize.
  * **inventory** ([*ProjectInventory*](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory)) – All discovered projects.
  * **git** ([*GitOperations*](#stelion.workspace.application.protocols.GitOperations)) – Git infrastructure operations.
* **Returns:**
  Sync plan with local HEAD as the source commit.
* **Return type:**
  [SyncPlan](workspace-domain.md#stelion.workspace.domain.sync.SyncPlan)

<a id="stelion.workspace.application.sync.SuperprojectOriginResolver"></a>

### *class* stelion.workspace.application.sync.SuperprojectOriginResolver(source_superproject, remote='origin', branch='main')

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Resolve sync origin from a superproject’s submodule pointer.

* **Parameters:**
  * **source_superproject** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the superproject to read the submodule pointer from.
  * **remote** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Remote name for the push spec.
  * **branch** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Branch name for the push spec.

<a id="stelion.workspace.application.sync.SuperprojectOriginResolver.resolve"></a>

#### resolve(dependency, targets, inventory, git)

Resolve the source commit from the superproject’s submodule pointer.

* **Parameters:**
  * **dependency** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the dependency project.
  * **targets** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*SubmoduleTarget*](workspace-domain.md#stelion.workspace.domain.sync.SubmoduleTarget) *,*  *...* *]*) – Submodule targets to synchronize.
  * **inventory** ([*ProjectInventory*](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory)) – All discovered projects.
  * **git** ([*GitOperations*](#stelion.workspace.application.protocols.GitOperations)) – Git infrastructure operations.
* **Returns:**
  Sync plan with the superproject’s recorded commit as the source.
* **Return type:**
  [SyncPlan](workspace-domain.md#stelion.workspace.domain.sync.SyncPlan)

<a id="stelion.workspace.application.sync.RemoteOriginResolver"></a>

### *class* stelion.workspace.application.sync.RemoteOriginResolver(remote='origin', branch='main')

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Resolve sync origin from the remote tracking branch.

* **Parameters:**
  * **remote** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Remote name to fetch from and resolve HEAD.
  * **branch** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Branch name to resolve on the remote.

<a id="stelion.workspace.application.sync.RemoteOriginResolver.resolve"></a>

#### resolve(dependency, targets, inventory, git)

Resolve the source commit from the remote tracking branch.

* **Parameters:**
  * **dependency** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the dependency project.
  * **targets** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*SubmoduleTarget*](workspace-domain.md#stelion.workspace.domain.sync.SubmoduleTarget) *,*  *...* *]*) – Submodule targets to synchronize.
  * **inventory** ([*ProjectInventory*](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory)) – All discovered projects.
  * **git** ([*GitOperations*](#stelion.workspace.application.protocols.GitOperations)) – Git infrastructure operations.
* **Returns:**
  Sync plan with the remote tracking branch HEAD as the source.
* **Return type:**
  [SyncPlan](workspace-domain.md#stelion.workspace.domain.sync.SyncPlan)

<a id="stelion.workspace.application.sync.resolve_submodule_targets"></a>

### stelion.workspace.application.sync.resolve_submodule_targets(dependency, graph, manifest, inventory=None)

Extract git-submodule edges for a dependency and resolve to filesystem targets.

* **Parameters:**
  * **dependency** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the dependency project.
  * **graph** ([*DependencyGraph*](workspace-domain.md#stelion.workspace.domain.dependency.DependencyGraph)) – Project dependency graph.
  * **manifest** ([*WorkspaceManifest*](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)) – Workspace manifest with superproject path configuration.
  * **inventory** ([*ProjectInventory*](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory) *|* *None*) – Optional project inventory for fallback resolution.
* **Returns:**
  Resolved submodule targets for the dependency.
* **Return type:**
  [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[SubmoduleTarget](workspace-domain.md#stelion.workspace.domain.sync.SubmoduleTarget), …]

<a id="stelion.workspace.application.sync.make_resolver"></a>

### stelion.workspace.application.sync.make_resolver(origin, \*, source_superproject=None, remote='origin', branch='main')

Factory for creating the appropriate resolver from an origin enum.

* **Parameters:**
  * **origin** ([*SyncOrigin*](workspace-domain.md#stelion.workspace.domain.sync.SyncOrigin)) – How the source commit is determined.
  * **source_superproject** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *|* *None*) – Required when *origin* is `SUPERPROJECT`.
  * **remote** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Remote name passed to the resolver.
  * **branch** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Branch name passed to the resolver.
* **Returns:**
  Resolver instance matching the origin strategy.
* **Return type:**
  [SyncOriginResolver](#stelion.workspace.application.sync.SyncOriginResolver)

<a id="stelion.workspace.application.sync.plan_sync"></a>

### stelion.workspace.application.sync.plan_sync(dependency, targets, inventory, origin, git, \*, source_superproject=None, remote='origin', branch='main', resolver=None)

Determine the source commit, local update, remote push, and submodule targets.

When *resolver* is provided it is used directly; otherwise a resolver is
constructed from *origin* and the keyword parameters.

* **Parameters:**
  * **dependency** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the dependency project.
  * **targets** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*SubmoduleTarget*](workspace-domain.md#stelion.workspace.domain.sync.SubmoduleTarget) *,*  *...* *]*) – Submodule targets to synchronize.
  * **inventory** ([*ProjectInventory*](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory)) – All discovered projects.
  * **origin** ([*SyncOrigin*](workspace-domain.md#stelion.workspace.domain.sync.SyncOrigin)) – How the source commit is determined.
  * **git** ([*GitOperations*](#stelion.workspace.application.protocols.GitOperations)) – Git infrastructure operations.
  * **source_superproject** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *|* *None*) – Required when *origin* is `SUPERPROJECT`.
  * **remote** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Remote name passed to the resolver.
  * **branch** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Branch name passed to the resolver.
  * **resolver** ([*SyncOriginResolver*](#stelion.workspace.application.sync.SyncOriginResolver) *|* *None*) – Pre-built resolver; overrides *origin* when provided.
* **Returns:**
  Resolved sync plan.
* **Return type:**
  [SyncPlan](workspace-domain.md#stelion.workspace.domain.sync.SyncPlan)

<a id="stelion.workspace.application.sync.execute_sync"></a>

### stelion.workspace.application.sync.execute_sync(plan, git, \*, commit=True, dry_run=False)

Execute sync plan in order: local clone, remote push, submodule pointers.

* **Parameters:**
  * **plan** ([*SyncPlan*](workspace-domain.md#stelion.workspace.domain.sync.SyncPlan)) – Resolved sync plan to execute.
  * **git** ([*GitOperations*](#stelion.workspace.application.protocols.GitOperations)) – Git infrastructure operations.
  * **commit** ([*bool*](https://docs.python.org/3/builtins/functions.html#bool)) – If True, commit submodule pointer updates.
  * **dry_run** ([*bool*](https://docs.python.org/3/builtins/functions.html#bool)) – If True, skip all side effects.
* **Returns:**
  Aggregated outcomes of the sync operation.
* **Return type:**
  [SyncResult](workspace-domain.md#stelion.workspace.domain.sync.SyncResult)

<a id="module-stelion.workspace.application.bulk"></a>

<a id="bulk"></a>

## Bulk

Application use-cases for bulk operations across projects.

<a id="stelion.workspace.application.bulk.select_projects"></a>

### stelion.workspace.application.bulk.select_projects(inventory, filter_=None, \*, names=(), pattern=None, git_only=False, exclude=())

Filter the project inventory to the target set.

Accepts either a `ProjectFilter` object or individual keyword arguments
for backward compatibility.

* **Parameters:**
  * **inventory** ([*ProjectInventory*](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory)) – Full project inventory to filter.
  * **filter** ([*ProjectFilter*](workspace-domain.md#stelion.workspace.domain.bulk.ProjectFilter) *|* *None*) – Optional filter object; overrides keyword arguments when provided.
  * **names** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,*  *...* *]*) – Explicit project names to select.
  * **pattern** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *|* *None*) – Regex pattern to match against project names.
  * **git_only** ([*bool*](https://docs.python.org/3/builtins/functions.html#bool)) – If True, keep only projects with a git repository.
  * **exclude** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,*  *...* *]*) – Project names to exclude from the result.
* **Returns:**
  Sorted tuple of projects matching the filters.
* **Return type:**
  [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[ProjectMetadata](workspace-domain.md#stelion.workspace.domain.project.ProjectMetadata), …]
* **Raises:**
  [**WorkspaceError**](workspace-exceptions.md#stelion.workspace.exceptions.WorkspaceError) – If an explicit name is not found in the inventory, or if the
      resolved set is empty after all filters are applied.

<a id="stelion.workspace.application.bulk.execute_bulk"></a>

### stelion.workspace.application.bulk.execute_bulk(projects, operation, \*, dry_run=False)

Run an operation on each project, collecting all outcomes.

Never short-circuits on failure: all projects are processed.

* **Parameters:**
  * **projects** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*ProjectMetadata*](workspace-domain.md#stelion.workspace.domain.project.ProjectMetadata) *,*  *...* *]*) – Projects to operate on.
  * **operation** ([*BulkOperation*](#stelion.workspace.application.protocols.BulkOperation)) – Operation to execute on each project.
  * **dry_run** ([*bool*](https://docs.python.org/3/builtins/functions.html#bool)) – If True, skip side effects.
* **Returns:**
  Aggregated outcomes from all projects.
* **Return type:**
  [BulkResult](workspace-domain.md#stelion.workspace.domain.bulk.BulkResult)

<a id="module-stelion.workspace.application.comparison"></a>

<a id="comparison"></a>

## Comparison

Application use-cases for cross-project comparison.

<a id="stelion.workspace.application.comparison.compare_trees"></a>

### stelion.workspace.application.comparison.compare_trees(projects, target, scanner)

Scan each project’s file tree and match nodes hierarchically.

* **Parameters:**
  * **projects** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*ProjectMetadata*](workspace-domain.md#stelion.workspace.domain.project.ProjectMetadata) *,*  *...* *]*) – Projects to compare.
  * **target** ([*TreeTarget*](workspace-domain.md#stelion.workspace.domain.comparison.TreeTarget)) – Target specification for tree comparison.
  * **scanner** ([*TreeScanner*](#stelion.workspace.application.protocols.TreeScanner)) – Infrastructure scanner for file-tree snapshots.
* **Returns:**
  Matched nodes and summary statistics.
* **Return type:**
  [TreeReport](workspace-domain.md#stelion.workspace.domain.comparison.TreeReport)

<a id="stelion.workspace.application.comparison.compare_files"></a>

### stelion.workspace.application.comparison.compare_files(projects, target, reader, parser)

Compare specific files across projects.

For each `FileTargetEntry`, resolves the actual path per project,
reads content via *reader*, and dispatches to structured or unstructured
comparison.  Per-file errors are captured in the result, not raised.

* **Parameters:**
  * **projects** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*ProjectMetadata*](workspace-domain.md#stelion.workspace.domain.project.ProjectMetadata) *,*  *...* *]*) – Projects to compare.
  * **target** ([*FileTarget*](workspace-domain.md#stelion.workspace.domain.comparison.FileTarget)) – Target specification with file entries and options.
  * **reader** ([*FileReader*](#stelion.workspace.application.protocols.FileReader)) – Infrastructure reader for file content.
  * **parser** ([*StructuredParser*](#stelion.workspace.application.protocols.StructuredParser)) – Infrastructure parser for structured files.
* **Returns:**
  Per-file diff results and summary statistics.
* **Return type:**
  [FileReport](workspace-domain.md#stelion.workspace.domain.comparison.FileReport)
