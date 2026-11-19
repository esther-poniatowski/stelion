"""Command-line interface for the `stelion` package.

Defines commands available via ``python -m stelion`` or ``stelion`` if installed as a script.

Top-level commands:

- ``info``: Display diagnostic information.
- ``workspace``: Multi-project workspace management.
- ``submodule``: Submodule synchronization commands.
- ``compare``: Cross-project comparison commands.
- ``layout``: Check a repository against the layout that its consumer declares.

See Also
--------
typer.Typer
    Library for building CLI applications: https://typer.tiangolo.com/
"""

import json
from pathlib import Path
from typing import Optional

import typer
from . import info, __version__
from .workspace.adapters.commands import app as workspace_app
from .workspace.adapters.comparison_commands import app as compare_app
from .workspace.adapters.submodule_commands import app as submodule_app

app = typer.Typer(add_completion=False, no_args_is_help=True)
layout_app = typer.Typer(no_args_is_help=True, help="Check a repository against its layout.")

EXIT_ERROR = 2
"""Exit status of `layout check` when the check cannot run."""


# --- Global Commands ------------------------------------------------------------------------------


@app.command("info")
def cli_info() -> None:
    """Display version and platform diagnostics."""
    typer.echo(info())


@layout_app.command("check")
def cli_layout_check(
    layout: Path = typer.Option(..., "--layout", "-l", help="The layout to check against."),
    root: Path = typer.Option(
        Path("."), "--root", "-r", envvar="STELION_ROOT", help="The root of the repository."
    ),
    output_format: str = typer.Option(
        "text", "--format", help="Report format: `text`, or `sarif` for a findings log."
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="File of the report; standard output by default."
    ),
) -> None:
    """
    Check the repository at the root against a layout of format `stelion:layout@1`.

    The exit status is 0 when no finding is reported, 1 when one is, and 2 when the check cannot
    run: an unreadable or invalid layout, or an invalid configuration of Anagraphe.
    """
    try:
        # The check needs the extra `layout`, which the other commands do not.
        # pylint: disable-next=import-outside-toplevel
        from .layout import LayoutError, check_layout, load_layout, sarif_log, text_lines

        # pylint: disable-next=import-outside-toplevel
        from .layout.anagraphe import AnagrapheReader
    except ImportError as error:
        typer.echo(f"stelion: layout needs the extra stelion[layout]: {error}", err=True)
        raise typer.Exit(EXIT_ERROR) from error
    if output_format not in ("text", "sarif"):
        typer.echo(f"stelion: --format takes text or sarif, not {output_format}", err=True)
        raise typer.Exit(EXIT_ERROR)
    stopped: str | None = None
    findings = []
    try:
        resolved = root.resolve()
        findings = check_layout(load_layout(layout), resolved, AnagrapheReader(resolved))
    except (LayoutError, ValueError) as error:
        stopped = str(error)
    if output_format == "sarif":
        report = json.dumps(sarif_log(findings, stopped), indent=2, ensure_ascii=False) + "\n"
    else:
        report = "\n".join([f"stelion: {stopped}"] if stopped else text_lines(findings)) + "\n"
    if output is None:
        typer.echo(report, nl=False)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
    if stopped is not None:
        raise typer.Exit(EXIT_ERROR)
    raise typer.Exit(1 if findings else 0)


app.add_typer(layout_app, name="layout")


def _print_version(value: bool) -> None:
    """Print the package version and exit, before any command is required."""
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool = typer.Option(  # pylint: disable=unused-argument
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
