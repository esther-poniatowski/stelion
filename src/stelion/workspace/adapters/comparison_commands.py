"""Typer commands for cross-project comparison."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..composition import (
    build_workspace_context,
    create_comparison_services,
    create_services,
    resolve_manifest,
    run_compare_files,
    run_compare_trees,
)
from ..domain.comparison import (
    ContentKind,
    FileDiffResult,
    FileReport,
    FileTarget,
    FileTargetEntry,
    NodeMatch,
    TreeReport,
    TreeTarget,
)
from ..exceptions import ComparisonError, WorkspaceError
from ..infrastructure.renderers.comparison import render_file_yaml, render_tree_yaml
from ._cli_common import parse_project_filter

app = typer.Typer(name="compare", help="Cross-project comparison.", no_args_is_help=True)
console = Console(stderr=True)


# ---------------------------------------------------------------------------
# Shared option definitions
# ---------------------------------------------------------------------------

_opt_names = typer.Option(None, "--names", "-n", help="Comma-separated project names to include.")
_opt_pattern = typer.Option(None, "--pattern", "-p", help="Regex pattern to match project names.")
_opt_git_only = typer.Option(False, "--git-only", help="Only projects with a git repository.")
_opt_exclude = typer.Option(None, "--exclude", "-e", help="Comma-separated project names to exclude.")
_opt_manifest = typer.Option("stelion.yml", "--manifest", help="Path to workspace manifest.")
_opt_format = typer.Option("table", "--format", "-f", help="Output format: table or yaml.")
_opt_instruction = typer.Option(None, "--instruction", "-i", help="Path to instruction YAML file.")
_opt_output = typer.Option(None, "--output", "-o", help="Save report to a file instead of printing.")


def _resolve_format(fmt: str, output: str | None) -> str:
    """Determine the effective output format.

    When ``--output`` targets a ``.yml`` or ``.yaml`` file, YAML is used
    regardless of ``--format``.  Otherwise the explicit ``--format`` wins.
    """
    if output is not None:
        suffix = Path(output).suffix.lower()
        if suffix in (".yml", ".yaml"):
            return "yaml"
    return fmt


def _write_output(content: str, output: str) -> None:
    """Write *content* to *output* and print a confirmation to stderr."""
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    console.print(f"Report saved to [bold]{path}[/bold]")


def _capture_rich(*renderables: object) -> str:
    """Render Rich objects to plain text (no ANSI codes)."""
    buf = StringIO()
    file_console = Console(file=buf, force_terminal=False, width=200)
    for r in renderables:
        file_console.print(r)
    return buf.getvalue()


def _check_mutual_exclusivity(
    instruction: str | None,
    **cli_options: object,
) -> None:
    """Fail if ``--instruction`` is combined with target/filter options."""
    if instruction is None:
        return
    conflicts = [f"--{k.replace('_', '-')}" for k, v in cli_options.items() if v]
    if conflicts:
        raise typer.BadParameter(
            f"--instruction is mutually exclusive with {', '.join(conflicts)}. "
            "Remove conflicting options or omit --instruction."
        )


# ---------------------------------------------------------------------------
# compare tree
# ---------------------------------------------------------------------------


@app.command("tree")
def compare_tree(
    subtree: Optional[str] = typer.Option(None, "--subtree", "-s", help="Limit scan to a subdirectory."),
    include: Optional[str] = typer.Option(None, "--include", help="Comma-separated include glob patterns."),
    exclude_pattern: Optional[str] = typer.Option(None, "--exclude-pattern", help="Comma-separated exclude glob patterns."),
    names: Optional[str] = _opt_names,
    pattern: Optional[str] = _opt_pattern,
    git_only: bool = _opt_git_only,
    exclude: Optional[str] = _opt_exclude,
    instruction: Optional[str] = _opt_instruction,
    fmt: str = _opt_format,
    output: Optional[str] = _opt_output,
    manifest: Path = _opt_manifest,
) -> None:
    """Compare directory structures across projects."""
    _check_mutual_exclusivity(
        instruction, subtree=subtree, include=include, exclude_pattern=exclude_pattern,
        names=names, pattern=pattern, git_only=git_only, exclude_projects=exclude,
    )

    ws_services = create_services()
    cmp_services = create_comparison_services()

    try:
        m = resolve_manifest(Path(manifest))
        ctx = build_workspace_context(m, ws_services)

        if instruction:
            spec = cmp_services.spec_loader.load(Path(instruction))
            if not isinstance(spec.target, TreeTarget):
                raise ComparisonError("Instruction file specifies 'files' mode, but 'tree' command was invoked.")
            target = spec.target
            filter_ = parse_project_filter(
                ",".join(spec.project_names) if spec.project_names else None,
                None, False, None,
            )
        else:
            target = TreeTarget(
                subtree=subtree,
                include_patterns=tuple(include.split(",")) if include else (),
                exclude_patterns=tuple(exclude_pattern.split(",")) if exclude_pattern else (),
            )
            filter_ = parse_project_filter(names, pattern, git_only, exclude)

        report = run_compare_trees(ctx, cmp_services, target, filter_=filter_)

    except (WorkspaceError, ComparisonError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)

    effective_fmt = _resolve_format(fmt, output)
    if effective_fmt == "yaml":
        content = render_tree_yaml(report)
    else:
        content = _capture_tree_report(report)

    if output:
        _write_output(content, output)
    elif effective_fmt == "yaml":
        typer.echo(content)
    else:
        _print_tree_report(report)


# ---------------------------------------------------------------------------
# compare files
# ---------------------------------------------------------------------------


@app.command("files")
def compare_files_cmd(
    paths: list[str] = typer.Argument(None, help="Relative file paths to compare across projects."),
    granularity: str = typer.Option("survey", "--granularity", "-g", help="Comparison granularity: survey or detail."),
    reference: Optional[str] = typer.Option(
        None,
        "--reference",
        "-r",
        help="Reference project for detail-mode diffs.",
    ),
    names: Optional[str] = _opt_names,
    pattern: Optional[str] = _opt_pattern,
    git_only: bool = _opt_git_only,
    exclude: Optional[str] = _opt_exclude,
    instruction: Optional[str] = _opt_instruction,
    fmt: str = _opt_format,
    output: Optional[str] = _opt_output,
    manifest: Path = _opt_manifest,
) -> None:
    """Compare specific files across projects."""
    _check_mutual_exclusivity(
        instruction, paths=paths, granularity=(granularity != "survey"),
        reference=reference, names=names, pattern=pattern, git_only=git_only, exclude_projects=exclude,
    )

    ws_services = create_services()
    cmp_services = create_comparison_services()

    try:
        m = resolve_manifest(Path(manifest))
        ctx = build_workspace_context(m, ws_services)

        if instruction:
            spec = cmp_services.spec_loader.load(Path(instruction))
            if not isinstance(spec.target, FileTarget):
                raise ComparisonError("Instruction file specifies 'tree' mode, but 'files' command was invoked.")
            target = spec.target
            filter_ = parse_project_filter(
                ",".join(spec.project_names) if spec.project_names else None,
                None, False, None,
            )
        else:
            if not paths:
                raise ComparisonError("Provide at least one file path to compare, or use --instruction.")
            entries = tuple(FileTargetEntry(canonical=p) for p in paths)
            try:
                target = FileTarget(
                    entries=entries,
                    granularity=granularity,
                    reference_project=reference,
                )
            except ValueError as exc:
                raise ComparisonError(str(exc)) from exc
            filter_ = parse_project_filter(names, pattern, git_only, exclude)

        report = run_compare_files(ctx, cmp_services, target, filter_=filter_)

    except (WorkspaceError, ComparisonError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)

    effective_fmt = _resolve_format(fmt, output)
    if effective_fmt == "yaml":
        content = render_file_yaml(report)
    else:
        content = _capture_file_report(report)

    if output:
        _write_output(content, output)
    elif effective_fmt == "yaml":
        typer.echo(content)
    else:
        _print_file_report(report)


# ---------------------------------------------------------------------------
# Rich terminal rendering
# ---------------------------------------------------------------------------


def _build_tree_table(report: TreeReport) -> tuple[Table, str]:
    """Build the Rich table and summary line for a tree report."""
    title = "Architecture Comparison"
    if report.subtree:
        title += f" ({report.subtree})"

    table = Table(title=title)
    table.add_column("Path")
    table.add_column("Type")
    for proj in report.projects:
        table.add_column(proj, justify="center")
    table.add_column("Match", justify="center")
    table.add_column("Similarity", justify="right")

    _add_tree_rows(table, report.matches, report.projects)

    s = report.summary
    summary = (
        f"Summary: {s.total_nodes} nodes — "
        f"{s.in_all} in all, {s.in_some} in some, {s.in_one} unique  "
        f"({s.directories_matched} dirs, {s.files_matched} files)"
    )
    return table, summary


def _print_tree_report(report: TreeReport) -> None:
    """Render a tree comparison as Rich tables to the terminal."""
    table, summary = _build_tree_table(report)
    console.print(table)
    console.print(f"\n[bold]{summary}[/bold]")


def _capture_tree_report(report: TreeReport) -> str:
    """Render a tree comparison to plain text for file output."""
    table, summary = _build_tree_table(report)
    return _capture_rich(table) + "\n" + summary + "\n"


def _add_tree_rows(
    table: Table,
    matches: tuple[NodeMatch, ...],
    projects: tuple[str, ...],
    indent: int = 0,
) -> None:
    """Recursively add rows for matched nodes."""
    for node in matches:
        prefix = "  " * indent
        type_label = "dir" if node.is_directory else "file"
        presence_cells = [
            "[green]\u2713[/green]" if p in node.present_in else "[red]\u2717[/red]"
            for p in projects
        ]
        method_style = {
            "exact": "[green]exact[/green]",
            "case-insensitive": "[yellow]case[/yellow]",
            "fuzzy": "[cyan]fuzzy[/cyan]",
        }
        row = [
            f"{prefix}{node.canonical_path}",
            type_label,
            *presence_cells,
            method_style.get(node.method.value, node.method.value),
            f"{node.similarity:.2f}" if node.method.value == "fuzzy" else "",
        ]
        table.add_row(*row)
        if node.children:
            _add_tree_rows(table, node.children, projects, indent + 1)


def _build_file_renderables(report: FileReport) -> tuple[list[object], str]:
    """Build Rich renderables and summary line for a file report."""
    renderables: list[object] = []
    for result in report.results:
        renderables.extend(_build_single_file_renderables(result, report.projects))

    s = report.summary
    summary = (
        f"Summary: {s.files_compared} files — "
        f"{s.fully_identical} identical, {s.with_differences} different, "
        f"{s.with_errors} errors"
    )
    return renderables, summary


def _print_file_report(report: FileReport) -> None:
    """Render a file comparison as Rich panels to the terminal."""
    renderables, summary = _build_file_renderables(report)
    for r in renderables:
        console.print(r)
    console.print(f"\n[bold]{summary}[/bold]")


def _capture_file_report(report: FileReport) -> str:
    """Render a file comparison to plain text for file output."""
    renderables, summary = _build_file_renderables(report)
    return _capture_rich(*renderables) + "\n" + summary + "\n"


def _build_single_file_renderables(result: FileDiffResult, projects: tuple[str, ...]) -> list[object]:
    """Build Rich renderables for one file's comparison result."""
    status = "[green]identical[/green]" if result.is_identical else "[yellow]differs[/yellow]"
    if result.issue:
        status = "[red]error[/red]"

    header = f"[bold]{result.canonical_path}[/bold] — {status}"
    if result.absent_from:
        header += f"  [dim](absent from: {', '.join(sorted(result.absent_from))})[/dim]"

    renderables: list[object] = []

    if result.content_kind == ContentKind.STRUCTURED and result.field_diffs:
        table = Table(show_header=True, box=None, pad_edge=False)
        table.add_column("Field", style="bold")
        for proj in projects:
            table.add_column(proj)

        for fd in result.field_diffs:
            values = []
            for proj in projects:
                val = fd.values.get(proj)
                if val is None:
                    values.append("[dim]—[/dim]")
                else:
                    values.append(_truncate(str(val), 40))
            style = "" if fd.is_identical else "yellow"
            table.add_row(fd.path, *values, style=style)

        renderables.append(Panel(table, title=header, expand=False))

    elif result.content_kind == ContentKind.UNSTRUCTURED and result.variants:
        if result.reference_diffs:
            lines: list[str] = []
            if result.reference_project is not None:
                lines.append(f"Reference: {result.reference_project}")
            for ref_diff in result.reference_diffs:
                if lines:
                    lines.append("")
                lines.append(f"{result.reference_project} -> {ref_diff.project}")
                if ref_diff.diff_lines:
                    lines.extend(ref_diff.diff_lines)
                else:
                    lines.append("(no changes)")
            if result.similarities:
                lines.append("")
                lines.append("Similarities:")
                for sim in result.similarities:
                    lines.append(f"{sim.project_a} \u2194 {sim.project_b}: {sim.score:.1%}")
            renderables.append(Panel(Text("\n".join(lines)), title=header, expand=False))
        else:
            lines = []
            for i, variant in enumerate(result.variants, 1):
                projs = ", ".join(sorted(variant.projects))
                lines.append(f"  Group {i}: {projs} ({variant.line_count} lines)")
            if result.similarities:
                lines.append("")
                for sim in result.similarities:
                    lines.append(f"  {sim.project_a} \u2194 {sim.project_b}: {sim.score:.1%}")
            renderables.append(Panel("\n".join(lines), title=header, expand=False))

    else:
        renderables.append(Text(header))

    if result.issue:
        renderables.append(Text(f"  {result.issue}"))

    return renderables


def _truncate(text: str, max_len: int) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 1] + "\u2026"
