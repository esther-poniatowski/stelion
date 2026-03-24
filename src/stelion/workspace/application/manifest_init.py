"""Default manifest generation use-case."""

from __future__ import annotations

from pathlib import Path

from ..domain.manifest import DiscoveryConfig
from ..domain.project import ProjectInventory
from .discovery import discover_projects
from .protocols import MetadataExtractor


def generate_default_manifest_content(
    manifest_dir: Path,
    extractor: MetadataExtractor,
    github_user: str = "",
) -> tuple[str, ProjectInventory]:
    """Build the text content for a new stelion.yml with auto-discovered projects.

    Parameters
    ----------
    manifest_dir
        Directory that will contain the new manifest.
    extractor
        Infrastructure component for reading pyproject.toml metadata.
    github_user
        GitHub username for template defaults (e.g. from git config).

    Returns
    -------
    tuple[str, ProjectInventory]
        The YAML content string and the discovered project inventory.
    """
    config = DiscoveryConfig(scan_dirs=("../",), exclude=(manifest_dir.name,))
    inventory = discover_projects(config, extractor, manifest_dir)

    project_names = sorted(p.name for p in inventory.projects)

    lines = [
        "# stelion.yml --- Workspace manifest for multi-project coordination.",
        "",
        "discovery:",
        '  scan_dirs: ["../"]',
        f"  exclude: [\"{manifest_dir.name}\"]",
        '  markers: ["pyproject.toml"]',
        "  include_self: true",
        f'  self_name: "{manifest_dir.name}"',
        "",
        "template:",
        '  source: "../keystone"',
        "",
        "defaults:",
        f'  github_user: "{github_user}"',
        '  channel_name: ""',
        '  license: "GPL-3.0-or-later"',
        "",
        "vscode:",
        '  source: "defaults"',
        "",
        "generate:",
        "  workspace_file:",
        '    output: "dev-repos.code-workspace"',
        "  projects_registry:",
        '    output: "projects.yml"',
        "  dependency_graph:",
        '    output: "dependencies.yml"',
        "  shared_environment:",
        '    output: "environment.yml"',
        f'    name: "{manifest_dir.name}"',
        "",
        "names_in_use: {}",
        "",
        "integrations:",
        "  canonical_mechanisms: {}",
        "  reference_implementations: []",
        "",
        "dependencies:",
        "  manual_edges: []",
        "  extra_scan_dirs: []",
        "",
    ]

    return "\n".join(lines), inventory
