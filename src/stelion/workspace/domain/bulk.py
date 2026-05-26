"""Domain models for bulk operations across projects.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


@dataclass(frozen=True)
class ProjectFilter:
    """Criteria for selecting a subset of projects.
    """

    names: tuple[str, ...] = ()
    """Explicit project names to include."""
    pattern: str | None = None
    """Glob pattern for matching project names."""
    git_only: bool = False
    """If true, restrict to projects with a git repository."""
    exclude: tuple[str, ...] = ()
    """Project names to exclude from selection."""


class OutcomeStatus(Enum):
    """Result status for a single project within a bulk operation."""

    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass(frozen=True)
class ProjectOutcome:
    """Outcome of executing a bulk operation on a single project.
    """

    project: str
    """Name of the project."""
    path: Path
    """Filesystem path to the project directory."""
    status: OutcomeStatus
    """Result status of the operation."""
    detail: str
    """Human-readable description of the outcome."""
    error: str = ""
    """Error message, empty if the operation succeeded."""


@dataclass(frozen=True)
class BulkResult:
    """Aggregated outcomes from a bulk operation across projects.
    """

    label: str
    """Human-readable label describing the bulk operation."""
    outcomes: tuple[ProjectOutcome, ...] = ()
    """Per-project outcomes in execution order."""

    @property
    def success_count(self) -> int:
        """Number of projects where the operation succeeded.

        Returns
        -------
        int
            Count of outcomes with ``SUCCESS`` status.
        """
        return sum(1 for o in self.outcomes if o.status == OutcomeStatus.SUCCESS)

    @property
    def has_errors(self) -> bool:
        """True if any project operation failed.

        Returns
        -------
        bool
            Whether at least one outcome has ``FAILED`` status.
        """
        return any(o.status == OutcomeStatus.FAILED for o in self.outcomes)
