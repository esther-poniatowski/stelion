"""Typer command group for submodule operations.

Functions
---------
submodule_sync
    Propagate a commit across all replicas of a submodule dependency.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..composition import (
    build_workspace_context,
    create_services,
    resolve_manifest,
    run_submodule_sync,
)
from ..domain.sync import OutcomeKind, SyncOrigin, SyncResult
from ..exceptions import SyncError

app = typer.Typer(
    name="submodule",
    help="Git submodule synchronization across superprojects.",
    no_args_is_help=True,
)
console = Console(stderr=True)


@app.command("sync")
def submodule_sync(
    dependency: str = typer.Argument(
        ..., help="Name of the dependency to synchronize.",
    ),
    from_source: str = typer.Option(
        "local", "--from",
        help="Sync source: 'local', 'remote', or a superproject name.",
    ),
    no_commit: bool = typer.Option(
        False, "--no-commit",
        help="Update submodule pointers without committing.",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run",
        help="Preview updates without applying.",
    ),
    manifest: Path = typer.Option(
        "stelion.yml", "--manifest", "-m",
        help="Path to workspace manifest.",
    ),
    remote: str = typer.Option(
        "origin", "--remote",
        help="Remote name (for remote origin).",
    ),
    branch: str = typer.Option(
        "main", "--branch",
        help="Branch name (for remote origin).",
    ),
) -> None:
    """Propagate a commit across all replicas of a submodule dependency.

    Parameters
    ----------
    dependency : str
        Name of the dependency to synchronize.
    from_source : str
        Sync source: ``"local"``, ``"remote"``, or a superproject name.
    no_commit : bool
        Update submodule pointers without committing.
    dry_run : bool
        Preview updates without applying.
    manifest : Path
        Path to the workspace manifest.
    remote : str
        Remote name (for remote origin).
    branch : str
        Branch name (for remote origin).
    """
    services = create_services()
    m = resolve_manifest(Path(manifest))
    ctx = build_workspace_context(m, services)

    origin, source_superproject = _parse_origin(from_source)

    try:
        result = run_submodule_sync(
            ctx,
            dependency=dependency,
            origin=origin,
            source_superproject=source_superproject,
            remote=remote,
            branch=branch,
            commit=not no_commit,
            dry_run=dry_run,
        )
    except SyncError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)

    _print_sync_result(result, dry_run)

    if result.has_errors:
        raise typer.Exit(1)


# --- Helpers ------------------------------------------------------------------


def _parse_origin(from_source: str) -> tuple[SyncOrigin, str | None]:
    """Classify the ``--from`` value into a SyncOrigin and optional superproject name.

    Parameters
    ----------
    from_source : str
        Raw ``--from`` CLI value.

    Returns
    -------
    tuple[SyncOrigin, str | None]
        Parsed origin kind and optional superproject name.
    """
    if from_source == "local":
        return SyncOrigin.LOCAL, None
    if from_source == "remote":
        return SyncOrigin.REMOTE, None
    return SyncOrigin.SUPERPROJECT, from_source


def _print_sync_result(result: SyncResult, dry_run: bool) -> None:
    """Print sync outcomes as a Rich table.

    Parameters
    ----------
    result : SyncResult
        Aggregated sync outcomes for all replicas.
    dry_run : bool
        Whether the operation was a dry run (affects status labels).
    """
    title = "Submodule Sync (dry run)" if dry_run else "Submodule Sync"
    table = Table(title=title)
    table.add_column("Replica")
    table.add_column("Location")
    table.add_column("Old")
    table.add_column("New")
    table.add_column("Status")

    for outcome in result.outcomes:
        old_short = outcome.old_ref[:8] if outcome.old_ref else "—"
        new_short = outcome.new_ref[:8] if outcome.new_ref else "—"

        if outcome.error:
            status = f"[red]error: {outcome.error}[/red]"
        elif not outcome.applied and outcome.old_ref == outcome.new_ref:
            status = "[dim]current[/dim]"
        elif dry_run:
            status = "[yellow]would update[/yellow]"
        elif outcome.kind == OutcomeKind.REMOTE:
            status = "[green]pushed[/green]"
        else:
            status = "[green]updated[/green]"

        table.add_row(
            outcome.kind.value,
            outcome.label,
            old_short,
            new_short,
            status,
        )

    console.print(table)
    console.print(
        f"\n[bold]{result.dependency}[/bold]: "
        f"{result.applied_count} of {len(result.outcomes)} replicas updated."
    )
