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
    exclude: tuple[str, ...] = ("dev",)
    markers: tuple[str, ...] = ("pyproject.toml",)
    extra_paths: tuple[str, ...] = ()
    include_self: bool = True
    self_name: str = "dev"


@dataclass(frozen=True)
class TemplateConfig:
    """Template source and substitution rules for bootstrapping new projects."""

    source: str
    delimiters: tuple[str, str] = ("{{ ", " }}")
    exclude_patterns: tuple[str, ...] = ()
    renames: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if len(self.delimiters) != 2 or not all(isinstance(part, str) for part in self.delimiters):
            raise ValueError("Template delimiters must contain exactly two strings.")
        object.__setattr__(self, "exclude_patterns", tuple(self.exclude_patterns))
        object.__setattr__(self, "renames", MappingProxyType(dict(self.renames)))


@dataclass(frozen=True)
class EcosystemDefaults:
    """Default values for placeholder substitution and project metadata."""

    github_user: str = ""
    channel_name: str = ""
    license: str = "GPL-3.0-or-later"


@dataclass(frozen=True)
class VSCodeConfig:
    """VS Code workspace settings source and overrides."""

    source: str = "defaults"
    settings_overrides: Mapping[str, Any] = field(default_factory=dict)
    extensions_overrides: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "settings_overrides",
            MappingProxyType(dict(self.settings_overrides)),
        )
        object.__setattr__(self, "extensions_overrides", tuple(self.extensions_overrides))

    def uses_defaults(self) -> bool:
        """Whether VS Code assets should come from bundled defaults."""
        return self.source == "defaults"


@dataclass(frozen=True)
class WorkspaceFileConfig:
    """Generation target for the VS Code .code-workspace file."""

    output: str = "dev-repos.code-workspace"


@dataclass(frozen=True)
class ProjectsRegistryConfig:
    """Generation target for the projects registry (YAML)."""

    output: str = "projects.yml"


@dataclass(frozen=True)
class DependencyGraphConfig:
    """Generation target for the dependency graph (YAML)."""

    output: str = "dependencies.yml"


@dataclass(frozen=True)
class SharedEnvironmentConfig:
    """Generation target for the shared Conda environment."""

    output: str = "environment.yml"
    name: str = "dev"


@dataclass(frozen=True)
class GenerateConfig:
    """All generation targets."""

    workspace_file: WorkspaceFileConfig = field(default_factory=WorkspaceFileConfig)
    projects_registry: ProjectsRegistryConfig = field(default_factory=ProjectsRegistryConfig)
    dependency_graph: DependencyGraphConfig = field(default_factory=DependencyGraphConfig)
    shared_environment: SharedEnvironmentConfig = field(default_factory=SharedEnvironmentConfig)


@dataclass(frozen=True)
class CanonicalMechanism:
    """Integration mechanism assignment for a library."""

    type: str
    mechanism: str


@dataclass(frozen=True)
class ReferenceImplementation:
    """A reference implementation of the integration module pattern."""

    module: str
    description: str


@dataclass(frozen=True)
class IntegrationsConfig:
    """Project-specific integration mechanism assignments and references."""

    canonical_mechanisms: Mapping[str, CanonicalMechanism] = field(default_factory=dict)
    reference_implementations: tuple[ReferenceImplementation, ...] = ()

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
    dependency: str
    mechanism: str
    detail: str = ""


@dataclass(frozen=True)
class DependenciesConfig:
    """Manual dependency declarations and supplemental repository paths.

    Attributes
    ----------
    scan_paths
        Directories scanned for dependency *edges* (editable pip installs,
        gitmodules). Used by ``build_dependency_graph``.
    superproject_paths
        Directories resolved as superproject *locations* for submodule sync.
        Used by ``resolve_submodule_targets`` to find superproject directories
        by name.
    """

    manual_edges: tuple[ManualEdge, ...] = ()
    scan_paths: tuple[str, ...] = ()
    superproject_paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReferencesConfig:
    """Expected reference documents in the workspace."""

    expected: tuple[str, ...] = ()


@dataclass(frozen=True)
class WorkspaceManifest:
    """Complete workspace manifest parsed from stelion.yml."""

    discovery: DiscoveryConfig
    template: TemplateConfig
    defaults: EcosystemDefaults
    vscode: VSCodeConfig
    generate: GenerateConfig
    integrations: IntegrationsConfig
    names_in_use: Mapping[str, str]
    dependencies: DependenciesConfig
    references: ReferencesConfig
    manifest_dir: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "names_in_use", MappingProxyType(dict(self.names_in_use)))

    def with_added_extra_path(self, extra_path: str) -> "WorkspaceManifest":
        """Return a manifest that explicitly discovers *extra_path*."""
        if extra_path in self.discovery.extra_paths:
            return self
        return replace(
            self,
            discovery=replace(
                self.discovery,
                extra_paths=self.discovery.extra_paths + (extra_path,),
            ),
        )
