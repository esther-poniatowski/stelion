"""Domain models for submodule synchronization."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class SyncOrigin(Enum):
    """How the source commit for synchronization is determined."""

    LOCAL = "local"
    SUPERPROJECT = "superproject"
    REMOTE = "remote"


@dataclass(frozen=True)
class SubmoduleTarget:
    """A superproject containing a submodule that should be updated."""

    superproject_name: str
    superproject_dir: Path
    submodule_path: str


@dataclass(frozen=True)
class PushSpec:
    """Remote push parameters."""

    repo_dir: Path
    remote: str
    branch: str


@dataclass(frozen=True)
class SyncPlan:
    """Resolved plan for propagating a commit across all replicas of a dependency."""

    dependency: str
    origin: SyncOrigin
    source_label: str
    target_commit: str
    submodule_targets: tuple[SubmoduleTarget, ...]
    local_dir: Path | None = None
    push_spec: PushSpec | None = None


class OutcomeKind(Enum):
    """Which replica kind a sync outcome refers to."""

    SUBMODULE = "submodule"
    LOCAL = "local"
    REMOTE = "remote"


@dataclass(frozen=True)
class SyncOutcome:
    """Result of a single synchronization action."""

    kind: OutcomeKind
    label: str
    old_ref: str
    new_ref: str
    applied: bool
    error: str = ""


@dataclass(frozen=True)
class SyncResult:
    """Aggregated outcomes from executing a sync plan."""

    dependency: str
    target_commit: str
    outcomes: tuple[SyncOutcome, ...] = ()

    @property
    def applied_count(self) -> int:
        """Number of replicas that were actually changed."""
        return sum(1 for o in self.outcomes if o.applied)

    @property
    def has_errors(self) -> bool:
        """True if any action failed."""
        return any(o.error for o in self.outcomes)
