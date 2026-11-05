"""Dependency graph construction use-case."""

from __future__ import annotations

import os
from dataclasses import replace
from pathlib import Path

from ..domain.dependency import (
    DependencyEdge,
    DependencyGraph,
    DependencyKind,
    DependencyMechanism,
    EdgeProvenance,
    manual_edge_to_dependency_edge,
)
from ..domain.manifest import WorkspaceManifest
from ..domain.project import ProjectInventory
from .protocols import DependencyScanner


def build_dependency_graph(
    manifest: WorkspaceManifest,
    inventory: ProjectInventory,
    scanners: tuple[DependencyScanner, ...],
) -> DependencyGraph:
    """Build the full dependency graph from auto-detection and manifest data.

    Scans each project for editable pip installs in ``environment.yml``
    and git submodule relationships, then merges with manually declared
    edges from the manifest.

    Parameters
    ----------
    manifest : WorkspaceManifest
        Workspace manifest with dependency configuration.
    inventory : ProjectInventory
        All discovered projects.
    scanners : tuple[DependencyScanner, ...]
        Infrastructure scanners for detecting dependency edges.

    Returns
    -------
    DependencyGraph
        Combined graph of detected and manual dependency edges.
    """
    all_names = {p.name for p in inventory.projects}
    detected: list[DependencyEdge] = []

    # Collect all directories to scan: inventory projects + configured extra scan paths.
    scan_dirs: list[tuple[str, Path]] = [(p.name, p.path) for p in inventory.projects]
    for extra_dir_str in manifest.dependencies.scan_paths:
        extra_dir = (manifest.manifest_dir / extra_dir_str).resolve()
        if extra_dir.is_dir():
            scan_dirs.append((extra_dir.name, extra_dir))

    for project_name, project_path in scan_dirs:
        for scanner in scanners:
            for edge in scanner.scan(project_name, project_path, all_names):
                policy = manifest.integrations.canonical_mechanisms.get(edge.dependency)
                if policy is not None and policy.edge_kind:
                    try:
                        overridden_kind = DependencyKind(policy.edge_kind)
                    except ValueError as exc:
                        known = ", ".join(kind.value for kind in DependencyKind)
                        raise ValueError(
                            f"Unknown edge kind '{policy.edge_kind}' for integration "
                            f"'{edge.dependency}'. Known kinds: {known}"
                        ) from exc
                    edge = replace(edge, kind=overridden_kind)
                detected.append(edge)

    workspace_name = manifest.discovery.self_name or manifest.manifest_dir.name
    for project in inventory.projects:
        if project.name == workspace_name:
            continue
        detected.append(
            DependencyEdge(
                dependent=workspace_name,
                dependency=project.name,
                kind=DependencyKind.WORKSPACE_CONTAINMENT,
                mechanism=DependencyMechanism.WORKSPACE_DISCOVERY,
                source_declaration="stelion.yml:discovery",
                version_policy="workspace_checkout",
                optional=False,
                provenance=EdgeProvenance.AUTOMATIC,
                integration_path=os.path.relpath(project.path, manifest.manifest_dir),
            )
        )

    manual = tuple(
        manual_edge_to_dependency_edge(e) for e in manifest.dependencies.manual_edges
    )
    manually_asserted_pairs = {(edge.dependent, edge.dependency) for edge in manual}
    detected = [
        edge
        for edge in detected
        if (edge.dependent, edge.dependency) not in manually_asserted_pairs
    ]

    return DependencyGraph(
        detected=tuple(detected),
        manual=manual,
    )
