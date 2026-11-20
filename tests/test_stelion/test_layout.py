"""Tests of the check of a layout on a repository where each rule is broken once."""

import json
import posixpath
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import pytest
import yaml
from typer.testing import CliRunner

from stelion.cli import app
from stelion.layout import LayoutError, check_layout, load_layout, sarif_log
from stelion.layout.rules import headings


@dataclass(frozen=True)
class Pointer:
    """A pointer as the read package of Anagraphe returns it."""

    target: str | None
    named: str | None
    raw: str
    line: int
    column: int


class FakeReader:
    """Reads the frontmatter of notes and the Markdown links of a repository, for the tests."""

    def __init__(self, root: Path, exempt: tuple[str, ...] = ()) -> None:
        self.root = root
        self.exempt_prefixes = exempt

    def metadata(self, path: str) -> Mapping[str, Any]:
        file = self.root / path
        if not file.is_file():
            return {}
        text = file.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            return {}
        data = yaml.safe_load(text[4 : text.find("\n---", 4)])
        return data if isinstance(data, dict) else {}

    def references(self, path: str) -> list[Pointer]:
        import re

        found = []
        for number, line in enumerate((self.root / path).read_text().splitlines(), start=1):
            for match in re.finditer(r"\]\(([^)]+)\)", line):
                target = posixpath.normpath((Path(path).parent / match.group(1)).as_posix())
                exists = (self.root / target).is_file()
                found.append(
                    Pointer(
                        target if exists else None,
                        target,
                        match.group(1),
                        number,
                        match.start(1) + 1,
                    )
                )
        return found

    def exempt(self, path: str) -> bool:
        return path.startswith(self.exempt_prefixes)


LAYOUT = {
    "_schema": "stelion:layout@1",
    "extends": "project",
    "exclude": ["archive/**"],
    "areas": {"foundations": "foundations", "projects": "projects", "artifacts": "artifacts"},
    "folders": [
        {
            "id": "artifact",
            "match": "artifacts/*",
            "when": {"file": "_index.md", "key": "index_type", "equals": "artifact"},
            "requires": ["outline", "brief"],
            "phases": "phase",
        },
        {"id": "phase", "match": "artifacts/*/*"},
    ],
    "kinds": [
        {
            "id": "outline",
            "name": "^outline\\.md$",
            "in": ["artifact", "phase"],
            "role": "outline",
            "within": ["artifacts/**"],
            "skeleton": "skeletons/outline.md",
        },
        {"id": "brief", "name": "^brief\\.md$", "in": ["artifact", "phase"]},
    ],
    "roles": {"everywhere": ["index"], "by_area": {"foundations": ["definition"]}, "open": []},
    "links": {"forbidden": [{"id": "stand-alone", "from": "foundations", "to": ["projects"]}]},
    "retired": [{"prefix": "old/", "retained_in": ["NOTES.txt"]}],
    "tree": {
        "root": [
            {"name": "foundations", "folder": True},
            {"name": "projects", "folder": True},
            {"name": "artifacts", "folder": True},
            {"name": "skeletons", "folder": True},
            {"name": "NOTES.txt"},
            {"name": "layout.yml"},
            {"name": "LICENSE", "required": True},
        ],
        "max_file_mib": 0.001,
    },
}

FILES = {
    "README.md": "# Repository\n",
    "NOTES.txt": "old/ was retired\n",
    "skeletons/outline.md": "## Parts\n## Notes\n",
    "artifacts/talk/_index.md": "---\nrole: index\nindex_type: artifact\n---\n",
    "artifacts/talk/outline.md": "---\nrole: outline\n---\n## Notes\n## Parts\n",
    "artifacts/talk/v1/brief.md": "---\nrole: spec\n---\n",
    "artifacts/talk/v2/draft.txt": "a phase without a brief\n",
    "artifacts/plain/outline.md": "---\nrole: outline\n---\n",
    "foundations/a.md": "---\nrole: definition\n---\nSee [b](../projects/b.md) and old/a.md.\n",
    "foundations/c.md": "---\nrole: definition\n---\nSee [gone](../projects/gone.md).\n",
    "projects/b.md": "---\nrole: definition\n---\n",
    "src/pkg/run.py": "VALUE = 1\n",
    "scripts/run.py": "VALUE = 1\n",
    "data/table.csv": "a,b\n" * 400,
    "stray.txt": "stray\n",
    "archive/old.md": "---\nrole: definition\n---\n",
}


def repository(root: Path, layout: dict = LAYOUT) -> Path:
    for rel, text in FILES.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    path = root / "layout.yml"
    path.write_text(yaml.safe_dump(layout, sort_keys=False), encoding="utf-8")
    return path


def found(root: Path) -> set[tuple[str, str, str]]:
    layout = load_layout(repository(root))
    return {
        (finding.rule.identifier, finding.path, finding.discriminator)
        for finding in check_layout(layout, root, FakeReader(root))
    }


def test_each_rule_reports_its_planted_instance(tmp_path: Path) -> None:
    """Every planted breach of the layout is reported, and nothing else."""
    assert found(tmp_path) == {
        ("kind/sections", "artifacts/talk/outline.md", "outline"),
        ("kind/placement", "artifacts/plain/outline.md", "outline"),
        ("folder/missing-kind", "artifacts/talk/", "brief"),
        ("role/area", "projects/b.md", "definition"),
        ("link/direction", "foundations/a.md", "../projects/b.md"),
        ("link/direction", "foundations/c.md", "../projects/gone.md"),
        ("path/retired", "foundations/a.md", "old/"),
        ("tree/missing-root-entry", "LICENSE", "LICENSE"),
        ("tree/unknown-root-entry", "scripts/", "scripts"),
        ("tree/unknown-root-entry", "stray.txt", "stray.txt"),
        ("tree/misplaced", "scripts/run.py", "code"),
        ("tree/tracked", "data/table.csv", "data/table.csv"),
        ("tree/oversized", "data/table.csv", "data/table.csv"),
    }


def test_a_kind_declaring_another_role_is_reported(tmp_path: Path) -> None:
    layout = dict(LAYOUT)
    layout["kinds"] = [dict(kind) for kind in LAYOUT["kinds"]]
    layout["kinds"][1]["role"] = "brief"
    path = repository(tmp_path, layout)
    findings = check_layout(load_layout(path), tmp_path, FakeReader(tmp_path))
    assert ("kind/role", "artifacts/talk/v1/brief.md") in {
        (item.rule.identifier, item.path) for item in findings
    }


def test_exempt_files_escape_the_rules_of_notes(tmp_path: Path) -> None:
    layout = load_layout(repository(tmp_path))
    findings = check_layout(layout, tmp_path, FakeReader(tmp_path, exempt=("projects/",)))
    assert "role/area" not in {item.rule.identifier for item in findings}


def test_the_log_conforms_to_the_findings_profile(tmp_path: Path) -> None:
    profile = pytest.importorskip("elenchos.profile")
    layout = load_layout(repository(tmp_path))
    log = sarif_log(check_layout(layout, tmp_path, FakeReader(tmp_path)))
    assert profile.violations(log) == []
    assert profile.violations(sarif_log([], "the layout cannot be read")) == []


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (lambda data: data["folders"][0].update(requires=["ghost"]), "ghost"),
        (lambda data: data["kinds"][0].update({"in": ["nowhere"]}), "nowhere"),
        (lambda data: data["links"]["forbidden"][0].update(to=["elsewhere"]), "elsewhere"),
        (lambda data: data.update(extends="missing.yml"), "absent"),
        (lambda data: data.update(unknown=1), "unknown"),
    ],
    ids=["unknown-kind", "unknown-folder-kind", "unknown-area", "absent-parent", "unknown-key"],
)
def test_an_invalid_layout_is_refused(tmp_path: Path, edit, message: str) -> None:
    import copy

    data = copy.deepcopy(LAYOUT)
    edit(data)
    with pytest.raises(LayoutError, match=message):
        load_layout(repository(tmp_path, data))


def test_the_default_layout_extends_and_is_overridden(tmp_path: Path) -> None:
    """The shipped layout supplies its tree, which the extending layout completes by name."""
    layout = load_layout(repository(tmp_path))
    names = {entry.name: entry for entry in layout.root}
    assert names["README.md"].required and names["LICENSE"].required
    assert "foundations" in names and layout.untracked == ("data/**", "config/local/**")


def test_headings_skip_fenced_code() -> None:
    assert headings("## A\n```\n## B\n```\n## C\n") == ["A", "C"]


ANAGRAPHE_CONFIG = "settings/anagraphe.yml"


def checked_paths(root: Path, monkeypatch: pytest.MonkeyPatch, *options: str) -> tuple[int, dict]:
    """Run `stelion layout check` with the real reader of Anagraphe, from the root."""
    pytest.importorskip("anagraphe_read")
    repository(root)
    (root / ANAGRAPHE_CONFIG).parent.mkdir(parents=True)
    (root / ANAGRAPHE_CONFIG).write_text(
        "_schema: anagraphe:configuration@3\nexclude:\n  paths:\n    - projects/\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(root)
    result = CliRunner().invoke(
        app, ["layout", "check", "--layout", "layout.yml", "--format", "sarif", *options]
    )
    return result.exit_code, json.loads(result.output)


def rule_paths(log: dict) -> set[tuple[str, str]]:
    return {
        (item["ruleId"], item["locations"][0]["physicalLocation"]["artifactLocation"]["uri"])
        for item in log["runs"][0].get("results", [])
    }


def test_the_named_configuration_of_anagraphe_applies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The exclusion declared in a file outside the accepted places applies once it is named."""
    status, log = checked_paths(tmp_path, monkeypatch, "--anagraphe-config", ANAGRAPHE_CONFIG)
    assert status == 1
    assert ("role/area", "projects/b.md") not in rule_paths(log)
    assert ("link/direction", "foundations/a.md") in rule_paths(log)


def test_a_configuration_outside_the_accepted_places_is_not_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    status, log = checked_paths(tmp_path, monkeypatch)
    assert status == 1
    assert ("role/area", "projects/b.md") in rule_paths(log)


def test_a_missing_configuration_of_anagraphe_stops_the_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    status, log = checked_paths(tmp_path, monkeypatch, "--anagraphe-config", "settings/missing.yml")
    assert status == 2
    invocation = log["runs"][0]["invocations"][0]
    assert invocation["executionSuccessful"] is False
    assert "settings/missing.yml" in invocation["toolExecutionNotifications"][0]["message"]["text"]
