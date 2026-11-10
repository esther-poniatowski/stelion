"""Command-line interface for the `stelion` package.

Defines commands available via ``python -m stelion`` or ``stelion`` if installed as a script.

Top-level commands:

- ``info``: Display diagnostic information.
- ``workspace``: Multi-project workspace management.
- ``submodule``: Submodule synchronization commands.
- ``compare``: Cross-project comparison commands.

See Also
--------
typer.Typer
    Library for building CLI applications: https://typer.tiangolo.com/
"""

import typer
from . import info, __version__
from .workspace.adapters.commands import app as workspace_app
from .workspace.adapters.comparison_commands import app as compare_app
from .workspace.adapters.submodule_commands import app as submodule_app

app = typer.Typer(add_completion=False, no_args_is_help=True)


# --- Global Commands ------------------------------------------------------------------------------


@app.command("info")
def cli_info() -> None:
    """Display version and platform diagnostics."""
    typer.echo(info())


def _print_version(value: bool) -> None:
    """Print the package version and exit, before any command is required."""
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=_print_version,
        is_eager=True,
        help="Show the package version and exit.",
    )
) -> None:
    """Root command for the package command-line interface.

    Parameters
    ----------
    version : bool
        If ``True``, print the package version and exit.
    """


# --- Commands for Workspace Management ------------------------------------------------------------

app.add_typer(workspace_app, name="workspace")
app.add_typer(submodule_app, name="submodule")
app.add_typer(compare_app, name="compare")
