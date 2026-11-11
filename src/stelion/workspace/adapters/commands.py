"""Typer command group for workspace management."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..application.bootstrap import (
    WorkspaceBootstrapRequest,
    bootstrap_workspace_project,
)
from ..application.generation import GenerationArtifact, GenerationResult
from .bulk_commands import workspace_commit, workspace_exec, workspace_push
from ..composition import (
    WorkspaceRegistrationResult,
    build_workspace_context,
    compose_workspace_manifest,
    create_bootstrap_services,
    create_services,
    initialize_workspace_manifest,
    register_workspace_project,
    run_drift_check,
    run_generate,
    target_paths,
)
from ..domain.status import DriftReport, FileStatus
from ..exceptions import BootstrapError, ManifestValidationError, WorkspaceError
from ..infrastructure.manifest_codec import render_manifest
from ..infrastructure.settings_locator import resolve_root
from ._cli_common import (
    confirm_change,
    load_settings,
    locate,
    opt_config,
    opt_root,
    stop_with_usage_error,
)

app = typer.Typer(
    name="workspace", help="Multi-project workspace management.", no_args_is_help=True
)
console = Console(stderr=True)

app.command("exec")(workspace_exec)
app.command("commit")(workspace_commit)
app.command("push")(workspace_push)


@app.command("render-manifest")
def workspace_render_manifest(
    overlay: Path = typer.Argument(..., help="Path to a consumer manifest overlay."),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        dir_okay=False,
        help="File that receives the complete manifest. Without it, the manifest goes to the "
        "standard output.",
    ),
    root: Path | None = opt_root,
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Print the complete manifest without writing it.",
    ),
) -> None:
    """Compose canonical defaults with a consumer overlay.

    The root of the workspace that the manifest configures determines its path-sensitive
    defaults, such as the workspace name; it may differ from the folder of *output* when the
    output is staged elsewhere.

    Parameters
    ----------
    overlay : Path
        YAML mapping containing consumer-specific values.
    output : Path | None
        Destination for the complete validated manifest, or ``None`` for the standard output.
    root : Path | None
        Root of the workspace that the manifest configures.
    dry_run : bool
        Print the result without writing *output*.
    """
    try:
        resolved_root = resolve_root(root, cwd=Path.cwd())
        manifest = compose_workspace_manifest(overlay, resolved_root)
    except (FileNotFoundError, ManifestValidationError) as exc:
        raise stop_with_usage_error(exc) from exc

    content = render_manifest(manifest)
    if dry_run or output is None:
        typer.echo(content, nl=False)
        return

    output = output.resolve()
    create_services().writer.write(output, content)
    console.print(f"[green]Rendered[/green] {output}")


@app.command("init")
def workspace_init(
    root: Path | None = opt_root,
    config: Path | None = opt_config,
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview actions without writing."
    ),
) -> None:
    """Initialize or regenerate a workspace from its configuration file.

    Without a configuration file, the command writes ``stelion.yml`` at the root with the
    auto-discovered projects. With a configuration file, it regenerates every workspace artifact.

    Parameters
    ----------
    root : Path | None
        Root of the workspace.
    config : Path | None
        Configuration file of the workspace.
    dry_run : bool
        Preview actions without writing.
    """
    location = locate(root, config)
    services = create_services()

    if location.settings_path is None:
        result = initialize_workspace_manifest(
            location.target_path, services, dry_run=dry_run, root=location.root
        )
        _print_manifest_init(result)
        return

    _location, m = load_settings(root, config)
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
    root: Path | None = opt_root,
    config: Path | None = opt_config,
    target: str | None = typer.Option(
        None,
        "--target",
        "-t",
        help="Single target to sync: workspace-file, projects, dependencies, or environment.",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show the drift without writing."),
) -> None:
    """Re-scan projects and update generated workspace files.

    The generated files are derived from the configuration file and the projects, so the command
    overwrites them whenever their content changes.

    Parameters
    ----------
    root : Path | None
        Root of the workspace.
    config : Path | None
        Configuration file of the workspace.
    target : str | None
        Single generation target to sync.
    dry_run : bool
        Preview without writing.
    """
    services = create_services()
    _location, m = load_settings(root, config)
    ctx = build_workspace_context(m, services)
    selected_targets = _parse_generation_targets(target)

    if dry_run:
        report = run_drift_check(ctx, services, selected_targets=selected_targets)
        _print_drift(report, m.manifest_dir)
        return

    results = run_generate(ctx, services, selected_targets=selected_targets)
    _print_generation_results("Workspace Sync", results, m.manifest_dir)


@app.command("register")
def workspace_register(
    path: Path = typer.Argument(..., help="Path to the project directory."),
    root: Path | None = opt_root,
    config: Path | None = opt_config,
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Answer yes to the confirmation that the configuration file is rewritten.",
    ),
) -> None:
    """Register an existing project into workspace artifacts.

    When the project lies outside the discovery scan directories, the command adds it to
    ``discovery.extra_paths`` and rewrites the configuration file in canonical form, which drops its
    comments. It asks for a confirmation on a terminal before that rewrite.

    Parameters
    ----------
    path : Path
        Path to the project directory.
    root : Path | None
        Root of the workspace.
    config : Path | None
        Configuration file of the workspace.
    yes : bool
        Answer yes to the confirmation.
    """
    services = create_services()
    location = locate(root, config)
    project_dir = path.resolve()

    def _confirm(settings_path: Path) -> None:
        confirm_change(
            f"Add {project_dir} to discovery.extra_paths and rewrite {settings_path} in canonical "
            "form (its comments are lost)?",
            yes=yes,
        )

    try:
        result = register_workspace_project(
            location.target_path,
            project_dir,
            services,
            root=location.root,
            confirm_manifest_rewrite=_confirm,
        )
    except ManifestValidationError as exc:
        raise stop_with_usage_error(exc) from exc
    except WorkspaceError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)

    _print_registration_result(result)


@app.command("new")
def workspace_new(
    name: str = typer.Argument(..., help="Project name (lowercase, underscores)."),
    description: str = typer.Argument(..., help="One-line project description."),
    root: Path | None = opt_root,
    config: Path | None = opt_config,
    parent: Path | None = typer.Option(
        None,
        "--parent",
        file_okay=False,
        help="Folder that receives the new project; it must be one of the discovery scan "
        "directories. Defaults to the first scan directory.",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show the target without writing."),
    no_git: bool = typer.Option(False, "--no-git", help="Skip git init."),
) -> None:
    """Bootstrap a new project from the template.

    Parameters
    ----------
    name : str
        Project name (lowercase, underscores).
    description : str
        One-line project description.
    root : Path | None
        Root of the workspace.
    config : Path | None
        Configuration file of the workspace.
    parent : Path | None
        Folder that receives the new project, read from the current folder.
    dry_run : bool
        Preview without writing.
    no_git : bool
        Skip git init.
    """
    location, m = load_settings(root, config)
    request = WorkspaceBootstrapRequest(
        manifest_dir=location.root,
        name=name,
        description=description,
        template=m.template,
        defaults=m.defaults,
        discovery_scan_dirs=m.discovery.scan_dirs,
        parent_dir=parent.resolve() if parent is not None else None,
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
        console.print(
            f"[bold]Dry run:[/bold] would create project at {result.target_dir}"
        )
        return

    console.print(f"Replaced {result.placeholders_replaced} placeholder occurrences.")
    console.print(f"Renamed {result.files_renamed} paths.")
    if result.git_initialized:
        console.print("Initialized git repository.")
    console.print(
        f"\n[bold green]Project '{name}' created at {result.target_dir}[/bold green]"
    )
    console.print(
        "\nRun [bold]stelion workspace register[/bold] to persist it into workspace artifacts."
    )


@app.command("status")
def workspace_status(
    root: Path | None = opt_root,
    config: Path | None = opt_config,
) -> None:
    """Show which generated files are out of date, and exit with status 1 when one is.

    Parameters
    ----------
    root : Path | None
        Root of the workspace.
    config : Path | None
        Configuration file of the workspace.
    """
    services = create_services()
    _location, m = load_settings(root, config)
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
        status = (
            f"[green]{result.reason}[/green]"
            if result.written
            else "[dim]current[/dim]"
        )
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
    console.print(
        f"Registered [bold]{result.project.name}[/bold] at {result.project.path}"
    )
    if result.project.issue:
        console.print(f"[yellow]Metadata warning:[/yellow] {result.project.issue}")
    if result.manifest_updated:
        console.print("Updated manifest discovery.extra_paths.")
    _print_generation_results(
        "Workspace Register", result.generated, result.manifest.manifest_dir
    )


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
        raise typer.BadParameter(
            f"Unknown target '{target}'. Expected one of: {choices}."
        ) from exc
