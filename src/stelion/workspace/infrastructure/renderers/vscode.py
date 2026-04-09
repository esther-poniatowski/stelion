"""Render VS Code .code-workspace files (JSON with comments).

Classes
-------
VSCodeWorkspaceFileRenderer
    Render a VS Code workspace file using injected package data loading.

Functions
---------
_relative_path
    Compute a relative path from the manifest directory to the project.
"""

from __future__ import annotations

import json
from pathlib import Path

from ...application.protocols import FileReader, PackageDataLoader
from ...domain.manifest import WorkspaceManifest
from ...domain.project import ProjectInventory


class VSCodeWorkspaceFileRenderer:
    """Render a VS Code workspace file using injected package data loading.

    Parameters
    ----------
    loader : PackageDataLoader
        Loader for bundled package data files.
    reader : FileReader | None
        Optional file reader for custom settings sources.
    """

    def __init__(
        self,
        loader: PackageDataLoader,
        reader: FileReader | None = None,
    ) -> None:
        self._loader = loader
        self._reader = reader

    def __call__(self, manifest: WorkspaceManifest, inventory: ProjectInventory) -> str:
        """Generate a VS Code multi-root workspace file.

        Parameters
        ----------
        manifest : WorkspaceManifest
            Workspace configuration.
        inventory : ProjectInventory
            Discovered projects.

        Returns
        -------
        str
            JSON workspace file content.
        """
        folders = []
        for project in sorted(inventory.projects, key=lambda p: p.name):
            rel = _relative_path(manifest.manifest_dir, project.path)
            folders.append({"name": project.name, "path": rel})

        if manifest.discovery.include_self:
            folders.append({"name": manifest.discovery.self_name, "path": "."})

        workspace = {
            "folders": folders,
            "settings": self._load_settings(manifest),
            "extensions": {"recommendations": self._load_extensions(manifest)},
        }
        return json.dumps(workspace, indent="\t", ensure_ascii=False) + "\n"

    def _load_settings(self, manifest: WorkspaceManifest) -> dict:
        """Load VS Code settings from the configured source.

        Parameters
        ----------
        manifest : WorkspaceManifest
            Workspace configuration with VS Code settings source.

        Returns
        -------
        dict
            Merged settings dictionary.
        """
        if manifest.vscode.uses_defaults():
            settings = self._loader.load_json("vscode/settings.json")
        else:
            source_path = manifest.manifest_dir / manifest.vscode.source
            if self._reader is not None:
                settings = json.loads(self._reader.read(source_path))
            else:
                with open(source_path, encoding="utf-8") as f:
                    settings = json.load(f)

        settings.update(manifest.vscode.settings_overrides)
        return settings

    def _load_extensions(self, manifest: WorkspaceManifest) -> list[str]:
        """Load VS Code extension recommendations from the configured source.

        Parameters
        ----------
        manifest : WorkspaceManifest
            Workspace configuration with VS Code extension overrides.

        Returns
        -------
        list[str]
            Combined extension recommendation identifiers.
        """
        if manifest.vscode.uses_defaults():
            extensions = self._loader.load_json("vscode/extensions.json")
        else:
            extensions = []

        extensions.extend(manifest.vscode.extensions_overrides)
        return extensions


def _relative_path(manifest_dir: Path, project_path: Path) -> str:
    """Compute a relative path from the manifest directory to the project.

    Parameters
    ----------
    manifest_dir : Path
        Directory containing the workspace manifest.
    project_path : Path
        Absolute path to the project directory.

    Returns
    -------
    str
        Relative path string suitable for a workspace file entry.
    """
    try:
        rel = project_path.relative_to(manifest_dir)
        return str(rel)
    except ValueError:
        try:
            rel = project_path.relative_to(manifest_dir.parent)
            return f"../{rel}"
        except ValueError:
            return str(project_path)
