"""Shared CLI utilities for adapter commands.

Every command that reads the settings of a workspace takes the options ``-r``/``--root`` and
``-c``/``--config``, defined here, and loads its settings through :func:`load_settings`. A settings
error is a configuration error, so it ends the command with status 2.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console

from ..composition import (
    WorkspaceContext,
    WorkspaceServices,
    build_workspace_context,
    create_services,
    resolve_settings,
)
from ..domain.bulk import ProjectFilter
from ..domain.manifest import WorkspaceManifest
from ..exceptions import ManifestValidationError, SettingsError
from ..infrastructure.settings_locator import (
    ROOT_ENVIRONMENT_VARIABLE,
    SettingsLocation,
    locate_settings,
)

USAGE_ERROR = 2
"""Exit status of a usage or configuration error."""

console = Console(stderr=True)

opt_root = typer.Option(
    None,
    "--root",
    "-r",
    envvar=ROOT_ENVIRONMENT_VARIABLE,
    file_okay=False,
    help=(
        "Root of the workspace. Defaults to STELION_ROOT, else to the nearest ancestor holding "
        "stelion.yml (in config/tools/ or at its level), else to the current folder."
    ),
)
opt_config = typer.Option(
    None,
    "--config",
    "-c",
    dir_okay=False,
    help="Settings file. Defaults to config/tools/stelion.yml or stelion.yml below the root.",
)


def parse_project_filter(
    names: str | None = None,
    pattern: str | None = None,
    git_only: bool = False,
    exclude: str | None = None,
) -> ProjectFilter:
    """Convert CLI option strings into a ``ProjectFilter``.

    Parameters
    ----------
    names : str | None
        Comma-separated project names to include.
    pattern : str | None
        Regex pattern to match project names.
    git_only : bool
        Only include projects with a git repository.
    exclude : str | None
        Comma-separated project names to exclude.

    Returns
    -------
    ProjectFilter
        Populated filter instance.
    """
    return ProjectFilter(
        names=tuple(names.split(",")) if names else (),
        pattern=pattern,
        git_only=git_only,
        exclude=tuple(exclude.split(",")) if exclude else (),
    )


def stop_with_usage_error(message: object) -> typer.Exit:
    """Print *message* as an error and return the exit of a usage or configuration error."""
    console.print(f"[red]Error:[/red] {message}")
    return typer.Exit(USAGE_ERROR)


def locate(root: Path | None, config: Path | None) -> SettingsLocation:
    """Resolve the root and the settings file, or stop with status 2.

    Parameters
    ----------
    root : Path | None
        Value of ``--root`` (or ``STELION_ROOT``).
    config : Path | None
        Value of ``--config``.
    """
    try:
        return locate_settings(root, config, cwd=Path.cwd())
    except SettingsError as exc:
        raise stop_with_usage_error(exc) from exc


def load_settings(
    root: Path | None, config: Path | None
) -> tuple[SettingsLocation, WorkspaceManifest]:
    """Resolve the settings of a workspace and load them, or stop with status 2.

    Parameters
    ----------
    root : Path | None
        Value of ``--root`` (or ``STELION_ROOT``).
    config : Path | None
        Value of ``--config``.

    Returns
    -------
    tuple[SettingsLocation, WorkspaceManifest]
        The resolved location, and the manifest read from the settings file or built from the
        defaults when the workspace has no settings file.
    """
    location = locate(root, config)
    try:
        return location, resolve_settings(location)
    except (FileNotFoundError, ManifestValidationError) as exc:
        raise stop_with_usage_error(exc) from exc


def resolve_workspace(
    root: Path | None, config: Path | None
) -> tuple[WorkspaceContext, WorkspaceServices]:
    """Load the settings of a workspace and build the full workspace context.

    Parameters
    ----------
    root : Path | None
        Value of ``--root`` (or ``STELION_ROOT``).
    config : Path | None
        Value of ``--config``.

    Returns
    -------
    tuple[WorkspaceContext, WorkspaceServices]
        Resolved workspace context and its associated services.
    """
    services = create_services()
    _location, manifest = load_settings(root, config)
    ctx = build_workspace_context(manifest, services)
    return ctx, services


def stdin_is_terminal() -> bool:
    """Return whether the standard input is a terminal that can answer a confirmation."""
    return sys.stdin.isatty()


def confirm_change(question: str, *, yes: bool) -> None:
    """Ask for a confirmation before a change of files outside the outputs of a command.

    Parameters
    ----------
    question : str
        Question shown on the terminal.
    yes : bool
        Value of ``--yes``, which answers the confirmation.

    Raises
    ------
    typer.Exit
        With status 2 when the standard input is not a terminal and ``--yes`` is absent.
    click.exceptions.Abort
        When the researcher declines; the command then exits with status 1.
    """
    if yes:
        return
    if not stdin_is_terminal():
        raise stop_with_usage_error(
            "this command asks for a confirmation, but the standard input is not a terminal; "
            "give --yes to confirm."
        )
    typer.confirm(question, default=False, abort=True)
