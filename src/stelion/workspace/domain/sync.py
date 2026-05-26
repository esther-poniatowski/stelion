"""Domain models for submodule synchronization.
"""

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
class Superproject:
    """A project that consumes dependencies as git submodules.
    """

    name: str
    """Project name."""
    path: Path
    """Filesystem path to the superproject root."""


@dataclass(frozen=True)
class SubmoduleTarget:
    """A superproject containing a submodule that should be updated.
    """

    superproject_name: str
    """Name of the superproject."""
    superproject_dir: Path
    """Filesystem path to the superproject root."""
    submodule_path: str
    """Relative path of the submodule within the superproject."""


@dataclass(frozen=True)
class PushSpec:
    """Remote push parameters.
    """

    repo_dir: Path
    """Filesystem path to the repository."""
    remote: str
    """Name of the git remote."""
    branch: str
    """Branch to push."""


@dataclass(frozen=True)
class SyncPlan:
    """Resolved plan for propagating a commit across all replicas of a dependency.
    """

    dependency: str
    """Name of the dependency being synchronized."""
    origin: SyncOrigin
    """How the source commit was determined."""
    source_label: str
    """Human-readable description of the commit source."""
    target_commit: str
    """Git commit hash to propagate."""
    submodule_targets: tuple[SubmoduleTarget, ...]
    """Superprojects whose submodule pointers should be updated."""
    local_dir: Path | None = None
    """Local clone directory, if the dependency has one."""
    push_spec: PushSpec | None = None
    """Remote push parameters, if a push is planned."""


class OutcomeKind(Enum):
    """Which replica kind a sync outcome refers to."""

    SUBMODULE = "submodule"
    LOCAL = "local"
    REMOTE = "remote"


@dataclass(frozen=True)
class SyncOutcome:
    """Result of a single synchronization action.
    """

    kind: OutcomeKind
    """Which replica kind was targeted."""
    label: str
    """Human-readable identifier for the target."""
    old_ref: str
    """Git ref before the sync action."""
    new_ref: str
    """Git ref after the sync action."""
    applied: bool
    """Whether the action actually changed the replica."""
    error: str = ""
    """Error message, empty on success."""


@dataclass(frozen=True)
class SyncResult:
    """Aggregated outcomes from executing a sync plan.
    """

    dependency: str
    """Name of the dependency that was synchronized."""
    target_commit: str
    """Git commit hash that was propagated."""
    outcomes: tuple[SyncOutcome, ...] = ()
    """Per-replica outcomes in execution order."""

    @property
    def applied_count(self) -> int:
        """Number of replicas that were actually changed.

        Returns
        -------
        int
            Count of outcomes where ``applied`` is true.
        """
        return sum(1 for o in self.outcomes if o.applied)

    @property
    def has_errors(self) -> bool:
        """True if any action failed.

        Returns
        -------
        bool
            Whether any outcome has a non-empty error message.
        """
        return any(o.error for o in self.outcomes)
