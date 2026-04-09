"""Application use-cases for bulk operations across projects.

Functions
---------
select_projects
    Filter the project inventory to the target set.
execute_bulk
    Run an operation on each project, collecting all outcomes.
"""

from __future__ import annotations

import re

from ..domain.bulk import BulkResult, ProjectFilter, ProjectOutcome
from ..domain.project import ProjectInventory, ProjectMetadata
from ..exceptions import WorkspaceError
from .protocols import BulkOperation


def select_projects(
    inventory: ProjectInventory,
    filter_: ProjectFilter | None = None,
    *,
    names: tuple[str, ...] = (),
    pattern: str | None = None,
    git_only: bool = False,
    exclude: tuple[str, ...] = (),
) -> tuple[ProjectMetadata, ...]:
    """Filter the project inventory to the target set.

    Accepts either a ``ProjectFilter`` object or individual keyword arguments
    for backward compatibility.

    Parameters
    ----------
    inventory : ProjectInventory
        Full project inventory to filter.
    filter_ : ProjectFilter | None
        Optional filter object; overrides keyword arguments when provided.
    names : tuple[str, ...]
        Explicit project names to select.
    pattern : str | None
        Regex pattern to match against project names.
    git_only : bool
        If True, keep only projects with a git repository.
    exclude : tuple[str, ...]
        Project names to exclude from the result.

    Returns
    -------
    tuple[ProjectMetadata, ...]
        Sorted tuple of projects matching the filters.

    Raises
    ------
    WorkspaceError
        If an explicit name is not found in the inventory, or if the
        resolved set is empty after all filters are applied.
    """
    if filter_ is not None:
        names = filter_.names
        pattern = filter_.pattern
        git_only = filter_.git_only
        exclude = filter_.exclude

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

    Parameters
    ----------
    projects : tuple[ProjectMetadata, ...]
        Projects to operate on.
    operation : BulkOperation
        Operation to execute on each project.
    dry_run : bool
        If True, skip side effects.

    Returns
    -------
    BulkResult
        Aggregated outcomes from all projects.
    """
    outcomes: list[ProjectOutcome] = []
    for project in projects:
        outcomes.append(operation(project, dry_run=dry_run))
    return BulkResult(label=operation.label, outcomes=tuple(outcomes))
