"""Render Markdown workspace artifacts: projects.md, dependencies.md."""

from __future__ import annotations

from ...domain.dependency import DependencyGraph
from ...domain.manifest import WorkspaceManifest
from ...domain.project import ProjectInventory


def render_projects_index(manifest: WorkspaceManifest, inventory: ProjectInventory) -> str:
    """Generate projects.md from discovered project metadata."""
    lines = [
        "# Project Index",
        "",
        "Overview of all projects under the workspace.",
        "",
        "Project names draw from Greek and Latin etymologies (see [names.md](names.md)).",
        "",
    ]

    categorized = inventory.by_category()
    for category, projects in categorized.items():
        lines.append(f"## {category}")
        lines.append("")
        lines.append("| Project | Path | Description | Status |")
        lines.append("|---------|------|-------------|--------|")
        for p in projects:
            link = f"[{p.name}](../{p.name}/)"
            rel_path = f"`projects/{p.name}`"
            status = p.status or ""
            lines.append(f"| {link} | {rel_path} | {p.description} | {status} |")
        lines.append("")

    uncategorized = inventory.uncategorized()
    if uncategorized:
        lines.append("## Uncategorized")
        lines.append("")
        lines.append("| Project | Path | Description | Status |")
        lines.append("|---------|------|-------------|--------|")
        for p in uncategorized:
            link = f"[{p.name}](../{p.name}/)"
            rel_path = f"`projects/{p.name}`"
            status = p.status or ""
            lines.append(f"| {link} | {rel_path} | {p.description} | {status} |")
        lines.append("")

    return "\n".join(lines)


def render_dependency_md(graph: DependencyGraph) -> str:
    """Generate dependencies.md as a human-readable view of the dependency graph."""
    lines = [
        "# Inter-Project Dependencies",
        "",
        "Dependency graph across the workspace. Auto-detected edges are regenerated",
        "by `stelion workspace sync`. Manual and proposed edges come from `stelion.yml`.",
        "",
    ]

    all_edges = graph.all_edges
    if all_edges:
        # By dependent
        lines.append("## By Dependent")
        lines.append("")
        lines.append("| Dependent | Dependency | Mechanism |")
        lines.append("|-----------|------------|-----------|")
        for edge in sorted(all_edges, key=lambda e: (e.dependent, e.dependency)):
            lines.append(f"| {edge.dependent} | {edge.dependency} | {edge.mechanism.value} |")
        lines.append("")

        # By dependency
        lines.append("## By Dependency")
        lines.append("")
        lines.append("| Dependency | Dependents | Mechanism |")
        lines.append("|------------|------------|-----------|")
        by_dep = graph.by_dependency()
        for dep_name in sorted(by_dep):
            edges = by_dep[dep_name]
            dependents = ", ".join(sorted(e.dependent for e in edges))
            mechanisms = ", ".join(sorted({e.mechanism.value for e in edges}))
            lines.append(f"| {dep_name} | {dependents} | {mechanisms} |")
        lines.append("")

    # Proposed integrations
    if graph.proposed:
        lines.append("## Proposed Integrations")
        lines.append("")
        lines.append("| Consumer | Library | Integration | Priority | Notes |")
        lines.append("|----------|---------|-------------|----------|-------|")
        for p in graph.proposed:
            lines.append(
                f"| {p.consumer} | {p.library} | {p.integration} | {p.priority} | {p.notes} |"
            )
        lines.append("")

    return "\n".join(lines)
