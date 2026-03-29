"""Workspace-specific exception types."""


class WorkspaceError(Exception):
    """Base exception for workspace application and infrastructure failures."""


class ManifestValidationError(WorkspaceError):
    """Raised when a workspace manifest is structurally invalid."""


class ProjectMetadataParseError(WorkspaceError):
    """Raised when project metadata cannot be parsed from pyproject.toml."""


class EnvironmentParseError(WorkspaceError):
    """Raised when environment.yml exists but cannot be parsed."""


class BootstrapError(WorkspaceError):
    """Raised when bootstrapping a new project cannot proceed."""


class SyncError(WorkspaceError):
    """Raised when submodule synchronization cannot proceed."""


class ComparisonError(WorkspaceError):
    """Raised when a comparison operation cannot proceed."""
