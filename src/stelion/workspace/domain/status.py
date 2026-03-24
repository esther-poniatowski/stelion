"""Domain models for workspace drift detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class FileStatus(Enum):
    """Status of a generated file relative to its expected content."""

    CURRENT = "current"
    STALE = "stale"
    MISSING = "missing"


@dataclass(frozen=True)
class DriftEntry:
    """Drift status for a single generated file."""

    path: Path
    status: FileStatus
    detail: str = ""


@dataclass(frozen=True)
class DriftReport:
    """Aggregated drift report for all generated workspace files."""

    entries: list[DriftEntry] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        """True if any file is stale or missing."""
        return any(e.status != FileStatus.CURRENT for e in self.entries)
