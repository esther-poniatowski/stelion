"""Domain models for bulk operations across projects."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


@dataclass(frozen=True)
class ProjectFilter:
    """Criteria for selecting a subset of projects."""

    names: tuple[str, ...] = ()
    pattern: str | None = None
    git_only: bool = False
    exclude: tuple[str, ...] = ()


class OutcomeStatus(Enum):
    """Result status for a single project within a bulk operation."""

    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass(frozen=True)
class ProjectOutcome:
    """Outcome of executing a bulk operation on a single project."""

    project: str
    path: Path
    status: OutcomeStatus
    detail: str
    error: str = ""


@dataclass(frozen=True)
class BulkResult:
    """Aggregated outcomes from a bulk operation across projects."""

    label: str
    outcomes: tuple[ProjectOutcome, ...] = ()

    @property
    def success_count(self) -> int:
        """Number of projects where the operation succeeded."""
        return sum(1 for o in self.outcomes if o.status == OutcomeStatus.SUCCESS)

    @property
    def has_errors(self) -> bool:
        """True if any project operation failed."""
        return any(o.status == OutcomeStatus.FAILED for o in self.outcomes)
