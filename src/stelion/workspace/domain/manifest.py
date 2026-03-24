"""Typed representations of the workspace manifest (stelion.yml)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


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
    renames: dict[str, str] = field(default_factory=dict)


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
    settings_overrides: dict = field(default_factory=dict)
    extensions_overrides: tuple[str, ...] = ()


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

    canonical_mechanisms: dict[str, CanonicalMechanism] = field(default_factory=dict)
    reference_implementations: tuple[ReferenceImplementation, ...] = ()


@dataclass(frozen=True)
class ManualEdge:
    """A manually declared dependency edge."""

    dependent: str
    dependency: str
    mechanism: str
    detail: str = ""


@dataclass(frozen=True)
class DependenciesConfig:
    """Manually declared dependency edges and extra scan directories."""

    manual_edges: tuple[ManualEdge, ...] = ()
    extra_scan_dirs: tuple[str, ...] = ()


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
    names_in_use: dict[str, str]
    dependencies: DependenciesConfig
    references: ReferencesConfig
    manifest_dir: Path
