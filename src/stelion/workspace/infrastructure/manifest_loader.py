"""Parse stelion.yml into a WorkspaceManifest."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from ..domain.manifest import (
    CanonicalMechanism,
    DependenciesConfig,
    DiscoveryConfig,
    EcosystemDefaults,
    GenerateConfig,
    DependencyGraphConfig,
    IntegrationsConfig,
    ManualEdge,
    ProjectsRegistryConfig,
    ReferenceImplementation,
    ReferencesConfig,
    SharedEnvironmentConfig,
    TemplateConfig,
    VSCodeConfig,
    WorkspaceFileConfig,
    WorkspaceManifest,
)

logger = logging.getLogger(__name__)


def load_manifest(path: Path) -> WorkspaceManifest:
    """Load and validate a workspace manifest from a YAML file.

    Parameters
    ----------
    path
        Absolute or relative path to ``stelion.yml``.

    Returns
    -------
    WorkspaceManifest
        Fully parsed and typed manifest.

    Raises
    ------
    FileNotFoundError
        If the manifest file does not exist.
    ValueError
        If required fields are missing or invalid.
    """
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")

    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    _validate_manifest(raw)

    manifest_dir = path.parent

    return WorkspaceManifest(
        discovery=_parse_discovery(raw.get("discovery", {})),
        template=_parse_template(raw.get("template", {})),
        defaults=_parse_defaults(raw.get("defaults", {})),
        vscode=_parse_vscode(raw.get("vscode", {})),
        generate=_parse_generate(raw.get("generate", {})),
        integrations=_parse_integrations(raw.get("integrations", {})),
        names_in_use=raw.get("names_in_use", {}),
        dependencies=_parse_dependencies(raw.get("dependencies", {})),
        references=_parse_references(raw.get("references", {})),
        manifest_dir=manifest_dir,
    )


_KNOWN_TOP_LEVEL_KEYS = frozenset({
    "discovery",
    "template",
    "defaults",
    "vscode",
    "generate",
    "integrations",
    "names_in_use",
    "dependencies",
    "references",
})


def _validate_manifest(raw: dict) -> None:
    """Validate required fields and warn on unknown top-level keys.

    Raises
    ------
    ValueError
        If a required section is missing or has an invalid type.
    """
    # Check required sections
    if "discovery" not in raw:
        raise ValueError("Manifest is missing required section 'discovery'.")
    discovery = raw["discovery"]
    if not isinstance(discovery, dict):
        raise ValueError("Section 'discovery' must be a mapping.")
    if "scan_dirs" not in discovery:
        raise ValueError(
            "Section 'discovery' is missing required field 'scan_dirs'."
        )

    if "generate" not in raw:
        raise ValueError("Manifest is missing required section 'generate'.")
    if not isinstance(raw["generate"], dict):
        raise ValueError("Section 'generate' must be a mapping.")

    # Warn on unknown top-level keys
    unknown = set(raw) - _KNOWN_TOP_LEVEL_KEYS
    if unknown:
        logger.warning(
            "Unknown top-level keys in manifest: %s",
            ", ".join(sorted(unknown)),
        )


def _parse_discovery(raw: dict) -> DiscoveryConfig:
    return DiscoveryConfig(
        scan_dirs=tuple(raw.get("scan_dirs", ["../"])),
        exclude=tuple(raw.get("exclude", ["dev"])),
        markers=tuple(raw.get("markers", ["pyproject.toml"])),
        extra_paths=tuple(raw.get("extra_paths", [])),
        include_self=raw.get("include_self", True),
        self_name=raw.get("self_name", "dev"),
    )


def _parse_template(raw: dict) -> TemplateConfig:
    delimiters = raw.get("delimiters", ["{{ ", " }}"])
    return TemplateConfig(
        source=raw.get("source", ""),
        delimiters=(delimiters[0], delimiters[1]) if len(delimiters) >= 2 else ("{{ ", " }}"),
        exclude_patterns=tuple(raw.get("exclude_patterns", [])),
        renames=raw.get("renames", {}),
    )


def _parse_defaults(raw: dict) -> EcosystemDefaults:
    return EcosystemDefaults(
        github_user=raw.get("github_user", ""),
        channel_name=raw.get("channel_name", ""),
        license=raw.get("license", "GPL-3.0-or-later"),
    )


def _parse_vscode(raw: dict) -> VSCodeConfig:
    return VSCodeConfig(
        source=raw.get("source", "defaults"),
        settings_overrides=raw.get("settings_overrides", {}),
        extensions_overrides=tuple(raw.get("extensions_overrides", [])),
    )


def _parse_generate(raw: dict) -> GenerateConfig:
    wf = raw.get("workspace_file", {})
    pr = raw.get("projects_registry", {})
    dg = raw.get("dependency_graph", {})
    se = raw.get("shared_environment", {})
    return GenerateConfig(
        workspace_file=WorkspaceFileConfig(output=wf.get("output", "dev-repos.code-workspace")),
        projects_registry=ProjectsRegistryConfig(
            output=pr.get("output", "projects.yml"),
        ),
        dependency_graph=DependencyGraphConfig(
            output=dg.get("output", "dependencies.yml"),
        ),
        shared_environment=SharedEnvironmentConfig(
            output=se.get("output", "environment.yml"),
            name=se.get("name", "dev"),
        ),
    )


def _parse_integrations(raw: dict) -> IntegrationsConfig:
    mechanisms = {}
    for name, val in raw.get("canonical_mechanisms", {}).items():
        mechanisms[name] = CanonicalMechanism(
            type=val.get("type", ""),
            mechanism=val.get("mechanism", ""),
        )
    refs = tuple(
        ReferenceImplementation(
            module=r.get("module", ""),
            description=r.get("description", ""),
        )
        for r in raw.get("reference_implementations", [])
    )
    return IntegrationsConfig(
        canonical_mechanisms=mechanisms,
        reference_implementations=refs,
    )


def _parse_dependencies(raw: dict) -> DependenciesConfig:
    edges = tuple(
        ManualEdge(
            dependent=e.get("dependent", ""),
            dependency=e.get("dependency", ""),
            mechanism=e.get("mechanism", ""),
            detail=e.get("detail", ""),
        )
        for e in raw.get("manual_edges", [])
    )
    return DependenciesConfig(
        manual_edges=edges,
        extra_scan_dirs=tuple(raw.get("extra_scan_dirs", [])),
    )


def _parse_references(raw: dict) -> ReferencesConfig:
    return ReferencesConfig(expected=tuple(raw.get("expected", [])))
