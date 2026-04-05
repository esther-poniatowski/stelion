"""Shared CLI utilities for adapter commands."""

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
    """Convert CLI option strings into a ``ProjectFilter``."""
    return ProjectFilter(
        names=tuple(names.split(",")) if names else (),
        pattern=pattern,
        git_only=git_only,
        exclude=tuple(exclude.split(",")) if exclude else (),
    )


def resolve_workspace(manifest_path: str) -> tuple[WorkspaceContext, WorkspaceServices]:
    """Load a manifest and build the full workspace context."""
    services = create_services()
    manifest = resolve_manifest(Path(manifest_path))
    ctx = build_workspace_context(manifest, services)
    return ctx, services
