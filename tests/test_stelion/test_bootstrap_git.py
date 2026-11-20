"""Tests of the Git repository that the bootstrap of a project initializes."""

from pathlib import Path
import shutil
import subprocess

import pytest

from stelion.workspace.infrastructure.bootstrap_git import init_repository


@pytest.mark.skipif(shutil.which("git") is None, reason="the command git is absent")
def test_the_first_commit_names_the_configured_template(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The message of the first commit names the template that the manifest configures."""
    for variable, value in (
        ("GIT_AUTHOR_NAME", "Test"),
        ("GIT_AUTHOR_EMAIL", "test@example.org"),
        ("GIT_COMMITTER_NAME", "Test"),
        ("GIT_COMMITTER_EMAIL", "test@example.org"),
        ("GIT_CONFIG_GLOBAL", str(tmp_path / "gitconfig")),
    ):
        monkeypatch.setenv(variable, value)
    project = tmp_path / "project"
    project.mkdir()
    (project / "README.md").write_text("project\n", encoding="utf-8")
    init_repository(project, "lab-template")
    message = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        cwd=project,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert message == "feat: Initialize project from lab-template template"
