"""Submodule synchronization use-case."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Protocol

from ..domain.dependency import DependencyGraph, DependencyMechanism
from ..domain.manifest import WorkspaceManifest
from ..domain.project import ProjectInventory
from ..domain.sync import (
    OutcomeKind,
    PushSpec,
    SubmoduleTarget,
    SyncOrigin,
    SyncOutcome,
    SyncPlan,
    SyncResult,
)
from ..exceptions import SyncError
from .protocols import GitOperations


class SyncOriginResolver(Protocol):
    """Strategy for resolving the source commit in a sync operation."""

    def resolve(
        self,
        dependency: str,
        targets: tuple[SubmoduleTarget, ...],
        inventory: ProjectInventory,
        git: GitOperations,
    ) -> SyncPlan: ...


class LocalOriginResolver:
    """Resolve sync origin from the local clone's HEAD."""

    def __init__(self, remote: str = "origin", branch: str = "main") -> None:
        self._remote = remote
        self._branch = branch

    def resolve(
        self,
        dependency: str,
        targets: tuple[SubmoduleTarget, ...],
        inventory: ProjectInventory,
        git: GitOperations,
    ) -> SyncPlan:
        dep_meta = inventory.by_name().get(dependency)
        local_dir = dep_meta.path if dep_meta else None
        if local_dir is None:
            raise SyncError(
                f"Local origin requires '{dependency}' in the project inventory."
            )
        target_commit = git.head_commit(local_dir)
        return SyncPlan(
            dependency=dependency,
            origin=SyncOrigin.LOCAL,
            source_label="local HEAD",
            target_commit=target_commit,
            submodule_targets=targets,
            local_dir=None,
            push_spec=PushSpec(repo_dir=local_dir, remote=self._remote, branch=self._branch),
        )


class SuperprojectOriginResolver:
    """Resolve sync origin from a superproject's submodule pointer."""

    def __init__(
        self,
        source_superproject: str,
        remote: str = "origin",
        branch: str = "main",
    ) -> None:
        self._source_superproject = source_superproject
        self._remote = remote
        self._branch = branch

    def resolve(
        self,
        dependency: str,
        targets: tuple[SubmoduleTarget, ...],
        inventory: ProjectInventory,
        git: GitOperations,
    ) -> SyncPlan:
        dep_meta = inventory.by_name().get(dependency)
        local_dir = dep_meta.path if dep_meta else None
        source = _find_target(targets, self._source_superproject)
        target_commit = git.submodule_commit(
            source.superproject_dir, source.submodule_path,
        )
        source_label = f"{source.superproject_name}/{source.submodule_path}"
        submodule_targets = tuple(
            t for t in targets if t.superproject_name != self._source_superproject
        )
        push_spec: PushSpec | None = (
            PushSpec(repo_dir=local_dir, remote=self._remote, branch=self._branch)
            if local_dir else None
        )
        return SyncPlan(
            dependency=dependency,
            origin=SyncOrigin.SUPERPROJECT,
            source_label=source_label,
            target_commit=target_commit,
            submodule_targets=submodule_targets,
            local_dir=local_dir,
            push_spec=push_spec,
        )


class RemoteOriginResolver:
    """Resolve sync origin from the remote tracking branch."""

    def __init__(self, remote: str = "origin", branch: str = "main") -> None:
        self._remote = remote
        self._branch = branch

    def resolve(
        self,
        dependency: str,
        targets: tuple[SubmoduleTarget, ...],
        inventory: ProjectInventory,
        git: GitOperations,
    ) -> SyncPlan:
        dep_meta = inventory.by_name().get(dependency)
        local_dir = dep_meta.path if dep_meta else None
        if local_dir is None:
            raise SyncError(
                f"Remote origin requires '{dependency}' in the project inventory."
            )
        git.fetch_remote(local_dir)
        target_commit = git.remote_head(local_dir, self._remote, self._branch)
        return SyncPlan(
            dependency=dependency,
            origin=SyncOrigin.REMOTE,
            source_label=f"{self._remote}/{self._branch}",
            target_commit=target_commit,
            submodule_targets=targets,
            local_dir=local_dir,
            push_spec=None,
        )


def resolve_submodule_targets(
    dependency: str,
    graph: DependencyGraph,
    manifest: WorkspaceManifest,
    inventory: ProjectInventory | None = None,
) -> tuple[SubmoduleTarget, ...]:
    """Extract git-submodule edges for a dependency and resolve to filesystem targets."""
    edges_by_dep = graph.by_dependency()
    edges = edges_by_dep.get(dependency, [])
    submodule_edges = [
        e for e in edges if e.mechanism == DependencyMechanism.GIT_SUBMODULE
    ]
    if not submodule_edges:
        raise SyncError(
            f"No git-submodule edges found for dependency '{dependency}' "
            f"in the dependency graph."
        )
    targets: list[SubmoduleTarget] = []
    for edge in submodule_edges:
        superproject_dir = _resolve_superproject_dir(edge.dependent, manifest, inventory)
        targets.append(
            SubmoduleTarget(
                superproject_name=edge.dependent,
                superproject_dir=superproject_dir,
                submodule_path=edge.detail,
            )
        )
    return tuple(targets)


def make_resolver(
    origin: SyncOrigin,
    *,
    source_superproject: str | None = None,
    remote: str = "origin",
    branch: str = "main",
) -> SyncOriginResolver:
    """Factory for creating the appropriate resolver from an origin enum."""
    if origin == SyncOrigin.LOCAL:
        return LocalOriginResolver(remote=remote, branch=branch)
    elif origin == SyncOrigin.SUPERPROJECT:
        if source_superproject is None:
            raise SyncError("Superproject origin requires --from <superproject>.")
        return SuperprojectOriginResolver(
            source_superproject=source_superproject, remote=remote, branch=branch,
        )
    elif origin == SyncOrigin.REMOTE:
        return RemoteOriginResolver(remote=remote, branch=branch)
    else:
        raise SyncError(f"Unknown sync origin: {origin}")


def plan_sync(
    dependency: str,
    targets: tuple[SubmoduleTarget, ...],
    inventory: ProjectInventory,
    origin: SyncOrigin,
    git: GitOperations,
    *,
    source_superproject: str | None = None,
    remote: str = "origin",
    branch: str = "main",
    resolver: SyncOriginResolver | None = None,
) -> SyncPlan:
    """Determine the source commit, local update, remote push, and submodule targets.

    When *resolver* is provided it is used directly; otherwise a resolver is
    constructed from *origin* and the keyword parameters.
    """
    if resolver is None:
        resolver = make_resolver(
            origin,
            source_superproject=source_superproject,
            remote=remote,
            branch=branch,
        )
    return resolver.resolve(dependency, targets, inventory, git)


def execute_sync(
    plan: SyncPlan,
    git: GitOperations,
    *,
    commit: bool = True,
    dry_run: bool = False,
) -> SyncResult:
    """Execute sync plan in order: local clone, remote push, submodule pointers."""
    outcomes: list[SyncOutcome] = []

    if plan.local_dir is not None:
        outcomes.append(
            _sync_local(plan.local_dir, plan.target_commit, git, dry_run),
        )

    if plan.push_spec is not None:
        outcomes.append(
            _sync_remote(plan.push_spec, git, dry_run),
        )

    for target in plan.submodule_targets:
        outcomes.append(
            _sync_submodule(target, plan.dependency, plan.target_commit, git, commit, dry_run),
        )

    return SyncResult(
        dependency=plan.dependency,
        target_commit=plan.target_commit,
        outcomes=tuple(outcomes),
    )


# --- Sync action helper -------------------------------------------------------


def _execute_sync_action(
    kind: OutcomeKind,
    label: str,
    get_current_ref: Callable[[], str],
    perform_action: Callable[[], None],
    target_ref: str,
    dry_run: bool,
) -> SyncOutcome:
    """Execute a sync action with the common try/check/apply/error pattern."""
    try:
        current = get_current_ref()
        if current == target_ref:
            return SyncOutcome(
                kind=kind, label=label,
                old_ref=current, new_ref=target_ref, applied=False,
            )
        if dry_run:
            return SyncOutcome(
                kind=kind, label=label,
                old_ref=current, new_ref=target_ref, applied=False,
            )
        perform_action()
        return SyncOutcome(
            kind=kind, label=label,
            old_ref=current, new_ref=target_ref, applied=True,
        )
    except SyncError as exc:
        return SyncOutcome(
            kind=kind, label=label,
            old_ref="", new_ref=target_ref, applied=False, error=str(exc),
        )


# --- Internal helpers ---------------------------------------------------------


def _sync_local(
    local_dir: Path, target_commit: str, git: GitOperations, dry_run: bool,
) -> SyncOutcome:
    """Update the local clone to the target commit."""
    return _execute_sync_action(
        kind=OutcomeKind.LOCAL,
        label=str(local_dir.name),
        get_current_ref=lambda: git.head_commit(local_dir),
        perform_action=lambda: git.update_local_clone(local_dir, target_commit),
        target_ref=target_commit,
        dry_run=dry_run,
    )


def _sync_remote(
    push_spec: PushSpec, git: GitOperations, dry_run: bool,
) -> SyncOutcome:
    """Push the local clone to the remote."""
    label = f"{push_spec.remote}/{push_spec.branch}"
    current_head = git.head_commit(push_spec.repo_dir)
    return _execute_sync_action(
        kind=OutcomeKind.REMOTE,
        label=label,
        get_current_ref=lambda: git.remote_head(push_spec.repo_dir, push_spec.remote, push_spec.branch),
        perform_action=lambda: git.push_to_remote(push_spec.repo_dir, push_spec.remote, push_spec.branch),
        target_ref=current_head,
        dry_run=dry_run,
    )


def _sync_submodule(
    target: SubmoduleTarget,
    dependency: str,
    target_commit: str,
    git: GitOperations,
    commit: bool,
    dry_run: bool,
) -> SyncOutcome:
    """Update a single submodule pointer in a superproject."""
    label = f"{target.superproject_name}/{target.submodule_path}"

    def _perform() -> None:
        git.update_submodule_pointer(
            target.superproject_dir, target.submodule_path, target_commit,
        )
        if commit:
            git.commit_submodule_update(
                target.superproject_dir, target.submodule_path,
                dependency, target_commit[:8],
            )

    return _execute_sync_action(
        kind=OutcomeKind.SUBMODULE,
        label=label,
        get_current_ref=lambda: git.submodule_commit(target.superproject_dir, target.submodule_path),
        perform_action=_perform,
        target_ref=target_commit,
        dry_run=dry_run,
    )


def _resolve_superproject_dir(
    superproject_name: str,
    manifest: WorkspaceManifest,
    inventory: ProjectInventory | None = None,
) -> Path:
    """Resolve a superproject's absolute path from configured superproject paths.

    Matches by directory basename, assuming project names are unique across the
    workspace (which is enforced by project discovery deduplication).

    Falls back to the project inventory if the name is not found in
    ``dependencies.superproject_paths``.
    """
    for extra_dir_str in manifest.dependencies.superproject_paths:
        candidate = (manifest.manifest_dir / extra_dir_str).resolve()
        if candidate.name == superproject_name and candidate.is_dir():
            return candidate
    # Fallback: look up in the project inventory.
    if inventory is not None:
        meta = inventory.by_name().get(superproject_name)
        if meta is not None:
            return meta.path
    raise SyncError(
        f"Superproject '{superproject_name}' not found in "
        f"dependencies.superproject_paths: {list(manifest.dependencies.superproject_paths)}"
    )


def _find_target(
    targets: tuple[SubmoduleTarget, ...],
    superproject_name: str,
) -> SubmoduleTarget:
    """Find a target by superproject name."""
    for t in targets:
        if t.superproject_name == superproject_name:
            return t
    known = [t.superproject_name for t in targets]
    raise SyncError(
        f"Superproject '{superproject_name}' is not a known consumer. "
        f"Known: {known}"
    )
