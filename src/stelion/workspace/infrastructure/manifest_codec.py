"""Manifest parsing, defaulting, and rendering infrastructure."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml

from ..domain.manifest import (
    CanonicalMechanism,
    DependenciesConfig,
    DependencyGraphConfig,
    DiscoveryConfig,
    EcosystemDefaults,
    GenerateConfig,
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
from ..exceptions import ManifestValidationError


def default_workspace_manifest(manifest_dir: Path, github_user: str = "") -> WorkspaceManifest:
    """Create the canonical default manifest model for a new workspace."""
    return WorkspaceManifest(
        discovery=DiscoveryConfig(
            scan_dirs=("../",),
            exclude=(manifest_dir.name,),
            markers=("pyproject.toml",),
            include_self=True,
            self_name=manifest_dir.name,
        ),
        template=TemplateConfig(source="../keystone"),
        defaults=EcosystemDefaults(github_user=github_user),
        vscode=VSCodeConfig(),
        generate=GenerateConfig(
            shared_environment=SharedEnvironmentConfig(name=manifest_dir.name),
        ),
        integrations=IntegrationsConfig(),
        names_in_use={},
        dependencies=DependenciesConfig(),
        references=ReferencesConfig(),
        manifest_dir=manifest_dir,
    )


def parse_workspace_manifest(raw: Mapping[str, Any], manifest_dir: Path) -> WorkspaceManifest:
    """Parse a raw manifest mapping into a typed workspace manifest."""
    raw = _to_mapping(raw, "manifest")
    _validate_manifest_mapping(raw)
    defaults = default_workspace_manifest(manifest_dir)

    discovery_raw = _get_section(raw, "discovery", required=True)
    template_raw = _get_section(raw, "template")
    defaults_raw = _get_section(raw, "defaults")
    vscode_raw = _get_section(raw, "vscode")
    generate_raw = _get_section(raw, "generate", required=True)
    integrations_raw = _get_section(raw, "integrations")
    dependencies_raw = _get_section(raw, "dependencies")
    references_raw = _get_section(raw, "references")

    try:
        return WorkspaceManifest(
            discovery=DiscoveryConfig(
                scan_dirs=_coalesce_tuple(discovery_raw.get("scan_dirs"), defaults.discovery.scan_dirs, "discovery.scan_dirs"),
                exclude=_coalesce_tuple(discovery_raw.get("exclude"), defaults.discovery.exclude, "discovery.exclude"),
                markers=_coalesce_tuple(discovery_raw.get("markers"), defaults.discovery.markers, "discovery.markers"),
                extra_paths=_coalesce_tuple(discovery_raw.get("extra_paths"), defaults.discovery.extra_paths, "discovery.extra_paths"),
                include_self=_coalesce_bool(discovery_raw.get("include_self"), defaults.discovery.include_self, "discovery.include_self"),
                self_name=_coalesce_str(discovery_raw.get("self_name"), defaults.discovery.self_name, "discovery.self_name"),
            ),
            template=TemplateConfig(
                source=_coalesce_str(template_raw.get("source"), defaults.template.source, "template.source"),
                delimiters=_coalesce_delimiters(
                    template_raw.get("delimiters"),
                    defaults.template.delimiters,
                    "template.delimiters",
                ),
                exclude_patterns=_coalesce_tuple(
                    template_raw.get("exclude_patterns"),
                    defaults.template.exclude_patterns,
                    "template.exclude_patterns",
                ),
                renames=_coalesce_str_map(
                    template_raw.get("renames"),
                    dict(defaults.template.renames),
                    "template.renames",
                ),
            ),
            defaults=EcosystemDefaults(
                github_user=_coalesce_str(defaults_raw.get("github_user"), defaults.defaults.github_user, "defaults.github_user"),
                channel_name=_coalesce_str(defaults_raw.get("channel_name"), defaults.defaults.channel_name, "defaults.channel_name"),
                license=_coalesce_str(defaults_raw.get("license"), defaults.defaults.license, "defaults.license"),
            ),
            vscode=VSCodeConfig(
                source=_coalesce_str(vscode_raw.get("source"), defaults.vscode.source, "vscode.source"),
                settings_overrides=_coalesce_mapping(
                    vscode_raw.get("settings_overrides"),
                    defaults.vscode.settings_overrides,
                    "vscode.settings_overrides",
                ),
                extensions_overrides=_coalesce_tuple(
                    vscode_raw.get("extensions_overrides"),
                    defaults.vscode.extensions_overrides,
                    "vscode.extensions_overrides",
                ),
            ),
            generate=_parse_generate_config(generate_raw, defaults.generate),
            integrations=_parse_integrations_config(integrations_raw),
            names_in_use=_coalesce_str_map(raw.get("names_in_use"), {}, "names_in_use"),
            dependencies=_parse_dependencies_config(dependencies_raw),
            references=ReferencesConfig(
                expected=_coalesce_tuple(references_raw.get("expected"), (), "references.expected"),
            ),
            manifest_dir=manifest_dir,
        )
    except ValueError as exc:
        raise ManifestValidationError(str(exc)) from exc


def manifest_to_dict(manifest: WorkspaceManifest) -> dict[str, Any]:
    """Serialize a manifest model into YAML-safe primitives."""
    return {
        "discovery": {
            "scan_dirs": list(manifest.discovery.scan_dirs),
            "exclude": list(manifest.discovery.exclude),
            "markers": list(manifest.discovery.markers),
            "extra_paths": list(manifest.discovery.extra_paths),
            "include_self": manifest.discovery.include_self,
            "self_name": manifest.discovery.self_name,
        },
        "template": {
            "source": manifest.template.source,
            "delimiters": list(manifest.template.delimiters),
            "exclude_patterns": list(manifest.template.exclude_patterns),
            "renames": dict(manifest.template.renames),
        },
        "defaults": {
            "github_user": manifest.defaults.github_user,
            "channel_name": manifest.defaults.channel_name,
            "license": manifest.defaults.license,
        },
        "vscode": {
            "source": manifest.vscode.source,
            "settings_overrides": dict(manifest.vscode.settings_overrides),
            "extensions_overrides": list(manifest.vscode.extensions_overrides),
        },
        "generate": {
            "workspace_file": {"output": manifest.generate.workspace_file.output},
            "projects_registry": {"output": manifest.generate.projects_registry.output},
            "dependency_graph": {"output": manifest.generate.dependency_graph.output},
            "shared_environment": {
                "output": manifest.generate.shared_environment.output,
                "name": manifest.generate.shared_environment.name,
            },
        },
        "names_in_use": dict(manifest.names_in_use),
        "integrations": {
            "canonical_mechanisms": {
                name: {"type": value.type, "mechanism": value.mechanism}
                for name, value in manifest.integrations.canonical_mechanisms.items()
            },
            "reference_implementations": [
                {"module": ref.module, "description": ref.description}
                for ref in manifest.integrations.reference_implementations
            ],
        },
        "dependencies": {
            "manual_edges": [
                {
                    "dependent": edge.dependent,
                    "dependency": edge.dependency,
                    "mechanism": edge.mechanism,
                    "detail": edge.detail,
                }
                for edge in manifest.dependencies.manual_edges
            ],
            "scan_paths": list(manifest.dependencies.scan_paths),
            "superproject_paths": list(manifest.dependencies.superproject_paths),
        },
        "references": {"expected": list(manifest.references.expected)},
    }


def render_manifest(manifest: WorkspaceManifest) -> str:
    """Render a workspace manifest to YAML."""
    return yaml.safe_dump(manifest_to_dict(manifest), sort_keys=False)


_KNOWN_TOP_LEVEL_KEYS = frozenset(
    {
        "discovery",
        "template",
        "defaults",
        "vscode",
        "generate",
        "integrations",
        "names_in_use",
        "dependencies",
        "references",
    }
)


def _validate_manifest_mapping(raw: Mapping[str, Any]) -> None:
    unknown = set(raw) - _KNOWN_TOP_LEVEL_KEYS
    if unknown:
        raise ManifestValidationError(
            f"Unknown top-level manifest key(s): {', '.join(sorted(unknown))}."
        )

    discovery = _get_section(raw, "discovery", required=True)
    if "scan_dirs" not in discovery:
        raise ManifestValidationError(
            "Section 'discovery' is missing required field 'scan_dirs'."
        )
    _ensure_known_keys(
        discovery,
        {"scan_dirs", "exclude", "markers", "extra_paths", "include_self", "self_name"},
        "discovery",
    )
    _ensure_known_keys(
        _get_section(raw, "template"),
        {"source", "delimiters", "exclude_patterns", "renames"},
        "template",
    )
    _ensure_known_keys(
        _get_section(raw, "defaults"),
        {"github_user", "channel_name", "license"},
        "defaults",
    )
    _ensure_known_keys(
        _get_section(raw, "vscode"),
        {"source", "settings_overrides", "extensions_overrides"},
        "vscode",
    )
    _ensure_known_keys(
        _get_section(raw, "generate", required=True),
        {"workspace_file", "projects_registry", "dependency_graph", "shared_environment"},
        "generate",
    )
    _ensure_known_keys(
        _get_section(raw, "integrations"),
        {"canonical_mechanisms", "reference_implementations"},
        "integrations",
    )
    _ensure_known_keys(
        _get_section(raw, "dependencies"),
        {"manual_edges", "scan_paths", "superproject_paths", "extra_scan_dirs"},
        "dependencies",
    )
    _ensure_known_keys(
        _get_section(raw, "references"),
        {"expected"},
        "references",
    )


def _parse_generate_config(raw: Mapping[str, Any], defaults: GenerateConfig) -> GenerateConfig:
    wf = _get_nested_section(raw, "workspace_file", "generate")
    pr = _get_nested_section(raw, "projects_registry", "generate")
    dg = _get_nested_section(raw, "dependency_graph", "generate")
    se = _get_nested_section(raw, "shared_environment", "generate")
    return GenerateConfig(
        workspace_file=WorkspaceFileConfig(
            output=_coalesce_str(wf.get("output"), defaults.workspace_file.output, "generate.workspace_file.output")
        ),
        projects_registry=ProjectsRegistryConfig(
            output=_coalesce_str(pr.get("output"), defaults.projects_registry.output, "generate.projects_registry.output")
        ),
        dependency_graph=DependencyGraphConfig(
            output=_coalesce_str(dg.get("output"), defaults.dependency_graph.output, "generate.dependency_graph.output")
        ),
        shared_environment=SharedEnvironmentConfig(
            output=_coalesce_str(se.get("output"), defaults.shared_environment.output, "generate.shared_environment.output"),
            name=_coalesce_str(se.get("name"), defaults.shared_environment.name, "generate.shared_environment.name"),
        ),
    )


def _parse_integrations_config(raw: Mapping[str, Any]) -> IntegrationsConfig:
    mechanisms_raw = _get_nested_section(raw, "canonical_mechanisms", "integrations")
    refs_raw = raw.get("reference_implementations", ())
    if refs_raw is None:
        refs_raw = ()
    if not isinstance(refs_raw, (list, tuple)):
        raise ManifestValidationError("Section 'integrations.reference_implementations' must be a sequence.")
    mechanisms: dict[str, CanonicalMechanism] = {}
    for name, value in mechanisms_raw.items():
        value_map = _to_mapping(value, f"integrations.canonical_mechanisms.{name}")
        _ensure_known_keys(value_map, {"type", "mechanism"}, f"integrations.canonical_mechanisms.{name}")
        mechanisms[name] = CanonicalMechanism(
            type=_coalesce_str(value_map.get("type"), "", f"integrations.canonical_mechanisms.{name}.type"),
            mechanism=_coalesce_str(
                value_map.get("mechanism"),
                "",
                f"integrations.canonical_mechanisms.{name}.mechanism",
            ),
        )
    refs = []
    for index, item in enumerate(refs_raw):
        item_map = _to_mapping(item, f"integrations.reference_implementations[{index}]")
        _ensure_known_keys(
            item_map,
            {"module", "description"},
            f"integrations.reference_implementations[{index}]",
        )
        refs.append(
            ReferenceImplementation(
                module=_coalesce_str(item_map.get("module"), "", f"integrations.reference_implementations[{index}].module"),
                description=_coalesce_str(
                    item_map.get("description"),
                    "",
                    f"integrations.reference_implementations[{index}].description",
                ),
            )
        )
    return IntegrationsConfig(
        canonical_mechanisms=mechanisms,
        reference_implementations=tuple(refs),
    )


def _parse_dependencies_config(raw: Mapping[str, Any]) -> DependenciesConfig:
    edges_raw = raw.get("manual_edges", ())
    if edges_raw is None:
        edges_raw = ()
    if not isinstance(edges_raw, (list, tuple)):
        raise ManifestValidationError("Section 'dependencies.manual_edges' must be a sequence.")
    edges = []
    for index, item in enumerate(edges_raw):
        item_map = _to_mapping(item, f"dependencies.manual_edges[{index}]")
        _ensure_known_keys(
            item_map,
            {"dependent", "dependency", "mechanism", "detail"},
            f"dependencies.manual_edges[{index}]",
        )
        edges.append(
            ManualEdge(
                dependent=_coalesce_str(item_map.get("dependent"), "", f"dependencies.manual_edges[{index}].dependent"),
                dependency=_coalesce_str(item_map.get("dependency"), "", f"dependencies.manual_edges[{index}].dependency"),
                mechanism=_coalesce_str(item_map.get("mechanism"), "", f"dependencies.manual_edges[{index}].mechanism"),
                detail=_coalesce_str(item_map.get("detail"), "", f"dependencies.manual_edges[{index}].detail"),
            )
        )

    legacy_extra = _coalesce_tuple(raw.get("extra_scan_dirs"), (), "dependencies.extra_scan_dirs")
    return DependenciesConfig(
        manual_edges=tuple(edges),
        scan_paths=_coalesce_tuple(raw.get("scan_paths"), legacy_extra, "dependencies.scan_paths"),
        superproject_paths=_coalesce_tuple(
            raw.get("superproject_paths"),
            legacy_extra,
            "dependencies.superproject_paths",
        ),
    )


def _get_section(raw: Mapping[str, Any], name: str, required: bool = False) -> Mapping[str, Any]:
    if name not in raw:
        if required:
            raise ManifestValidationError(f"Manifest is missing required section '{name}'.")
        return {}
    return _to_mapping(raw[name], name)


def _get_nested_section(raw: Mapping[str, Any], key: str, section: str) -> Mapping[str, Any]:
    value = raw.get(key, {})
    return _to_mapping(value, f"{section}.{key}")


def _ensure_known_keys(raw: Mapping[str, Any], allowed: set[str], section: str) -> None:
    unknown = set(raw) - allowed
    if unknown:
        raise ManifestValidationError(
            f"Unknown key(s) in section '{section}': {', '.join(sorted(unknown))}."
        )


def _to_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ManifestValidationError(f"Section '{label}' must be a mapping.")
    return value


def _to_str_tuple(value: Any, label: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise ManifestValidationError(f"Section '{label}' must be a sequence of strings.")
    result = tuple(value)
    if not all(isinstance(item, str) for item in result):
        raise ManifestValidationError(f"Section '{label}' must contain only strings.")
    return result


def _to_str_map(value: Any, label: str) -> dict[str, str]:
    mapping = _to_mapping(value, label)
    result: dict[str, str] = {}
    for key, item in mapping.items():
        if not isinstance(key, str) or not isinstance(item, str):
            raise ManifestValidationError(f"Section '{label}' must map strings to strings.")
        result[key] = item
    return result


def _coalesce_tuple(value: Any, default: tuple[str, ...], label: str) -> tuple[str, ...]:
    if value is None:
        return default
    return _to_str_tuple(value, label)


def _coalesce_delimiters(
    value: Any,
    default: tuple[str, str],
    label: str,
) -> tuple[str, str]:
    delimiters = _coalesce_tuple(value, default, label)
    if len(delimiters) != 2:
        raise ManifestValidationError(f"Section '{label}' must contain exactly two strings.")
    return delimiters[0], delimiters[1]


def _coalesce_bool(value: Any, default: bool, label: str) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise ManifestValidationError(f"Field '{label}' must be a boolean.")
    return value


def _coalesce_str(value: Any, default: str, label: str) -> str:
    if value is None:
        return default
    if not isinstance(value, str):
        raise ManifestValidationError(f"Field '{label}' must be a string.")
    return value


def _coalesce_mapping(value: Any, default: Mapping[str, Any], label: str) -> dict[str, Any]:
    if value is None:
        return dict(default)
    return dict(_to_mapping(value, label))


def _coalesce_str_map(value: Any, default: Mapping[str, str], label: str) -> dict[str, str]:
    if value is None:
        return dict(default)
    return _to_str_map(value, label)
