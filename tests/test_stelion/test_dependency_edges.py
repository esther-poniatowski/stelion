"""Tests for typed and evidenced inter-project dependency edges."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from stelion.workspace.application.graph import build_dependency_graph
from stelion.workspace.domain.dependency import (
    DependencyEdge,
    DependencyGraph,
    DependencyKind,
    DependencyMechanism,
    EdgeProvenance,
    manual_edge_to_dependency_edge,
)
from stelion.workspace.domain.environment import EnvironmentSpec
from stelion.workspace.domain.manifest import (
    CanonicalMechanism,
    IntegrationsConfig,
    ManualEdge,
)
from stelion.workspace.domain.project import ProjectInventory, ProjectMetadata
from stelion.workspace.exceptions import ManifestValidationError
from stelion.workspace.infrastructure.dependency_scanners import (
    _extract_editable_pip_edges,
)
from stelion.workspace.infrastructure.gitmodules_parser import scan_gitmodules
from stelion.workspace.infrastructure.manifest_codec import (
    default_workspace_manifest,
    manifest_to_dict,
    parse_workspace_manifest,
)
from stelion.workspace.infrastructure.renderers.yaml import render_dependency_yaml


def test_dependency_kind_vocabulary_covers_four_independent_roles() -> None:
    """The public kind vocabulary must preserve each required semantic role."""
    assert {kind.value for kind in DependencyKind} == {
        "runtime/package",
        "build/tooling",
        "content/submodule",
        "workspace/containment",
    }


def test_editable_pip_edge_records_complete_automatic_evidence() -> None:
    """An editable install must yield a required runtime edge with its declaration."""
    edges = _extract_editable_pip_edges(
        EnvironmentSpec(pip_dependencies=("-e ../morpha[dev]",)),
        "consumer",
        {"consumer", "morpha"},
    )

    assert edges == [
        DependencyEdge(
            dependent="consumer",
            dependency="morpha",
            kind=DependencyKind.RUNTIME_PACKAGE,
            mechanism=DependencyMechanism.EDITABLE_PIP,
            source_declaration="environment.yml:pip:-e ../morpha[dev]",
            version_policy="workspace_checkout",
            optional=False,
            provenance=EdgeProvenance.AUTOMATIC,
            integration_path="-e ../morpha[dev]",
        )
    ]


def test_git_submodule_edge_records_commit_policy_and_source(tmp_path: Path) -> None:
    """A submodule must retain its declaration, path and pinned-commit policy."""
    (tmp_path / ".gitmodules").write_text(
        '[submodule "vendor/scholia"]\n'
        "\tpath = vendor/scholia\n"
        "\turl = git@example.test:scholia.git\n",
        encoding="utf-8",
    )

    [edge] = scan_gitmodules(tmp_path, {"scholia"})

    assert edge.kind is DependencyKind.CONTENT_SUBMODULE
    assert edge.source_declaration == '.gitmodules:submodule "vendor/scholia"'
    assert edge.mechanism is DependencyMechanism.GIT_SUBMODULE
    assert edge.version_policy == "pinned_commit"
    assert edge.optional is False
    assert edge.provenance is EdgeProvenance.AUTOMATIC
    assert edge.integration_path == "vendor/scholia"


def test_graph_applies_semantic_override_and_adds_workspace_edges(
    tmp_path: Path,
) -> None:
    """Consumer policy may reclassify transport while containment stays automatic."""
    manifest_dir = tmp_path / "dev"
    manifest_dir.mkdir()
    alpha = ProjectMetadata(name="alpha", path=tmp_path / "alpha")
    ktisma = ProjectMetadata(name="ktisma", path=tmp_path / "ktisma")
    inventory = ProjectInventory(projects=(alpha, ktisma))
    manifest = default_workspace_manifest(manifest_dir)
    manifest = replace(
        manifest,
        integrations=IntegrationsConfig(
            canonical_mechanisms={
                "ktisma": CanonicalMechanism(
                    type="tool",
                    mechanism="git_submodule",
                    edge_kind="build/tooling",
                )
            }
        ),
    )

    class Scanner:
        def scan(
            self,
            project_name: str,
            project_dir: Path,
            all_project_names: set[str],
        ) -> list[DependencyEdge]:
            del project_dir, all_project_names
            if project_name != "alpha":
                return []
            return [
                DependencyEdge(
                    dependent="alpha",
                    dependency="ktisma",
                    kind=DependencyKind.CONTENT_SUBMODULE,
                    mechanism=DependencyMechanism.GIT_SUBMODULE,
                    source_declaration='.gitmodules:submodule "vendor/ktisma"',
                    version_policy="pinned_commit",
                    optional=False,
                    provenance=EdgeProvenance.AUTOMATIC,
                    integration_path="vendor/ktisma",
                )
            ]

    graph = build_dependency_graph(manifest, inventory, (Scanner(),))

    tool_edge = next(edge for edge in graph.detected if edge.dependent == "alpha")
    assert tool_edge.kind is DependencyKind.BUILD_TOOLING
    containment = [
        edge
        for edge in graph.detected
        if edge.kind is DependencyKind.WORKSPACE_CONTAINMENT
    ]
    assert {edge.dependency for edge in containment} == {"alpha", "ktisma"}
    assert all(edge.dependent == "dev" for edge in containment)
    assert all(
        edge.mechanism is DependencyMechanism.WORKSPACE_DISCOVERY
        for edge in containment
    )


def test_manual_edge_has_manual_provenance_and_validated_kind() -> None:
    """A manifest assertion must preserve optionality and manual provenance."""
    edge = manual_edge_to_dependency_edge(
        ManualEdge(
            dependent="workspace",
            dependency="external",
            kind="workspace/containment",
            mechanism="workspace_manifest",
            source_declaration="stelion.yml:dependencies.manual_edges[0]",
            version_policy="tracked_branch:main",
            optional=True,
            integration_path="../external",
        )
    )

    assert edge.kind is DependencyKind.WORKSPACE_CONTAINMENT
    assert edge.provenance is EdgeProvenance.MANUAL
    assert edge.optional is True


def test_manual_edge_replaces_automatic_edge_for_the_same_pair(tmp_path: Path) -> None:
    """An endpoint-specific assertion must replace its automatic default edge."""
    manifest_dir = tmp_path / "dev"
    manifest_dir.mkdir()
    consumers = (
        ProjectMetadata(name="analysis", path=tmp_path / "analysis"),
        ProjectMetadata(name="documentation", path=tmp_path / "documentation"),
    )
    manifest = replace(
        default_workspace_manifest(manifest_dir),
        dependencies=replace(
            default_workspace_manifest(manifest_dir).dependencies,
            manual_edges=(
                ManualEdge(
                    dependent="documentation",
                    dependency="scholia",
                    kind="content/submodule",
                    mechanism="git_submodule",
                    source_declaration="stelion.yml:dependencies.manual_edges[0]",
                    version_policy="pinned_commit",
                    optional=False,
                    integration_path="vendor/scholia",
                ),
            ),
        ),
    )

    class Scanner:
        def scan(
            self,
            project_name: str,
            project_dir: Path,
            all_project_names: set[str],
        ) -> list[DependencyEdge]:
            del project_dir, all_project_names
            return [
                DependencyEdge(
                    dependent=project_name,
                    dependency="scholia",
                    kind=DependencyKind.BUILD_TOOLING,
                    mechanism=DependencyMechanism.GIT_SUBMODULE,
                    source_declaration='.gitmodules:submodule "vendor/scholia"',
                    version_policy="pinned_commit",
                    optional=False,
                    provenance=EdgeProvenance.AUTOMATIC,
                    integration_path="vendor/scholia",
                )
            ]

    graph = build_dependency_graph(
        manifest,
        ProjectInventory(projects=consumers),
        (Scanner(),),
    )
    scholia_edges = [edge for edge in graph.all_edges if edge.dependency == "scholia"]

    assert [(edge.dependent, edge.kind, edge.provenance) for edge in scholia_edges] == [
        ("analysis", DependencyKind.BUILD_TOOLING, EdgeProvenance.AUTOMATIC),
        ("documentation", DependencyKind.CONTENT_SUBMODULE, EdgeProvenance.MANUAL),
    ]


def test_workspace_kind_and_mechanism_must_coincide() -> None:
    """Containment cannot be represented as package transport or conversely."""
    with pytest.raises(ValueError, match="Workspace-containment"):
        DependencyEdge(
            dependent="workspace",
            dependency="alpha",
            kind=DependencyKind.WORKSPACE_CONTAINMENT,
            mechanism=DependencyMechanism.GIT_SUBMODULE,
            source_declaration='.gitmodules:submodule "alpha"',
            version_policy="pinned_commit",
            optional=False,
            provenance=EdgeProvenance.AUTOMATIC,
        )
    with pytest.raises(ValueError, match="workspace mechanisms"):
        DependencyEdge(
            dependent="alpha",
            dependency="workspace",
            kind=DependencyKind.RUNTIME_PACKAGE,
            mechanism=DependencyMechanism.WORKSPACE_DISCOVERY,
            source_declaration="stelion.yml:discovery",
            version_policy="workspace_checkout",
            optional=False,
            provenance=EdgeProvenance.AUTOMATIC,
        )


def test_dependency_yaml_uses_one_complete_edge_schema() -> None:
    """Generated records must answer every required question without section context."""
    edge = DependencyEdge(
        dependent="alpha",
        dependency="morpha",
        kind=DependencyKind.RUNTIME_PACKAGE,
        mechanism=DependencyMechanism.EDITABLE_PIP,
        source_declaration="environment.yml:pip:-e ../morpha",
        version_policy="workspace_checkout",
        optional=False,
        provenance=EdgeProvenance.AUTOMATIC,
        integration_path="-e ../morpha",
    )

    rendered = render_dependency_yaml(DependencyGraph(detected=(edge,)))
    parsed = yaml.safe_load(rendered)

    assert list(parsed) == ["edges"]
    assert parsed["edges"] == [
        {
            "dependent": "alpha",
            "dependency": "morpha",
            "kind": "runtime/package",
            "source_declaration": "environment.yml:pip:-e ../morpha",
            "mechanism": "editable_pip",
            "version_policy": "workspace_checkout",
            "optional": False,
            "provenance": "automatic",
            "integration_path": "-e ../morpha",
        }
    ]


def test_legacy_manual_detail_is_migrated_to_canonical_fields(tmp_path: Path) -> None:
    """Existing manifests must load while the next render emits the stronger schema."""
    raw = manifest_to_dict(default_workspace_manifest(tmp_path))
    raw["dependencies"]["manual_edges"] = [
        {
            "dependent": "alpha",
            "dependency": "scholia",
            "mechanism": "git_submodule",
            "detail": "vendor/scholia",
        }
    ]

    manifest = parse_workspace_manifest(raw, tmp_path)
    [edge] = manifest.dependencies.manual_edges

    assert edge.kind == "content/submodule"
    assert edge.source_declaration == "stelion.yml:dependencies.manual_edges[0]"
    assert edge.version_policy == "pinned_commit"
    assert edge.optional is False
    assert edge.integration_path == "vendor/scholia"


def test_manual_edge_rejects_non_boolean_optionality(tmp_path: Path) -> None:
    """Optionality must remain a boolean at the manifest boundary."""
    raw = manifest_to_dict(default_workspace_manifest(tmp_path))
    raw["dependencies"] = {
        "manual_edges": [
            {
                "dependent": "alpha",
                "dependency": "morpha",
                "kind": "runtime/package",
                "mechanism": "editable_pip",
                "source_declaration": "pyproject.toml:project.dependencies",
                "version_policy": ">=1",
                "optional": "false",
            }
        ]
    }

    with pytest.raises(ManifestValidationError, match="must be a boolean"):
        parse_workspace_manifest(raw, tmp_path)


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("manual", "kind", "transport/submodule"),
        ("manual", "mechanism", "unknown_transport"),
        ("integration", "edge_kind", "transport/submodule"),
        ("integration", "mechanism", "unknown_transport"),
    ],
)
def test_manifest_rejects_unknown_edge_vocabulary(
    tmp_path: Path,
    section: str,
    field: str,
    value: str,
) -> None:
    """Unknown kinds and mechanisms must fail when the manifest is parsed."""
    raw = manifest_to_dict(default_workspace_manifest(tmp_path))
    if section == "integration":
        raw["integrations"]["canonical_mechanisms"] = {
            "morpha": {
                "type": "library",
                "mechanism": "editable_pip",
                field: value,
            }
        }
    else:
        raw["dependencies"]["manual_edges"] = [
            {
                "dependent": "alpha",
                "dependency": "morpha",
                "kind": "runtime/package",
                "mechanism": "editable_pip",
                "source_declaration": "environment.yml:pip:-e ../morpha",
                "version_policy": "workspace_checkout",
                field: value,
            }
        ]

    with pytest.raises(ManifestValidationError, match="must be one of"):
        parse_workspace_manifest(raw, tmp_path)
