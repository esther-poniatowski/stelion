"""Immutable domain models and pure functions for cross-project comparison.

Classes
-------
MatchMethod
    How correspondence between nodes was established.
ContentKind
    Dispatches the comparison strategy for file content.
FileGranularity
    Level of detail for file content comparison.
TreeTarget
    Target specification for architecture (tree) comparison.
FileTargetEntry
    One logical file to compare across projects.
FileTarget
    Target specification for file content comparison.
ComparisonSpec
    Full declarative specification for a comparison operation.
TreeEntry
    A single node within a project's file tree.
TreeSnapshot
    Complete file-tree scan for one project.
NodeMatch
    An N-way mapping of one logical node across projects.
TreeSummary
    Aggregate counts for a tree comparison.
TreeReport
    Full architecture comparison result.
FieldDiff
    One structured field compared across N projects.
VariantGroup
    Projects with identical content for an unstructured file.
PairwiseSimilarity
    Similarity score between two projects for an unstructured file.
ReferenceDiff
    Unified diff against the reference project for one compared file.
FileDiffResult
    Comparison result for one logical file across projects.
FileSummary
    Aggregate counts for a file comparison.
FileReport
    Full file comparison result.

Functions
---------
match_tree_nodes
    Match file-tree nodes across projects hierarchically.
diff_structured
    Compare parsed structured data field by field across projects.
group_variants
    Group projects by identical content.
compute_pairwise_similarity
    Compute SequenceMatcher ratio for every pair of projects.
compute_reference_diffs
    Compute unified diffs from the reference project to every other project.
compute_tree_summary
    Derive aggregate counts from matched nodes.
compute_file_summary
    Derive aggregate counts from file comparison results.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from difflib import SequenceMatcher, unified_diff
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class MatchMethod(StrEnum):
    """How correspondence between nodes was established."""

    EXACT = "exact"
    CASE_INSENSITIVE = "case-insensitive"
    FUZZY = "fuzzy"


class ContentKind(StrEnum):
    """Dispatches the comparison strategy for file content."""

    STRUCTURED = "structured"
    UNSTRUCTURED = "unstructured"


class FileGranularity(StrEnum):
    """Level of detail for file content comparison."""

    SURVEY = "survey"
    DETAIL = "detail"


# ---------------------------------------------------------------------------
# Specification types (input)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TreeTarget:
    """Target specification for architecture (tree) comparison.

    Attributes
    ----------
    subtree : str | None
        Relative path prefix to restrict the comparison scope.
    include_patterns : tuple[str, ...]
        Glob patterns for paths to include.
    exclude_patterns : tuple[str, ...]
        Glob patterns for paths to exclude.
    """

    subtree: str | None = None
    include_patterns: tuple[str, ...] = ()
    exclude_patterns: tuple[str, ...] = ()


@dataclass(frozen=True)
class FileTargetEntry:
    """One logical file to compare across projects.

    Attributes
    ----------
    canonical : str
        The standard relative path (e.g. ``pyproject.toml``).
    overrides : Mapping[str, str]
        Project-specific path remappings: ``{project_name: actual_path}``.
    selectors : tuple[str, ...]
        Dotted field paths to compare for structured files (empty = all).
    parser_hint : str | None
        Force a parser regardless of extension (e.g. ``"toml"``).
    """

    canonical: str
    overrides: Mapping[str, str] = field(default_factory=dict)
    selectors: tuple[str, ...] = ()
    parser_hint: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "overrides", MappingProxyType(dict(self.overrides)))


@dataclass(frozen=True)
class FileTarget:
    """Target specification for file content comparison.

    Attributes
    ----------
    entries : tuple[FileTargetEntry, ...]
        Logical files to compare.
    granularity : FileGranularity
        Level of detail for the comparison.
    reference_project : str | None
        Project used as the baseline for detail-level diffs.
    """

    entries: tuple[FileTargetEntry, ...]
    granularity: FileGranularity = FileGranularity.SURVEY
    reference_project: str | None = None

    def __post_init__(self) -> None:
        if not self.entries:
            raise ValueError("File target must include at least one entry.")
        if not isinstance(self.granularity, FileGranularity):
            object.__setattr__(
                self, "granularity", FileGranularity(self.granularity)
            )
        if self.granularity == FileGranularity.DETAIL and not self.reference_project:
            raise ValueError("Detail granularity requires a reference project.")
        if self.granularity != FileGranularity.DETAIL and self.reference_project is not None:
            raise ValueError("A reference project is only valid with detail granularity.")


@dataclass(frozen=True)
class ComparisonSpec:
    """Full declarative specification for a comparison operation.

    Constructed from an instruction file or from CLI arguments.
    ``target`` is either a :class:`TreeTarget` or a :class:`FileTarget`
    --- the tagged union makes invalid states unrepresentable.

    Attributes
    ----------
    project_names : tuple[str, ...]
        Names of projects to compare.
    target : TreeTarget | FileTarget
        What to compare (architecture tree or file contents).
    """

    project_names: tuple[str, ...]
    target: TreeTarget | FileTarget


# ---------------------------------------------------------------------------
# Tree comparison result types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TreeEntry:
    """A single node within a project's file tree.

    Attributes
    ----------
    relative_path : str
        Forward-slash path relative to the project root.
    project : str
        Name of the project this entry belongs to.
    is_directory : bool
        Whether the node is a directory.
    """

    relative_path: str
    project: str
    is_directory: bool


@dataclass(frozen=True)
class TreeSnapshot:
    """Complete file-tree scan for one project.

    Attributes
    ----------
    project : str
        Project name.
    root : str
        Filesystem root used for the scan.
    entries : tuple[TreeEntry, ...]
        All nodes discovered in the tree.
    """

    project: str
    root: str
    entries: tuple[TreeEntry, ...]


@dataclass(frozen=True)
class NodeMatch:
    """An N-way mapping of one logical node across projects.

    Presence is explicit: ``present_in`` lists projects that contain this
    node, ``absent_from`` lists selected projects that do not.

    Attributes
    ----------
    canonical_path : str
        Normalized path used as the canonical key.
    resolved : Mapping[str, str]
        Mapping from project name to actual relative path.
    present_in : frozenset[str]
        Projects that contain this node.
    absent_from : frozenset[str]
        Selected projects that lack this node.
    method : MatchMethod
        How correspondence was established.
    similarity : float
        Match confidence score (1.0 for exact).
    is_directory : bool
        Whether the node is a directory.
    children : tuple[NodeMatch, ...]
        Recursively matched child nodes (directories only).
    """

    canonical_path: str
    resolved: Mapping[str, str]
    present_in: frozenset[str]
    absent_from: frozenset[str]
    method: MatchMethod
    similarity: float
    is_directory: bool
    children: tuple[NodeMatch, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "resolved", MappingProxyType(dict(self.resolved)))


@dataclass(frozen=True)
class TreeSummary:
    """Aggregate counts for a tree comparison.

    Attributes
    ----------
    total_nodes : int
        Total number of matched logical nodes.
    in_all : int
        Nodes present in every compared project.
    in_some : int
        Nodes present in more than one but not all projects.
    in_one : int
        Nodes unique to a single project.
    directories_matched : int
        Number of directory nodes.
    files_matched : int
        Number of file nodes.
    """

    total_nodes: int
    in_all: int
    in_some: int
    in_one: int
    directories_matched: int
    files_matched: int


@dataclass(frozen=True)
class TreeReport:
    """Full architecture comparison result.

    Attributes
    ----------
    projects : tuple[str, ...]
        Names of the compared projects.
    subtree : str | None
        Subtree prefix that was compared, or ``None`` for the full tree.
    matches : tuple[NodeMatch, ...]
        Top-level matched nodes.
    summary : TreeSummary
        Aggregate counts.
    """

    projects: tuple[str, ...]
    subtree: str | None
    matches: tuple[NodeMatch, ...]
    summary: TreeSummary


# ---------------------------------------------------------------------------
# File comparison result types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FieldDiff:
    """One structured field compared across N projects.

    Status is derived from the values: all equal means identical, some
    ``None`` means partial presence, all different means diverged.

    Attributes
    ----------
    path : str
        Dotted field path within the structured document.
    values : Mapping[str, str | None]
        Per-project stringified values (``None`` if absent).
    """

    path: str
    values: Mapping[str, str | None]

    def __post_init__(self) -> None:
        object.__setattr__(self, "values", MappingProxyType(dict(self.values)))

    @property
    def is_identical(self) -> bool:
        """All projects have the same non-None value.

        Returns
        -------
        bool
            True when every project has the field and all values are equal.
        """
        vals = [v for v in self.values.values() if v is not None]
        return len(vals) == len(self.values) and len(set(vals)) == 1

    @property
    def is_partial(self) -> bool:
        """The field is absent in at least one project.

        Returns
        -------
        bool
            True when at least one project lacks this field.
        """
        return any(v is None for v in self.values.values())


@dataclass(frozen=True)
class VariantGroup:
    """Projects with identical content for an unstructured file.

    Attributes
    ----------
    projects : frozenset[str]
        Project names sharing the same content.
    digest : str
        Truncated SHA-256 hex digest of the content.
    line_count : int
        Number of lines in the content.
    """

    projects: frozenset[str]
    digest: str
    line_count: int


@dataclass(frozen=True)
class PairwiseSimilarity:
    """Similarity score between two projects for an unstructured file.

    Attributes
    ----------
    project_a : str
        First project name.
    project_b : str
        Second project name.
    score : float
        SequenceMatcher ratio between the two files.
    """

    project_a: str
    project_b: str
    score: float


@dataclass(frozen=True)
class ReferenceDiff:
    """Unified diff against the reference project for one compared file.

    Attributes
    ----------
    project : str
        Name of the project being compared to the reference.
    diff_lines : tuple[str, ...]
        Lines of the unified diff output.
    """

    project: str
    diff_lines: tuple[str, ...]


@dataclass(frozen=True)
class FileDiffResult:
    """Comparison result for one logical file across projects.

    Attributes
    ----------
    canonical_path : str
        Normalized file path used as the comparison key.
    actual_paths : Mapping[str, str]
        Per-project resolved file paths.
    present_in : frozenset[str]
        Projects where the file exists.
    absent_from : frozenset[str]
        Projects where the file is missing.
    content_kind : ContentKind
        Whether the file was compared as structured or unstructured.
    field_diffs : tuple[FieldDiff, ...]
        Per-field diffs (structured files only).
    variants : tuple[VariantGroup, ...]
        Content groups (unstructured files only).
    similarities : tuple[PairwiseSimilarity, ...]
        Pairwise similarity scores (unstructured files only).
    reference_project : str | None
        Baseline project for detail-level diffs.
    reference_diffs : tuple[ReferenceDiff, ...]
        Unified diffs against the reference project.
    issue : str
        Error message if comparison failed for this file.
    """

    canonical_path: str
    actual_paths: Mapping[str, str]
    present_in: frozenset[str]
    absent_from: frozenset[str]
    content_kind: ContentKind
    field_diffs: tuple[FieldDiff, ...] = ()
    variants: tuple[VariantGroup, ...] = ()
    similarities: tuple[PairwiseSimilarity, ...] = ()
    reference_project: str | None = None
    reference_diffs: tuple[ReferenceDiff, ...] = ()
    issue: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "actual_paths", MappingProxyType(dict(self.actual_paths)))

    @property
    def is_identical(self) -> bool:
        """All projects have identical content (no absent, no differences).

        Returns
        -------
        bool
            True when no project is missing the file and all content matches.
        """
        if self.issue or self.absent_from:
            return False
        if self.content_kind == ContentKind.STRUCTURED:
            return all(fd.is_identical for fd in self.field_diffs)
        return len(self.variants) == 1


@dataclass(frozen=True)
class FileSummary:
    """Aggregate counts for a file comparison.

    Attributes
    ----------
    files_compared : int
        Total number of logical files compared.
    fully_identical : int
        Files identical across all projects.
    with_differences : int
        Files with at least one difference.
    with_errors : int
        Files that could not be compared due to errors.
    """

    files_compared: int
    fully_identical: int
    with_differences: int
    with_errors: int


@dataclass(frozen=True)
class FileReport:
    """Full file comparison result.

    Attributes
    ----------
    projects : tuple[str, ...]
        Names of the compared projects.
    results : tuple[FileDiffResult, ...]
        Per-file comparison results.
    summary : FileSummary
        Aggregate counts.
    """

    projects: tuple[str, ...]
    results: tuple[FileDiffResult, ...]
    summary: FileSummary


# ---------------------------------------------------------------------------
# Pure domain functions — tree matching
# ---------------------------------------------------------------------------

_FUZZY_THRESHOLD = 0.6


def match_tree_nodes(
    snapshots: tuple[TreeSnapshot, ...],
    all_projects: frozenset[str],
) -> tuple[NodeMatch, ...]:
    """Match file-tree nodes across projects hierarchically.

    Directories are matched first at each depth level, then files within
    matched directories.  Each level uses a three-pass strategy: exact
    name, case-insensitive, then fuzzy (above ``_FUZZY_THRESHOLD``).

    Parameters
    ----------
    snapshots : tuple[TreeSnapshot, ...]
        Per-project file-tree scans.
    all_projects : frozenset[str]
        Complete set of project names being compared.

    Returns
    -------
    tuple[NodeMatch, ...]
        Hierarchically matched nodes sorted by canonical path.
    """
    entries_by_project: dict[str, list[TreeEntry]] = {s.project: list(s.entries) for s in snapshots}
    return _match_at_level(entries_by_project, all_projects, prefix="")


def _match_at_level(
    entries_by_project: dict[str, list[TreeEntry]],
    all_projects: frozenset[str],
    prefix: str,
) -> tuple[NodeMatch, ...]:
    """Recursively match nodes at a given directory level.

    Parameters
    ----------
    entries_by_project : dict[str, list[TreeEntry]]
        Remaining tree entries keyed by project name.
    all_projects : frozenset[str]
        Complete set of project names being compared.
    prefix : str
        Current directory path prefix.

    Returns
    -------
    tuple[NodeMatch, ...]
        Matched nodes at this level and below, sorted by canonical path.
    """
    dir_entries: dict[str, dict[str, str]] = {}  # canonical -> {project: actual}
    file_entries: dict[str, dict[str, str]] = {}

    for project, entries in entries_by_project.items():
        for entry in entries:
            rel = entry.relative_path
            if not _is_direct_child(rel, prefix):
                continue
            name = _basename(rel)
            bucket = dir_entries if entry.is_directory else file_entries
            bucket.setdefault(name, {})[project] = rel

    dir_matches = _three_pass_match(dir_entries, all_projects, is_directory=True, prefix=prefix)
    file_matches = _three_pass_match(file_entries, all_projects, is_directory=False, prefix=prefix)

    # Recurse into matched directories.
    enriched_dirs: list[NodeMatch] = []
    for dm in dir_matches:
        child_entries: dict[str, list[TreeEntry]] = {}
        for project, actual_path in dm.resolved.items():
            child_entries[project] = [
                e for e in entries_by_project.get(project, [])
                if e.relative_path.startswith(actual_path + "/")
            ]
        children = _match_at_level(child_entries, all_projects, prefix=dm.canonical_path)
        if children != dm.children:
            dm = NodeMatch(
                canonical_path=dm.canonical_path,
                resolved=dm.resolved,
                present_in=dm.present_in,
                absent_from=dm.absent_from,
                method=dm.method,
                similarity=dm.similarity,
                is_directory=True,
                children=children,
            )
        enriched_dirs.append(dm)

    return tuple(sorted(enriched_dirs + file_matches, key=lambda m: m.canonical_path))


def _three_pass_match(
    items: dict[str, dict[str, str]],
    all_projects: frozenset[str],
    *,
    is_directory: bool,
    prefix: str = "",
) -> list[NodeMatch]:
    """Three-pass matching: exact, case-insensitive, then fuzzy.

    *prefix* is prepended to basenames to produce full canonical paths
    (e.g. prefix ``"docs"`` + name ``"guide.md"`` gives ``"docs/guide.md"``).

    Parameters
    ----------
    items : dict[str, dict[str, str]]
        Basename to ``{project: actual_path}`` mapping.
    all_projects : frozenset[str]
        Complete set of project names being compared.
    is_directory : bool
        Whether the items are directories.
    prefix : str
        Parent directory path prepended to canonical names.

    Returns
    -------
    list[NodeMatch]
        Matched nodes produced by the three passes.
    """
    results: list[NodeMatch] = []
    remaining: dict[str, dict[str, str]] = dict(items)

    # Pass 1: exact name match — names that appear in multiple projects.
    exact_keys = [k for k, v in remaining.items() if len(v) > 1]
    for key in exact_keys:
        resolved = remaining.pop(key)
        results.append(
            _make_match(key, resolved, all_projects, MatchMethod.EXACT, 1.0, is_directory, prefix)
        )

    # Single-project entries — candidates for case-insensitive and fuzzy.
    singles: dict[str, dict[str, str]] = {k: v for k, v in remaining.items() if len(v) == 1}
    remaining = {k: v for k, v in remaining.items() if len(v) != 1}
    # Also add any multi-project leftovers back (shouldn't happen, but be safe).
    for k, v in remaining.items():
        results.append(
            _make_match(k, v, all_projects, MatchMethod.EXACT, 1.0, is_directory, prefix)
        )

    # Pass 2: case-insensitive merging among singles.
    ci_groups: dict[str, list[tuple[str, dict[str, str]]]] = {}
    for name, projects in singles.items():
        ci_groups.setdefault(name.lower(), []).append((name, projects))

    unmatched: dict[str, dict[str, str]] = {}
    for _lower, group in ci_groups.items():
        if len(group) > 1:
            canonical = group[0][0]
            merged: dict[str, str] = {}
            for _name, projs in group:
                merged.update(projs)
            results.append(
                _make_match(
                    canonical, merged, all_projects, MatchMethod.CASE_INSENSITIVE, 1.0, is_directory, prefix,
                )
            )
        else:
            name, projs = group[0]
            unmatched[name] = projs

    # Pass 3: fuzzy matching among remaining unmatched singles.
    unmatched_names = list(unmatched.keys())
    used: set[str] = set()
    while True:
        cluster = _best_fuzzy_cluster(unmatched, used)
        if cluster is None:
            break
        canonical, member_names, merged, similarity = cluster
        results.append(
            _make_match(
                canonical, merged, all_projects, MatchMethod.FUZZY, similarity, is_directory, prefix,
            )
        )
        used.update(member_names)

    # Remaining truly unique entries.
    for name in unmatched_names:
        if name not in used:
            results.append(
                _make_match(name, unmatched[name], all_projects, MatchMethod.EXACT, 1.0, is_directory, prefix)
            )

    return results


def _best_fuzzy_cluster(
    unmatched: dict[str, dict[str, str]],
    used: set[str],
) -> tuple[str, frozenset[str], dict[str, str], float] | None:
    """Build the strongest fuzzy cluster available across distinct projects.

    Parameters
    ----------
    unmatched : dict[str, dict[str, str]]
        Remaining single-project entries to cluster.
    used : set[str]
        Names already consumed by a previous cluster.

    Returns
    -------
    tuple[str, frozenset[str], dict[str, str], float] | None
        ``(canonical, member_names, merged_resolved, avg_similarity)``
        or ``None`` if no cluster exceeds the threshold.
    """
    available = sorted(name for name in unmatched if name not in used)
    best_cluster: tuple[str, frozenset[str], dict[str, str], float] | None = None

    for seed in available:
        merged = dict(unmatched[seed])
        best_by_project: dict[str, tuple[str, float]] = {}
        for candidate in available:
            if candidate == seed:
                continue
            candidate_project = _single_project_name(unmatched[candidate])
            if candidate_project in merged:
                continue
            score = SequenceMatcher(None, seed.lower(), candidate.lower()).ratio()
            if score < _FUZZY_THRESHOLD:
                continue
            current = best_by_project.get(candidate_project)
            if current is None or score > current[1]:
                best_by_project[candidate_project] = (candidate, score)

        if not best_by_project:
            continue

        member_names = {seed}
        scores: list[float] = []
        for candidate, score in best_by_project.values():
            member_names.add(candidate)
            merged.update(unmatched[candidate])
            scores.append(score)

        similarity = sum(scores) / len(scores)
        cluster = (seed, frozenset(member_names), merged, similarity)
        if _is_better_fuzzy_cluster(cluster, best_cluster):
            best_cluster = cluster

    return best_cluster


def _is_better_fuzzy_cluster(
    candidate: tuple[str, frozenset[str], dict[str, str], float],
    incumbent: tuple[str, frozenset[str], dict[str, str], float] | None,
) -> bool:
    """Prefer clusters with more projects, then higher average similarity.

    Parameters
    ----------
    candidate : tuple[str, frozenset[str], dict[str, str], float]
        Cluster being evaluated.
    incumbent : tuple[str, frozenset[str], dict[str, str], float] | None
        Current best cluster, or ``None``.

    Returns
    -------
    bool
        True if *candidate* should replace *incumbent*.
    """
    if incumbent is None:
        return True
    candidate_name, candidate_members, _candidate_resolved, candidate_score = candidate
    incumbent_name, incumbent_members, _incumbent_resolved, incumbent_score = incumbent
    return (
        len(candidate_members),
        candidate_score,
        -len(candidate_name),
        candidate_name,
    ) > (
        len(incumbent_members),
        incumbent_score,
        -len(incumbent_name),
        incumbent_name,
    )


def _single_project_name(resolved: Mapping[str, str]) -> str:
    """Return the sole project key for a single-project node candidate.

    Parameters
    ----------
    resolved : Mapping[str, str]
        Single-entry mapping from project name to actual path.

    Returns
    -------
    str
        The project name.
    """
    return next(iter(resolved))


def _make_match(
    name: str,
    resolved: dict[str, str],
    all_projects: frozenset[str],
    method: MatchMethod,
    similarity: float,
    is_directory: bool,
    prefix: str = "",
) -> NodeMatch:
    canonical = f"{prefix}/{name}" if prefix else name
    present = frozenset(resolved.keys())
    return NodeMatch(
        canonical_path=canonical,
        resolved=resolved,
        present_in=present,
        absent_from=all_projects - present,
        method=method,
        similarity=similarity,
        is_directory=is_directory,
    )


def _is_direct_child(path: str, prefix: str) -> bool:
    """True if *path* is an immediate child of *prefix*.

    Parameters
    ----------
    path : str
        Forward-slash relative path to test.
    prefix : str
        Parent directory path (empty string for root).

    Returns
    -------
    bool
        Whether *path* is a direct child of *prefix*.
    """
    if prefix:
        if not path.startswith(prefix + "/"):
            return False
        remainder = path[len(prefix) + 1:]
    else:
        remainder = path
    return "/" not in remainder


def _basename(path: str) -> str:
    """Return the last component of a forward-slash path.

    Parameters
    ----------
    path : str
        Forward-slash delimited path.

    Returns
    -------
    str
        Final path component.
    """
    return path.rsplit("/", 1)[-1]


# ---------------------------------------------------------------------------
# Pure domain functions — structured file diffing
# ---------------------------------------------------------------------------


def diff_structured(
    contents: Mapping[str, dict],
    selectors: tuple[str, ...] = (),
) -> tuple[FieldDiff, ...]:
    """Compare parsed structured data field by field across projects.

    Parameters
    ----------
    contents : Mapping[str, dict]
        ``{project_name: parsed_dict}`` for each project that has this file.
    selectors : tuple[str, ...]
        Dotted field paths to limit the comparison. Empty means compare all.

    Returns
    -------
    tuple[FieldDiff, ...]
        Per-field comparison results.
    """
    if selectors:
        return tuple(_diff_selected_fields(contents, selectors))
    all_paths = _collect_all_paths(contents)
    return tuple(
        FieldDiff(
            path=p,
            values={proj: _resolve_dotted(d, p) for proj, d in contents.items()},
        )
        for p in sorted(all_paths)
    )


def _diff_selected_fields(
    contents: Mapping[str, dict],
    selectors: tuple[str, ...],
) -> list[FieldDiff]:
    results: list[FieldDiff] = []
    for selector in selectors:
        values: dict[str, str | None] = {}
        for proj, data in contents.items():
            values[proj] = _resolve_dotted(data, selector)
        results.append(FieldDiff(path=selector, values=values))
    return results


def _collect_all_paths(contents: Mapping[str, dict]) -> set[str]:
    """Enumerate all dotted paths across every project's parsed dict.

    Parameters
    ----------
    contents : Mapping[str, dict]
        Per-project parsed dictionaries.

    Returns
    -------
    set[str]
        Union of all dotted leaf paths found across projects.
    """
    paths: set[str] = set()
    for data in contents.values():
        _walk_dict(data, "", paths)
    return paths


def _walk_dict(d: dict, prefix: str, out: set[str]) -> None:
    for key, value in d.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            _walk_dict(value, path, out)
        else:
            out.add(path)


def _resolve_dotted(d: dict, path: str) -> str | None:
    """Walk a nested dict by dotted path. Returns ``None`` if absent.

    Parameters
    ----------
    d : dict
        Nested dictionary to traverse.
    path : str
        Dotted key path (e.g. ``"tool.poetry.name"``).

    Returns
    -------
    str | None
        Stringified leaf value, or ``None`` if the path does not exist.
    """
    parts = path.split(".")
    current: object = d
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    if isinstance(current, dict):
        return str(current)
    return str(current)


# ---------------------------------------------------------------------------
# Pure domain functions — unstructured file comparison
# ---------------------------------------------------------------------------


def group_variants(contents: Mapping[str, str]) -> tuple[VariantGroup, ...]:
    """Group projects by identical content.

    Returns groups sorted by descending size (largest group first).

    Parameters
    ----------
    contents : Mapping[str, str]
        Per-project raw file content.

    Returns
    -------
    tuple[VariantGroup, ...]
        Groups sorted by descending member count.
    """
    by_digest: dict[str, tuple[set[str], int]] = {}
    for project, text in contents.items():
        digest = hashlib.sha256(text.encode()).hexdigest()[:16]
        if digest not in by_digest:
            by_digest[digest] = (set(), text.count("\n") + 1)
        by_digest[digest][0].add(project)

    groups = [
        VariantGroup(projects=frozenset(projs), digest=digest, line_count=lc)
        for digest, (projs, lc) in by_digest.items()
    ]
    return tuple(sorted(groups, key=lambda g: (-len(g.projects), g.digest)))


def compute_pairwise_similarity(
    contents: Mapping[str, str],
) -> tuple[PairwiseSimilarity, ...]:
    """Compute SequenceMatcher ratio for every pair of projects.

    Parameters
    ----------
    contents : Mapping[str, str]
        Per-project raw file content.

    Returns
    -------
    tuple[PairwiseSimilarity, ...]
        Similarity scores for all unique project pairs.
    """
    projects = sorted(contents.keys())
    results: list[PairwiseSimilarity] = []
    for i, a in enumerate(projects):
        for b in projects[i + 1:]:
            score = SequenceMatcher(None, contents[a], contents[b]).ratio()
            results.append(PairwiseSimilarity(project_a=a, project_b=b, score=score))
    return tuple(results)


def compute_reference_diffs(
    contents: Mapping[str, str],
    reference_project: str,
) -> tuple[ReferenceDiff, ...]:
    """Compute unified diffs from the reference project to every other project.

    Parameters
    ----------
    contents : Mapping[str, str]
        Per-project raw file content.
    reference_project : str
        Project name used as the diff baseline.

    Returns
    -------
    tuple[ReferenceDiff, ...]
        Unified diffs for each non-reference project.
    """
    if reference_project not in contents:
        raise ValueError(f"Reference project {reference_project!r} has no readable content.")

    reference_lines = contents[reference_project].splitlines()
    diffs: list[ReferenceDiff] = []
    for project in sorted(contents):
        if project == reference_project:
            continue
        diff_lines = tuple(
            unified_diff(
                reference_lines,
                contents[project].splitlines(),
                fromfile=reference_project,
                tofile=project,
                lineterm="",
            )
        )
        diffs.append(ReferenceDiff(project=project, diff_lines=diff_lines))
    return tuple(diffs)


# ---------------------------------------------------------------------------
# Pure domain functions — summaries
# ---------------------------------------------------------------------------


def compute_tree_summary(
    matches: tuple[NodeMatch, ...],
    all_projects: frozenset[str],
) -> TreeSummary:
    """Derive aggregate counts from matched nodes.

    Parameters
    ----------
    matches : tuple[NodeMatch, ...]
        Top-level matched nodes (children are counted recursively).
    all_projects : frozenset[str]
        Complete set of project names being compared.

    Returns
    -------
    TreeSummary
        Aggregate presence and type counts.
    """
    total = 0
    in_all = 0
    in_some = 0
    in_one = 0
    dirs = 0
    files = 0

    def _count(nodes: tuple[NodeMatch, ...]) -> None:
        nonlocal total, in_all, in_some, in_one, dirs, files
        for node in nodes:
            total += 1
            n = len(node.present_in)
            if n == len(all_projects):
                in_all += 1
            elif n == 1:
                in_one += 1
            else:
                in_some += 1
            if node.is_directory:
                dirs += 1
            else:
                files += 1
            _count(node.children)

    _count(matches)
    return TreeSummary(
        total_nodes=total,
        in_all=in_all,
        in_some=in_some,
        in_one=in_one,
        directories_matched=dirs,
        files_matched=files,
    )


def compute_file_summary(results: tuple[FileDiffResult, ...]) -> FileSummary:
    """Derive aggregate counts from file comparison results.

    Parameters
    ----------
    results : tuple[FileDiffResult, ...]
        Per-file comparison results.

    Returns
    -------
    FileSummary
        Counts of identical, different, and errored files.
    """
    errors = sum(1 for r in results if r.issue)
    identical = sum(1 for r in results if r.is_identical)
    differences = sum(1 for r in results if not r.issue and not r.is_identical)
    return FileSummary(
        files_compared=len(results),
        fully_identical=identical,
        with_differences=differences,
        with_errors=errors,
    )
