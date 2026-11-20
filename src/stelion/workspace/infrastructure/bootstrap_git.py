"""Git-backed bootstrap helpers.
"""

from __future__ import annotations

from pathlib import Path
import subprocess


def read_git_identity() -> tuple[str, str]:
    """Read author identity from git config when available.

    Returns
    -------
    tuple[str, str]
        A ``(name, email)`` pair, both empty if git config is unavailable.
    """
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
    return author_name, author_email


def init_repository(target_dir: Path, template: str) -> None:
    """Initialize a git repository for a bootstrapped project.

    Parameters
    ----------
    target_dir : Path
        Root directory of the newly created project.
    template : str
        Name of the configured template, written in the message of the first commit.
    """
    subprocess.run(["git", "init", "--quiet"], cwd=target_dir, check=True)
    subprocess.run(["git", "add", "."], cwd=target_dir, check=True)
    subprocess.run(
        ["git", "commit", "--quiet", "-m", f"feat: Initialize project from {template} template"],
        cwd=target_dir,
        check=True,
    )
