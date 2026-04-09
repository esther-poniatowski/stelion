"""Submodule synchronization use-case.

Classes
-------
SyncOriginResolver
    Strategy for resolving the source commit in a sync operation.
LocalOriginResolver
    Resolve sync origin from the local clone's HEAD.
SuperprojectOriginResolver
    Resolve sync origin from a superproject's submodule pointer.
RemoteOriginResolver
    Resolve sync origin from the remote tracking branch.

Functions
---------
resolve_submodule_targets
    Extract git-submodule edges for a dependency and resolve to filesystem targets.
make_resolver
    Factory for creating the appropriate resolver from an origin enum.
plan_sync
    Determine the source commit, local update, remote push, and submodule targets.
execute_sync
    Execute sync plan in order: local clone, remote push, submodule pointers.
"""

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
    ) -> SyncPlan:
        """Resolve the source commit and build a sync plan.

        Parameters
        ----------
        dependency : str
            Name of the dependency project.
        targets : tuple[SubmoduleTarget, ...]
            Submodule targets to synchronize.
        inventory : ProjectInventory
            All discovered projects.
        git : GitOperations
            Git infrastructure operations.
        """
        ...


class LocalOriginResolver:
    """Resolve sync origin from the local clone's HEAD.

    Parameters
    ----------
    remote : str
        Remote name for the push spec.
    branch : str
        Branch name for the push spec.
    """

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
        """Resolve the source commit from the local clone's HEAD.

        Parameters
        ----------
        dependency : str
            Name of the dependency project.
        targets : tuple[SubmoduleTarget, ...]
            Submodule targets to synchronize.
        inventory : ProjectInventory
            All discovered projects.
        git : GitOperations
            Git infrastructure operations.

        Returns
        -------
        SyncPlan
            Sync plan with local HEAD as the source commit.
        """
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
    """Resolve sync origin from a superproject's submodule pointer.

    Parameters
    ----------
    source_superproject : str
        Name of the superproject to read the submodule pointer from.
    remote : str
        Remote name for the push spec.
    branch : str
        Branch name for the push spec.
    """

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
        """Resolve the source commit from the superproject's submodule pointer.

        Parameters
        ----------
        dependency : str
            Name of the dependency project.
        targets : tuple[SubmoduleTarget, ...]
            Submodule targets to synchronize.
        inventory : ProjectInventory
            All discovered projects.
        git : GitOperations
            Git infrastructure operations.

        Returns
        -------
        SyncPlan
            Sync plan with the superproject's recorded commit as the source.
        """
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
    """Resolve sync origin from the remote tracking branch.

    Parameters
    ----------
    remote : str
        Remote name to fetch from and resolve HEAD.
    branch : str
        Branch name to resolve on the remote.
    """

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
        """Resolve the source commit from the remote tracking branch.

        Parameters
        ----------
        dependency : str
            Name of the dependency project.
        targets : tuple[SubmoduleTarget, ...]
            Submodule targets to synchronize.
        inventory : ProjectInventory
            All discovered projects.
        git : GitOperations
            Git infrastructure operations.

        Returns
        -------
        SyncPlan
            Sync plan with the remote tracking branch HEAD as the source.
        """
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
    """Extract git-submodule edges for a dependency and resolve to filesystem targets.

    Parameters
    ----------
    dependency : str
        Name of the dependency project.
    graph : DependencyGraph
        Project dependency graph.
    manifest : WorkspaceManifest
        Workspace manifest with superproject path configuration.
    inventory : ProjectInventory | None
        Optional project inventory for fallback resolution.

    Returns
    -------
    tuple[SubmoduleTarget, ...]
        Resolved submodule targets for the dependency.
    """
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
    """Factory for creating the appropriate resolver from an origin enum.

    Parameters
    ----------
    origin : SyncOrigin
        How the source commit is determined.
    source_superproject : str | None
        Required when *origin* is ``SUPERPROJECT``.
    remote : str
        Remote name passed to the resolver.
    branch : str
        Branch name passed to the resolver.

    Returns
    -------
    SyncOriginResolver
        Resolver instance matching the origin strategy.
    """
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

    Parameters
    ----------
    dependency : str
        Name of the dependency project.
    targets : tuple[SubmoduleTarget, ...]
        Submodule targets to synchronize.
    inventory : ProjectInventory
        All discovered projects.
    origin : SyncOrigin
        How the source commit is determined.
    git : GitOperations
        Git infrastructure operations.
    source_superproject : str | None
        Required when *origin* is ``SUPERPROJECT``.
    remote : str
        Remote name passed to the resolver.
    branch : str
        Branch name passed to the resolver.
    resolver : SyncOriginResolver | None
        Pre-built resolver; overrides *origin* when provided.

    Returns
    -------
    SyncPlan
        Resolved sync plan.
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
    """Execute sync plan in order: local clone, remote push, submodule pointers.

    Parameters
    ----------
    plan : SyncPlan
        Resolved sync plan to execute.
    git : GitOperations
        Git infrastructure operations.
    commit : bool
        If True, commit submodule pointer updates.
    dry_run : bool
        If True, skip all side effects.

    Returns
    -------
    SyncResult
        Aggregated outcomes of the sync operation.
    """
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
    """Execute a sync action with the common try/check/apply/error pattern.

    Parameters
    ----------
    kind : OutcomeKind
        Category of the sync action.
    label : str
        Human-readable label for the action.
    get_current_ref : Callable[[], str]
        Callable returning the current reference.
    perform_action : Callable[[], None]
        Callable that performs the sync action.
    target_ref : str
        Target reference to synchronize to.
    dry_run : bool
        If True, skip the action.

    Returns
    -------
    SyncOutcome
        Outcome of the sync action.
    """
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
    """Update the local clone to the target commit.

    Parameters
    ----------
    local_dir : Path
        Path to the local clone.
    target_commit : str
        Commit hash to check out.
    git : GitOperations
        Git infrastructure operations.
    dry_run : bool
        If True, skip the update.

    Returns
    -------
    SyncOutcome
        Outcome of the local update.
    """
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
    """Push the local clone to the remote.

    Parameters
    ----------
    push_spec : PushSpec
        Remote push parameters.
    git : GitOperations
        Git infrastructure operations.
    dry_run : bool
        If True, skip the push.

    Returns
    -------
    SyncOutcome
        Outcome of the remote push.
    """
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
    """Update a single submodule pointer in a superproject.

    Parameters
    ----------
    target : SubmoduleTarget
        Superproject and submodule path to update.
    dependency : str
        Name of the dependency project.
    target_commit : str
        Commit hash to set the submodule pointer to.
    git : GitOperations
        Git infrastructure operations.
    commit : bool
        If True, commit the pointer update.
    dry_run : bool
        If True, skip the update.

    Returns
    -------
    SyncOutcome
        Outcome of the submodule update.
    """
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

    Parameters
    ----------
    superproject_name : str
        Name of the superproject to resolve.
    manifest : WorkspaceManifest
        Workspace manifest with superproject path configuration.
    inventory : ProjectInventory | None
        Optional project inventory for fallback resolution.

    Returns
    -------
    Path
        Absolute path to the superproject directory.

    Raises
    ------
    SyncError
        If the superproject is not found in configured paths or inventory.
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
    """Find a target by superproject name.

    Parameters
    ----------
    targets : tuple[SubmoduleTarget, ...]
        Available submodule targets.
    superproject_name : str
        Name of the superproject to find.

    Returns
    -------
    SubmoduleTarget
        Matching target.

    Raises
    ------
    SyncError
        If no target matches the given superproject name.
    """
    for t in targets:
        if t.superproject_name == superproject_name:
            return t
    known = [t.superproject_name for t in targets]
    raise SyncError(
        f"Superproject '{superproject_name}' is not a known consumer. "
        f"Known: {known}"
    )
