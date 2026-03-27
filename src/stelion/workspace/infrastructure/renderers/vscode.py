"""Render VS Code .code-workspace files (JSON with comments)."""

from __future__ import annotations

import json
from pathlib import Path

from ...domain.manifest import WorkspaceManifest
from ...domain.project import ProjectInventory
from ..data_loader import StelionDataLoader


def render_workspace_file(manifest: WorkspaceManifest, inventory: ProjectInventory) -> str:
    """Generate a VS Code multi-root workspace file.

    Combines discovered projects as folder entries with VS Code settings
    and extension recommendations from the manifest's VS Code config.
    """
    # Build folder list: discovered projects sorted alphabetically, self last
    folders = []
    for project in sorted(inventory.projects, key=lambda p: p.name):
        rel = _relative_path(manifest.manifest_dir, project.path)
        folders.append({"name": project.name, "path": rel})

    if manifest.discovery.include_self:
        folders.append({"name": manifest.discovery.self_name, "path": "."})

    # Load VS Code settings from source
    settings = _load_settings(manifest)
    extensions = _load_extensions(manifest)

    # Build the workspace structure
    workspace = {
        "folders": folders,
        "settings": settings,
        "extensions": {"recommendations": extensions},
    }

    return json.dumps(workspace, indent="\t", ensure_ascii=False) + "\n"


def _relative_path(manifest_dir: Path, project_path: Path) -> str:
    """Compute a relative path from the manifest directory to the project."""
    try:
        rel = project_path.relative_to(manifest_dir)
        return str(rel)
    except ValueError:
        # Not under the same parent; use ../ paths
        try:
            rel = project_path.relative_to(manifest_dir.parent)
            return f"../{rel}"
        except ValueError:
            return str(project_path)


def _load_settings(manifest: WorkspaceManifest) -> dict:
    """Load VS Code settings from the configured source."""
    if manifest.vscode.uses_defaults():
        loader = StelionDataLoader()
        settings = loader.load_json("vscode/settings.json")
    else:
        source_path = manifest.manifest_dir / manifest.vscode.source
        with open(source_path, encoding="utf-8") as f:
            settings = json.load(f)

    # Merge overrides
    settings.update(manifest.vscode.settings_overrides)
    return settings


def _load_extensions(manifest: WorkspaceManifest) -> list[str]:
    """Load VS Code extension recommendations from the configured source."""
    if manifest.vscode.uses_defaults():
        loader = StelionDataLoader()
        extensions = loader.load_json("vscode/extensions.json")
    else:
        extensions = []

    # Append overrides
    extensions.extend(manifest.vscode.extensions_overrides)
    return extensions
