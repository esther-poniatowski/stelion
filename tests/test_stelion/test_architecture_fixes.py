from __future__ import annotations

from pathlib import Path

import pytest

from stelion.workspace.application.bootstrap import (
    BootstrapServices,
    WorkspaceBootstrapRequest,
    bootstrap_workspace_project,
    plan_bootstrap_request,
)
from stelion.workspace.domain.manifest import (
    EcosystemDefaults,
    TemplateConfig,
    WorkspaceManifest,
    default_workspace_manifest,
)
from stelion.workspace.exceptions import ManifestValidationError
from stelion.workspace.infrastructure.pyproject_parser import PyprojectExtractor
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


def test_workspace_bootstrap_moves_orchestration_out_of_cli(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "workspace"
    template_dir = tmp_path / "template"
    scan_root = tmp_path / "projects"
    manifest_dir.mkdir()
    template_dir.mkdir()
    scan_root.mkdir()
    (template_dir / "README.md").write_text("{{ project_name }}\n", encoding="utf-8")

    events: list[str] = []
    request = WorkspaceBootstrapRequest(
        manifest_dir=manifest_dir,
        name="sample",
        description="desc",
        template=TemplateConfig(source="../template"),
        defaults=EcosystemDefaults(github_user="user"),
        discovery_scan_dirs=("../projects",),
        initialize_git=True,
    )
    services = BootstrapServices(
        read_git_identity=lambda: ("Ada Lovelace", "ada@example.com"),
        copy_template=lambda source, target: (
            events.append(f"copy:{source.name}->{target.name}"),
            target.mkdir(),
            (target / "README.md").write_text((source / "README.md").read_text(encoding="utf-8"), encoding="utf-8"),
        )[-1],
        substitute_directory=lambda root, bindings, patterns: (
            events.append(f"substitute:{root.name}:{len(patterns)}"),
            substitute_in_file(root / "README.md", bindings, patterns),
        )[-1],
        rename_paths=lambda root, renames, bindings: events.append(f"rename:{root.name}") or 0,
        init_repository=lambda target: events.append(f"git:{target.name}"),
    )

    result = bootstrap_workspace_project(request, services)

    assert result.target_dir == (scan_root / "sample").resolve()
    assert "copy:template->sample" in events
    assert "substitute:sample:0" in events
    assert "git:sample" in events
    assert (scan_root / "sample" / "README.md").read_text(encoding="utf-8") == "sample\n"


def test_workspace_manifest_parses_from_single_domain_boundary(tmp_path: Path) -> None:
    manifest = WorkspaceManifest.from_dict(
        {
            "discovery": {"scan_dirs": ["../projects"]},
            "generate": {},
            "template": {"renames": {"src/template": "src/{{ project_name }}"}},
            "vscode": {"settings_overrides": {"files.exclude": {"__pycache__": True}}},
            "names_in_use": {"old": "new"},
        },
        tmp_path,
    )

    assert manifest.discovery.scan_dirs == ("../projects",)
    assert manifest.template.renames["src/template"] == "src/{{ project_name }}"
    assert manifest.vscode.settings_overrides["files.exclude"] == {"__pycache__": True}
    assert manifest.names_in_use["old"] == "new"


def test_workspace_manifest_rejects_unknown_keys_at_domain_boundary(tmp_path: Path) -> None:
    with pytest.raises(ManifestValidationError, match="Unknown key"):
        WorkspaceManifest.from_dict(
            {
                "discovery": {"scan_dirs": ["../projects"]},
                "generate": {},
                "template": {"unknown": "value"},
            },
            tmp_path,
        )


def test_default_manifest_stays_serializable_from_domain_model(tmp_path: Path) -> None:
    manifest = default_workspace_manifest(tmp_path, github_user="eresther")

    raw = manifest.to_dict() if hasattr(manifest, "to_dict") else None
    if raw is None:
        from stelion.workspace.domain.manifest import manifest_to_dict

        raw = manifest_to_dict(manifest)

    assert raw["defaults"]["github_user"] == "eresther"
    assert raw["discovery"]["scan_dirs"] == ["../"]


def test_pyproject_parser_fails_closed_on_invalid_toml(tmp_path: Path) -> None:
    project_dir = tmp_path / "broken"
    project_dir.mkdir()
    (project_dir / "pyproject.toml").write_text("[project\nname='broken'\n", encoding="utf-8")

    with pytest.raises(Exception):
        PyprojectExtractor().extract(project_dir)


def test_environment_reader_fails_closed_on_invalid_yaml(tmp_path: Path) -> None:
    pytest.importorskip("yaml")
    from stelion.workspace.infrastructure.environment_parser import CondaEnvironmentReader

    project_dir = tmp_path / "broken"
    project_dir.mkdir()
    (project_dir / "environment.yml").write_text("dependencies: [\n", encoding="utf-8")

    with pytest.raises(Exception):
        CondaEnvironmentReader().read(project_dir)
