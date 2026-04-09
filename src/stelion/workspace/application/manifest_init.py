"""Default manifest generation use-case.

Classes
-------
ManifestInitServices
    Injected collaborators for initializing a new workspace manifest.
ManifestInitResult
    Result of creating a default workspace manifest.

Functions
---------
initialize_default_manifest
    Build and optionally persist a default manifest for a new workspace.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from ..domain.manifest import WorkspaceManifest
from ..domain.project import ProjectInventory
from .discovery import discover_projects
from .protocols import MetadataExtractor


@dataclass(frozen=True)
class ManifestInitServices:
    """Injected collaborators for initializing a new workspace manifest.

    Attributes
    ----------
    read_git_identity : Callable[[], tuple[str, str]]
        Read the git user name and email.
    build_default_manifest : Callable[[Path, str], WorkspaceManifest]
        Build a default manifest for the given directory.
    render_manifest : Callable[[WorkspaceManifest], str]
        Render a manifest to YAML text.
    write_manifest : Callable[[Path, str], None]
        Write manifest content to disk.
    """

    read_git_identity: Callable[[], tuple[str, str]]
    build_default_manifest: Callable[[Path, str], WorkspaceManifest]
    render_manifest: Callable[[WorkspaceManifest], str]
    write_manifest: Callable[[Path, str], None]


@dataclass(frozen=True)
class ManifestInitResult:
    """Result of creating a default workspace manifest.

    Attributes
    ----------
    manifest_path : Path
        Absolute path to the manifest file.
    manifest : WorkspaceManifest
        The generated workspace manifest.
    inventory : ProjectInventory
        Projects discovered during initialization.
    content : str
        Rendered YAML content of the manifest.
    written : bool
        Whether the manifest was written to disk.
    """

    manifest_path: Path
    manifest: WorkspaceManifest
    inventory: ProjectInventory
    content: str
    written: bool

    @property
    def project_names(self) -> tuple[str, ...]:
        """Alphabetical list of discovered project names.

        Returns
        -------
        tuple[str, ...]
            Sorted project names from the inventory.
        """
        return tuple(sorted(project.name for project in self.inventory.projects))


def initialize_default_manifest(
    manifest_path: Path,
    extractor: MetadataExtractor,
    services: ManifestInitServices,
    *,
    dry_run: bool = False,
) -> ManifestInitResult:
    """Build and optionally persist a default manifest for a new workspace.

    Parameters
    ----------
    manifest_path : Path
        Target path for the manifest file.
    extractor : MetadataExtractor
        Infrastructure extractor for project metadata.
    services : ManifestInitServices
        Injected collaborators.
    dry_run : bool
        If True, skip writing the manifest to disk.

    Returns
    -------
    ManifestInitResult
        Result containing the manifest, inventory, and write status.
    """
    manifest_path = manifest_path.resolve()
    manifest_dir = manifest_path.parent
    github_user, _ = services.read_git_identity()
    manifest = services.build_default_manifest(manifest_dir, github_user=github_user)
    inventory = discover_projects(manifest.discovery, extractor, manifest_dir)
    content = services.render_manifest(manifest)
    if not dry_run:
        services.write_manifest(manifest_path, content)
    return ManifestInitResult(
        manifest_path=manifest_path,
        manifest=manifest,
        inventory=inventory,
        content=content,
        written=not dry_run,
    )
