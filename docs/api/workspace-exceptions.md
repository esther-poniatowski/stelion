<a id="module-stelion.workspace.exceptions"></a>

<a id="workspace-exceptions"></a>

# Workspace Exceptions

Workspace-specific exception types.

<a id="stelion.workspace.exceptions.WorkspaceError"></a>

### *exception* stelion.workspace.exceptions.WorkspaceError

Bases: [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception)

Base exception for workspace application and infrastructure failures.

<a id="stelion.workspace.exceptions.ManifestValidationError"></a>

### *exception* stelion.workspace.exceptions.ManifestValidationError

Bases: [`WorkspaceError`](#stelion.workspace.exceptions.WorkspaceError)

Raised when a workspace manifest is structurally invalid.

<a id="stelion.workspace.exceptions.ProjectMetadataParseError"></a>

### *exception* stelion.workspace.exceptions.ProjectMetadataParseError

Bases: [`WorkspaceError`](#stelion.workspace.exceptions.WorkspaceError)

Raised when project metadata cannot be parsed from pyproject.toml.

<a id="stelion.workspace.exceptions.EnvironmentParseError"></a>

### *exception* stelion.workspace.exceptions.EnvironmentParseError

Bases: [`WorkspaceError`](#stelion.workspace.exceptions.WorkspaceError)

Raised when environment.yml exists but cannot be parsed.

<a id="stelion.workspace.exceptions.BootstrapError"></a>

### *exception* stelion.workspace.exceptions.BootstrapError

Bases: [`WorkspaceError`](#stelion.workspace.exceptions.WorkspaceError)

Raised when bootstrapping a new project cannot proceed.

<a id="stelion.workspace.exceptions.SyncError"></a>

### *exception* stelion.workspace.exceptions.SyncError

Bases: [`WorkspaceError`](#stelion.workspace.exceptions.WorkspaceError)

Raised when submodule synchronization cannot proceed.

<a id="stelion.workspace.exceptions.ComparisonError"></a>

### *exception* stelion.workspace.exceptions.ComparisonError

Bases: [`WorkspaceError`](#stelion.workspace.exceptions.WorkspaceError)

Raised when a comparison operation cannot proceed.
