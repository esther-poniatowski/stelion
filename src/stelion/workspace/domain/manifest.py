"""Immutable domain models for workspace manifest configuration."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True)
class DiscoveryConfig:
    """Rules for discovering projects on disk."""

    scan_dirs: tuple[str, ...]
    """Directories to scan for projects."""
    exclude: tuple[str, ...] = ()
    """Directory names to skip during scanning."""
    markers: tuple[str, ...] = ("pyproject.toml",)
    """Filenames whose presence identifies a project root."""
    extra_paths: tuple[str, ...] = ()
    """Additional paths to include as projects unconditionally."""
    include_self: bool = True
    """Whether to include the workspace root as a project."""
    self_name: str = ""
    """Name assigned to the workspace root project."""


@dataclass(frozen=True)
class TemplateConfig:
    """Template source and substitution rules for bootstrapping new projects."""

    source: str
    """Path or identifier of the template source."""
    delimiters: tuple[str, str] = ("{{ ", " }}")
    """Opening and closing delimiter pair for placeholders."""
    exclude_patterns: tuple[str, ...] = ()
    """Glob patterns for files excluded from template processing."""
    renames: Mapping[str, str] = field(default_factory=dict)
    """Filename substitution rules applied during bootstrapping."""

    def __post_init__(self) -> None:
        if len(self.delimiters) != 2 or not all(
            isinstance(part, str) for part in self.delimiters
        ):
            raise ValueError("Template delimiters must contain exactly two strings.")
        object.__setattr__(self, "exclude_patterns", tuple(self.exclude_patterns))
        object.__setattr__(self, "renames", MappingProxyType(dict(self.renames)))


@dataclass(frozen=True)
class EcosystemDefaults:
    """Default values for placeholder substitution and project metadata."""

    github_user: str = ""
    """Default GitHub username for new projects."""
    channel_name: str = ""
    """Default Conda channel name."""
    license: str = ""
    """Default SPDX license identifier."""


@dataclass(frozen=True)
class VSCodeConfig:
    """VS Code workspace settings source and overrides."""

    source: str = "defaults"
    """Settings source identifier (``"defaults"`` for bundled defaults)."""
    settings_overrides: Mapping[str, Any] = field(default_factory=dict)
    """User overrides merged into VS Code settings."""
    extensions_overrides: tuple[str, ...] = ()
    """Additional VS Code extension identifiers to recommend."""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "settings_overrides",
            MappingProxyType(dict(self.settings_overrides)),
        )
        object.__setattr__(
            self, "extensions_overrides", tuple(self.extensions_overrides)
        )

    def uses_defaults(self) -> bool:
        """Whether VS Code assets should come from bundled defaults.

        Returns
        -------
        bool
            True if source is ``"defaults"``.
        """
        return self.source == "defaults"


@dataclass(frozen=True)
class WorkspaceFileConfig:
    """Generation target for the VS Code .code-workspace file."""

    output: str = "dev-repos.code-workspace"
    """Filename for the generated .code-workspace file."""


@dataclass(frozen=True)
class ProjectsRegistryConfig:
    """Generation target for the projects registry (YAML)."""

    output: str = "projects.yml"
    """Filename for the generated projects registry."""


@dataclass(frozen=True)
class DependencyGraphConfig:
    """Generation target for the dependency graph (YAML)."""

    output: str = "dependencies.yml"
    """Filename for the generated dependency graph."""


@dataclass(frozen=True)
class SharedEnvironmentConfig:
    """Generation target for the shared Conda environment."""

    output: str = "environment.yml"
    """Filename for the generated environment file."""
    name: str = ""
    """Conda environment name."""


@dataclass(frozen=True)
class GenerateConfig:
    """All generation targets."""

    workspace_file: WorkspaceFileConfig = field(default_factory=WorkspaceFileConfig)
    """Configuration for the VS Code .code-workspace file."""
    projects_registry: ProjectsRegistryConfig = field(
        default_factory=ProjectsRegistryConfig
    )
    """Configuration for the projects registry."""
    dependency_graph: DependencyGraphConfig = field(
        default_factory=DependencyGraphConfig
    )
    """Configuration for the dependency graph."""
    shared_environment: SharedEnvironmentConfig = field(
        default_factory=SharedEnvironmentConfig
    )
    """Configuration for the shared Conda environment."""


@dataclass(frozen=True)
class CanonicalMechanism:
    """Integration mechanism assignment for a library."""

    type: str
    """Library type identifier."""
    mechanism: str
    """Integration mechanism name."""
    edge_kind: str = ""
    """Semantic dependency kind used to classify detected edges."""


@dataclass(frozen=True)
class ReferenceImplementation:
    """A reference implementation of the integration module pattern."""

    module: str
    """Fully qualified module path."""
    description: str
    """Human-readable description of the reference implementation."""


@dataclass(frozen=True)
class IntegrationsConfig:
    """Project-specific integration mechanism assignments and references."""

    canonical_mechanisms: Mapping[str, CanonicalMechanism] = field(default_factory=dict)
    """Library-to-mechanism assignments keyed by library name."""
    reference_implementations: tuple[ReferenceImplementation, ...] = ()
    """Known reference implementations of the integration pattern."""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "canonical_mechanisms",
            MappingProxyType(dict(self.canonical_mechanisms)),
        )
        object.__setattr__(
            self,
            "reference_implementations",
            tuple(self.reference_implementations),
        )


@dataclass(frozen=True)
class ManualEdge:
    """A manually declared dependency edge."""

    dependent: str
    """Name of the project that depends on another."""
    dependency: str
    """Name of the project being depended upon."""
    mechanism: str
    """How the dependency is consumed (e.g. submodule, editable install)."""
    kind: str
    """Semantic role of the dependency."""
    source_declaration: str
    """Configuration declaration that asserts the edge."""
    version_policy: str
    """Rule selecting the dependency version or commit."""
    optional: bool = False
    """Whether the dependent can operate without this relation."""
    integration_path: str = ""
    """Path or target used by the integration mechanism, when applicable."""


@dataclass(frozen=True)
class DependenciesConfig:
    """Manual dependency declarations and supplemental repository paths."""

    manual_edges: tuple[ManualEdge, ...] = ()
    """Explicitly declared dependency edges."""
    scan_paths: tuple[str, ...] = ()
    """Directories scanned for dependency *edges* (editable pip installs,
    gitmodules). Used by ``build_dependency_graph``.
    """
    superproject_paths: tuple[str, ...] = ()
    """Directories resolved as superproject *locations* for submodule sync.
    Used by ``resolve_submodule_targets`` to find superproject directories
    by name.
    """


@dataclass(frozen=True)
class ReferencesConfig:
    """Expected reference documents in the workspace."""

    expected: tuple[str, ...] = ()
    """Filenames of reference documents that should be present."""


@dataclass(frozen=True)
class WorkspaceManifest:
    """Complete workspace manifest parsed from stelion.yml."""

    discovery: DiscoveryConfig
    """Project discovery rules."""
    template: TemplateConfig
    """Template bootstrapping configuration."""
    defaults: EcosystemDefaults
    """Default placeholder values."""
    vscode: VSCodeConfig
    """VS Code workspace settings."""
    generate: GenerateConfig
    """All generation target configurations."""
    integrations: IntegrationsConfig
    """Integration mechanism assignments and references."""
    names_in_use: Mapping[str, str]
    """Reserved project names mapped to their descriptions."""
    dependencies: DependenciesConfig
    """Manual dependency declarations and scan paths."""
    references: ReferencesConfig
    """Expected reference documents in the workspace."""
    manifest_dir: Path
    """Root of the workspace, against which the paths written in the manifest are resolved.

    The manifest lies at the root or in its ``config/tools/`` folder, so this folder is not always
    the folder of the manifest file."""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "names_in_use", MappingProxyType(dict(self.names_in_use))
        )

    def with_added_extra_path(self, extra_path: str) -> "WorkspaceManifest":
        """Return a manifest that explicitly discovers *extra_path*.

        Parameters
        ----------
        extra_path : str
            Additional path to include in project discovery.

        Returns
        -------
        WorkspaceManifest
            Updated manifest (or self if the path is already present).
        """
        if extra_path in self.discovery.extra_paths:
            return self
        return replace(
            self,
            discovery=replace(
                self.discovery,
                extra_paths=self.discovery.extra_paths + (extra_path,),
            ),
        )
