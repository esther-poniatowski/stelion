"""Tests for cross-project comparison domain, application, and infrastructure."""

from __future__ import annotations

from pathlib import Path

import pytest

from stelion.workspace.domain.comparison import (
    ContentKind,
    FieldDiff,
    FileDiffResult,
    FileReport,
    FileSummary,
    FileTargetEntry,
    FileTarget,
    MatchMethod,
    NodeMatch,
    PairwiseSimilarity,
    TreeEntry,
    TreeReport,
    TreeSnapshot,
    TreeSummary,
    VariantGroup,
    compute_file_summary,
    compute_pairwise_similarity,
    compute_tree_summary,
    diff_structured,
    group_variants,
    match_tree_nodes,
)
from stelion.workspace.domain.project import MetadataStatus, ProjectMetadata
from stelion.workspace.application.comparison import compare_files, compare_trees
from stelion.workspace.domain.comparison import TreeTarget
from stelion.workspace.infrastructure.structured_parsers import (
    DispatchingParser,
    JsonParser,
    TomlParser,
    YamlParser,
)
from stelion.workspace.infrastructure.spec_loader import YamlSpecLoader
from stelion.workspace.infrastructure.tree_scanner import LocalTreeScanner
from stelion.workspace.infrastructure.renderers.comparison import (
    render_file_yaml,
    render_tree_yaml,
)
from stelion.workspace.exceptions import ComparisonError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _snapshot(project: str, paths: list[tuple[str, bool]]) -> TreeSnapshot:
    """Build a synthetic TreeSnapshot."""
    entries = tuple(TreeEntry(relative_path=p, project=project, is_directory=d) for p, d in paths)
    return TreeSnapshot(project=project, root="", entries=entries)


def _project(name: str, path: Path) -> ProjectMetadata:
    return ProjectMetadata(
        name=name,
        path=path,
        description="",
        version="0.0.0",
        homepage="",
        has_git=True,
        languages=(),
        status=MetadataStatus.CURRENT,
        issue="",
    )


# ===========================================================================
# Domain: match_tree_nodes
# ===========================================================================


class TestMatchTreeNodes:
    """Tests for the hierarchical tree matching algorithm."""

    def test_exact_match(self) -> None:
        a = _snapshot("alpha", [("src", True), ("src/main.py", False), ("README.md", False)])
        b = _snapshot("beta", [("src", True), ("src/main.py", False), ("README.md", False)])
        all_projects = frozenset({"alpha", "beta"})

        matches = match_tree_nodes((a, b), all_projects)

        paths = {m.canonical_path for m in matches}
        assert "README.md" in paths
        assert "src" in paths
        for m in matches:
            assert m.present_in == all_projects
            assert m.absent_from == frozenset()
            assert m.method == MatchMethod.EXACT

    def test_case_insensitive_match(self) -> None:
        a = _snapshot("alpha", [("README.md", False)])
        b = _snapshot("beta", [("readme.md", False)])
        all_projects = frozenset({"alpha", "beta"})

        matches = match_tree_nodes((a, b), all_projects)

        assert len(matches) == 1
        assert matches[0].method == MatchMethod.CASE_INSENSITIVE
        assert matches[0].present_in == all_projects

    def test_fuzzy_match(self) -> None:
        a = _snapshot("alpha", [("architecture.md", False)])
        b = _snapshot("beta", [("ARCHITECTURE.txt", False)])
        all_projects = frozenset({"alpha", "beta"})

        matches = match_tree_nodes((a, b), all_projects)

        # Should match case-insensitively or fuzzy depending on similarity.
        assert len(matches) == 1
        assert matches[0].present_in == all_projects

    def test_unique_entries(self) -> None:
        a = _snapshot("alpha", [("README.md", False), ("CHANGELOG.md", False)])
        b = _snapshot("beta", [("README.md", False)])
        all_projects = frozenset({"alpha", "beta"})

        matches = match_tree_nodes((a, b), all_projects)

        by_path = {m.canonical_path: m for m in matches}
        assert by_path["README.md"].present_in == all_projects
        assert by_path["CHANGELOG.md"].present_in == frozenset({"alpha"})
        assert by_path["CHANGELOG.md"].absent_from == frozenset({"beta"})

    def test_directory_matching_with_children(self) -> None:
        a = _snapshot("alpha", [
            ("docs", True),
            ("docs/guide.md", False),
        ])
        b = _snapshot("beta", [
            ("docs", True),
            ("docs/guide.md", False),
            ("docs/extra.md", False),
        ])
        all_projects = frozenset({"alpha", "beta"})

        matches = match_tree_nodes((a, b), all_projects)

        docs_match = next(m for m in matches if m.canonical_path == "docs")
        assert docs_match.is_directory
        assert docs_match.present_in == all_projects

        child_paths = {c.canonical_path for c in docs_match.children}
        assert "docs/guide.md" in child_paths
        assert "docs/extra.md" in child_paths

    def test_three_projects_partial_presence(self) -> None:
        a = _snapshot("alpha", [("config.toml", False)])
        b = _snapshot("beta", [("config.toml", False)])
        c = _snapshot("gamma", [])
        all_projects = frozenset({"alpha", "beta", "gamma"})

        matches = match_tree_nodes((a, b, c), all_projects)

        assert len(matches) == 1
        m = matches[0]
        assert m.present_in == frozenset({"alpha", "beta"})
        assert m.absent_from == frozenset({"gamma"})

    def test_fuzzy_matching_clusters_three_projects(self) -> None:
        a = _snapshot("alpha", [("guide", True)])
        b = _snapshot("beta", [("guides", True)])
        c = _snapshot("gamma", [("guidance", True)])
        all_projects = frozenset({"alpha", "beta", "gamma"})

        matches = match_tree_nodes((a, b, c), all_projects)

        assert len(matches) == 1
        match = matches[0]
        assert match.method == MatchMethod.FUZZY
        assert match.present_in == all_projects


# ===========================================================================
# Domain: diff_structured
# ===========================================================================


class TestDiffStructured:
    """Tests for structured field-by-field comparison."""

    def test_identical_dicts(self) -> None:
        contents = {
            "alpha": {"project": {"name": "foo", "version": "1.0"}},
            "beta": {"project": {"name": "foo", "version": "1.0"}},
        }
        diffs = diff_structured(contents)
        assert all(fd.is_identical for fd in diffs)

    def test_different_values(self) -> None:
        contents = {
            "alpha": {"project": {"name": "alpha", "version": "1.0"}},
            "beta": {"project": {"name": "beta", "version": "2.0"}},
        }
        diffs = diff_structured(contents)
        by_path = {fd.path: fd for fd in diffs}
        assert not by_path["project.name"].is_identical
        assert by_path["project.name"].values["alpha"] == "alpha"
        assert by_path["project.name"].values["beta"] == "beta"

    def test_missing_fields(self) -> None:
        contents = {
            "alpha": {"project": {"name": "foo", "version": "1.0"}},
            "beta": {"project": {"name": "foo"}},
        }
        diffs = diff_structured(contents)
        by_path = {fd.path: fd for fd in diffs}
        assert by_path["project.version"].values["beta"] is None
        assert by_path["project.version"].is_partial

    def test_selectors_limit_fields(self) -> None:
        contents = {
            "alpha": {"project": {"name": "foo", "version": "1.0", "desc": "A"}},
            "beta": {"project": {"name": "bar", "version": "2.0", "desc": "B"}},
        }
        diffs = diff_structured(contents, selectors=("project.name",))
        assert len(diffs) == 1
        assert diffs[0].path == "project.name"

    def test_extra_fields(self) -> None:
        contents = {
            "alpha": {"a": "1"},
            "beta": {"a": "1", "b": "2"},
        }
        diffs = diff_structured(contents)
        by_path = {fd.path: fd for fd in diffs}
        assert "b" in by_path
        assert by_path["b"].values["alpha"] is None
        assert by_path["b"].values["beta"] == "2"


# ===========================================================================
# Domain: group_variants and pairwise similarity
# ===========================================================================


class TestUnstructuredComparison:
    """Tests for variant grouping and similarity computation."""

    def test_identical_content_single_group(self) -> None:
        contents = {"alpha": "hello\nworld", "beta": "hello\nworld", "gamma": "hello\nworld"}
        groups = group_variants(contents)
        assert len(groups) == 1
        assert groups[0].projects == frozenset({"alpha", "beta", "gamma"})

    def test_two_variants(self) -> None:
        contents = {"alpha": "version A", "beta": "version B", "gamma": "version A"}
        groups = group_variants(contents)
        assert len(groups) == 2
        # Largest group first.
        assert len(groups[0].projects) == 2
        assert len(groups[1].projects) == 1

    def test_pairwise_identical(self) -> None:
        contents = {"alpha": "same text", "beta": "same text"}
        sims = compute_pairwise_similarity(contents)
        assert len(sims) == 1
        assert sims[0].score == 1.0

    def test_pairwise_different(self) -> None:
        contents = {"alpha": "aaa", "beta": "bbb"}
        sims = compute_pairwise_similarity(contents)
        assert len(sims) == 1
        assert sims[0].score < 1.0

    def test_three_projects_pairwise_count(self) -> None:
        contents = {"alpha": "a", "beta": "b", "gamma": "c"}
        sims = compute_pairwise_similarity(contents)
        assert len(sims) == 3  # C(3,2) = 3


# ===========================================================================
# Domain: summaries
# ===========================================================================


class TestSummaries:
    """Tests for tree and file summary computation."""

    def test_tree_summary(self) -> None:
        all_projects = frozenset({"a", "b", "c"})
        matches = (
            NodeMatch(
                canonical_path="f1", resolved={"a": "f1", "b": "f1", "c": "f1"},
                present_in=frozenset({"a", "b", "c"}), absent_from=frozenset(),
                method=MatchMethod.EXACT, similarity=1.0, is_directory=False,
            ),
            NodeMatch(
                canonical_path="f2", resolved={"a": "f2"},
                present_in=frozenset({"a"}), absent_from=frozenset({"b", "c"}),
                method=MatchMethod.EXACT, similarity=1.0, is_directory=False,
            ),
            NodeMatch(
                canonical_path="d1", resolved={"a": "d1", "b": "d1"},
                present_in=frozenset({"a", "b"}), absent_from=frozenset({"c"}),
                method=MatchMethod.EXACT, similarity=1.0, is_directory=True,
            ),
        )
        summary = compute_tree_summary(matches, all_projects)
        assert summary.total_nodes == 3
        assert summary.in_all == 1
        assert summary.in_some == 1
        assert summary.in_one == 1
        assert summary.directories_matched == 1
        assert summary.files_matched == 2

    def test_file_summary(self) -> None:
        results = (
            FileDiffResult(
                canonical_path="a.toml", actual_paths={"x": "a.toml", "y": "a.toml"},
                present_in=frozenset({"x", "y"}), absent_from=frozenset(),
                content_kind=ContentKind.STRUCTURED,
                field_diffs=(FieldDiff(path="k", values={"x": "1", "y": "1"}),),
            ),
            FileDiffResult(
                canonical_path="b.md", actual_paths={"x": "b.md", "y": "b.md"},
                present_in=frozenset({"x", "y"}), absent_from=frozenset(),
                content_kind=ContentKind.UNSTRUCTURED,
                variants=(VariantGroup(projects=frozenset({"x"}), digest="aaa", line_count=1),
                          VariantGroup(projects=frozenset({"y"}), digest="bbb", line_count=1)),
            ),
            FileDiffResult(
                canonical_path="c.txt", actual_paths={"x": "c.txt"},
                present_in=frozenset({"x"}), absent_from=frozenset({"y"}),
                content_kind=ContentKind.UNSTRUCTURED, issue="y: not found",
            ),
        )
        summary = compute_file_summary(results)
        assert summary.files_compared == 3
        assert summary.fully_identical == 1
        assert summary.with_errors == 1
        assert summary.with_differences == 1

    def test_file_summary_excludes_error_results_from_identical_count(self) -> None:
        result = FileDiffResult(
            canonical_path="broken.toml",
            actual_paths={"x": "broken.toml", "y": "broken.toml"},
            present_in=frozenset({"x", "y"}),
            absent_from=frozenset(),
            content_kind=ContentKind.STRUCTURED,
            issue="parse error",
        )

        summary = compute_file_summary((result,))

        assert not result.is_identical
        assert summary.fully_identical == 0
        assert summary.with_errors == 1
        assert summary.with_differences == 0


# ===========================================================================
# Infrastructure: structured parsers
# ===========================================================================


class TestStructuredParsers:
    """Tests for TOML/YAML/JSON parsing."""

    def test_toml_parser(self) -> None:
        result = TomlParser().parse('[project]\nname = "foo"\nversion = "1.0"')
        assert result["project"]["name"] == "foo"

    def test_yaml_parser(self) -> None:
        result = YamlParser().parse("project:\n  name: foo\n  version: '1.0'")
        assert result["project"]["name"] == "foo"

    def test_json_parser(self) -> None:
        result = JsonParser().parse('{"project": {"name": "foo"}}')
        assert result["project"]["name"] == "foo"

    def test_dispatching_parser_by_extension(self) -> None:
        dp = DispatchingParser({".toml": TomlParser(), ".yaml": YamlParser(), ".json": JsonParser()})
        result = dp.parse('{"a": 1}', extension=".json")
        assert result == {"a": 1}

    def test_dispatching_parser_by_hint(self) -> None:
        dp = DispatchingParser({".toml": TomlParser()})
        result = dp.parse('[x]\ny = 1', hint="toml")
        assert result["x"]["y"] == 1

    def test_dispatching_parser_unknown_extension(self) -> None:
        dp = DispatchingParser({".toml": TomlParser()})
        with pytest.raises(ComparisonError, match="No parser registered"):
            dp.parse("data", extension=".ini")

    def test_toml_parser_invalid(self) -> None:
        with pytest.raises(ValueError, match="Invalid TOML"):
            TomlParser().parse("not valid toml {{{}}")

    def test_yaml_parser_non_mapping(self) -> None:
        with pytest.raises(ValueError, match="Expected YAML mapping"):
            YamlParser().parse("- item1\n- item2")

    def test_json_parser_non_object(self) -> None:
        with pytest.raises(ValueError, match="Expected JSON object"):
            JsonParser().parse("[1, 2, 3]")


# ===========================================================================
# Infrastructure: spec loader
# ===========================================================================


class TestSpecLoader:
    """Tests for instruction YAML loading."""

    def test_load_tree_spec(self, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.yml"
        spec_file.write_text(
            "projects: [alpha, beta]\n"
            "mode: tree\n"
            "tree:\n"
            "  subtree: src/\n"
            "  include_patterns: ['*.py']\n"
        )
        spec = YamlSpecLoader().load(spec_file)
        assert spec.project_names == ("alpha", "beta")
        assert isinstance(spec.target, TreeTarget)
        assert spec.target.subtree == "src/"
        assert spec.target.include_patterns == ("*.py",)

    def test_load_file_spec(self, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.yml"
        spec_file.write_text(
            "projects: [alpha]\n"
            "mode: files\n"
            "files:\n"
            "  granularity: survey\n"
            "  entries:\n"
            "    - canonical: pyproject.toml\n"
            "      selectors: [project.name]\n"
            "    - canonical: README.md\n"
            "      overrides:\n"
            "        alpha: readme.md\n"
        )
        spec = YamlSpecLoader().load(spec_file)
        from stelion.workspace.domain.comparison import FileTarget
        assert isinstance(spec.target, FileTarget)
        assert len(spec.target.entries) == 2
        assert spec.target.entries[0].selectors == ("project.name",)
        assert spec.target.entries[1].overrides["alpha"] == "readme.md"

    def test_load_missing_mode(self, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.yml"
        spec_file.write_text("projects: [alpha]\n")
        with pytest.raises(ComparisonError, match="mode must be a non-empty string"):
            YamlSpecLoader().load(spec_file)

    def test_load_both_sections_rejected(self, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.yml"
        spec_file.write_text(
            "mode: tree\n"
            "tree:\n  subtree: src/\n"
            "files:\n  entries:\n    - canonical: a.toml\n"
        )
        with pytest.raises(ComparisonError, match="both 'tree' and 'files'"):
            YamlSpecLoader().load(spec_file)

    def test_load_missing_file(self) -> None:
        with pytest.raises(ComparisonError, match="Could not read instruction file"):
            YamlSpecLoader().load(Path("/tmp/does-not-exist-comparison-spec.yml"))

    def test_projects_must_be_sequence(self, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.yml"
        spec_file.write_text("projects: alpha\nmode: tree\ntree: {}\n")

        with pytest.raises(ComparisonError, match="projects must be a sequence"):
            YamlSpecLoader().load(spec_file)

    def test_entries_must_be_sequence_of_mappings(self, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.yml"
        spec_file.write_text("mode: files\nfiles:\n  entries: not-a-list\n")

        with pytest.raises(ComparisonError, match="files.entries must be a sequence"):
            YamlSpecLoader().load(spec_file)

    def test_detail_requires_reference(self, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.yml"
        spec_file.write_text(
            "mode: files\n"
            "files:\n"
            "  granularity: detail\n"
            "  entries:\n"
            "    - canonical: README.md\n"
        )

        with pytest.raises(ComparisonError, match="requires a reference project"):
            YamlSpecLoader().load(spec_file)

    def test_include_patterns_must_be_sequence(self, tmp_path: Path) -> None:
        spec_file = tmp_path / "spec.yml"
        spec_file.write_text("mode: tree\ntree:\n  include_patterns: '*.py'\n")

        with pytest.raises(ComparisonError, match="tree.include_patterns must be a sequence"):
            YamlSpecLoader().load(spec_file)


# ===========================================================================
# Infrastructure: tree scanner
# ===========================================================================


class TestTreeScanner:
    """Tests for LocalTreeScanner."""

    def test_basic_scan(self, tmp_path: Path) -> None:
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("pass")
        (tmp_path / "README.md").write_text("# Hi")

        scanner = LocalTreeScanner()
        snapshot = scanner.scan(tmp_path, subtree=None, include=(), exclude=())

        paths = {e.relative_path for e in snapshot.entries}
        assert "src" in paths
        assert "src/main.py" in paths
        assert "README.md" in paths

    def test_exclude_pattern(self, tmp_path: Path) -> None:
        (tmp_path / "main.py").write_text("pass")
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "main.cpython-312.pyc").write_text("")

        scanner = LocalTreeScanner()
        snapshot = scanner.scan(tmp_path, subtree=None, include=(), exclude=("__pycache__",))

        paths = {e.relative_path for e in snapshot.entries}
        assert "main.py" in paths
        assert "__pycache__" not in paths

    def test_include_pattern(self, tmp_path: Path) -> None:
        (tmp_path / "main.py").write_text("pass")
        (tmp_path / "data.txt").write_text("data")

        scanner = LocalTreeScanner()
        snapshot = scanner.scan(tmp_path, subtree=None, include=("*.py",), exclude=())

        file_paths = {e.relative_path for e in snapshot.entries if not e.is_directory}
        assert "main.py" in file_paths
        assert "data.txt" not in file_paths

    def test_subtree_scan(self, tmp_path: Path) -> None:
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "app.py").write_text("pass")
        (tmp_path / "README.md").write_text("# Hi")

        scanner = LocalTreeScanner()
        snapshot = scanner.scan(tmp_path, subtree="src", include=(), exclude=())

        paths = {e.relative_path for e in snapshot.entries}
        assert "src/app.py" in paths
        assert "README.md" not in paths


# ===========================================================================
# Application: integration tests
# ===========================================================================


class TestCompareTreesIntegration:
    """Integration tests for compare_trees using real filesystem."""

    def test_compare_two_projects(self, tmp_path: Path) -> None:
        proj_a = tmp_path / "alpha"
        proj_b = tmp_path / "beta"
        proj_a.mkdir()
        proj_b.mkdir()

        (proj_a / "README.md").write_text("# Alpha")
        (proj_a / "src").mkdir()
        (proj_a / "src" / "main.py").write_text("pass")

        (proj_b / "README.md").write_text("# Beta")
        (proj_b / "src").mkdir()
        (proj_b / "src" / "main.py").write_text("pass")
        (proj_b / "CHANGELOG.md").write_text("# Changes")

        projects = (_project("alpha", proj_a), _project("beta", proj_b))
        target = TreeTarget()
        scanner = LocalTreeScanner()

        report = compare_trees(projects, target, scanner)

        assert set(report.projects) == {"alpha", "beta"}
        assert report.summary.total_nodes > 0
        paths = {m.canonical_path for m in report.matches}
        assert "README.md" in paths
        assert "src" in paths

    def test_compare_uses_logical_project_names_not_directory_names(self, tmp_path: Path) -> None:
        proj_a = tmp_path / "path-alpha"
        proj_b = tmp_path / "path-beta"
        proj_a.mkdir()
        proj_b.mkdir()
        (proj_a / "README.md").write_text("# Alpha")
        (proj_b / "README.md").write_text("# Beta")

        projects = (_project("alpha", proj_a), _project("beta", proj_b))
        report = compare_trees(projects, TreeTarget(), LocalTreeScanner())

        match = next(m for m in report.matches if m.canonical_path == "README.md")
        assert match.present_in == frozenset({"alpha", "beta"})
        assert match.absent_from == frozenset()
        assert dict(match.resolved) == {"alpha": "README.md", "beta": "README.md"}


class TestCompareFilesIntegration:
    """Integration tests for compare_files using real filesystem."""

    def test_compare_toml_files(self, tmp_path: Path) -> None:
        proj_a = tmp_path / "alpha"
        proj_b = tmp_path / "beta"
        proj_a.mkdir()
        proj_b.mkdir()

        (proj_a / "pyproject.toml").write_text(
            '[project]\nname = "alpha"\nversion = "1.0"\n'
        )
        (proj_b / "pyproject.toml").write_text(
            '[project]\nname = "beta"\nversion = "2.0"\n'
        )

        projects = (_project("alpha", proj_a), _project("beta", proj_b))
        target = FileTarget(
            entries=(FileTargetEntry(canonical="pyproject.toml"),),
        )
        reader = _TextFileReader()
        parser = DispatchingParser({
            ".toml": TomlParser(), ".yaml": YamlParser(), ".json": JsonParser(),
        })

        report = compare_files(projects, target, reader, parser)

        assert report.summary.files_compared == 1
        result = report.results[0]
        assert result.content_kind == ContentKind.STRUCTURED
        by_path = {fd.path: fd for fd in result.field_diffs}
        assert by_path["project.name"].values["alpha"] == "alpha"
        assert by_path["project.name"].values["beta"] == "beta"

    def test_compare_unstructured_files(self, tmp_path: Path) -> None:
        proj_a = tmp_path / "alpha"
        proj_b = tmp_path / "beta"
        proj_a.mkdir()
        proj_b.mkdir()

        (proj_a / "README.md").write_text("# Shared Title\nAlpha specific.")
        (proj_b / "README.md").write_text("# Shared Title\nBeta specific.")

        projects = (_project("alpha", proj_a), _project("beta", proj_b))
        target = FileTarget(entries=(FileTargetEntry(canonical="README.md"),))
        reader = _TextFileReader()
        parser = DispatchingParser({".toml": TomlParser()})

        report = compare_files(projects, target, reader, parser)

        result = report.results[0]
        assert result.content_kind == ContentKind.UNSTRUCTURED
        assert len(result.variants) == 2  # different content
        assert len(result.similarities) == 1

    def test_missing_file_resilience(self, tmp_path: Path) -> None:
        proj_a = tmp_path / "alpha"
        proj_b = tmp_path / "beta"
        proj_a.mkdir()
        proj_b.mkdir()

        (proj_a / "config.toml").write_text('[x]\ny = 1')
        # beta has no config.toml

        projects = (_project("alpha", proj_a), _project("beta", proj_b))
        target = FileTarget(entries=(FileTargetEntry(canonical="config.toml"),))
        reader = _TextFileReader()
        parser = DispatchingParser({".toml": TomlParser()})

        report = compare_files(projects, target, reader, parser)

        result = report.results[0]
        assert "alpha" in result.present_in
        assert "beta" in result.absent_from
        assert result.issue  # records the read error

    def test_parse_failures_are_not_counted_as_identical(self, tmp_path: Path) -> None:
        proj_a = tmp_path / "alpha"
        proj_b = tmp_path / "beta"
        proj_a.mkdir()
        proj_b.mkdir()
        (proj_a / "pyproject.toml").write_text("not valid toml {{{")
        (proj_b / "pyproject.toml").write_text("still invalid {{{")

        projects = (_project("alpha", proj_a), _project("beta", proj_b))
        target = FileTarget(entries=(FileTargetEntry(canonical="pyproject.toml"),))
        reader = _TextFileReader()
        parser = DispatchingParser({".toml": TomlParser()})

        report = compare_files(projects, target, reader, parser)

        result = report.results[0]
        assert not result.is_identical
        assert report.summary.fully_identical == 0
        assert report.summary.with_errors == 1
        assert report.summary.with_differences == 0

    def test_detail_mode_emits_reference_diffs(self, tmp_path: Path) -> None:
        proj_a = tmp_path / "alpha"
        proj_b = tmp_path / "beta"
        proj_c = tmp_path / "gamma"
        proj_a.mkdir()
        proj_b.mkdir()
        proj_c.mkdir()

        (proj_a / "README.md").write_text("line 1\nshared\n")
        (proj_b / "README.md").write_text("line 1\nbeta only\n")
        (proj_c / "README.md").write_text("line 1\nshared\n")

        projects = (_project("alpha", proj_a), _project("beta", proj_b), _project("gamma", proj_c))
        target = FileTarget(
            entries=(FileTargetEntry(canonical="README.md"),),
            granularity="detail",
            reference_project="alpha",
        )
        reader = _TextFileReader()
        parser = DispatchingParser({".toml": TomlParser()})

        report = compare_files(projects, target, reader, parser)

        result = report.results[0]
        assert result.reference_project == "alpha"
        assert {d.project for d in result.reference_diffs} == {"beta", "gamma"}
        beta_diff = next(d for d in result.reference_diffs if d.project == "beta")
        gamma_diff = next(d for d in result.reference_diffs if d.project == "gamma")
        assert any(line.startswith("--- alpha") for line in beta_diff.diff_lines)
        assert any(line.startswith("+++ beta") for line in beta_diff.diff_lines)
        assert gamma_diff.diff_lines == ()


class _TextFileReader:
    """Minimal FileReader for tests — reads UTF-8 text from disk."""

    def read(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")


# ===========================================================================
# YAML renderers
# ===========================================================================


class TestYamlRenderers:
    """Tests for YAML serialization of reports."""

    def test_render_tree_yaml(self) -> None:
        report = TreeReport(
            projects=("alpha", "beta"),
            subtree=None,
            matches=(
                NodeMatch(
                    canonical_path="README.md", resolved={"alpha": "README.md", "beta": "README.md"},
                    present_in=frozenset({"alpha", "beta"}), absent_from=frozenset(),
                    method=MatchMethod.EXACT, similarity=1.0, is_directory=False,
                ),
            ),
            summary=TreeSummary(
                total_nodes=1, in_all=1, in_some=0, in_one=0,
                directories_matched=0, files_matched=1,
            ),
        )
        output = render_tree_yaml(report)
        assert "README.md" in output
        assert "alpha" in output
        assert "comparison-tree.yml" in output

    def test_render_file_yaml(self) -> None:
        report = FileReport(
            projects=("alpha", "beta"),
            results=(
                FileDiffResult(
                    canonical_path="pyproject.toml",
                    actual_paths={"alpha": "pyproject.toml", "beta": "pyproject.toml"},
                    present_in=frozenset({"alpha", "beta"}),
                    absent_from=frozenset(),
                    content_kind=ContentKind.STRUCTURED,
                    field_diffs=(
                        FieldDiff(path="project.name", values={"alpha": "a", "beta": "b"}),
                    ),
                ),
            ),
            summary=compute_file_summary((
                FileDiffResult(
                    canonical_path="pyproject.toml",
                    actual_paths={"alpha": "pyproject.toml", "beta": "pyproject.toml"},
                    present_in=frozenset({"alpha", "beta"}),
                    absent_from=frozenset(),
                    content_kind=ContentKind.STRUCTURED,
                    field_diffs=(
                        FieldDiff(path="project.name", values={"alpha": "a", "beta": "b"}),
                    ),
                ),
            )),
        )
        output = render_file_yaml(report)
        assert "pyproject.toml" in output
        assert "project.name" in output
        assert "comparison-files.yml" in output

    def test_render_file_yaml_with_reference_diffs(self) -> None:
        report = FileReport(
            projects=("alpha", "beta"),
            results=(
                FileDiffResult(
                    canonical_path="README.md",
                    actual_paths={"alpha": "README.md", "beta": "README.md"},
                    present_in=frozenset({"alpha", "beta"}),
                    absent_from=frozenset(),
                    content_kind=ContentKind.UNSTRUCTURED,
                    variants=(
                        VariantGroup(projects=frozenset({"alpha"}), digest="aaa", line_count=2),
                        VariantGroup(projects=frozenset({"beta"}), digest="bbb", line_count=2),
                    ),
                    reference_project="alpha",
                    reference_diffs=(),
                ),
            ),
            summary=compute_file_summary((
                FileDiffResult(
                    canonical_path="README.md",
                    actual_paths={"alpha": "README.md", "beta": "README.md"},
                    present_in=frozenset({"alpha", "beta"}),
                    absent_from=frozenset(),
                    content_kind=ContentKind.UNSTRUCTURED,
                    variants=(
                        VariantGroup(projects=frozenset({"alpha"}), digest="aaa", line_count=2),
                        VariantGroup(projects=frozenset({"beta"}), digest="bbb", line_count=2),
                    ),
                    reference_project="alpha",
                    reference_diffs=(),
                ),
            )),
        )

        output = render_file_yaml(report)

        assert "reference_project: alpha" in output
