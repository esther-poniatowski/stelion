"""Parse stelion.yml into a WorkspaceManifest."""

from __future__ import annotations

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
    ProjectsIndexConfig,
    ProposedIntegration,
    ReferenceImplementation,
    ReferencesConfig,
    SharedEnvironmentConfig,
    TemplateConfig,
    VSCodeConfig,
    WorkspaceFileConfig,
    WorkspaceManifest,
)


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

    manifest_dir = path.parent

    return WorkspaceManifest(
        discovery=_parse_discovery(raw.get("discovery", {})),
        template=_parse_template(raw.get("template", {})),
        defaults=_parse_defaults(raw.get("defaults", {})),
        vscode=_parse_vscode(raw.get("vscode", {})),
        generate=_parse_generate(raw.get("generate", {})),
        integrations=_parse_integrations(raw.get("integrations", {})),
        names_in_use=raw.get("names_in_use", {}),
        proposed_integrations=_parse_proposed(raw.get("proposed_integrations", [])),
        dependencies=_parse_dependencies(raw.get("dependencies", {})),
        references=_parse_references(raw.get("references", {})),
        manifest_dir=manifest_dir,
    )


def _parse_discovery(raw: dict) -> DiscoveryConfig:
    return DiscoveryConfig(
        scan_dirs=raw.get("scan_dirs", ["../"]),
        exclude=raw.get("exclude", ["dev"]),
        markers=raw.get("markers", ["pyproject.toml"]),
        include_self=raw.get("include_self", True),
        self_name=raw.get("self_name", "dev"),
    )


def _parse_template(raw: dict) -> TemplateConfig:
    delimiters = raw.get("delimiters", ["{{ ", " }}"])
    return TemplateConfig(
        source=raw.get("source", ""),
        delimiters=(delimiters[0], delimiters[1]) if len(delimiters) >= 2 else ("{{ ", " }}"),
        exclude_patterns=raw.get("exclude_patterns", []),
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
        extensions_overrides=raw.get("extensions_overrides", []),
    )


def _parse_generate(raw: dict) -> GenerateConfig:
    wf = raw.get("workspace_file", {})
    pi = raw.get("projects_index", {})
    dg = raw.get("dependency_graph", {})
    se = raw.get("shared_environment", {})
    return GenerateConfig(
        workspace_file=WorkspaceFileConfig(output=wf.get("output", "dev-repos.code-workspace")),
        projects_index=ProjectsIndexConfig(
            output=pi.get("output", "projects.md"),
            categories=pi.get("categories", {}),
        ),
        dependency_graph=DependencyGraphConfig(
            output_yaml=dg.get("output_yaml", "dependencies.yml"),
            output_md=dg.get("output_md", "dependencies.md"),
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
    refs = [
        ReferenceImplementation(
            module=r.get("module", ""),
            description=r.get("description", ""),
        )
        for r in raw.get("reference_implementations", [])
    ]
    return IntegrationsConfig(
        canonical_mechanisms=mechanisms,
        reference_implementations=refs,
    )


def _parse_proposed(raw: list) -> list[ProposedIntegration]:
    return [
        ProposedIntegration(
            consumer=item.get("consumer", ""),
            library=item.get("library", ""),
            integration=item.get("integration", ""),
            priority=item.get("priority", ""),
            notes=item.get("notes", ""),
        )
        for item in (raw or [])
    ]


def _parse_dependencies(raw: dict) -> DependenciesConfig:
    edges = [
        ManualEdge(
            dependent=e.get("dependent", ""),
            dependency=e.get("dependency", ""),
            mechanism=e.get("mechanism", ""),
            detail=e.get("detail", ""),
        )
        for e in raw.get("manual_edges", [])
    ]
    return DependenciesConfig(
        manual_edges=edges,
        extra_scan_dirs=raw.get("extra_scan_dirs", []),
    )


def _parse_references(raw: dict) -> ReferencesConfig:
    return ReferencesConfig(expected=raw.get("expected", []))
