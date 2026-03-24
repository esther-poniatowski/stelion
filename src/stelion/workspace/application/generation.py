"""Workspace artifact generation use-cases."""

from __future__ import annotations

from dataclasses import dataclass
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
    ProjectsYamlRenderer,
    WorkspaceFileRenderer,
)


@dataclass(frozen=True)
class GenerationResult:
    """Outcome of generating a single file."""

    path: Path
    written: bool
    reason: str


@dataclass(frozen=True)
class GenerationTarget:
    """A single file to generate: its output path and a renderer callable."""

    path: Path
    render: Callable[[], str]


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
    """Build the ordered list of generation targets from manifest config."""
    return (
        GenerationTarget(
            path=manifest.manifest_dir / manifest.generate.workspace_file.output,
            render=lambda: render_workspace_file(manifest, inventory),
        ),
        GenerationTarget(
            path=manifest.manifest_dir / manifest.generate.projects_registry.output,
            render=lambda: render_projects_yaml(inventory, manifest.manifest_dir),
        ),
        GenerationTarget(
            path=manifest.manifest_dir / manifest.generate.dependency_graph.output,
            render=lambda: render_dependency_yaml(graph),
        ),
        GenerationTarget(
            path=manifest.manifest_dir / manifest.generate.shared_environment.output,
            render=lambda: render_environment(environment),
        ),
    )


def generate_all(
    manifest: WorkspaceManifest,
    inventory: ProjectInventory,
    graph: DependencyGraph,
    environment: EnvironmentSpec,
    render_workspace_file: WorkspaceFileRenderer,
    render_projects_yaml: ProjectsYamlRenderer,
    render_dependency_yaml: DependencyYamlRenderer,
    render_environment: EnvironmentRenderer,
    writer: FileWriter,
    reader: FileReader,
    hasher: FileHasher,
    force: bool = False,
) -> list[GenerationResult]:
    """Generate all enabled workspace artifacts.

    Each target is rendered to a string, compared with the existing file via
    content hash, and written only if the content differs (or ``force`` is set).
    """
    targets = _build_targets(
        manifest, inventory, graph, environment,
        render_workspace_file, render_projects_yaml,
        render_dependency_yaml, render_environment,
    )

    results: list[GenerationResult] = []
    for target in targets:
        content = target.render()
        if not force and target.path.exists():
            existing = reader.read(target.path)
            if hasher.hash_content(existing) == hasher.hash_content(content):
                results.append(GenerationResult(target.path, written=False, reason="current"))
                continue
        writer.write(target.path, content)
        reason = "created" if not target.path.exists() else "updated"
        results.append(GenerationResult(target.path, written=True, reason=reason))

    return results


def compute_drift(
    manifest: WorkspaceManifest,
    inventory: ProjectInventory,
    graph: DependencyGraph,
    environment: EnvironmentSpec,
    render_workspace_file: WorkspaceFileRenderer,
    render_projects_yaml: ProjectsYamlRenderer,
    render_dependency_yaml: DependencyYamlRenderer,
    render_environment: EnvironmentRenderer,
    reader: FileReader,
    hasher: FileHasher,
) -> DriftReport:
    """Compare generated content with existing files without writing."""
    targets = _build_targets(
        manifest, inventory, graph, environment,
        render_workspace_file, render_projects_yaml,
        render_dependency_yaml, render_environment,
    )

    entries: list[DriftEntry] = []
    for target in targets:
        expected = target.render()
        if not target.path.exists():
            entries.append(DriftEntry(target.path, FileStatus.MISSING))
            continue
        actual = reader.read(target.path)
        if hasher.hash_content(actual) == hasher.hash_content(expected):
            entries.append(DriftEntry(target.path, FileStatus.CURRENT))
        else:
            entries.append(DriftEntry(target.path, FileStatus.STALE))

    return DriftReport(entries=tuple(entries))
