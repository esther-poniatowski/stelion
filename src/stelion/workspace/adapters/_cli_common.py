"""Shared CLI utilities for adapter commands.

Functions
---------
parse_project_filter
    Convert CLI option strings into a ``ProjectFilter``.
resolve_workspace
    Load a manifest and build the full workspace context.
"""

from __future__ import annotations

from pathlib import Path

from ..composition import (
    WorkspaceContext,
    WorkspaceServices,
    build_workspace_context,
    create_services,
    resolve_manifest,
)
from ..domain.bulk import ProjectFilter


def parse_project_filter(
    names: str | None = None,
    pattern: str | None = None,
    git_only: bool = False,
    exclude: str | None = None,
) -> ProjectFilter:
    """Convert CLI option strings into a ``ProjectFilter``.

    Parameters
    ----------
    names : str | None
        Comma-separated project names to include.
    pattern : str | None
        Regex pattern to match project names.
    git_only : bool
        Only include projects with a git repository.
    exclude : str | None
        Comma-separated project names to exclude.

    Returns
    -------
    ProjectFilter
        Populated filter instance.
    """
    return ProjectFilter(
        names=tuple(names.split(",")) if names else (),
        pattern=pattern,
        git_only=git_only,
        exclude=tuple(exclude.split(",")) if exclude else (),
    )


def resolve_workspace(manifest_path: str) -> tuple[WorkspaceContext, WorkspaceServices]:
    """Load a manifest and build the full workspace context.

    Parameters
    ----------
    manifest_path : str
        Path to the workspace manifest file.

    Returns
    -------
    tuple[WorkspaceContext, WorkspaceServices]
        Resolved workspace context and its associated services.
    """
    services = create_services()
    manifest = resolve_manifest(Path(manifest_path))
    ctx = build_workspace_context(manifest, services)
    return ctx, services
