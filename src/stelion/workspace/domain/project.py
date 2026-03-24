"""Domain models for project metadata and inventory."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectMetadata:
    """Metadata extracted from a single project's pyproject.toml and filesystem."""

    name: str
    path: Path
    description: str = ""
    version: str = "0.0.0"
    status: str | None = None
    homepage: str | None = None
    has_git: bool = False
    languages: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProjectInventory:
    """Collection of discovered projects."""

    projects: tuple[ProjectMetadata, ...] = ()

    def by_name(self) -> dict[str, ProjectMetadata]:
        """Index projects by name."""
        return {p.name: p for p in self.projects}
