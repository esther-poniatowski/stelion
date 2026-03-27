"""Typer command group for workspace management."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..application.bootstrap import WorkspaceBootstrapRequest, bootstrap_workspace_project
from ..application.manifest_init import generate_default_manifest_content
from ..application.registration import register_project
from ..composition import (
    build_workspace_context,
    create_bootstrap_services,
    create_services,
    resolve_manifest,
    run_drift_check,
    run_generate,
    target_paths,
)
from ..domain.status import DriftReport, FileStatus
from ..exceptions import BootstrapError

app = typer.Typer(name="workspace", help="Multi-project workspace management.", no_args_is_help=True)
console = Console(stderr=True)


@app.command("init")
def workspace_init(
    manifest: Path = typer.Option(
        "stelion.yml", "--manifest", "-m", help="Path to workspace manifest."
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview actions without writing."),
) -> None:
    """Initialize or regenerate a workspace from its manifest.

    If stelion.yml does not exist, generates one with auto-discovered projects
    and sensible defaults. If it exists, generates all workspace artifacts.
    """
    manifest_path = Path(manifest).resolve()

    if not manifest_path.exists():
        _handle_default_manifest(manifest_path, dry_run)
        return

    services = create_services()
    m = resolve_manifest(manifest_path)
    ctx = build_workspace_context(m, services)

    if dry_run:
        console.print("[bold]Dry run:[/bold] the following files would be generated:")
        for target in target_paths(m):
            console.print(f"  {target}")
        return

    results = run_generate(ctx, services, force=True)

    table = Table(title="Workspace Init")
    table.add_column("File")
    table.add_column("Status")
    for r in results:
        status = f"[green]{r.reason}[/green]" if r.written else "[dim]current[/dim]"
        table.add_row(str(r.path.relative_to(m.manifest_dir)), status)
    console.print(table)


@app.command("sync")
def workspace_sync(
    manifest: Path = typer.Option("stelion.yml", "--manifest", "-m"),
    target: str = typer.Option("", "--target", "-t", help="Single target to sync."),
    dry_run: bool = typer.Option(False, "--dry-run"),
    force: bool = typer.Option(False, "--force", help="Overwrite even if current."),
) -> None:
    """Re-scan projects and update generated workspace files."""
    services = create_services()
    m = resolve_manifest(Path(manifest))
    ctx = build_workspace_context(m, services)

    if dry_run:
        report = run_drift_check(ctx, services)
        _print_drift(report, m.manifest_dir)
        return

    results = run_generate(ctx, services, force=force)

    table = Table(title="Workspace Sync")
    table.add_column("File")
    table.add_column("Status")
    for r in results:
        status = f"[green]{r.reason}[/green]" if r.written else "[dim]current[/dim]"
        table.add_row(str(r.path.relative_to(m.manifest_dir)), status)
    console.print(table)


@app.command("register")
def workspace_register(
    path: str = typer.Argument(..., help="Path to the project directory."),
    manifest: Path = typer.Option("stelion.yml", "--manifest", "-m"),
) -> None:
    """Register an existing project into workspace artifacts."""
    services = create_services()
    project_dir = Path(path).resolve()

    metadata = register_project(project_dir, services.extractor)
    console.print(f"Registered [bold]{metadata.name}[/bold] ({metadata.description})")
    console.print(f"Run [bold]stelion workspace sync[/bold] to update workspace files.")


@app.command("new")
def workspace_new(
    name: str = typer.Argument(..., help="Project name (lowercase, underscores)."),
    description: str = typer.Argument(..., help="One-line project description."),
    manifest: Path = typer.Option("stelion.yml", "--manifest", "-m"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    no_git: bool = typer.Option(False, "--no-git", help="Skip git init."),
) -> None:
    """Bootstrap a new project from the template and register it."""
    m = resolve_manifest(Path(manifest))
    request = WorkspaceBootstrapRequest(
        manifest_dir=m.manifest_dir,
        name=name,
        description=description,
        template=m.template,
        defaults=m.defaults,
        discovery_scan_dirs=m.discovery.scan_dirs,
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
    console.print(f"\nRun [bold]stelion workspace sync[/bold] to update workspace files.")


@app.command("status")
def workspace_status(
    manifest: Path = typer.Option("stelion.yml", "--manifest", "-m"),
) -> None:
    """Show which generated files are out of date."""
    services = create_services()
    m = resolve_manifest(Path(manifest))
    ctx = build_workspace_context(m, services)

    report = run_drift_check(ctx, services)
    _print_drift(report, m.manifest_dir)

    if report.has_drift:
        raise typer.Exit(1)


# --- Helpers ------------------------------------------------------------------


def _print_drift(report: DriftReport, manifest_dir: Path) -> None:
    """Print a drift report as a Rich table."""
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


def _handle_default_manifest(manifest_path: Path, dry_run: bool) -> None:
    """Auto-generate a stelion.yml with discovered projects and sensible defaults."""
    import subprocess

    manifest_dir = manifest_path.parent

    # Get author info from git config
    github_user = ""
    try:
        github_user = subprocess.run(
            ["git", "config", "user.name"], capture_output=True, text=True, check=False
        ).stdout.strip()
    except FileNotFoundError:
        pass

    services = create_services()
    content, inventory = generate_default_manifest_content(
        manifest_dir, services.extractor, github_user,
    )
    project_names = sorted(p.name for p in inventory.projects)

    if dry_run:
        console.print(f"[bold]Dry run:[/bold] would create {manifest_path}")
        console.print(f"  Discovered {len(project_names)} projects: {', '.join(project_names)}")
        return

    manifest_path.write_text(content, encoding="utf-8")
    console.print(f"[green]Created[/green] {manifest_path}")
    console.print(f"Discovered {len(project_names)} projects: {', '.join(project_names)}")
    console.print("\nNext steps:")
    console.print("  1. Fill in names_in_use and integrations in stelion.yml")
    console.print("  2. Run: stelion workspace init")
