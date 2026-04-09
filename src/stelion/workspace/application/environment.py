"""Shared environment construction use-case."""

from __future__ import annotations

from ..domain.environment import EnvironmentSpec, merge_environments
from ..domain.manifest import WorkspaceManifest
from ..domain.project import ProjectInventory
from .protocols import EnvironmentReader


def build_shared_environment(
    manifest: WorkspaceManifest,
    inventory: ProjectInventory,
    env_reader: EnvironmentReader,
    env_specs: dict[str, EnvironmentSpec | None] | None = None,
) -> EnvironmentSpec:
    """Merge all project environments into a single shared spec.

    When *env_specs* is provided, uses pre-read specs instead of calling
    *env_reader* per project. Otherwise reads each project's
    ``environment.yml`` via *env_reader*.

    Parameters
    ----------
    manifest : WorkspaceManifest
        Workspace manifest with shared environment configuration.
    inventory : ProjectInventory
        All discovered projects.
    env_reader : EnvironmentReader
        Infrastructure reader for Conda environment specs.
    env_specs : dict[str, EnvironmentSpec | None] | None
        Pre-read environment specs keyed by project name.

    Returns
    -------
    EnvironmentSpec
        Merged shared environment specification.
    """
    specs: list[EnvironmentSpec] = []
    for project in inventory.projects:
        if env_specs is not None:
            spec = env_specs.get(project.name)
        else:
            spec = env_reader.read(project.path)
        if spec:
            specs.append(spec)
    return merge_environments(specs, manifest.generate.shared_environment.name)
