"""Application use-cases for cross-project comparison."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from ..domain.comparison import (
    ContentKind,
    FileDiffResult,
    FileReport,
    FileTarget,
    FieldDiff,
    TreeReport,
    TreeTarget,
    compute_file_summary,
    compute_pairwise_similarity,
    compute_reference_diffs,
    compute_tree_summary,
    diff_structured,
    group_variants,
    match_tree_nodes,
)
from ..domain.project import ProjectMetadata
from ..exceptions import ComparisonError
from .protocols import FileReader, StructuredParser, TreeScanner


# ---------------------------------------------------------------------------
# Structured-file extension set
# ---------------------------------------------------------------------------

_STRUCTURED_EXTENSIONS: frozenset[str] = frozenset({".toml", ".yaml", ".yml", ".json", ".md"})


def _is_structured(path: str, parser_hint: str | None) -> bool:
    """Determine whether a file should be parsed as structured data."""
    if parser_hint is not None:
        return True
    suffix = Path(path).suffix.lower()
    return suffix in _STRUCTURED_EXTENSIONS


# ---------------------------------------------------------------------------
# Tree comparison
# ---------------------------------------------------------------------------


def compare_trees(
    projects: tuple[ProjectMetadata, ...],
    target: TreeTarget,
    scanner: TreeScanner,
) -> TreeReport:
    """Scan each project's file tree and match nodes hierarchically."""
    all_names = frozenset(p.name for p in projects)
    snapshots = tuple(
        scanner.scan(
            p.path,
            target.subtree,
            target.include_patterns,
            target.exclude_patterns,
            project_name=p.name,
        )
        for p in projects
    )
    matches = match_tree_nodes(snapshots, all_names)
    summary = compute_tree_summary(matches, all_names)
    return TreeReport(
        projects=tuple(p.name for p in projects),
        subtree=target.subtree,
        matches=matches,
        summary=summary,
    )


# ---------------------------------------------------------------------------
# File comparison
# ---------------------------------------------------------------------------


def compare_files(
    projects: tuple[ProjectMetadata, ...],
    target: FileTarget,
    reader: FileReader,
    parser: StructuredParser,
) -> FileReport:
    """Compare specific files across projects.

    For each :class:`FileTargetEntry`, resolves the actual path per project,
    reads content via *reader*, and dispatches to structured or unstructured
    comparison.  Per-file errors are captured in the result, not raised.
    """
    all_names = frozenset(p.name for p in projects)
    if target.reference_project is not None and target.reference_project not in all_names:
        raise ComparisonError(
            f"Unknown reference project {target.reference_project!r}. "
            f"Selected projects: {', '.join(sorted(all_names))}"
        )
    results: list[FileDiffResult] = []

    for entry in target.entries:
        result = _compare_single_file(
            projects, entry.canonical, entry.overrides, entry.selectors,
            entry.parser_hint, target.granularity, target.reference_project,
            all_names, reader, parser,
        )
        results.append(result)

    summary = compute_file_summary(tuple(results))
    return FileReport(
        projects=tuple(p.name for p in projects),
        results=tuple(results),
        summary=summary,
    )


def _compare_single_file(
    projects: tuple[ProjectMetadata, ...],
    canonical: str,
    overrides: Mapping[str, str],
    selectors: tuple[str, ...],
    parser_hint: str | None,
    granularity: str,
    reference_project: str | None,
    all_names: frozenset[str],
    reader: FileReader,
    parser: StructuredParser,
) -> FileDiffResult:
    """Compare one logical file across all projects."""
    actual_paths: dict[str, str] = {}
    contents: dict[str, str] = {}
    issues: list[str] = []

    for project in projects:
        actual = overrides.get(project.name, canonical)
        actual_paths[project.name] = actual
        file_path = project.path / actual
        try:
            contents[project.name] = reader.read(file_path)
        except (OSError, ValueError) as exc:
            issues.append(f"{project.name}: {exc}")

    present_in = frozenset(contents.keys())
    absent_from = all_names - present_in

    if not contents:
        return FileDiffResult(
            canonical_path=canonical,
            actual_paths=actual_paths,
            present_in=present_in,
            absent_from=absent_from,
            content_kind=ContentKind.UNSTRUCTURED,
            issue="; ".join(issues),
        )

    structured = _is_structured(canonical, parser_hint)

    if structured:
        return _diff_structured_file(
            canonical, actual_paths, present_in, absent_from,
            contents, selectors, parser_hint, parser, issues,
        )
    return _diff_unstructured_file(
        canonical, actual_paths, present_in, absent_from, contents,
        granularity, reference_project, issues,
    )


def _diff_structured_file(
    canonical: str,
    actual_paths: dict[str, str],
    present_in: frozenset[str],
    absent_from: frozenset[str],
    contents: dict[str, str],
    selectors: tuple[str, ...],
    parser_hint: str | None,
    parser: StructuredParser,
    issues: list[str],
) -> FileDiffResult:
    """Parse and diff a structured file."""
    extension = Path(canonical).suffix.lower()
    parsed: dict[str, dict] = {}
    for project, text in contents.items():
        try:
            parsed[project] = parser.parse(text, extension=extension, hint=parser_hint)
        except (ComparisonError, ValueError) as exc:
            issues.append(f"{project}: parse error: {exc}")

    field_diffs: tuple[FieldDiff, ...] = ()
    if parsed:
        field_diffs = diff_structured(parsed, selectors)

    return FileDiffResult(
        canonical_path=canonical,
        actual_paths=actual_paths,
        present_in=present_in,
        absent_from=absent_from,
        content_kind=ContentKind.STRUCTURED,
        field_diffs=field_diffs,
        issue="; ".join(issues),
    )


def _diff_unstructured_file(
    canonical: str,
    actual_paths: dict[str, str],
    present_in: frozenset[str],
    absent_from: frozenset[str],
    contents: dict[str, str],
    granularity: str,
    reference_project: str | None,
    issues: list[str],
) -> FileDiffResult:
    """Group variants and compute similarity for an unstructured file."""
    variants = group_variants(contents)
    similarities = compute_pairwise_similarity(contents)
    reference_diffs = ()
    if granularity == "detail":
        if reference_project is None:
            issues.append("Detail granularity requires a reference project.")
        elif reference_project not in contents:
            issues.append(
                f"Reference project {reference_project!r} is missing or unreadable for {canonical}."
            )
        else:
            reference_diffs = compute_reference_diffs(contents, reference_project)

    return FileDiffResult(
        canonical_path=canonical,
        actual_paths=actual_paths,
        present_in=present_in,
        absent_from=absent_from,
        content_kind=ContentKind.UNSTRUCTURED,
        variants=variants,
        similarities=similarities,
        reference_project=reference_project,
        reference_diffs=reference_diffs,
        issue="; ".join(issues),
    )
