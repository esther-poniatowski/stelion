"""Submodule synchronization use-case."""

from __future__ import annotations

from pathlib import Path

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


def resolve_submodule_targets(
    dependency: str,
    graph: DependencyGraph,
    manifest: WorkspaceManifest,
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
        superproject_dir = _resolve_superproject_dir(edge.dependent, manifest)
        targets.append(
            SubmoduleTarget(
                superproject_name=edge.dependent,
                superproject_dir=superproject_dir,
                submodule_path=edge.detail,
            )
        )
    return tuple(targets)


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
) -> SyncPlan:
    """Determine the source commit, local update, remote push, and submodule targets."""
    dep_meta = inventory.by_name().get(dependency)
    local_dir = dep_meta.path if dep_meta else None

    if origin == SyncOrigin.LOCAL:
        if local_dir is None:
            raise SyncError(
                f"Local origin requires '{dependency}' in the project inventory."
            )
        target_commit = git.head_commit(local_dir)
        source_label = "local HEAD"
        submodule_targets = targets
        update_local = None
        push_spec = PushSpec(repo_dir=local_dir, remote=remote, branch=branch)

    elif origin == SyncOrigin.SUPERPROJECT:
        if source_superproject is None:
            raise SyncError("Superproject origin requires --from <superproject>.")
        source = _find_target(targets, source_superproject)
        target_commit = git.submodule_commit(
            source.superproject_dir, source.submodule_path,
        )
        source_label = f"{source.superproject_name}/{source.submodule_path}"
        submodule_targets = tuple(
            t for t in targets if t.superproject_name != source_superproject
        )
        update_local = local_dir
        push_spec = (
            PushSpec(repo_dir=local_dir, remote=remote, branch=branch)
            if local_dir else None
        )

    elif origin == SyncOrigin.REMOTE:
        if local_dir is None:
            raise SyncError(
                f"Remote origin requires '{dependency}' in the project inventory."
            )
        git.fetch_remote(local_dir)
        target_commit = git.remote_head(local_dir, remote, branch)
        source_label = f"{remote}/{branch}"
        submodule_targets = targets
        update_local = local_dir
        push_spec = None

    else:
        raise SyncError(f"Unknown sync origin: {origin}")

    return SyncPlan(
        dependency=dependency,
        origin=origin,
        source_label=source_label,
        target_commit=target_commit,
        submodule_targets=submodule_targets,
        local_dir=update_local,
        push_spec=push_spec,
    )


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


# --- Internal helpers ---------------------------------------------------------


def _sync_local(
    local_dir: Path, target_commit: str, git: GitOperations, dry_run: bool,
) -> SyncOutcome:
    """Update the local clone to the target commit."""
    try:
        old_ref = git.head_commit(local_dir)
        if old_ref == target_commit:
            return SyncOutcome(
                kind=OutcomeKind.LOCAL, label=str(local_dir.name),
                old_ref=old_ref, new_ref=target_commit, applied=False,
            )
        if dry_run:
            return SyncOutcome(
                kind=OutcomeKind.LOCAL, label=str(local_dir.name),
                old_ref=old_ref, new_ref=target_commit, applied=False,
            )
        git.update_local_clone(local_dir, target_commit)
        return SyncOutcome(
            kind=OutcomeKind.LOCAL, label=str(local_dir.name),
            old_ref=old_ref, new_ref=target_commit, applied=True,
        )
    except SyncError as exc:
        return SyncOutcome(
            kind=OutcomeKind.LOCAL, label=str(local_dir.name),
            old_ref="", new_ref=target_commit, applied=False, error=str(exc),
        )


def _sync_remote(
    push_spec: PushSpec, git: GitOperations, dry_run: bool,
) -> SyncOutcome:
    """Push the local clone to the remote."""
    label = f"{push_spec.remote}/{push_spec.branch}"
    try:
        old_ref = git.remote_head(push_spec.repo_dir, push_spec.remote, push_spec.branch)
        current_head = git.head_commit(push_spec.repo_dir)
        if old_ref == current_head:
            return SyncOutcome(
                kind=OutcomeKind.REMOTE, label=label,
                old_ref=old_ref, new_ref=current_head, applied=False,
            )
        if dry_run:
            return SyncOutcome(
                kind=OutcomeKind.REMOTE, label=label,
                old_ref=old_ref, new_ref=current_head, applied=False,
            )
        git.push_to_remote(push_spec.repo_dir, push_spec.remote, push_spec.branch)
        return SyncOutcome(
            kind=OutcomeKind.REMOTE, label=label,
            old_ref=old_ref, new_ref=current_head, applied=True,
        )
    except SyncError as exc:
        return SyncOutcome(
            kind=OutcomeKind.REMOTE, label=label,
            old_ref="", new_ref="", applied=False, error=str(exc),
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
    try:
        old_ref = git.submodule_commit(target.superproject_dir, target.submodule_path)
        if old_ref == target_commit:
            return SyncOutcome(
                kind=OutcomeKind.SUBMODULE, label=label,
                old_ref=old_ref, new_ref=target_commit, applied=False,
            )
        if dry_run:
            return SyncOutcome(
                kind=OutcomeKind.SUBMODULE, label=label,
                old_ref=old_ref, new_ref=target_commit, applied=False,
            )
        git.update_submodule_pointer(
            target.superproject_dir, target.submodule_path, target_commit,
        )
        if commit:
            git.commit_submodule_update(
                target.superproject_dir, target.submodule_path,
                dependency, target_commit[:8],
            )
        return SyncOutcome(
            kind=OutcomeKind.SUBMODULE, label=label,
            old_ref=old_ref, new_ref=target_commit, applied=True,
        )
    except SyncError as exc:
        return SyncOutcome(
            kind=OutcomeKind.SUBMODULE, label=label,
            old_ref="", new_ref=target_commit, applied=False, error=str(exc),
        )


def _resolve_superproject_dir(
    superproject_name: str,
    manifest: WorkspaceManifest,
) -> Path:
    """Resolve a superproject's absolute path from configured superproject paths.

    Matches by directory basename, assuming project names are unique across the
    workspace (which is enforced by project discovery deduplication).
    """
    for extra_dir_str in manifest.dependencies.superproject_paths:
        candidate = (manifest.manifest_dir / extra_dir_str).resolve()
        if candidate.name == superproject_name and candidate.is_dir():
            return candidate
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
