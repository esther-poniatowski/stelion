"""Domain models for project metadata and inventory."""

from __future__ import annotations

from dataclasses import dataclass, field
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


@dataclass(frozen=True)
class ProjectInventory:
    """Collection of discovered projects with category groupings."""

    projects: list[ProjectMetadata] = field(default_factory=list)
    categories: dict[str, list[str]] = field(default_factory=dict)

    def by_name(self) -> dict[str, ProjectMetadata]:
        """Index projects by name."""
        return {p.name: p for p in self.projects}

    def by_category(self) -> dict[str, list[ProjectMetadata]]:
        """Group projects by their declared category.

        Projects assigned to a category in the manifest are grouped under that
        category name. The order of projects within each category follows the
        manifest declaration order.
        """
        index = self.by_name()
        result: dict[str, list[ProjectMetadata]] = {}
        for category, names in self.categories.items():
            result[category] = [index[n] for n in names if n in index]
        return result

    def uncategorized(self) -> list[ProjectMetadata]:
        """Return projects not assigned to any category."""
        assigned = {name for names in self.categories.values() for name in names}
        return [p for p in self.projects if p.name not in assigned]
