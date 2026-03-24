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
) -> EnvironmentSpec:
    """Merge all project environments into a single shared spec.

    Reads each project's ``environment.yml`` via *env_reader*, then
    delegates to the domain ``merge_environments`` function.
    """
    specs: list[EnvironmentSpec] = []
    for project in inventory.projects:
        spec = env_reader.read(project.path)
        if spec:
            specs.append(spec)
    return merge_environments(specs, manifest.generate.shared_environment.name)
