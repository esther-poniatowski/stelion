"""Application use-cases for bulk operations across projects."""

from __future__ import annotations

import re

from ..domain.bulk import BulkResult, ProjectOutcome
from ..domain.project import ProjectInventory, ProjectMetadata
from ..exceptions import WorkspaceError
from .protocols import BulkOperation


def select_projects(
    inventory: ProjectInventory,
    *,
    names: tuple[str, ...] = (),
    pattern: str | None = None,
    git_only: bool = False,
    exclude: tuple[str, ...] = (),
) -> tuple[ProjectMetadata, ...]:
    """Filter the project inventory to the target set.

    Raises
    ------
    WorkspaceError
        If an explicit name is not found in the inventory, or if the
        resolved set is empty after all filters are applied.
    """
    by_name = inventory.by_name()
    projects: list[ProjectMetadata] = list(inventory.projects)

    if names:
        unknown = set(names) - by_name.keys()
        if unknown:
            raise WorkspaceError(f"Unknown project(s): {', '.join(sorted(unknown))}")
        projects = [by_name[n] for n in names]

    if pattern:
        compiled = re.compile(pattern)
        projects = [p for p in projects if compiled.search(p.name)]

    if git_only:
        projects = [p for p in projects if p.has_git]

    if exclude:
        excluded = set(exclude)
        projects = [p for p in projects if p.name not in excluded]

    result = tuple(sorted(projects, key=lambda p: p.name))

    if not result:
        raise WorkspaceError("No projects match the given filters.")

    return result


def execute_bulk(
    projects: tuple[ProjectMetadata, ...],
    operation: BulkOperation,
    *,
    dry_run: bool = False,
) -> BulkResult:
    """Run an operation on each project, collecting all outcomes.

    Never short-circuits on failure: all projects are processed.
    """
    outcomes: list[ProjectOutcome] = []
    for project in projects:
        outcomes.append(operation(project, dry_run=dry_run))
    return BulkResult(label=operation.label, outcomes=tuple(outcomes))
