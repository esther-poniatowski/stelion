"""Domain models for workspace drift detection.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class FileStatus(Enum):
    """Status of a generated file relative to its expected content."""

    CURRENT = "current"
    STALE = "stale"
    MISSING = "missing"


@dataclass(frozen=True)
class DriftEntry:
    """Drift status for a single generated file.
    """

    path: Path
    """Filesystem path of the generated file."""
    status: FileStatus
    """Whether the file is current, stale, or missing."""
    detail: str = ""
    """Human-readable explanation of the drift."""


@dataclass(frozen=True)
class DriftReport:
    """Aggregated drift report for all generated workspace files.
    """

    entries: tuple[DriftEntry, ...] = ()
    """Individual drift entries for each generated file."""

    @property
    def has_drift(self) -> bool:
        """True if any file is stale or missing.

        Returns
        -------
        bool
            Whether any entry has a non-current status.
        """
        return any(e.status != FileStatus.CURRENT for e in self.entries)
