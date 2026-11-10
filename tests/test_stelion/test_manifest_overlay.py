"""Tests for composing complete workspace manifests from consumer overlays."""

from __future__ import annotations

from pathlib import Path

import pytest

from stelion.workspace.application.manifest_overlay import merge_manifest_mappings
from stelion.workspace.composition import compose_workspace_manifest
from stelion.workspace.exceptions import ManifestValidationError
from stelion.workspace.infrastructure.manifest_codec import render_manifest
from stelion.workspace.infrastructure.manifest_loader import load_manifest


def test_nested_mappings_merge_while_sequences_replace() -> None:
    """An overlay must preserve unrelated defaults and replace whole sequences."""
    base = {
        "discovery": {
            "scan_dirs": ["../"],
            "exclude": ["dev"],
        },
        "defaults": {"license": "GPL-3.0-or-later"},
    }
    overlay = {
        "discovery": {"scan_dirs": ["../projects", "../research"]},
    }

    merged = merge_manifest_mappings(base, overlay)

    assert merged == {
        "discovery": {
            "scan_dirs": ["../projects", "../research"],
            "exclude": ["dev"],
        },
        "defaults": {"license": "GPL-3.0-or-later"},
    }
    assert base == {
        "discovery": {"scan_dirs": ["../"], "exclude": ["dev"]},
        "defaults": {"license": "GPL-3.0-or-later"},
    }


def test_empty_mapping_clears_a_default_mapping() -> None:
    """An explicit empty mapping must differ from an omitted inherited mapping."""
    base = {"vscode": {"settings_overrides": {"files.exclude": {"build": True}}}}
    overlay = {"vscode": {"settings_overrides": {}}}

    merged = merge_manifest_mappings(base, overlay)

    assert merged == {"vscode": {"settings_overrides": {}}}


def test_null_overlay_value_is_rejected_with_its_field_path() -> None:
    """Null must not acquire inconsistent meanings from field-level defaults."""
    with pytest.raises(ManifestValidationError, match="vscode.settings_overrides"):
        merge_manifest_mappings(
            {"vscode": {"settings_overrides": {}}},
            {"vscode": {"settings_overrides": None}},
        )


def test_compose_workspace_manifest_applies_typed_defaults(tmp_path: Path) -> None:
    """A minimal overlay must produce a complete typed manifest."""
    overlay_path = tmp_path / "consumer.overlay.yml"
    manifest_path = tmp_path / "workspace" / "stelion.yml"
    overlay_path.write_text(
        """
discovery:
  scan_dirs: [../projects]
template:
  renames:
    src/package_name: src/{{ package_name }}
defaults:
  github_user: example
""".lstrip(),
        encoding="utf-8",
    )

    manifest = compose_workspace_manifest(overlay_path, manifest_path.parent)

    assert manifest.discovery.scan_dirs == ("../projects",)
    assert manifest.discovery.exclude == ("workspace",)
    assert manifest.discovery.include_self is True
    assert manifest.template.source == ""
    assert manifest.template.renames["src/package_name"] == "src/{{ package_name }}"
    assert manifest.defaults.github_user == "example"
    assert manifest.defaults.license == ""
    assert manifest.generate.shared_environment.name == "workspace"
    assert manifest.manifest_dir == manifest_path.parent.resolve()


def test_rendered_overlay_round_trips_as_complete_manifest(tmp_path: Path) -> None:
    """The composed YAML must remain valid when loaded as a normal manifest."""
    overlay_path = tmp_path / "consumer.overlay.yml"
    manifest_path = tmp_path / "workspace" / "stelion.yml"
    overlay_path.write_text(
        "discovery:\n  scan_dirs: [../projects]\n",
        encoding="utf-8",
    )

    composed = compose_workspace_manifest(overlay_path, manifest_path.parent)
    manifest_path.parent.mkdir()
    manifest_path.write_text(render_manifest(composed), encoding="utf-8")

    loaded = load_manifest(manifest_path)

    assert loaded == composed


def test_unknown_overlay_key_is_rejected_before_output(tmp_path: Path) -> None:
    """Overlay composition must enforce the complete manifest schema."""
    overlay_path = tmp_path / "consumer.overlay.yml"
    overlay_path.write_text(
        "discovery:\n  scan_dirs: [../projects]\n  unexpected: true\n",
        encoding="utf-8",
    )

    with pytest.raises(ManifestValidationError, match="unexpected"):
        compose_workspace_manifest(overlay_path, tmp_path / "workspace")


@pytest.mark.parametrize(
    "content",
    ["null\n", "[]\n", "- not\n- a mapping\n", "discovery: [\n"],
)
def test_invalid_overlay_shape_or_yaml_is_rejected(
    tmp_path: Path, content: str
) -> None:
    """Malformed overlay input must fail at the loading boundary."""
    overlay_path = tmp_path / "consumer.overlay.yml"
    overlay_path.write_text(content, encoding="utf-8")

    with pytest.raises(ManifestValidationError):
        compose_workspace_manifest(overlay_path, tmp_path / "workspace")


def test_empty_mapping_is_a_valid_overlay(tmp_path: Path) -> None:
    """An explicit empty mapping must request the complete canonical manifest."""
    overlay_path = tmp_path / "consumer.overlay.yml"
    overlay_path.write_text("{}\n", encoding="utf-8")

    manifest = compose_workspace_manifest(
        overlay_path,
        tmp_path / "workspace",
    )

    assert manifest.discovery.scan_dirs == ("../",)
    assert manifest.discovery.self_name == "workspace"
