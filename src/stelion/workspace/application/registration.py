"""Project registration use-case.

Registers an existing project into workspace artifacts without regenerating
everything. Used for copy-pasted, imported, or manually created projects.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from ..domain.manifest import WorkspaceManifest
from ..domain.project import ProjectInventory, ProjectMetadata
from ..exceptions import WorkspaceError
from .protocols import MetadataExtractor


@dataclass(frozen=True)
class RegistrationResult:
    """Outcome of registering a project."""

    manifest: WorkspaceManifest
    project: ProjectMetadata
    manifest_updated: bool


def register_project(
    project_dir: Path,
    extractor: MetadataExtractor,
) -> ProjectMetadata:
    """Extract metadata from a project directory for registration.

    The caller (CLI adapter) is responsible for updating the workspace file,
    projects index, and dependency graph with the returned metadata.
    """
    if not project_dir.is_dir():
        raise FileNotFoundError(f"Project directory does not exist: {project_dir}")

    return extractor.extract(project_dir)


def apply_registration(
    manifest: WorkspaceManifest,
    inventory: ProjectInventory,
    project: ProjectMetadata,
) -> RegistrationResult:
    """Return the manifest state needed to include *project* in the workspace."""
    existing = inventory.by_name().get(project.name)
    if existing is not None and existing.path.resolve() != project.path.resolve():
        raise WorkspaceError(
            f"Project name '{project.name}' is already registered at {existing.path}."
        )

    if project.path.resolve() in inventory.by_path():
        return RegistrationResult(
            manifest=manifest,
            project=project,
            manifest_updated=False,
        )

    extra_path = os.path.relpath(project.path.resolve(), manifest.manifest_dir)
    updated_manifest = manifest.with_added_extra_path(extra_path)
    return RegistrationResult(
        manifest=updated_manifest,
        project=project,
        manifest_updated=updated_manifest != manifest,
    )
