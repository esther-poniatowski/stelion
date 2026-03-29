from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from stelion.workspace.application.bootstrap import (
    BootstrapServices,
    WorkspaceBootstrapRequest,
    bootstrap_workspace_project,
    plan_bootstrap_request,
)
from stelion.workspace.application.generation import GenerationArtifact, generate_all
from stelion.workspace.composition import create_services, register_workspace_project, resolve_manifest
from stelion.workspace.domain.dependency import DependencyGraph
from stelion.workspace.domain.environment import EnvironmentSpec, merge_environments
from stelion.workspace.domain.manifest import EcosystemDefaults, TemplateConfig
from stelion.workspace.domain.project import MetadataStatus, ProjectInventory, ProjectMetadata
from stelion.workspace.exceptions import ManifestValidationError
from stelion.workspace.infrastructure.environment_parser import (
    CondaEnvironmentReader,
    INVALID_ENVIRONMENT_MARKER,
)
from stelion.workspace.infrastructure.file_ops import LocalFileReader, LocalFileWriter, SHA256Hasher
from stelion.workspace.infrastructure.manifest_codec import (
    default_workspace_manifest,
    manifest_to_dict,
    parse_workspace_manifest,
    render_manifest,
)
from stelion.workspace.infrastructure.pyproject_parser import (
    INVALID_PYPROJECT_MARKER,
    PyprojectExtractor,
)
from stelion.workspace.infrastructure.renderers.yaml import render_environment, render_projects_yaml
from stelion.workspace.infrastructure.template_engine import substitute_in_file


def test_workspace_bootstrap_request_is_planned_from_manifest_dir(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "workspace"
    manifest_dir.mkdir()
    request = WorkspaceBootstrapRequest(
        manifest_dir=manifest_dir,
        name="example",
        description="desc",
        template=TemplateConfig(source="../template"),
        defaults=EcosystemDefaults(github_user="user"),
        discovery_scan_dirs=("../projects",),
        dry_run=True,
    )

    planned = plan_bootstrap_request(request)

    assert planned.template_source == (manifest_dir / "../template").resolve()
    assert planned.target_dir == (manifest_dir / "../projects/example").resolve()


def test_workspace_bootstrap_uses_explicit_destination_root(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "workspace"
    manifest_dir.mkdir()
    request = WorkspaceBootstrapRequest(
        manifest_dir=manifest_dir,
        name="example",
        description="desc",
        template=TemplateConfig(source="../template"),
        defaults=EcosystemDefaults(github_user="user"),
        discovery_scan_dirs=("../projects", "../scratch"),
        destination_root="../scratch",
        dry_run=True,
    )

    planned = plan_bootstrap_request(request)

    assert planned.target_dir == (manifest_dir / "../scratch/example").resolve()


def test_workspace_bootstrap_honors_custom_template_delimiters(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "workspace"
    template_dir = tmp_path / "template"
    scan_root = tmp_path / "projects"
    manifest_dir.mkdir()
    template_dir.mkdir()
    scan_root.mkdir()
    (template_dir / "README.md").write_text("<< project_name >>\n", encoding="utf-8")

    request = WorkspaceBootstrapRequest(
        manifest_dir=manifest_dir,
        name="sample",
        description="desc",
        template=TemplateConfig(source="../template", delimiters=("<< ", " >>")),
        defaults=EcosystemDefaults(github_user="user"),
        discovery_scan_dirs=("../projects",),
        initialize_git=False,
    )
    services = BootstrapServices(
        read_git_identity=lambda: ("Ada Lovelace", "ada@example.com"),
        copy_template=lambda source, target: (
            target.mkdir(),
            (target / "README.md").write_text(
                (source / "README.md").read_text(encoding="utf-8"),
                encoding="utf-8",
            ),
        )[-1],
        substitute_directory=lambda root, bindings, delimiters, patterns: substitute_in_file(
            root / "README.md",
            bindings,
            delimiters,
            patterns,
        ),
        rename_paths=lambda root, renames, bindings, delimiters: 0,
        init_repository=lambda target: None,
    )

    result = bootstrap_workspace_project(request, services)

    assert result.target_dir == (scan_root / "sample").resolve()
    assert (scan_root / "sample" / "README.md").read_text(encoding="utf-8") == "sample\n"


def test_workspace_manifest_parses_through_infrastructure_codec(tmp_path: Path) -> None:
    manifest = parse_workspace_manifest(
        {
            "discovery": {"scan_dirs": ["../projects"]},
            "generate": {},
            "template": {"renames": {"src/template": "src/{{ project_name }}"}},
            "vscode": {"settings_overrides": {"files.exclude": {"__pycache__": True}}},
            "names_in_use": {"old": "new"},
            "dependencies": {"scan_paths": ["../vendors"], "superproject_paths": ["../apps"]},
        },
        tmp_path,
    )

    assert manifest.discovery.scan_dirs == ("../projects",)
    assert manifest.template.renames["src/template"] == "src/{{ project_name }}"
    assert manifest.vscode.settings_overrides["files.exclude"] == {"__pycache__": True}
    assert manifest.names_in_use["old"] == "new"
    assert manifest.dependencies.scan_paths == ("../vendors",)
    assert manifest.dependencies.superproject_paths == ("../apps",)


def test_workspace_manifest_rejects_unknown_keys_at_codec_boundary(tmp_path: Path) -> None:
    with pytest.raises(ManifestValidationError, match="Unknown key"):
        parse_workspace_manifest(
            {
                "discovery": {"scan_dirs": ["../projects"]},
                "generate": {},
                "template": {"unknown": "value"},
            },
            tmp_path,
        )


def test_default_manifest_stays_serializable_through_codec(tmp_path: Path) -> None:
    manifest = default_workspace_manifest(tmp_path, github_user="eresther")
    raw = manifest_to_dict(manifest)

    assert raw["defaults"]["github_user"] == "eresther"
    assert raw["discovery"]["scan_dirs"] == ["../"]


def test_legacy_extra_scan_dirs_populates_new_dependency_fields(tmp_path: Path) -> None:
    manifest = parse_workspace_manifest(
        {
            "discovery": {"scan_dirs": ["../projects"]},
            "generate": {},
            "dependencies": {"extra_scan_dirs": ["../legacy"]},
        },
        tmp_path,
    )

    assert manifest.dependencies.scan_paths == ("../legacy",)
    assert manifest.dependencies.superproject_paths == ("../legacy",)


def test_pyproject_parser_marks_invalid_toml_with_explicit_status(tmp_path: Path) -> None:
    project_dir = tmp_path / "broken"
    project_dir.mkdir()
    (project_dir / "pyproject.toml").write_text("[project\nname='broken'\n", encoding="utf-8")

    metadata = PyprojectExtractor().extract(project_dir)

    assert metadata.status == MetadataStatus.INVALID_PYPROJECT
    assert metadata.version == INVALID_PYPROJECT_MARKER
    assert metadata.description == INVALID_PYPROJECT_MARKER
    assert "invalid pyproject.toml" in metadata.issue


def test_projects_yaml_surfaces_metadata_markers(tmp_path: Path) -> None:
    project = ProjectMetadata(
        name="broken",
        path=tmp_path / "broken",
        version=INVALID_PYPROJECT_MARKER,
        status=MetadataStatus.INVALID_PYPROJECT,
        issue="broken: invalid pyproject.toml",
    )

    rendered = render_projects_yaml(ProjectInventory((project,)), tmp_path)

    assert "status: invalid_pyproject" in rendered
    assert f"version: {INVALID_PYPROJECT_MARKER}" in rendered
    assert "issue: 'broken: invalid pyproject.toml'" in rendered or "issue: broken: invalid pyproject.toml" in rendered


def test_environment_reader_carries_invalid_yaml_issue_without_raising(tmp_path: Path) -> None:
    project_dir = tmp_path / "broken"
    project_dir.mkdir()
    (project_dir / "environment.yml").write_text("dependencies: [\n", encoding="utf-8")

    spec = CondaEnvironmentReader().read(project_dir)
    assert spec is not None
    assert spec.name == INVALID_ENVIRONMENT_MARKER
    assert spec.dependencies == ()
    assert spec.issues

    merged = merge_environments([spec], "dev")
    rendered = render_environment(merged)
    assert "# WARNING: broken: invalid environment.yml" in rendered


def test_targeted_generation_respects_selected_artifact(tmp_path: Path) -> None:
    manifest = default_workspace_manifest(tmp_path)
    inventory = ProjectInventory(
        projects=(ProjectMetadata(name="alpha", path=tmp_path / "alpha"),)
    )
    graph = DependencyGraph()
    environment = EnvironmentSpec(name="dev")

    results = generate_all(
        manifest=manifest,
        inventory=inventory,
        graph=graph,
        environment=environment,
        render_workspace_file=lambda *_: "workspace\n",
        render_projects_yaml=lambda *_: "projects\n",
        render_dependency_yaml=lambda *_: "dependencies\n",
        render_environment=lambda *_: "name: dev\n",
        writer=LocalFileWriter(),
        reader=LocalFileReader(),
        hasher=SHA256Hasher(),
        selected_targets=(GenerationArtifact.PROJECTS,),
    )

    assert [result.artifact for result in results] == [GenerationArtifact.PROJECTS]
    assert (tmp_path / "projects.yml").exists()
    assert not (tmp_path / "dependencies.yml").exists()


def test_register_workspace_project_persists_manifest_and_updates_artifacts(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "workspace"
    projects_dir = tmp_path / "projects"
    external_dir = tmp_path / "external" / "manual"
    manifest_dir.mkdir()
    projects_dir.mkdir()
    _write_project(projects_dir / "alpha", "alpha")
    _write_project(external_dir, "manual")

    manifest = default_workspace_manifest(manifest_dir)
    manifest = replace(
        manifest,
        discovery=replace(manifest.discovery, scan_dirs=("../projects",)),
    )
    manifest_path = manifest_dir / "stelion.yml"
    manifest_path.write_text(render_manifest(manifest), encoding="utf-8")

    result = register_workspace_project(manifest_path, external_dir, create_services())
    reloaded = resolve_manifest(manifest_path)

    assert result.manifest_updated is True
    assert "../external/manual" in reloaded.discovery.extra_paths
    assert any(generated.path.name == "projects.yml" for generated in result.generated)
    assert "manual:" in (manifest_dir / "projects.yml").read_text(encoding="utf-8")


def _write_project(project_dir: Path, name: str) -> None:
    """Create a minimal Python project for discovery tests."""
    project_dir.mkdir(parents=True)
    (project_dir / "pyproject.toml").write_text(
        f"[project]\nname = '{name}'\nversion = '0.1.0'\n",
        encoding="utf-8",
    )
