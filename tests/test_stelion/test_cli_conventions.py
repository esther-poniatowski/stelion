"""Tests for the command-line conventions shared by the tools of the workspace.

Stelion resolves its root from ``--root``, then ``STELION_ROOT``, then the nearest ancestor holding
``stelion.yml`` (in ``config/tools/`` or at its level), then the current folder. It reads its
settings file from one of those two places, rejects two competing files, and resolves the paths
written in the file against the root. Former option names are rejected.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
from typer.testing import CliRunner

from stelion.cli import app
from stelion.workspace.exceptions import SettingsError
from stelion.workspace.infrastructure.manifest_codec import (
    default_workspace_manifest,
    render_manifest,
)
from stelion.workspace.infrastructure.manifest_loader import load_manifest
from stelion.workspace.infrastructure.settings_locator import locate_settings

runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_root_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STELION_ROOT", raising=False)


def _write_project(project_dir: Path, name: str) -> None:
    project_dir.mkdir(parents=True)
    (project_dir / "pyproject.toml").write_text(
        f"[project]\nname = '{name}'\nversion = '0.1.0'\n", encoding="utf-8"
    )


def _write_settings(root: Path, place: Path, scan_dirs: tuple[str, ...] = ("projects",)) -> Path:
    """Write a settings file at *place* below *root*, scanning *scan_dirs* from the root."""
    manifest = default_workspace_manifest(root)
    manifest = replace(manifest, discovery=replace(manifest.discovery, scan_dirs=scan_dirs))
    path = root / place
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_manifest(manifest), encoding="utf-8")
    return path


# --- Locating the settings ------------------------------------------------------------------------


def test_locate_finds_the_nearest_ancestor_holding_the_settings(tmp_path: Path) -> None:
    root = tmp_path / "hub"
    settings = _write_settings(root, Path("config/tools/stelion.yml"))
    nested = root / "a" / "b"
    nested.mkdir(parents=True)

    location = locate_settings(None, None, cwd=nested)

    assert location.root == root.resolve()
    assert location.settings_path == settings.resolve()


def test_locate_falls_back_to_the_current_folder_without_settings(tmp_path: Path) -> None:
    location = locate_settings(None, None, cwd=tmp_path)

    assert location.root == tmp_path.resolve()
    assert location.settings_path is None


def test_locate_rejects_two_competing_settings_files(tmp_path: Path) -> None:
    _write_settings(tmp_path, Path("config/tools/stelion.yml"))
    _write_settings(tmp_path, Path("stelion.yml"))

    with pytest.raises(SettingsError, match="Two settings files"):
        locate_settings(tmp_path, None, cwd=tmp_path)


def test_locate_rejects_an_absent_config(tmp_path: Path) -> None:
    with pytest.raises(SettingsError, match="not found"):
        locate_settings(None, Path("missing.yml"), cwd=tmp_path)


def test_paths_of_the_settings_resolve_against_the_root(tmp_path: Path) -> None:
    settings = _write_settings(tmp_path, Path("config/tools/stelion.yml"))

    manifest = load_manifest(settings, tmp_path)

    assert manifest.manifest_dir == tmp_path.resolve()


# --- Commands -------------------------------------------------------------------------------------


def test_sync_reads_settings_from_config_tools_and_writes_at_the_root(tmp_path: Path) -> None:
    _write_settings(tmp_path, Path("config/tools/stelion.yml"))
    _write_project(tmp_path / "projects" / "alpha", "alpha")

    result = runner.invoke(app, ["workspace", "sync", "-r", str(tmp_path)])

    assert result.exit_code == 0, result.output + result.stderr
    assert "alpha" in (tmp_path / "projects.yml").read_text(encoding="utf-8")
    assert not (tmp_path / "config" / "tools" / "projects.yml").exists()


def test_status_finds_the_root_from_a_subfolder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_settings(tmp_path, Path("stelion.yml"))
    _write_project(tmp_path / "projects" / "alpha", "alpha")
    assert runner.invoke(app, ["workspace", "sync", "--root", str(tmp_path)]).exit_code == 0
    monkeypatch.chdir(tmp_path / "projects" / "alpha")

    result = runner.invoke(app, ["workspace", "status"])

    assert result.exit_code == 0, result.output + result.stderr


def test_status_takes_the_root_from_the_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_settings(tmp_path, Path("stelion.yml"))
    _write_project(tmp_path / "projects" / "alpha", "alpha")
    monkeypatch.setenv("STELION_ROOT", str(tmp_path))

    result = runner.invoke(app, ["workspace", "status"])

    assert result.exit_code == 1
    assert "missing" in result.stderr


def test_two_competing_settings_files_stop_with_status_2(tmp_path: Path) -> None:
    _write_settings(tmp_path, Path("config/tools/stelion.yml"))
    _write_settings(tmp_path, Path("stelion.yml"))

    result = runner.invoke(app, ["workspace", "status", "--root", str(tmp_path)])

    assert result.exit_code == 2
    assert "Two settings files" in result.stderr


def test_an_absent_config_stops_with_status_2(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["workspace", "status", "-r", str(tmp_path), "-c", str(tmp_path / "missing.yml")]
    )

    assert result.exit_code == 2


def test_init_writes_the_settings_file_at_the_root(tmp_path: Path) -> None:
    result = runner.invoke(app, ["workspace", "init", "--root", str(tmp_path)])

    assert result.exit_code == 0, result.output + result.stderr
    assert (tmp_path / "stelion.yml").is_file()


@pytest.mark.parametrize(
    "arguments",
    [
        ["workspace", "status", "--manifest", "stelion.yml"],
        ["workspace", "status", "-m", "stelion.yml"],
        ["workspace", "sync", "--force"],
        ["workspace", "new", "alpha", "desc", "--destination", "../"],
        ["workspace", "render-manifest", "overlay.yml", "--manifest-dir", "."],
        ["compare", "tree", "--format", "table"],
        ["compare", "tree", "-f", "yaml"],
        ["submodule", "sync", "alpha", "--manifest", "stelion.yml"],
    ],
)
def test_former_option_names_are_rejected(arguments: list[str]) -> None:
    result = runner.invoke(app, arguments)

    assert result.exit_code == 2


def test_render_manifest_writes_to_the_standard_output_without_output(tmp_path: Path) -> None:
    overlay = tmp_path / "overlay.yml"
    overlay.write_text("{}\n", encoding="utf-8")
    hub = tmp_path / "hub"

    result = runner.invoke(app, ["workspace", "render-manifest", str(overlay), "-r", str(hub)])

    assert result.exit_code == 0, result.output + result.stderr
    assert "self_name: hub" in result.stdout
    assert not (tmp_path / "stelion.yml").exists()


def test_render_manifest_writes_the_output_with_defaults_of_the_root(tmp_path: Path) -> None:
    overlay = tmp_path / "overlay.yml"
    overlay.write_text("{}\n", encoding="utf-8")
    output = tmp_path / "stage" / "stelion.yml"

    result = runner.invoke(
        app,
        ["workspace", "render-manifest", str(overlay), "-o", str(output),
         "--root", str(tmp_path / "hub")],
    )

    assert result.exit_code == 0, result.output + result.stderr
    assert "self_name: hub" in output.read_text(encoding="utf-8")


# --- Confirmation of a rewrite of the settings file -----------------------------------------------


@pytest.fixture
def registration(tmp_path: Path) -> tuple[Path, Path, str]:
    """Return a root, an external project outside the scan dirs, and the original settings."""
    settings = _write_settings(tmp_path, Path("stelion.yml"))
    _write_project(tmp_path / "projects" / "alpha", "alpha")
    external = tmp_path / "external" / "manual"
    _write_project(external, "manual")
    return tmp_path, external, settings.read_text(encoding="utf-8")


def _terminal(monkeypatch: pytest.MonkeyPatch, is_terminal: bool) -> None:
    monkeypatch.setattr(
        "stelion.workspace.adapters._cli_common.stdin_is_terminal", lambda: is_terminal
    )


def test_register_stops_without_a_terminal_and_without_yes(
    registration: tuple[Path, Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, external, original = registration
    _terminal(monkeypatch, False)

    result = runner.invoke(app, ["workspace", "register", str(external), "-r", str(root)])

    assert result.exit_code == 2
    assert "--yes" in result.stderr
    assert (root / "stelion.yml").read_text(encoding="utf-8") == original


def test_register_rewrites_the_settings_with_yes(
    registration: tuple[Path, Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, external, original = registration
    _terminal(monkeypatch, False)

    result = runner.invoke(
        app, ["workspace", "register", str(external), "-r", str(root), "--yes"]
    )

    assert result.exit_code == 0, result.output + result.stderr
    assert "external/manual" in (root / "stelion.yml").read_text(encoding="utf-8")


def test_register_asks_on_a_terminal(
    registration: tuple[Path, Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, external, original = registration
    _terminal(monkeypatch, True)

    declined = runner.invoke(
        app, ["workspace", "register", str(external), "-r", str(root)], input="n\n"
    )

    assert declined.exit_code == 1
    assert (root / "stelion.yml").read_text(encoding="utf-8") == original
