"""Domain models for project metadata and inventory."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class MetadataStatus(StrEnum):
    """Status of metadata extracted from a project directory."""

    CURRENT = "current"
    MISSING_PYPROJECT = "missing_pyproject"
    INVALID_PYPROJECT = "invalid_pyproject"


@dataclass(frozen=True)
class ProjectMetadata:
    """Metadata extracted from a single project's pyproject.toml and filesystem."""

    name: str
    path: Path
    description: str = ""
    version: str = "0.0.0"
    homepage: str | None = None
    has_git: bool = False
    languages: tuple[str, ...] = ()
    status: MetadataStatus = MetadataStatus.CURRENT
    issue: str = ""


@dataclass(frozen=True)
class ProjectInventory:
    """Collection of discovered projects."""

    projects: tuple[ProjectMetadata, ...] = ()

    def by_name(self) -> dict[str, ProjectMetadata]:
        """Index projects by name."""
        return {p.name: p for p in self.projects}

    def by_path(self) -> dict[Path, ProjectMetadata]:
        """Index projects by their resolved filesystem path."""
        return {p.path.resolve(): p for p in self.projects}
