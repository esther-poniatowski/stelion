<a id="workspace-infrastructure"></a>

# Workspace Infrastructure

Infrastructure implementations of the application-layer protocols: filesystem,
git, parsers, renderers, and other concrete collaborators.

<a id="module-stelion.workspace.infrastructure.file_ops"></a>

<a id="file-operations"></a>

## File Operations

File system operations: read, write, copy, hash.

<a id="stelion.workspace.infrastructure.file_ops.LocalFileReader"></a>

### *class* stelion.workspace.infrastructure.file_ops.LocalFileReader

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Read file content from the local filesystem.

<a id="stelion.workspace.infrastructure.file_ops.LocalFileReader.read"></a>

#### read(path)

Read the full text content of a file.

* **Parameters:**
  **path** (*Path*) – File to read.
* **Returns:**
  UTF-8 decoded file content.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)

<a id="stelion.workspace.infrastructure.file_ops.LocalFileWriter"></a>

### *class* stelion.workspace.infrastructure.file_ops.LocalFileWriter

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Write file content to the local filesystem.

<a id="stelion.workspace.infrastructure.file_ops.LocalFileWriter.write"></a>

#### write(path, content)

Write text content to a file, creating parent directories as needed.

* **Parameters:**
  * **path** (*Path*) – Destination file path.
  * **content** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Text to write.

<a id="stelion.workspace.infrastructure.file_ops.SHA256Hasher"></a>

### *class* stelion.workspace.infrastructure.file_ops.SHA256Hasher

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Compute SHA-256 hash of string content for drift detection.

<a id="stelion.workspace.infrastructure.file_ops.SHA256Hasher.hash_content"></a>

#### hash_content(content)

Compute a SHA-256 hex digest of *content*.

* **Parameters:**
  **content** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Text to hash.
* **Returns:**
  Hexadecimal SHA-256 digest.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)

<a id="module-stelion.workspace.infrastructure.command_runner"></a>

<a id="command-runner"></a>

## Command Runner

Subprocess-based command runner for bulk operations.

<a id="stelion.workspace.infrastructure.command_runner.SubprocessCommandRunner"></a>

### *class* stelion.workspace.infrastructure.command_runner.SubprocessCommandRunner

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Run commands via subprocess with captured output.

<a id="stelion.workspace.infrastructure.command_runner.SubprocessCommandRunner.run"></a>

#### run(args, cwd)

Execute *args* in *cwd* and return the captured result.

* **Parameters:**
  * **args** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,*  *...* *]*) – Command and arguments to execute.
  * **cwd** (*Path*) – Working directory for the subprocess.
* **Returns:**
  Captured stdout, stderr, and return code.
* **Return type:**
  [CommandResult](workspace-application.md#stelion.workspace.application.protocols.CommandResult)

<a id="module-stelion.workspace.infrastructure.data_loader"></a>

<a id="data-loader"></a>

## Data Loader

Load bundled package data resources via importlib.resources.

<a id="stelion.workspace.infrastructure.data_loader.StelionDataLoader"></a>

### *class* stelion.workspace.infrastructure.data_loader.StelionDataLoader

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Load files from the stelion.data package.

<a id="stelion.workspace.infrastructure.data_loader.StelionDataLoader.load_text"></a>

#### load_text(resource_path)

Load a text resource from the data directory.

* **Parameters:**
  **resource_path** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Dot-separated or slash-separated path relative to stelion/data/.
  Examples: `"references/design-principles.md"`,
  `"vscode/settings.json"`.
* **Returns:**
  UTF-8 decoded text content of the resource.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)

<a id="stelion.workspace.infrastructure.data_loader.StelionDataLoader.load_json"></a>

#### load_json(resource_path)

Load and parse a JSON resource from the data directory.

* **Parameters:**
  **resource_path** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Slash-separated path relative to stelion/data/.
* **Returns:**
  Deserialized JSON content.
* **Return type:**
  Any

<a id="module-stelion.workspace.infrastructure.template_engine"></a>

<a id="template-engine"></a>

## Template Engine

Simple placeholder substitution engine for template instantiation.

Replaces `{{ key }}` patterns in text files while respecting exclusion
patterns (GitHub Actions `${{ }}`, Conda Jinja2 `{{ pyproject.* }}`).

This is a standalone Phase 1 implementation. When stelion’s full template
engine is built, this module can be replaced via the protocol interface.

<a id="stelion.workspace.infrastructure.template_engine.substitute_in_file"></a>

### stelion.workspace.infrastructure.template_engine.substitute_in_file(path, bindings, delimiters=('{{ ', ' }}'), exclude_patterns=None)

Replace placeholder strings in a single file.

* **Parameters:**
  * **path** (*Path*) – File to process.
  * **bindings** ([*dict*](https://docs.python.org/3/builtins/stdtypes.html#dict) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,* [*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *]*) – Mapping from placeholder name to replacement value.
  * **delimiters** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,* [*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *]*) – Opening and closing placeholder delimiters.
  * **exclude_patterns** (*Sequence* *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *]*  *|* *None*) – Regex patterns whose matches should be protected from substitution.
* **Returns:**
  Number of replacements made.
* **Return type:**
  [int](https://docs.python.org/3/builtins/functions.html#int)

<a id="stelion.workspace.infrastructure.template_engine.substitute_in_directory"></a>

### stelion.workspace.infrastructure.template_engine.substitute_in_directory(root, bindings, delimiters=('{{ ', ' }}'), exclude_patterns=None)

Replace placeholders in all text files under a directory.

* **Parameters:**
  * **root** (*Path*) – Directory to process recursively.
  * **bindings** ([*dict*](https://docs.python.org/3/builtins/stdtypes.html#dict) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,* [*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *]*) – Mapping from placeholder name to replacement value.
  * **delimiters** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,* [*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *]*) – Opening and closing placeholder delimiters.
  * **exclude_patterns** (*Sequence* *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *]*  *|* *None*) – Regex patterns whose matches should be protected from substitution.
* **Returns:**
  Total number of replacements across all files.
* **Return type:**
  [int](https://docs.python.org/3/builtins/functions.html#int)

<a id="stelion.workspace.infrastructure.template_engine.copy_template"></a>

### stelion.workspace.infrastructure.template_engine.copy_template(source, target)

Copy a template directory, excluding .git.

* **Parameters:**
  * **source** (*Path*) – Template directory to copy from.
  * **target** (*Path*) – Destination directory (must not already exist).

<a id="stelion.workspace.infrastructure.template_engine.rename_paths"></a>

### stelion.workspace.infrastructure.template_engine.rename_paths(root, renames, bindings, delimiters=('{{ ', ' }}'))

Rename directories and files according to the rename mapping.

The rename values may contain placeholder references that are resolved
against `bindings`.

* **Parameters:**
  * **root** (*Path*) – Base directory containing the paths to rename.
  * **renames** ([*dict*](https://docs.python.org/3/builtins/stdtypes.html#dict) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,* [*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *]*) – Mapping from old relative path to new relative path template.
  * **bindings** ([*dict*](https://docs.python.org/3/builtins/stdtypes.html#dict) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,* [*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *]*) – Placeholder values used to resolve templates in rename targets.
  * **delimiters** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,* [*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *]*) – Opening and closing placeholder delimiters.
* **Returns:**
  Number of renames performed.
* **Return type:**
  [int](https://docs.python.org/3/builtins/functions.html#int)

<a id="module-stelion.workspace.infrastructure.tree_scanner"></a>

<a id="tree-scanner"></a>

## Tree Scanner

Filesystem tree scanner for cross-project comparison.

<a id="stelion.workspace.infrastructure.tree_scanner.LocalTreeScanner"></a>

### *class* stelion.workspace.infrastructure.tree_scanner.LocalTreeScanner

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Scan a project directory and return a `TreeSnapshot`.

Uses `Path.iterdir()` recursively.  Respects include/exclude
glob patterns via [`fnmatch.fnmatch()`](https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatch).  Skips permission errors
and symlink cycles.

<a id="stelion.workspace.infrastructure.tree_scanner.LocalTreeScanner.scan"></a>

#### scan(project_dir, subtree, include, exclude, \*, project_name=None)

Scan a project directory and return a tree snapshot.

* **Parameters:**
  * **project_dir** (*Path*) – Root directory of the project.
  * **subtree** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *|* *None*) – Optional subdirectory to restrict the scan to.
  * **include** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,*  *...* *]*) – Glob patterns for files to include (empty means all).
  * **exclude** ([*tuple*](https://docs.python.org/3/builtins/stdtypes.html#tuple) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,*  *...* *]*) – Glob patterns for entries to skip.
  * **project_name** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *|* *None*) – Override for the project key (defaults to directory name).
* **Returns:**
  Snapshot of the scanned file tree.
* **Return type:**
  [TreeSnapshot](workspace-domain.md#stelion.workspace.domain.comparison.TreeSnapshot)

<a id="module-stelion.workspace.infrastructure.manifest_loader"></a>

<a id="manifest-loader"></a>

## Manifest Loader

Parse stelion.yml into a WorkspaceManifest.

<a id="stelion.workspace.infrastructure.manifest_loader.load_manifest_mapping"></a>

### stelion.workspace.infrastructure.manifest_loader.load_manifest_mapping(path, \*, label='Manifest')

Load a YAML mapping used as a manifest or manifest overlay.

* **Parameters:**
  * **path** (*Path*) – YAML file to load.
  * **label** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Object name used in validation errors.
* **Returns:**
  Parsed top-level mapping.
* **Return type:**
  Mapping[[str](https://docs.python.org/3/builtins/stdtypes.html#str), [object](https://docs.python.org/3/builtins/functions.html#object)]
* **Raises:**
  * [**FileNotFoundError**](https://docs.python.org/3/builtins/exceptions.html#FileNotFoundError) – If *path* does not exist.
  * [**ManifestValidationError**](workspace-exceptions.md#stelion.workspace.exceptions.ManifestValidationError) – If the YAML is invalid or its top level is not a mapping.

<a id="stelion.workspace.infrastructure.manifest_loader.load_manifest"></a>

### stelion.workspace.infrastructure.manifest_loader.load_manifest(path)

Load and validate a workspace manifest from a YAML file.

* **Parameters:**
  **path** (*Path*) – Absolute or relative path to `stelion.yml`.
* **Returns:**
  Fully parsed and typed manifest.
* **Return type:**
  [WorkspaceManifest](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)
* **Raises:**
  * [**FileNotFoundError**](https://docs.python.org/3/builtins/exceptions.html#FileNotFoundError) – If the manifest file does not exist.
  * [**ValueError**](https://docs.python.org/3/builtins/exceptions.html#ValueError) – If required fields are missing or invalid.

<a id="module-stelion.workspace.infrastructure.manifest_codec"></a>

<a id="manifest-codec"></a>

## Manifest Codec

Manifest parsing, defaulting, and rendering infrastructure.

<a id="stelion.workspace.infrastructure.manifest_codec.default_workspace_manifest"></a>

### stelion.workspace.infrastructure.manifest_codec.default_workspace_manifest(manifest_dir, github_user='')

Create the canonical default manifest model for a new workspace.

* **Parameters:**
  * **manifest_dir** (*Path*) – Directory that will contain `stelion.yml`.
  * **github_user** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – GitHub username for ecosystem defaults.
* **Returns:**
  Manifest with all fields set to their canonical defaults.
* **Return type:**
  [WorkspaceManifest](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)

<a id="stelion.workspace.infrastructure.manifest_codec.parse_workspace_manifest"></a>

### stelion.workspace.infrastructure.manifest_codec.parse_workspace_manifest(raw, manifest_dir)

Parse a raw manifest mapping into a typed workspace manifest.

* **Parameters:**
  * **raw** (*Mapping* *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,* *Any* *]*) – Raw YAML-loaded mapping.
  * **manifest_dir** (*Path*) – Directory containing the manifest file.
* **Returns:**
  Fully typed and validated manifest.
* **Return type:**
  [WorkspaceManifest](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)

<a id="stelion.workspace.infrastructure.manifest_codec.manifest_to_dict"></a>

### stelion.workspace.infrastructure.manifest_codec.manifest_to_dict(manifest)

Serialize a manifest model into YAML-safe primitives.

* **Parameters:**
  **manifest** ([*WorkspaceManifest*](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)) – Fully typed manifest model.
* **Returns:**
  Nested dictionary suitable for `yaml.safe_dump`.
* **Return type:**
  [dict](https://docs.python.org/3/builtins/stdtypes.html#dict)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), Any]

<a id="stelion.workspace.infrastructure.manifest_codec.render_manifest"></a>

### stelion.workspace.infrastructure.manifest_codec.render_manifest(manifest)

Render a workspace manifest to YAML.

* **Parameters:**
  **manifest** ([*WorkspaceManifest*](workspace-domain.md#stelion.workspace.domain.manifest.WorkspaceManifest)) – Fully typed manifest model.
* **Returns:**
  YAML text representation.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)

<a id="module-stelion.workspace.infrastructure.spec_loader"></a>

<a id="spec-loader"></a>

## Spec Loader

Loader for comparison instruction files.

<a id="stelion.workspace.infrastructure.spec_loader.YamlSpecLoader"></a>

### *class* stelion.workspace.infrastructure.spec_loader.YamlSpecLoader

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Load and validate a comparison instruction YAML file.

Follows the validation pattern of `manifest_loader.py`.

<a id="stelion.workspace.infrastructure.spec_loader.YamlSpecLoader.load"></a>

#### load(path)

Load and validate a comparison spec from a YAML file.

* **Parameters:**
  **path** (*Path*) – Path to the instruction YAML file.
* **Returns:**
  Typed comparison specification.
* **Return type:**
  [ComparisonSpec](workspace-domain.md#stelion.workspace.domain.comparison.ComparisonSpec)

<a id="module-stelion.workspace.infrastructure.pyproject_parser"></a>

<a id="pyproject-parser"></a>

## Pyproject Parser

Extract ProjectMetadata from a project’s pyproject.toml.

<a id="stelion.workspace.infrastructure.pyproject_parser.PyprojectExtractor"></a>

### *class* stelion.workspace.infrastructure.pyproject_parser.PyprojectExtractor

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Read pyproject.toml and produce a ProjectMetadata instance.

<a id="stelion.workspace.infrastructure.pyproject_parser.PyprojectExtractor.extract"></a>

#### extract(project_dir)

Extract metadata from a project directory.

Reads `pyproject.toml` for package metadata. Determines `has_git`
from the presence of a `.git` directory. If `pyproject.toml` is
missing or contains invalid TOML, a warning is emitted and all fields
derived from it fall back to their defaults; fields derivable from the
filesystem (`has_git`, `languages`, README description) are still
populated normally.

* **Parameters:**
  **project_dir** (*Path*) – Root directory of the project to inspect.
* **Returns:**
  Extracted metadata, possibly with degraded status.
* **Return type:**
  [ProjectMetadata](workspace-domain.md#stelion.workspace.domain.project.ProjectMetadata)

<a id="module-stelion.workspace.infrastructure.environment_parser"></a>

<a id="environment-parser"></a>

## Environment Parser

Parse Conda environment.yml files into EnvironmentSpec.

<a id="stelion.workspace.infrastructure.environment_parser.CondaEnvironmentReader"></a>

### *class* stelion.workspace.infrastructure.environment_parser.CondaEnvironmentReader

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Read and parse a project’s environment.yml.

<a id="stelion.workspace.infrastructure.environment_parser.CondaEnvironmentReader.read"></a>

#### read(project_dir)

Parse environment.yml from a project directory.

* **Parameters:**
  **project_dir** (*Path*) – Root directory of the project.
* **Returns:**
  Parsed environment, or `None` if the file does not exist.
* **Return type:**
  [EnvironmentSpec](workspace-domain.md#stelion.workspace.domain.environment.EnvironmentSpec) | None

<a id="module-stelion.workspace.infrastructure.structured_parsers"></a>

<a id="structured-parsers"></a>

## Structured Parsers

Structured-file parsers for cross-project comparison.

All parsers consume **text content** (not file paths) and return a
nested `dict`.  The [`DispatchingParser`](#stelion.workspace.infrastructure.structured_parsers.DispatchingParser) maps file extensions
to concrete parsers – the extension seam for new formats.

<a id="stelion.workspace.infrastructure.structured_parsers.ContentParser"></a>

### *class* stelion.workspace.infrastructure.structured_parsers.ContentParser(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Protocol for parsing text content into a dict.

<a id="stelion.workspace.infrastructure.structured_parsers.ContentParser.parse"></a>

#### parse(content)

Parse text content and return a dictionary.

* **Parameters:**
  **content** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Raw text to parse.
* **Returns:**
  Parsed content as a dictionary.
* **Return type:**
  [dict](https://docs.python.org/3/builtins/stdtypes.html#dict)

<a id="stelion.workspace.infrastructure.structured_parsers.TomlParser"></a>

### *class* stelion.workspace.infrastructure.structured_parsers.TomlParser

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Parse TOML text into a dict.

<a id="stelion.workspace.infrastructure.structured_parsers.TomlParser.parse"></a>

#### parse(content)

Parse TOML text and return a dictionary.

* **Parameters:**
  **content** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Raw TOML text.
* **Returns:**
  Parsed TOML data.
* **Return type:**
  [dict](https://docs.python.org/3/builtins/stdtypes.html#dict)

<a id="stelion.workspace.infrastructure.structured_parsers.YamlParser"></a>

### *class* stelion.workspace.infrastructure.structured_parsers.YamlParser

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Parse YAML text into a dict.

<a id="stelion.workspace.infrastructure.structured_parsers.YamlParser.parse"></a>

#### parse(content)

Parse YAML text and return a dictionary.

* **Parameters:**
  **content** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Raw YAML text.
* **Returns:**
  Parsed YAML mapping.
* **Return type:**
  [dict](https://docs.python.org/3/builtins/stdtypes.html#dict)

<a id="stelion.workspace.infrastructure.structured_parsers.JsonParser"></a>

### *class* stelion.workspace.infrastructure.structured_parsers.JsonParser

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Parse JSON text into a dict.

<a id="stelion.workspace.infrastructure.structured_parsers.JsonParser.parse"></a>

#### parse(content)

Parse JSON text and return a dictionary.

* **Parameters:**
  **content** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Raw JSON text.
* **Returns:**
  Parsed JSON object.
* **Return type:**
  [dict](https://docs.python.org/3/builtins/stdtypes.html#dict)

<a id="stelion.workspace.infrastructure.structured_parsers.MarkdownSectionParser"></a>

### *class* stelion.workspace.infrastructure.structured_parsers.MarkdownSectionParser

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Parse Markdown into a nested dict keyed by header text.

The H1 title (`# Project`) is discarded — it always varies across
projects.  Text before the first H2 header is stored under
`_preamble`.  Leaf sections hold their body text as the value.
Sections with both body text and subsections store the body under a
`_body` key.

Example:

```default
## Overview            →  {"Overview": {"Motivation": "...", "Advantages": "..."}}
### Motivation
...
### Advantages
...
## Features            →  {"Features": "- [X] item\n..."}
```

<a id="stelion.workspace.infrastructure.structured_parsers.MarkdownSectionParser.parse"></a>

#### parse(content)

Parse Markdown text into a section-keyed dictionary.

* **Parameters:**
  **content** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Raw Markdown text.
* **Returns:**
  Nested dictionary keyed by section headers.
* **Return type:**
  [dict](https://docs.python.org/3/builtins/stdtypes.html#dict)

<a id="stelion.workspace.infrastructure.structured_parsers.DispatchingParser"></a>

### *class* stelion.workspace.infrastructure.structured_parsers.DispatchingParser(parsers)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Route parsing to the correct backend based on file extension or hint.

* **Parameters:**
  **parsers** ([*dict*](https://docs.python.org/3/builtins/stdtypes.html#dict) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *,* [*ContentParser*](#stelion.workspace.infrastructure.structured_parsers.ContentParser) *]*) – Mapping from extension (including dot, e.g. `".toml"`) to a parser
  instance.

<a id="stelion.workspace.infrastructure.structured_parsers.DispatchingParser.parse"></a>

#### parse(content, \*, extension='', hint=None)

Parse *content* using the parser identified by *hint* or *extension*.

* **Parameters:**
  * **content** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Raw file text.
  * **extension** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – File extension including the dot (e.g. `".toml"`).
  * **hint** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *|* *None*) – Parser name override (e.g. `"toml"`), takes precedence over
    *extension*.
* **Returns:**
  Parsed content as a nested dictionary.
* **Return type:**
  [dict](https://docs.python.org/3/builtins/stdtypes.html#dict)

<a id="module-stelion.workspace.infrastructure.gitmodules_parser"></a>

<a id="gitmodules-parser"></a>

## Gitmodules Parser

Parse .gitmodules files to detect git submodule dependency edges.

<a id="stelion.workspace.infrastructure.gitmodules_parser.scan_gitmodules"></a>

### stelion.workspace.infrastructure.gitmodules_parser.scan_gitmodules(project_dir, all_project_names)

Scan a project’s .gitmodules for ecosystem-internal submodule dependencies.

Only submodules whose name matches a known ecosystem project are returned.

* **Parameters:**
  * **project_dir** (*Path*) – Root directory of the project containing `.gitmodules`.
  * **all_project_names** ([*set*](https://docs.python.org/3/builtins/stdtypes.html#set) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *]*) – Known project names in the ecosystem.
* **Returns:**
  Dependency edges for submodules that reference ecosystem projects.
* **Return type:**
  [list](https://docs.python.org/3/builtins/stdtypes.html#list)[[DependencyEdge](workspace-domain.md#stelion.workspace.domain.dependency.DependencyEdge)]

<a id="module-stelion.workspace.infrastructure.git_operations"></a>

<a id="git-operations"></a>

## Git Operations

Concrete git operations for submodule synchronization.

<a id="stelion.workspace.infrastructure.git_operations.SubprocessGitOperations"></a>

### *class* stelion.workspace.infrastructure.git_operations.SubprocessGitOperations

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Git operations implemented via subprocess calls.

<a id="stelion.workspace.infrastructure.git_operations.SubprocessGitOperations.head_commit"></a>

#### head_commit(repo_dir)

Read HEAD commit SHA from a repository.

* **Parameters:**
  **repo_dir** (*Path*) – Path to the git repository.
* **Returns:**
  Full SHA of the HEAD commit.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)

<a id="stelion.workspace.infrastructure.git_operations.SubprocessGitOperations.submodule_commit"></a>

#### submodule_commit(superproject_dir, submodule_path)

Read the recorded commit SHA for a submodule in a superproject.

* **Parameters:**
  * **superproject_dir** (*Path*) – Root directory of the superproject.
  * **submodule_path** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Relative path to the submodule within the superproject.
* **Returns:**
  Commit SHA recorded in the superproject tree.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)

<a id="stelion.workspace.infrastructure.git_operations.SubprocessGitOperations.fetch_remote"></a>

#### fetch_remote(repo_dir)

Fetch from the default remote.

* **Parameters:**
  **repo_dir** (*Path*) – Path to the git repository.

<a id="stelion.workspace.infrastructure.git_operations.SubprocessGitOperations.remote_head"></a>

#### remote_head(repo_dir, remote, branch)

Read the commit SHA of a remote tracking branch.

* **Parameters:**
  * **repo_dir** (*Path*) – Path to the git repository.
  * **remote** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Remote name (e.g. `"origin"`).
  * **branch** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Branch name on the remote.
* **Returns:**
  Full SHA of the remote tracking branch.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)

<a id="stelion.workspace.infrastructure.git_operations.SubprocessGitOperations.update_submodule_pointer"></a>

#### update_submodule_pointer(superproject_dir, submodule_path, commit)

Update a submodule to point at a specific commit.

* **Parameters:**
  * **superproject_dir** (*Path*) – Root directory of the superproject.
  * **submodule_path** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Relative path to the submodule.
  * **commit** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Target commit SHA.

<a id="stelion.workspace.infrastructure.git_operations.SubprocessGitOperations.commit_submodule_update"></a>

#### commit_submodule_update(superproject_dir, submodule_path, dependency, commit_short)

Stage and commit the submodule pointer change in the superproject.

* **Parameters:**
  * **superproject_dir** (*Path*) – Root directory of the superproject.
  * **submodule_path** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Relative path to the submodule.
  * **dependency** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the dependency project for the commit message.
  * **commit_short** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Abbreviated commit SHA for the commit message.

<a id="stelion.workspace.infrastructure.git_operations.SubprocessGitOperations.is_clean"></a>

#### is_clean(repo_dir)

Check whether the working tree has no uncommitted changes.

* **Parameters:**
  **repo_dir** (*Path*) – Path to the git repository.
* **Returns:**
  `True` if the working tree is clean.
* **Return type:**
  [bool](https://docs.python.org/3/builtins/functions.html#bool)

<a id="stelion.workspace.infrastructure.git_operations.SubprocessGitOperations.update_local_clone"></a>

#### update_local_clone(repo_dir, commit)

Update local clone to the target commit via fast-forward merge.

* **Parameters:**
  * **repo_dir** (*Path*) – Path to the local clone.
  * **commit** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Target commit SHA to fast-forward to.
* **Returns:**
  The previous HEAD commit SHA.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)
* **Raises:**
  [**SyncError**](workspace-exceptions.md#stelion.workspace.exceptions.SyncError) – If the working tree is dirty or fast-forward merge fails.

<a id="stelion.workspace.infrastructure.git_operations.SubprocessGitOperations.push_to_remote"></a>

#### push_to_remote(repo_dir, remote, branch)

Push the current HEAD to a remote branch.

* **Parameters:**
  * **repo_dir** (*Path*) – Path to the git repository.
  * **remote** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Remote name (e.g. `"origin"`).
  * **branch** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Branch to push.

<a id="module-stelion.workspace.infrastructure.bootstrap_git"></a>

<a id="bootstrap-git"></a>

## Bootstrap Git

Git-backed bootstrap helpers.

<a id="stelion.workspace.infrastructure.bootstrap_git.read_git_identity"></a>

### stelion.workspace.infrastructure.bootstrap_git.read_git_identity()

Read author identity from git config when available.

* **Returns:**
  A `(name, email)` pair, both empty if git config is unavailable.
* **Return type:**
  [tuple](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[str](https://docs.python.org/3/builtins/stdtypes.html#str), [str](https://docs.python.org/3/builtins/stdtypes.html#str)]

<a id="stelion.workspace.infrastructure.bootstrap_git.init_repository"></a>

### stelion.workspace.infrastructure.bootstrap_git.init_repository(target_dir)

Initialize a git repository for a bootstrapped project.

* **Parameters:**
  **target_dir** (*Path*) – Root directory of the newly created project.

<a id="module-stelion.workspace.infrastructure.bulk_operations"></a>

<a id="bulk-operations"></a>

## Bulk Operations

Concrete bulk operation implementations.

<a id="stelion.workspace.infrastructure.bulk_operations.ShellOperation"></a>

### *class* stelion.workspace.infrastructure.bulk_operations.ShellOperation(command, runner)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Run an arbitrary shell command in each project directory.

* **Parameters:**
  * **command** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Shell command string to execute.
  * **runner** ([*CommandRunner*](workspace-application.md#stelion.workspace.application.protocols.CommandRunner)) – Backend used to invoke shell processes.

<a id="stelion.workspace.infrastructure.bulk_operations.ShellOperation.label"></a>

#### *property* label *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)*

Human-readable label describing this operation.

* **Returns:**
  Formatted label prefixed with `exec:`.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)

<a id="stelion.workspace.infrastructure.bulk_operations.GitCommitOperation"></a>

### *class* stelion.workspace.infrastructure.bulk_operations.GitCommitOperation(message, runner)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Stage tracked changes and commit, skipping clean working trees.

* **Parameters:**
  * **message** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Commit message to use.
  * **runner** ([*CommandRunner*](workspace-application.md#stelion.workspace.application.protocols.CommandRunner)) – Backend used to invoke git processes.

<a id="stelion.workspace.infrastructure.bulk_operations.GitCommitOperation.label"></a>

#### *property* label *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)*

Human-readable label describing this operation.

* **Returns:**
  Formatted label prefixed with `commit:`.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)

<a id="stelion.workspace.infrastructure.bulk_operations.GitPushOperation"></a>

### *class* stelion.workspace.infrastructure.bulk_operations.GitPushOperation(remote, branch, runner)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Push the current branch to a remote.

* **Parameters:**
  * **remote** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Remote name (e.g. `"origin"`).
  * **branch** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Branch to push.
  * **runner** ([*CommandRunner*](workspace-application.md#stelion.workspace.application.protocols.CommandRunner)) – Backend used to invoke git processes.

<a id="stelion.workspace.infrastructure.bulk_operations.GitPushOperation.label"></a>

#### *property* label *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)*

Human-readable label describing this operation.

* **Returns:**
  Formatted label prefixed with `push:`.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)

<a id="module-stelion.workspace.infrastructure.dependency_scanners"></a>

<a id="dependency-scanners"></a>

## Dependency Scanners

Concrete dependency scanners used by the workspace graph builder.

<a id="stelion.workspace.infrastructure.dependency_scanners.EditablePipDependencyScanner"></a>

### *class* stelion.workspace.infrastructure.dependency_scanners.EditablePipDependencyScanner(env_reader)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Detect editable pip dependencies from environment.yml files.

* **Parameters:**
  **env_reader** ([*EnvironmentReader*](workspace-application.md#stelion.workspace.application.protocols.EnvironmentReader)) – Reader used to load environment specs from disk.

<a id="stelion.workspace.infrastructure.dependency_scanners.EditablePipDependencyScanner.scan"></a>

#### scan(project_name, project_dir, all_project_names)

Scan a project directory for editable pip dependency edges.

* **Parameters:**
  * **project_name** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the project to scan.
  * **project_dir** (*Path*) – Root directory of the project.
  * **all_project_names** ([*set*](https://docs.python.org/3/builtins/stdtypes.html#set) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *]*) – Known project names in the ecosystem.
* **Returns:**
  Detected editable pip dependency edges.
* **Return type:**
  [list](https://docs.python.org/3/builtins/stdtypes.html#list)[[DependencyEdge](workspace-domain.md#stelion.workspace.domain.dependency.DependencyEdge)]

<a id="stelion.workspace.infrastructure.dependency_scanners.EditablePipDependencyScanner.scan_with_spec"></a>

#### scan_with_spec(project_name, env_spec, all_project_names)

Scan using a pre-read environment spec instead of reading from disk.

* **Parameters:**
  * **project_name** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the project to scan.
  * **env_spec** ([*EnvironmentSpec*](workspace-domain.md#stelion.workspace.domain.environment.EnvironmentSpec) *|* *None*) – Pre-read environment spec, or `None` to skip.
  * **all_project_names** ([*set*](https://docs.python.org/3/builtins/stdtypes.html#set) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *]*) – Known project names in the ecosystem.
* **Returns:**
  Detected editable pip dependency edges.
* **Return type:**
  [list](https://docs.python.org/3/builtins/stdtypes.html#list)[[DependencyEdge](workspace-domain.md#stelion.workspace.domain.dependency.DependencyEdge)]

<a id="stelion.workspace.infrastructure.dependency_scanners.GitmodulesDependencyScanner"></a>

### *class* stelion.workspace.infrastructure.dependency_scanners.GitmodulesDependencyScanner

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Detect git submodule dependencies.

<a id="stelion.workspace.infrastructure.dependency_scanners.GitmodulesDependencyScanner.scan"></a>

#### scan(project_name, project_dir, all_project_names)

Scan a project for git submodule dependency edges.

* **Parameters:**
  * **project_name** ([*str*](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the project to scan.
  * **project_dir** (*Path*) – Root directory of the project.
  * **all_project_names** ([*set*](https://docs.python.org/3/builtins/stdtypes.html#set) *[*[*str*](https://docs.python.org/3/builtins/stdtypes.html#str) *]*) – Known project names in the ecosystem.
* **Returns:**
  Detected submodule dependency edges.
* **Return type:**
  [list](https://docs.python.org/3/builtins/stdtypes.html#list)[[DependencyEdge](workspace-domain.md#stelion.workspace.domain.dependency.DependencyEdge)]

<a id="module-stelion.workspace.infrastructure.renderers.comparison"></a>

<a id="renderers-comparison"></a>

## Renderers — Comparison

YAML serialization for comparison reports.

Terminal rendering (Rich tables) lives in the adapters layer. This module
handles only the machine-parseable YAML output, consistent with the
existing split where `renderers/yaml.py` serializes workspace artifacts.

<a id="stelion.workspace.infrastructure.renderers.comparison.render_tree_yaml"></a>

### stelion.workspace.infrastructure.renderers.comparison.render_tree_yaml(report)

Serialize a `TreeReport` to YAML.

* **Parameters:**
  **report** ([*TreeReport*](workspace-domain.md#stelion.workspace.domain.comparison.TreeReport)) – Aggregated tree comparison report.
* **Returns:**
  YAML text with a descriptive header comment.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)

<a id="stelion.workspace.infrastructure.renderers.comparison.render_file_yaml"></a>

### stelion.workspace.infrastructure.renderers.comparison.render_file_yaml(report)

Serialize a `FileReport` to YAML.

* **Parameters:**
  **report** ([*FileReport*](workspace-domain.md#stelion.workspace.domain.comparison.FileReport)) – Aggregated file comparison report.
* **Returns:**
  YAML text with a descriptive header comment.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)

<a id="module-stelion.workspace.infrastructure.renderers.vscode"></a>

<a id="renderers-vs-code"></a>

## Renderers — VS Code

Render VS Code .code-workspace files (JSON with comments).

<a id="stelion.workspace.infrastructure.renderers.vscode.VSCodeWorkspaceFileRenderer"></a>

### *class* stelion.workspace.infrastructure.renderers.vscode.VSCodeWorkspaceFileRenderer(loader, reader=None)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Render a VS Code workspace file using injected package data loading.

* **Parameters:**
  * **loader** ([*PackageDataLoader*](workspace-application.md#stelion.workspace.application.protocols.PackageDataLoader)) – Loader for bundled package data files.
  * **reader** ([*FileReader*](workspace-application.md#stelion.workspace.application.protocols.FileReader) *|* *None*) – Optional file reader for custom settings sources.

<a id="module-stelion.workspace.infrastructure.renderers.yaml"></a>

<a id="renderers-yaml"></a>

## Renderers — YAML

Render YAML workspace artifacts: dependencies.yml, projects.yml, environment.yml.

<a id="stelion.workspace.infrastructure.renderers.yaml.render_dependency_yaml"></a>

### stelion.workspace.infrastructure.renderers.yaml.render_dependency_yaml(graph)

Generate dependencies.yml as a structured YAML file.

* **Parameters:**
  **graph** ([*DependencyGraph*](workspace-domain.md#stelion.workspace.domain.dependency.DependencyGraph)) – Detected and manual dependency edges.
* **Returns:**
  YAML text with a descriptive header comment.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)

<a id="stelion.workspace.infrastructure.renderers.yaml.render_projects_yaml"></a>

### stelion.workspace.infrastructure.renderers.yaml.render_projects_yaml(inventory, manifest_dir)

Generate projects.yml as a structured YAML registry.

* **Parameters:**
  * **inventory** ([*ProjectInventory*](workspace-domain.md#stelion.workspace.domain.project.ProjectInventory)) – Discovered projects with metadata.
  * **manifest_dir** (*Path*) – Directory containing the workspace manifest, used for relative paths.
* **Returns:**
  YAML text with a descriptive header comment.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)

<a id="stelion.workspace.infrastructure.renderers.yaml.render_environment"></a>

### stelion.workspace.infrastructure.renderers.yaml.render_environment(environment)

Generate a shared Conda environment.yml.

* **Parameters:**
  **environment** ([*EnvironmentSpec*](workspace-domain.md#stelion.workspace.domain.environment.EnvironmentSpec)) – Merged environment specification.
* **Returns:**
  YAML text, prefixed with warning comments if issues were detected.
* **Return type:**
  [str](https://docs.python.org/3/builtins/stdtypes.html#str)
