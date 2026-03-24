"""Typer command group for workspace management."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..application.bootstrap import BootstrapResult, build_placeholder_bindings
from ..application.discovery import discover_projects
from ..application.generation import compute_drift, generate_all
from ..application.registration import register_project
from ..domain.dependency import DependencyGraph, manual_edge_to_dependency_edge
from ..domain.environment import EnvironmentSpec, merge_environments
from ..domain.status import FileStatus
from ..infrastructure.environment_parser import CondaEnvironmentReader
from ..infrastructure.file_ops import LocalFileReader, LocalFileWriter, SHA256Hasher
from ..infrastructure.manifest_loader import load_manifest
from ..infrastructure.pyproject_parser import PyprojectExtractor
from ..infrastructure.renderers.markdown import render_dependency_md, render_projects_index
from ..infrastructure.renderers.vscode import render_workspace_file
from ..infrastructure.renderers.yaml import render_dependency_yaml, render_environment
from ..infrastructure.template_engine import copy_template, rename_paths, substitute_in_directory

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
    and sensible defaults. If it exists, generates all workspace artifacts and
    copies reference documents from package data.
    """
    manifest_path = Path(manifest).resolve()

    if not manifest_path.exists():
        _generate_default_manifest(manifest_path, dry_run)
        return

    m = load_manifest(manifest_path)
    extractor = PyprojectExtractor()
    env_reader = CondaEnvironmentReader()
    writer = LocalFileWriter()
    reader = LocalFileReader()
    hasher = SHA256Hasher()

    inventory = discover_projects(m.discovery, m.generate.projects_index.categories, extractor, m.manifest_dir)
    graph = _build_graph(m, inventory, env_reader)
    environment = _build_environment(m, inventory, env_reader)

    if dry_run:
        console.print("[bold]Dry run:[/bold] the following files would be generated:")
        for target in _target_paths(m):
            console.print(f"  {target}")
        return

    results = generate_all(
        manifest=m,
        inventory=inventory,
        graph=graph,
        environment=environment,
        render_workspace_file=render_workspace_file,
        render_projects_index=render_projects_index,
        render_dependency_yaml=render_dependency_yaml,
        render_dependency_md=render_dependency_md,
        render_environment=render_environment,
        writer=writer,
        reader=reader,
        hasher=hasher,
        force=True,
    )

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
    m = load_manifest(Path(manifest).resolve())
    extractor = PyprojectExtractor()
    env_reader = CondaEnvironmentReader()
    writer = LocalFileWriter()
    reader = LocalFileReader()
    hasher = SHA256Hasher()

    inventory = discover_projects(m.discovery, m.generate.projects_index.categories, extractor, m.manifest_dir)
    graph = _build_graph(m, inventory, env_reader)
    environment = _build_environment(m, inventory, env_reader)

    if dry_run:
        report = compute_drift(
            m, inventory, graph, environment,
            render_workspace_file, render_projects_index,
            render_dependency_yaml, render_dependency_md, render_environment,
            reader, hasher,
        )
        _print_drift(report, m.manifest_dir)
        return

    results = generate_all(
        manifest=m, inventory=inventory, graph=graph, environment=environment,
        render_workspace_file=render_workspace_file,
        render_projects_index=render_projects_index,
        render_dependency_yaml=render_dependency_yaml,
        render_dependency_md=render_dependency_md,
        render_environment=render_environment,
        writer=writer, reader=reader, hasher=hasher, force=force,
    )

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
    m = load_manifest(Path(manifest).resolve())
    extractor = PyprojectExtractor()
    project_dir = Path(path).resolve()

    metadata = register_project(project_dir, extractor)
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
    import re
    import subprocess

    if not re.match(r"^[a-z][a-z0-9_]*$", name):
        console.print("[red]Error:[/red] Name must start with a lowercase letter and contain only lowercase letters, digits, and underscores.")
        raise typer.Exit(1)

    m = load_manifest(Path(manifest).resolve())
    template_source = (m.manifest_dir / m.template.source).resolve()

    if not template_source.is_dir():
        console.print(f"[red]Error:[/red] Template source not found: {template_source}")
        raise typer.Exit(1)

    # Determine target directory (first scan dir)
    scan_dir = (m.manifest_dir / m.discovery.scan_dirs[0]).resolve()
    target_dir = scan_dir / name

    if target_dir.exists():
        console.print(f"[red]Error:[/red] Directory already exists: {target_dir}")
        raise typer.Exit(1)

    if dry_run:
        console.print(f"[bold]Dry run:[/bold] would create project at {target_dir}")
        return

    # Build placeholder bindings
    author_name = ""
    author_email = ""
    try:
        author_name = subprocess.run(
            ["git", "config", "user.name"], capture_output=True, text=True, check=False
        ).stdout.strip()
        author_email = subprocess.run(
            ["git", "config", "user.email"], capture_output=True, text=True, check=False
        ).stdout.strip()
    except FileNotFoundError:
        pass

    bindings = build_placeholder_bindings(name, description, m.defaults, author_name, author_email)

    # Copy template
    console.print(f"Copying template from {template_source.name}...")
    copy_template(template_source, target_dir)

    # Substitute placeholders
    count = substitute_in_directory(target_dir, bindings, m.template.exclude_patterns)
    console.print(f"Replaced {count} placeholder occurrences.")

    # Rename directories and files
    renamed = rename_paths(target_dir, m.template.renames, bindings)
    console.print(f"Renamed {renamed} paths.")

    # Initialize git
    if not no_git:
        subprocess.run(["git", "init", "--quiet"], cwd=target_dir, check=True)
        subprocess.run(["git", "add", "."], cwd=target_dir, check=True)
        subprocess.run(
            ["git", "commit", "--quiet", "-m", "feat: Initialize project from keystone template"],
            cwd=target_dir, check=True,
        )
        console.print("Initialized git repository.")

    console.print(f"\n[bold green]Project '{name}' created at {target_dir}[/bold green]")
    console.print(f"\nRun [bold]stelion workspace sync[/bold] to update workspace files.")


@app.command("status")
def workspace_status(
    manifest: Path = typer.Option("stelion.yml", "--manifest", "-m"),
) -> None:
    """Show which generated files are out of date."""
    m = load_manifest(Path(manifest).resolve())
    extractor = PyprojectExtractor()
    env_reader = CondaEnvironmentReader()
    reader = LocalFileReader()
    hasher = SHA256Hasher()

    inventory = discover_projects(m.discovery, m.generate.projects_index.categories, extractor, m.manifest_dir)
    graph = _build_graph(m, inventory, env_reader)
    environment = _build_environment(m, inventory, env_reader)

    report = compute_drift(
        m, inventory, graph, environment,
        render_workspace_file, render_projects_index,
        render_dependency_yaml, render_dependency_md, render_environment,
        reader, hasher,
    )

    _print_drift(report, m.manifest_dir)

    if report.has_drift:
        raise typer.Exit(1)


# --- Helpers ------------------------------------------------------------------


def _build_graph(m, inventory, env_reader) -> DependencyGraph:
    """Build the full dependency graph from auto-detection and manifest data."""
    from ..infrastructure.gitmodules_parser import scan_gitmodules

    all_names = {p.name for p in inventory.projects}
    detected = []

    for project in inventory.projects:
        # Detect editable pip installs in environment.yml
        env = env_reader.read(project.path)
        if env:
            for pip_dep in env.pip_dependencies:
                stripped = pip_dep.strip()
                if stripped.startswith("-e"):
                    # Extract package name from path
                    dep_name = _extract_pip_dep_name(stripped)
                    if dep_name and dep_name in all_names and dep_name != project.name:
                        from ..domain.dependency import DependencyEdge, DependencyMechanism
                        detected.append(DependencyEdge(
                            dependent=project.name,
                            dependency=dep_name,
                            mechanism=DependencyMechanism.EDITABLE_PIP,
                            detail="environment.yml",
                        ))

        # Detect git submodules
        detected.extend(scan_gitmodules(project.path, all_names))

    manual = [manual_edge_to_dependency_edge(e) for e in m.dependencies.manual_edges]

    return DependencyGraph(
        detected=detected,
        manual=manual,
        proposed=m.proposed_integrations,
    )


def _build_environment(m, inventory, env_reader) -> EnvironmentSpec:
    """Merge all project environments into a shared spec."""
    specs = []
    for project in inventory.projects:
        spec = env_reader.read(project.path)
        if spec:
            specs.append(spec)
    return merge_environments(specs, m.generate.shared_environment.name)


def _extract_pip_dep_name(pip_line: str) -> str | None:
    """Extract a package name from an editable pip install line.

    Examples::

        -e /path/to/morpha[dev]  ->  morpha
        -e ../../projects/eikon  ->  eikon
    """
    # Remove -e flag and whitespace
    path_str = pip_line.replace("-e", "").strip()
    # Remove extras like [dev]
    if "[" in path_str:
        path_str = path_str[:path_str.index("[")]
    # The directory name is the package name
    from pathlib import Path
    return Path(path_str).name or None


def _target_paths(m) -> list[Path]:
    """List all generation target paths."""
    return [
        m.manifest_dir / m.generate.workspace_file.output,
        m.manifest_dir / m.generate.projects_index.output,
        m.manifest_dir / m.generate.dependency_graph.output_yaml,
        m.manifest_dir / m.generate.dependency_graph.output_md,
        m.manifest_dir / m.generate.shared_environment.output,
    ]


def _print_drift(report, manifest_dir: Path) -> None:
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


def _generate_default_manifest(manifest_path: Path, dry_run: bool) -> None:
    """Auto-generate a stelion.yml with discovered projects and sensible defaults."""
    import subprocess

    manifest_dir = manifest_path.parent
    extractor = PyprojectExtractor()

    # Discover projects in the parent directory
    from ..domain.manifest import DiscoveryConfig
    config = DiscoveryConfig(scan_dirs=["../"], exclude=[manifest_dir.name])
    from ..application.discovery import discover_projects as _discover
    inventory = _discover(config, {}, extractor, manifest_dir)

    # Get author info from git config
    github_user = ""
    try:
        github_user = subprocess.run(
            ["git", "config", "user.name"], capture_output=True, text=True, check=False
        ).stdout.strip()
    except FileNotFoundError:
        pass

    project_names = sorted(p.name for p in inventory.projects)

    lines = [
        "# stelion.yml --- Workspace manifest for multi-project coordination.",
        "",
        "discovery:",
        '  scan_dirs: ["../"]',
        f"  exclude: [\"{manifest_dir.name}\"]",
        '  markers: ["pyproject.toml"]',
        "  include_self: true",
        f'  self_name: "{manifest_dir.name}"',
        "",
        "template:",
        '  source: "../keystone"',
        "",
        "defaults:",
        f'  github_user: "{github_user}"',
        '  channel_name: ""',
        '  license: "GPL-3.0-or-later"',
        "",
        "vscode:",
        '  source: "defaults"',
        "",
        "generate:",
        "  workspace_file:",
        '    output: "dev-repos.code-workspace"',
        "  projects_index:",
        '    output: "projects.md"',
        "    categories: {}",
        "  dependency_graph:",
        '    output_yaml: "dependencies.yml"',
        '    output_md: "dependencies.md"',
        "  shared_environment:",
        '    output: "environment.yml"',
        f'    name: "{manifest_dir.name}"',
        "",
        "names_in_use: {}",
        "",
        "integrations:",
        "  canonical_mechanisms: {}",
        "  reference_implementations: []",
        "",
        "proposed_integrations: []",
        "",
        "dependencies:",
        "  manual_edges: []",
        "  extra_scan_dirs: []",
        "",
    ]

    content = "\n".join(lines)

    if dry_run:
        console.print(f"[bold]Dry run:[/bold] would create {manifest_path}")
        console.print(f"  Discovered {len(project_names)} projects: {', '.join(project_names)}")
        return

    manifest_path.write_text(content, encoding="utf-8")
    console.print(f"[green]Created[/green] {manifest_path}")
    console.print(f"Discovered {len(project_names)} projects: {', '.join(project_names)}")
    console.print("\nNext steps:")
    console.print("  1. Fill in categories, names_in_use, and integrations in stelion.yml")
    console.print("  2. Run: stelion workspace init")
