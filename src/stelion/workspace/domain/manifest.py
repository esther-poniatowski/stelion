"""Immutable domain models for workspace manifest configuration.

Classes
-------
DiscoveryConfig
    Rules for discovering projects on disk.
TemplateConfig
    Template source and substitution rules for bootstrapping new projects.
EcosystemDefaults
    Default values for placeholder substitution and project metadata.
VSCodeConfig
    VS Code workspace settings source and overrides.
WorkspaceFileConfig
    Generation target for the VS Code .code-workspace file.
ProjectsRegistryConfig
    Generation target for the projects registry (YAML).
DependencyGraphConfig
    Generation target for the dependency graph (YAML).
SharedEnvironmentConfig
    Generation target for the shared Conda environment.
GenerateConfig
    All generation targets.
CanonicalMechanism
    Integration mechanism assignment for a library.
ReferenceImplementation
    A reference implementation of the integration module pattern.
IntegrationsConfig
    Project-specific integration mechanism assignments and references.
ManualEdge
    A manually declared dependency edge.
DependenciesConfig
    Manual dependency declarations and supplemental repository paths.
ReferencesConfig
    Expected reference documents in the workspace.
WorkspaceManifest
    Complete workspace manifest parsed from stelion.yml.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True)
class DiscoveryConfig:
    """Rules for discovering projects on disk.

    Attributes
    ----------
    scan_dirs : tuple[str, ...]
        Directories to scan for projects.
    exclude : tuple[str, ...]
        Directory names to skip during scanning.
    markers : tuple[str, ...]
        Filenames whose presence identifies a project root.
    extra_paths : tuple[str, ...]
        Additional paths to include as projects unconditionally.
    include_self : bool
        Whether to include the workspace root as a project.
    self_name : str
        Name assigned to the workspace root project.
    """

    scan_dirs: tuple[str, ...]
    exclude: tuple[str, ...] = ("dev",)
    markers: tuple[str, ...] = ("pyproject.toml",)
    extra_paths: tuple[str, ...] = ()
    include_self: bool = True
    self_name: str = "dev"


@dataclass(frozen=True)
class TemplateConfig:
    """Template source and substitution rules for bootstrapping new projects.

    Attributes
    ----------
    source : str
        Path or identifier of the template source.
    delimiters : tuple[str, str]
        Opening and closing delimiter pair for placeholders.
    exclude_patterns : tuple[str, ...]
        Glob patterns for files excluded from template processing.
    renames : Mapping[str, str]
        Filename substitution rules applied during bootstrapping.
    """

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
    """Default values for placeholder substitution and project metadata.

    Attributes
    ----------
    github_user : str
        Default GitHub username for new projects.
    channel_name : str
        Default Conda channel name.
    license : str
        Default SPDX license identifier.
    """

    github_user: str = ""
    channel_name: str = ""
    license: str = "GPL-3.0-or-later"


@dataclass(frozen=True)
class VSCodeConfig:
    """VS Code workspace settings source and overrides.

    Attributes
    ----------
    source : str
        Settings source identifier (``"defaults"`` for bundled defaults).
    settings_overrides : Mapping[str, Any]
        User overrides merged into VS Code settings.
    extensions_overrides : tuple[str, ...]
        Additional VS Code extension identifiers to recommend.
    """

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
        """Whether VS Code assets should come from bundled defaults.

        Returns
        -------
        bool
            True if source is ``"defaults"``.
        """
        return self.source == "defaults"


@dataclass(frozen=True)
class WorkspaceFileConfig:
    """Generation target for the VS Code .code-workspace file.

    Attributes
    ----------
    output : str
        Filename for the generated .code-workspace file.
    """

    output: str = "dev-repos.code-workspace"


@dataclass(frozen=True)
class ProjectsRegistryConfig:
    """Generation target for the projects registry (YAML).

    Attributes
    ----------
    output : str
        Filename for the generated projects registry.
    """

    output: str = "projects.yml"


@dataclass(frozen=True)
class DependencyGraphConfig:
    """Generation target for the dependency graph (YAML).

    Attributes
    ----------
    output : str
        Filename for the generated dependency graph.
    """

    output: str = "dependencies.yml"


@dataclass(frozen=True)
class SharedEnvironmentConfig:
    """Generation target for the shared Conda environment.

    Attributes
    ----------
    output : str
        Filename for the generated environment file.
    name : str
        Conda environment name.
    """

    output: str = "environment.yml"
    name: str = "dev"


@dataclass(frozen=True)
class GenerateConfig:
    """All generation targets.

    Attributes
    ----------
    workspace_file : WorkspaceFileConfig
        Configuration for the VS Code .code-workspace file.
    projects_registry : ProjectsRegistryConfig
        Configuration for the projects registry.
    dependency_graph : DependencyGraphConfig
        Configuration for the dependency graph.
    shared_environment : SharedEnvironmentConfig
        Configuration for the shared Conda environment.
    """

    workspace_file: WorkspaceFileConfig = field(default_factory=WorkspaceFileConfig)
    projects_registry: ProjectsRegistryConfig = field(default_factory=ProjectsRegistryConfig)
    dependency_graph: DependencyGraphConfig = field(default_factory=DependencyGraphConfig)
    shared_environment: SharedEnvironmentConfig = field(default_factory=SharedEnvironmentConfig)


@dataclass(frozen=True)
class CanonicalMechanism:
    """Integration mechanism assignment for a library.

    Attributes
    ----------
    type : str
        Library type identifier.
    mechanism : str
        Integration mechanism name.
    """

    type: str
    mechanism: str


@dataclass(frozen=True)
class ReferenceImplementation:
    """A reference implementation of the integration module pattern.

    Attributes
    ----------
    module : str
        Fully qualified module path.
    description : str
        Human-readable description of the reference implementation.
    """

    module: str
    description: str


@dataclass(frozen=True)
class IntegrationsConfig:
    """Project-specific integration mechanism assignments and references.

    Attributes
    ----------
    canonical_mechanisms : Mapping[str, CanonicalMechanism]
        Library-to-mechanism assignments keyed by library name.
    reference_implementations : tuple[ReferenceImplementation, ...]
        Known reference implementations of the integration pattern.
    """

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
    """A manually declared dependency edge.

    Attributes
    ----------
    dependent : str
        Name of the project that depends on another.
    dependency : str
        Name of the project being depended upon.
    mechanism : str
        How the dependency is consumed (e.g. submodule, editable install).
    detail : str
        Optional additional detail about the dependency.
    """

    dependent: str
    dependency: str
    mechanism: str
    detail: str = ""


@dataclass(frozen=True)
class DependenciesConfig:
    """Manual dependency declarations and supplemental repository paths.

    Attributes
    ----------
    manual_edges : tuple[ManualEdge, ...]
        Explicitly declared dependency edges.
    scan_paths : tuple[str, ...]
        Directories scanned for dependency *edges* (editable pip installs,
        gitmodules). Used by ``build_dependency_graph``.
    superproject_paths : tuple[str, ...]
        Directories resolved as superproject *locations* for submodule sync.
        Used by ``resolve_submodule_targets`` to find superproject directories
        by name.
    """

    manual_edges: tuple[ManualEdge, ...] = ()
    scan_paths: tuple[str, ...] = ()
    superproject_paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReferencesConfig:
    """Expected reference documents in the workspace.

    Attributes
    ----------
    expected : tuple[str, ...]
        Filenames of reference documents that should be present.
    """

    expected: tuple[str, ...] = ()


@dataclass(frozen=True)
class WorkspaceManifest:
    """Complete workspace manifest parsed from stelion.yml.

    Attributes
    ----------
    discovery : DiscoveryConfig
        Project discovery rules.
    template : TemplateConfig
        Template bootstrapping configuration.
    defaults : EcosystemDefaults
        Default placeholder values.
    vscode : VSCodeConfig
        VS Code workspace settings.
    generate : GenerateConfig
        All generation target configurations.
    integrations : IntegrationsConfig
        Integration mechanism assignments and references.
    names_in_use : Mapping[str, str]
        Reserved project names mapped to their descriptions.
    dependencies : DependenciesConfig
        Manual dependency declarations and scan paths.
    references : ReferencesConfig
        Expected reference documents in the workspace.
    manifest_dir : Path
        Directory containing the manifest file.
    """

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
