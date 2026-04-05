"""Typer commands for bulk operations across workspace projects."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Optional

import typer
from rich.console import Console
from rich.table import Table

from ..composition import (
    run_bulk_commit,
    run_bulk_exec,
    run_bulk_push,
)
from ..domain.bulk import BulkResult, OutcomeStatus, ProjectFilter
from ..exceptions import WorkspaceError
from ._cli_common import parse_project_filter, resolve_workspace

console = Console(stderr=True)


# --- Shared helpers -----------------------------------------------------------


def _print_bulk_result(result: BulkResult, dry_run: bool) -> None:
    """Render a BulkResult as a Rich table."""
    title = f"{result.label} (dry run)" if dry_run else result.label
    table = Table(title=title)
    table.add_column("Project")
    table.add_column("Status")
    table.add_column("Detail")

    for outcome in result.outcomes:
        if outcome.status == OutcomeStatus.SUCCESS:
            status = "[green]success[/green]"
            detail = outcome.detail
        elif outcome.status == OutcomeStatus.SKIPPED:
            status = "[dim]skipped[/dim]"
            detail = outcome.detail
        else:
            status = "[red]failed[/red]"
            detail = f"[red]{outcome.error}[/red]"

        table.add_row(outcome.project, status, detail)

    console.print(table)

    total = len(result.outcomes)
    failed = sum(1 for o in result.outcomes if o.status == OutcomeStatus.FAILED)
    skipped = sum(1 for o in result.outcomes if o.status == OutcomeStatus.SKIPPED)
    console.print(
        f"\n[bold]{result.label}[/bold]: "
        f"{result.success_count} of {total} succeeded"
        f"{f', {failed} failed' if failed else ''}"
        f"{f', {skipped} skipped' if skipped else ''}"
    )


def _run_bulk_command(
    manifest: str,
    filter_: ProjectFilter,
    dry_run: bool,
    run_fn: Callable[..., BulkResult],
    **kwargs: Any,
) -> None:
    """Shared workspace setup, error handling, and result printing for bulk commands."""
    try:
        ctx, _services = resolve_workspace(manifest)
        result = run_fn(ctx, filter_=filter_, dry_run=dry_run, **kwargs)
        _print_bulk_result(result, dry_run)
        if result.has_errors:
            raise typer.Exit(1)
    except WorkspaceError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)


# --- Filter options common to all bulk commands -------------------------------

_opt_names = typer.Option(
    None, "--names", "-n",
    help="Comma-separated project names to include.",
)
_opt_pattern = typer.Option(
    None, "--pattern", "-p",
    help="Regex pattern to match project names.",
)
_opt_git_only = typer.Option(
    False, "--git-only",
    help="Only projects with a git repository.",
)
_opt_exclude = typer.Option(
    None, "--exclude", "-e",
    help="Comma-separated project names to exclude.",
)
_opt_dry_run = typer.Option(False, "--dry-run", help="Preview without executing.")
_opt_manifest = typer.Option(
    "stelion.yml", "--manifest",
    help="Path to workspace manifest.",
)


# --- Commands -----------------------------------------------------------------


def workspace_exec(
    command: str = typer.Argument(..., help="Shell command to run in each project."),
    names: Optional[str] = _opt_names,
    pattern: Optional[str] = _opt_pattern,
    git_only: bool = _opt_git_only,
    exclude: Optional[str] = _opt_exclude,
    dry_run: bool = _opt_dry_run,
    manifest: Path = _opt_manifest,
) -> None:
    """Run an arbitrary shell command in each project directory."""
    filter_ = parse_project_filter(names, pattern, git_only, exclude)
    _run_bulk_command(str(manifest), filter_, dry_run, run_bulk_exec, command=command)


def workspace_commit(
    message: str = typer.Option(..., "--message", "-m", help="Commit message."),
    names: Optional[str] = _opt_names,
    pattern: Optional[str] = _opt_pattern,
    git_only: bool = _opt_git_only,
    exclude: Optional[str] = _opt_exclude,
    dry_run: bool = _opt_dry_run,
    manifest: Path = _opt_manifest,
) -> None:
    """Stage tracked changes and commit across projects."""
    filter_ = parse_project_filter(names, pattern, git_only, exclude)
    _run_bulk_command(str(manifest), filter_, dry_run, run_bulk_commit, message=message)


def workspace_push(
    remote: str = typer.Option("origin", "--remote", help="Remote name."),
    branch: str = typer.Option("main", "--branch", help="Branch to push."),
    names: Optional[str] = _opt_names,
    pattern: Optional[str] = _opt_pattern,
    git_only: bool = _opt_git_only,
    exclude: Optional[str] = _opt_exclude,
    dry_run: bool = _opt_dry_run,
    manifest: Path = _opt_manifest,
) -> None:
    """Push the current branch to a remote across projects."""
    filter_ = parse_project_filter(names, pattern, git_only, exclude)
    _run_bulk_command(
        str(manifest), filter_, dry_run, run_bulk_push,
        remote=remote, branch=branch,
    )
