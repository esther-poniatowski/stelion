"""
Command-line interface for the `stelion` package.

Defines commands available via `python -m stelion` or `stelion` if installed as a script.

Commands
--------
info : Display diagnostic information.
workspace : Multi-project workspace management.

See Also
--------
typer.Typer
    Library for building CLI applications: https://typer.tiangolo.com/
"""

import typer
from . import info, __version__
from .workspace.adapters.commands import app as workspace_app
from .workspace.adapters.submodule_commands import app as submodule_app

app = typer.Typer(add_completion=False, no_args_is_help=True)


# --- Global Commands ------------------------------------------------------------------------------


@app.command("info")
def cli_info() -> None:
    """Display version and platform diagnostics."""
    typer.echo(info())


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False, "--version", "-v", help="Show the package version and exit."
    )
) -> None:
    """Root command for the package command-line interface."""
    if version:
        typer.echo(__version__)
        raise typer.Exit()


# --- Commands for Workspace Management ------------------------------------------------------------

app.add_typer(workspace_app, name="workspace")
app.add_typer(submodule_app, name="submodule")
