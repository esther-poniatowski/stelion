"""Workspace artifact generation use-cases.

Classes
-------
GenerationResult
    Outcome of generating a single file.
GenerationArtifact
    Identifier for a generated workspace artifact.
ArtifactSpec
    Identity and output path of a workspace artifact.
GenerationTarget
    A single file to generate: its output path and a renderer callable.

Functions
---------
compute_artifact_specs
    Compute the output paths for all generation artifacts.
generate_all
    Generate all enabled workspace artifacts.
compute_drift
    Compare generated content with existing files without writing.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Callable

from ..domain.dependency import DependencyGraph
from ..domain.environment import EnvironmentSpec
from ..domain.manifest import WorkspaceManifest
from ..domain.project import ProjectInventory
from ..domain.status import DriftEntry, DriftReport, FileStatus
from .protocols import (
    DependencyYamlRenderer,
    EnvironmentRenderer,
    FileHasher,
    FileReader,
    FileWriter,
    GenerationServices,
    ProjectsYamlRenderer,
    WorkspaceFileRenderer,
)


@dataclass(frozen=True)
class GenerationResult:
    """Outcome of generating a single file.

    Attributes
    ----------
    artifact : GenerationArtifact
        Identifier of the generated artifact.
    path : Path
        Output path of the generated file.
    written : bool
        Whether the file was actually written to disk.
    reason : str
        Short label describing the outcome (e.g. ``"created"``, ``"current"``).
    """

    artifact: "GenerationArtifact"
    path: Path
    written: bool
    reason: str


class GenerationArtifact(StrEnum):
    """Identifier for a generated workspace artifact."""

    WORKSPACE_FILE = "workspace-file"
    PROJECTS = "projects"
    DEPENDENCIES = "dependencies"
    ENVIRONMENT = "environment"


@dataclass(frozen=True)
class ArtifactSpec:
    """Identity and output path of a workspace artifact.

    Attributes
    ----------
    artifact : GenerationArtifact
        Artifact identifier.
    output_path : Path
        Resolved output path for this artifact.
    """

    artifact: GenerationArtifact
    output_path: Path


@dataclass(frozen=True)
class GenerationTarget:
    """A single file to generate: its output path and a renderer callable.

    Attributes
    ----------
    artifact : GenerationArtifact
        Artifact identifier.
    path : Path
        Output path of the file to generate.
    render : Callable[[], str]
        Zero-argument callable that produces the file content.
    """

    artifact: GenerationArtifact
    path: Path
    render: Callable[[], str]


def compute_artifact_specs(
    manifest: WorkspaceManifest,
) -> dict[GenerationArtifact, ArtifactSpec]:
    """Compute the output paths for all generation artifacts.

    Parameters
    ----------
    manifest : WorkspaceManifest
        Workspace manifest configuration.

    Returns
    -------
    dict[GenerationArtifact, ArtifactSpec]
        Mapping from artifact identifier to its output spec.
    """
    return {
        GenerationArtifact.WORKSPACE_FILE: ArtifactSpec(
            artifact=GenerationArtifact.WORKSPACE_FILE,
            output_path=manifest.manifest_dir / manifest.generate.workspace_file.output,
        ),
        GenerationArtifact.PROJECTS: ArtifactSpec(
            artifact=GenerationArtifact.PROJECTS,
            output_path=manifest.manifest_dir / manifest.generate.projects_registry.output,
        ),
        GenerationArtifact.DEPENDENCIES: ArtifactSpec(
            artifact=GenerationArtifact.DEPENDENCIES,
            output_path=manifest.manifest_dir / manifest.generate.dependency_graph.output,
        ),
        GenerationArtifact.ENVIRONMENT: ArtifactSpec(
            artifact=GenerationArtifact.ENVIRONMENT,
            output_path=manifest.manifest_dir / manifest.generate.shared_environment.output,
        ),
    }


def _build_targets(
    manifest: WorkspaceManifest,
    inventory: ProjectInventory,
    graph: DependencyGraph,
    environment: EnvironmentSpec,
    render_workspace_file: WorkspaceFileRenderer,
    render_projects_yaml: ProjectsYamlRenderer,
    render_dependency_yaml: DependencyYamlRenderer,
    render_environment: EnvironmentRenderer,
) -> tuple[GenerationTarget, ...]:
    """Build the ordered list of generation targets from manifest config.

    Parameters
    ----------
    manifest : WorkspaceManifest
        Workspace manifest configuration.
    inventory : ProjectInventory
        All discovered projects.
    graph : DependencyGraph
        Project dependency graph.
    environment : EnvironmentSpec
        Merged shared environment specification.
    render_workspace_file : WorkspaceFileRenderer
        Renderer for the VS Code workspace file.
    render_projects_yaml : ProjectsYamlRenderer
        Renderer for the projects registry YAML.
    render_dependency_yaml : DependencyYamlRenderer
        Renderer for the dependency graph YAML.
    render_environment : EnvironmentRenderer
        Renderer for the shared Conda environment YAML.

    Returns
    -------
    tuple[GenerationTarget, ...]
        Ordered generation targets.
    """
    specs = compute_artifact_specs(manifest)
    return (
        GenerationTarget(
            artifact=GenerationArtifact.WORKSPACE_FILE,
            path=specs[GenerationArtifact.WORKSPACE_FILE].output_path,
            render=lambda: render_workspace_file(manifest, inventory),
        ),
        GenerationTarget(
            artifact=GenerationArtifact.PROJECTS,
            path=specs[GenerationArtifact.PROJECTS].output_path,
            render=lambda: render_projects_yaml(inventory, manifest.manifest_dir),
        ),
        GenerationTarget(
            artifact=GenerationArtifact.DEPENDENCIES,
            path=specs[GenerationArtifact.DEPENDENCIES].output_path,
            render=lambda: render_dependency_yaml(graph),
        ),
        GenerationTarget(
            artifact=GenerationArtifact.ENVIRONMENT,
            path=specs[GenerationArtifact.ENVIRONMENT].output_path,
            render=lambda: render_environment(environment),
        ),
    )


def generate_all(
    manifest: WorkspaceManifest,
    inventory: ProjectInventory,
    graph: DependencyGraph,
    environment: EnvironmentSpec,
    services: GenerationServices,
    force: bool = False,
    selected_targets: tuple[GenerationArtifact, ...] = (),
) -> list[GenerationResult]:
    """Generate all enabled workspace artifacts.

    Each target is rendered to a string, compared with the existing file via
    content hash, and written only if the content differs (or ``force`` is set).

    Parameters
    ----------
    manifest : WorkspaceManifest
        Workspace manifest configuration.
    inventory : ProjectInventory
        All discovered projects.
    graph : DependencyGraph
        Project dependency graph.
    environment : EnvironmentSpec
        Merged shared environment specification.
    services : GenerationServices
        Bundled infrastructure services.
    force : bool
        If True, write all files regardless of content hash.
    selected_targets : tuple[GenerationArtifact, ...]
        Subset of artifacts to generate; empty means all.

    Returns
    -------
    list[GenerationResult]
        One result per artifact indicating whether it was written.
    """
    targets = _build_targets(
        manifest, inventory, graph, environment,
        services.render_workspace_file, services.render_projects_yaml,
        services.render_dependency_yaml, services.render_environment,
    )

    selected = _select_targets(targets, selected_targets)
    results: list[GenerationResult] = []
    for target in selected:
        content = target.render()
        existed = target.path.exists()
        if not force and target.path.exists():
            existing = services.reader.read(target.path)
            if services.hasher.hash_content(existing) == services.hasher.hash_content(content):
                results.append(
                    GenerationResult(
                        artifact=target.artifact,
                        path=target.path,
                        written=False,
                        reason="current",
                    )
                )
                continue
        services.writer.write(target.path, content)
        reason = "created" if not existed else "updated"
        results.append(
            GenerationResult(
                artifact=target.artifact,
                path=target.path,
                written=True,
                reason=reason,
            )
        )

    return results


def compute_drift(
    manifest: WorkspaceManifest,
    inventory: ProjectInventory,
    graph: DependencyGraph,
    environment: EnvironmentSpec,
    services: GenerationServices,
    selected_targets: tuple[GenerationArtifact, ...] = (),
) -> DriftReport:
    """Compare generated content with existing files without writing.

    Parameters
    ----------
    manifest : WorkspaceManifest
        Workspace manifest configuration.
    inventory : ProjectInventory
        All discovered projects.
    graph : DependencyGraph
        Project dependency graph.
    environment : EnvironmentSpec
        Merged shared environment specification.
    services : GenerationServices
        Bundled infrastructure services.
    selected_targets : tuple[GenerationArtifact, ...]
        Subset of artifacts to check; empty means all.

    Returns
    -------
    DriftReport
        Per-artifact drift status.
    """
    targets = _build_targets(
        manifest, inventory, graph, environment,
        services.render_workspace_file, services.render_projects_yaml,
        services.render_dependency_yaml, services.render_environment,
    )

    selected = _select_targets(targets, selected_targets)
    entries: list[DriftEntry] = []
    for target in selected:
        expected = target.render()
        if not target.path.exists():
            entries.append(DriftEntry(target.path, FileStatus.MISSING))
            continue
        actual = services.reader.read(target.path)
        if services.hasher.hash_content(actual) == services.hasher.hash_content(expected):
            entries.append(DriftEntry(target.path, FileStatus.CURRENT))
        else:
            entries.append(DriftEntry(target.path, FileStatus.STALE))

    return DriftReport(entries=tuple(entries))


def _select_targets(
    targets: tuple[GenerationTarget, ...],
    selected_targets: tuple[GenerationArtifact, ...],
) -> tuple[GenerationTarget, ...]:
    """Return either all targets or the caller-selected subset.

    Parameters
    ----------
    targets : tuple[GenerationTarget, ...]
        All available generation targets.
    selected_targets : tuple[GenerationArtifact, ...]
        Subset to keep; empty means all.

    Returns
    -------
    tuple[GenerationTarget, ...]
        Filtered generation targets.
    """
    if not selected_targets:
        return targets
    wanted = set(selected_targets)
    return tuple(target for target in targets if target.artifact in wanted)
