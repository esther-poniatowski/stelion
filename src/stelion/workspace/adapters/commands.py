"""Typer command group for workspace management.

Functions
---------
workspace_init
    Initialize or regenerate a workspace from its manifest.
workspace_sync
    Re-scan projects and update generated workspace files.
workspace_register
    Register an existing project into workspace artifacts.
workspace_new
    Bootstrap a new project from the template.
workspace_status
    Show which generated files are out of date.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..application.bootstrap import WorkspaceBootstrapRequest, bootstrap_workspace_project
from ..application.generation import GenerationArtifact, GenerationResult
from .bulk_commands import workspace_commit, workspace_exec, workspace_push
from ..composition import (
    WorkspaceRegistrationResult,
    build_workspace_context,
    create_bootstrap_services,
    create_services,
    initialize_workspace_manifest,
    register_workspace_project,
    resolve_manifest,
    run_drift_check,
    run_generate,
    target_paths,
)
from ..domain.status import DriftReport, FileStatus
from ..exceptions import BootstrapError, WorkspaceError

app = typer.Typer(name="workspace", help="Multi-project workspace management.", no_args_is_help=True)
console = Console(stderr=True)

app.command("exec")(workspace_exec)
app.command("commit")(workspace_commit)
app.command("push")(workspace_push)


@app.command("init")
def workspace_init(
    manifest: Path = typer.Option(
        "stelion.yml", "--manifest", "-m", help="Path to workspace manifest."
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview actions without writing."),
) -> None:
    """Initialize or regenerate a workspace from its manifest.

    Parameters
    ----------
    manifest : Path
        Path to the workspace manifest file.
    dry_run : bool
        Preview actions without writing.
    """
    manifest_path = Path(manifest).resolve()
    services = create_services()

    if not manifest_path.exists():
        result = initialize_workspace_manifest(manifest_path, services, dry_run=dry_run)
        _print_manifest_init(result)
        return

    m = resolve_manifest(manifest_path)
    ctx = build_workspace_context(m, services)

    if dry_run:
        console.print("[bold]Dry run:[/bold] the following files would be generated:")
        for target_path in target_paths(m):
            console.print(f"  {target_path}")
        return

    results = run_generate(ctx, services, force=True)
    _print_generation_results("Workspace Init", results, m.manifest_dir)


@app.command("sync")
def workspace_sync(
    manifest: Path = typer.Option("stelion.yml", "--manifest", "-m"),
    target: str | None = typer.Option(
        None,
        "--target",
        "-t",
        help="Single target to sync: workspace-file, projects, dependencies, or environment.",
    ),
    dry_run: bool = typer.Option(False, "--dry-run"),
    force: bool = typer.Option(False, "--force", help="Overwrite even if current."),
) -> None:
    """Re-scan projects and update generated workspace files.

    Parameters
    ----------
    manifest : Path
        Path to the workspace manifest file.
    target : str | None
        Single generation target to sync.
    dry_run : bool
        Preview without writing.
    force : bool
        Overwrite even if current.
    """
    services = create_services()
    m = resolve_manifest(Path(manifest))
    ctx = build_workspace_context(m, services)
    selected_targets = _parse_generation_targets(target)

    if dry_run:
        report = run_drift_check(ctx, services, selected_targets=selected_targets)
        _print_drift(report, m.manifest_dir)
        return

    results = run_generate(
        ctx,
        services,
        force=force,
        selected_targets=selected_targets,
    )
    _print_generation_results("Workspace Sync", results, m.manifest_dir)


@app.command("register")
def workspace_register(
    path: str = typer.Argument(..., help="Path to the project directory."),
    manifest: Path = typer.Option("stelion.yml", "--manifest", "-m"),
) -> None:
    """Register an existing project into workspace artifacts.

    Parameters
    ----------
    path : str
        Path to the project directory.
    manifest : Path
        Path to the workspace manifest file.
    """
    services = create_services()
    project_dir = Path(path).resolve()

    try:
        result = register_workspace_project(Path(manifest), project_dir, services)
    except WorkspaceError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)

    _print_registration_result(result)


@app.command("new")
def workspace_new(
    name: str = typer.Argument(..., help="Project name (lowercase, underscores)."),
    description: str = typer.Argument(..., help="One-line project description."),
    manifest: Path = typer.Option("stelion.yml", "--manifest", "-m"),
    destination: str | None = typer.Option(
        None,
        "--destination",
        "-d",
        help="Target discovery root relative to the manifest. Defaults to the first discovery scan dir.",
    ),
    dry_run: bool = typer.Option(False, "--dry-run"),
    no_git: bool = typer.Option(False, "--no-git", help="Skip git init."),
) -> None:
    """Bootstrap a new project from the template.

    Parameters
    ----------
    name : str
        Project name (lowercase, underscores).
    description : str
        One-line project description.
    manifest : Path
        Path to the workspace manifest file.
    destination : str | None
        Target discovery root relative to the manifest.
    dry_run : bool
        Preview without writing.
    no_git : bool
        Skip git init.
    """
    m = resolve_manifest(Path(manifest))
    request = WorkspaceBootstrapRequest(
        manifest_dir=m.manifest_dir,
        name=name,
        description=description,
        template=m.template,
        defaults=m.defaults,
        discovery_scan_dirs=m.discovery.scan_dirs,
        destination_root=destination,
        initialize_git=not no_git,
        dry_run=dry_run,
    )
    services = create_bootstrap_services()
    try:
        result = bootstrap_workspace_project(request, services)
    except BootstrapError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)

    if dry_run:
        console.print(f"[bold]Dry run:[/bold] would create project at {result.target_dir}")
        return

    console.print(f"Replaced {result.placeholders_replaced} placeholder occurrences.")
    console.print(f"Renamed {result.files_renamed} paths.")
    if result.git_initialized:
        console.print("Initialized git repository.")
    console.print(f"\n[bold green]Project '{name}' created at {result.target_dir}[/bold green]")
    console.print("\nRun [bold]stelion workspace register[/bold] to persist it into workspace artifacts.")


@app.command("status")
def workspace_status(
    manifest: Path = typer.Option("stelion.yml", "--manifest", "-m"),
) -> None:
    """Show which generated files are out of date.

    Parameters
    ----------
    manifest : Path
        Path to the workspace manifest file.
    """
    services = create_services()
    m = resolve_manifest(Path(manifest))
    ctx = build_workspace_context(m, services)

    report = run_drift_check(ctx, services)
    _print_drift(report, m.manifest_dir)

    if report.has_drift:
        raise typer.Exit(1)


def _print_drift(report: DriftReport, manifest_dir: Path) -> None:
    """Print a drift report as a Rich table.

    Parameters
    ----------
    report : DriftReport
        Drift report to display.
    manifest_dir : Path
        Workspace root used to compute relative file paths.
    """
    table = Table(title="Workspace Status")
    table.add_column("File")
    table.add_column("Status")
    for entry in report.entries:
        rel = str(entry.path.relative_to(manifest_dir))
        if entry.status == FileStatus.CURRENT:
            style = "[green]current[/green]"
        elif entry.status == FileStatus.STALE:
            style = "[yellow]stale[/yellow]"
        else:
            style = "[red]missing[/red]"
        table.add_row(rel, style)
    console.print(table)


def _print_generation_results(
    title: str,
    results: list[GenerationResult] | tuple[GenerationResult, ...],
    manifest_dir: Path,
) -> None:
    """Render generation results as a Rich table.

    Parameters
    ----------
    title : str
        Table title displayed above the results.
    results : list[GenerationResult] | tuple[GenerationResult, ...]
        Generation outcomes to display.
    manifest_dir : Path
        Workspace root used to compute relative file paths.
    """
    table = Table(title=title)
    table.add_column("File")
    table.add_column("Status")
    for result in results:
        status = f"[green]{result.reason}[/green]" if result.written else "[dim]current[/dim]"
        table.add_row(str(result.path.relative_to(manifest_dir)), status)
    console.print(table)


def _print_manifest_init(result) -> None:
    """Print the outcome of default manifest initialization.

    Parameters
    ----------
    result : object
        Result object from manifest initialization, carrying ``written``,
        ``manifest_path``, and ``project_names`` attributes.
    """
    if not result.written:
        console.print(f"[bold]Dry run:[/bold] would create {result.manifest_path}")
        console.print(
            f"  Discovered {len(result.project_names)} projects: {', '.join(result.project_names)}"
        )
        return

    console.print(f"[green]Created[/green] {result.manifest_path}")
    console.print(
        f"Discovered {len(result.project_names)} projects: {', '.join(result.project_names)}"
    )
    console.print("\nNext steps:")
    console.print("  1. Fill in names_in_use and integrations in stelion.yml")
    console.print("  2. Run: stelion workspace init")


def _print_registration_result(result: WorkspaceRegistrationResult) -> None:
    """Render the outcome of project registration.

    Parameters
    ----------
    result : WorkspaceRegistrationResult
        Registration outcome containing the registered project and generated artifacts.
    """
    console.print(f"Registered [bold]{result.project.name}[/bold] at {result.project.path}")
    if result.project.issue:
        console.print(f"[yellow]Metadata warning:[/yellow] {result.project.issue}")
    if result.manifest_updated:
        console.print("Updated manifest discovery.extra_paths.")
    _print_generation_results("Workspace Register", result.generated, result.manifest.manifest_dir)


def _parse_generation_targets(target: str | None) -> tuple[GenerationArtifact, ...]:
    """Translate the CLI target option into generation artifact identifiers.

    Parameters
    ----------
    target : str | None
        CLI ``--target`` value, or ``None`` to select all targets.

    Returns
    -------
    tuple[GenerationArtifact, ...]
        Matching artifact identifiers, or empty tuple for all.
    """
    if not target:
        return ()
    try:
        return (GenerationArtifact(target),)
    except ValueError as exc:
        choices = ", ".join(artifact.value for artifact in GenerationArtifact)
        raise typer.BadParameter(f"Unknown target '{target}'. Expected one of: {choices}.") from exc
