"""Project registration use-case.

Registers an existing project into workspace artifacts without regenerating
everything. Used for copy-pasted, imported, or manually created projects.

Classes
-------
RegistrationResult
    Outcome of registering a project.
ExecuteRegistrationResult
    Full outcome of registering and regenerating workspace artifacts.

Functions
---------
register_project
    Extract metadata from a project directory for registration.
apply_registration
    Return the manifest state needed to include a project in the workspace.
execute_registration
    Full registration use-case: inspect, update manifest, regenerate artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Callable

from ..domain.manifest import WorkspaceManifest
from ..domain.project import ProjectInventory, ProjectMetadata
from ..exceptions import WorkspaceError
from .generation import GenerationResult
from .protocols import GenerationServices, MetadataExtractor


@dataclass(frozen=True)
class RegistrationResult:
    """Outcome of registering a project.

    Attributes
    ----------
    manifest : WorkspaceManifest
        Workspace manifest after registration (may be unchanged).
    project : ProjectMetadata
        Metadata of the registered project.
    manifest_updated : bool
        Whether the manifest was modified to include the project.
    """

    manifest: WorkspaceManifest
    project: ProjectMetadata
    manifest_updated: bool


@dataclass(frozen=True)
class ExecuteRegistrationResult:
    """Full outcome of registering and regenerating workspace artifacts.

    Attributes
    ----------
    manifest : WorkspaceManifest
        Workspace manifest after registration.
    project : ProjectMetadata
        Metadata of the registered project.
    manifest_updated : bool
        Whether the manifest was modified to include the project.
    generated : tuple[GenerationResult, ...]
        Results of regenerating workspace artifacts.
    """

    manifest: WorkspaceManifest
    project: ProjectMetadata
    manifest_updated: bool
    generated: tuple[GenerationResult, ...]


def register_project(
    project_dir: Path,
    extractor: MetadataExtractor,
) -> ProjectMetadata:
    """Extract metadata from a project directory for registration.

    The caller (CLI adapter) is responsible for updating the workspace file,
    projects index, and dependency graph with the returned metadata.

    Parameters
    ----------
    project_dir : Path
        Absolute path to the project directory.
    extractor : MetadataExtractor
        Infrastructure extractor for project metadata.

    Returns
    -------
    ProjectMetadata
        Extracted project metadata.
    """
    if not project_dir.is_dir():
        raise FileNotFoundError(f"Project directory does not exist: {project_dir}")

    return extractor.extract(project_dir)


def apply_registration(
    manifest: WorkspaceManifest,
    inventory: ProjectInventory,
    project: ProjectMetadata,
) -> RegistrationResult:
    """Return the manifest state needed to include *project* in the workspace.

    Parameters
    ----------
    manifest : WorkspaceManifest
        Current workspace manifest.
    inventory : ProjectInventory
        Current project inventory.
    project : ProjectMetadata
        Project to register.

    Returns
    -------
    RegistrationResult
        Updated manifest and registration status.
    """
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


def execute_registration(
    manifest_path: Path,
    project_dir: Path,
    manifest: WorkspaceManifest,
    extractor: MetadataExtractor,
    discover: Callable[[WorkspaceManifest], ProjectInventory],
    build_context_and_generate: Callable[
        [WorkspaceManifest], tuple[ProjectInventory, tuple[GenerationResult, ...]]
    ],
    persist_manifest: Callable[[Path, WorkspaceManifest], None],
) -> ExecuteRegistrationResult:
    """Full registration use-case: inspect, update manifest, regenerate artifacts.

    Avoids building the full workspace context twice. If the project is already
    registered (its path is in the manifest's extra_paths), the manifest is
    used as-is. Otherwise, a discovery pass determines whether the manifest
    needs updating before the single context build.

    Parameters
    ----------
    manifest_path : Path
        Path to the manifest file on disk.
    project_dir : Path
        Path to the project directory to register.
    manifest : WorkspaceManifest
        Current workspace manifest.
    extractor : MetadataExtractor
        Infrastructure extractor for project metadata.
    discover : Callable[[WorkspaceManifest], ProjectInventory]
        Callable to discover projects from a manifest.
    build_context_and_generate : Callable[[WorkspaceManifest], tuple[ProjectInventory, tuple[GenerationResult, ...]]]
        Callable to build the workspace context and generate artifacts.
    persist_manifest : Callable[[Path, WorkspaceManifest], None]
        Callable to write the manifest to disk.

    Returns
    -------
    ExecuteRegistrationResult
        Full outcome including manifest update and generated artifacts.
    """
    project = register_project(project_dir.resolve(), extractor)
    resolved_project_path = project.path.resolve()
    extra_resolved = {
        (manifest.manifest_dir / ep).resolve() for ep in manifest.discovery.extra_paths
    }
    already_registered = resolved_project_path in extra_resolved

    if already_registered:
        _inventory, generated = build_context_and_generate(manifest)
        return ExecuteRegistrationResult(
            manifest=manifest,
            project=project,
            manifest_updated=False,
            generated=generated,
        )

    inventory = discover(manifest)
    registration = apply_registration(manifest, inventory, project)
    effective_manifest = registration.manifest
    if registration.manifest_updated:
        persist_manifest(manifest_path, effective_manifest)

    updated_inventory, generated = build_context_and_generate(effective_manifest)
    if resolved_project_path not in updated_inventory.by_path():
        raise WorkspaceError(
            f"Registered project at {project.path} is still not discoverable after updating the manifest."
        )

    return ExecuteRegistrationResult(
        manifest=effective_manifest,
        project=registration.project,
        manifest_updated=registration.manifest_updated,
        generated=generated,
    )
