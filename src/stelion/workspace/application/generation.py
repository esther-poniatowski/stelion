"""Workspace artifact generation use-cases."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..domain.dependency import DependencyGraph
from ..domain.environment import EnvironmentSpec
from ..domain.manifest import WorkspaceManifest
from ..domain.project import ProjectInventory
from ..domain.status import DriftEntry, DriftReport, FileStatus
from .protocols import FileHasher, FileReader, FileWriter


@dataclass(frozen=True)
class GenerationResult:
    """Outcome of generating a single file."""

    path: Path
    written: bool
    reason: str


def generate_all(
    manifest: WorkspaceManifest,
    inventory: ProjectInventory,
    graph: DependencyGraph,
    environment: EnvironmentSpec,
    render_workspace_file: callable,
    render_projects_index: callable,
    render_dependency_yaml: callable,
    render_dependency_md: callable,
    render_environment: callable,
    writer: FileWriter,
    reader: FileReader,
    hasher: FileHasher,
    force: bool = False,
) -> list[GenerationResult]:
    """Generate all enabled workspace artifacts.

    Each target is rendered to a string, compared with the existing file via
    content hash, and written only if the content differs (or ``force`` is set).
    """
    targets = [
        (
            manifest.manifest_dir / manifest.generate.workspace_file.output,
            lambda: render_workspace_file(manifest, inventory),
        ),
        (
            manifest.manifest_dir / manifest.generate.projects_index.output,
            lambda: render_projects_index(manifest, inventory),
        ),
        (
            manifest.manifest_dir / manifest.generate.dependency_graph.output_yaml,
            lambda: render_dependency_yaml(graph),
        ),
        (
            manifest.manifest_dir / manifest.generate.dependency_graph.output_md,
            lambda: render_dependency_md(graph),
        ),
        (
            manifest.manifest_dir / manifest.generate.shared_environment.output,
            lambda: render_environment(environment),
        ),
    ]

    results: list[GenerationResult] = []
    for path, render_fn in targets:
        content = render_fn()
        if not force and path.exists():
            existing = reader.read(path)
            if hasher.hash_content(existing) == hasher.hash_content(content):
                results.append(GenerationResult(path, written=False, reason="current"))
                continue
        writer.write(path, content)
        reason = "created" if not path.exists() else "updated"
        results.append(GenerationResult(path, written=True, reason=reason))

    return results


def compute_drift(
    manifest: WorkspaceManifest,
    inventory: ProjectInventory,
    graph: DependencyGraph,
    environment: EnvironmentSpec,
    render_workspace_file: callable,
    render_projects_index: callable,
    render_dependency_yaml: callable,
    render_dependency_md: callable,
    render_environment: callable,
    reader: FileReader,
    hasher: FileHasher,
) -> DriftReport:
    """Compare generated content with existing files without writing."""
    targets = [
        (
            manifest.manifest_dir / manifest.generate.workspace_file.output,
            lambda: render_workspace_file(manifest, inventory),
        ),
        (
            manifest.manifest_dir / manifest.generate.projects_index.output,
            lambda: render_projects_index(manifest, inventory),
        ),
        (
            manifest.manifest_dir / manifest.generate.dependency_graph.output_yaml,
            lambda: render_dependency_yaml(graph),
        ),
        (
            manifest.manifest_dir / manifest.generate.dependency_graph.output_md,
            lambda: render_dependency_md(graph),
        ),
        (
            manifest.manifest_dir / manifest.generate.shared_environment.output,
            lambda: render_environment(environment),
        ),
    ]

    entries: list[DriftEntry] = []
    for path, render_fn in targets:
        expected = render_fn()
        if not path.exists():
            entries.append(DriftEntry(path, FileStatus.MISSING))
            continue
        actual = reader.read(path)
        if hasher.hash_content(actual) == hasher.hash_content(expected):
            entries.append(DriftEntry(path, FileStatus.CURRENT))
        else:
            entries.append(DriftEntry(path, FileStatus.STALE))

    return DriftReport(entries=entries)
