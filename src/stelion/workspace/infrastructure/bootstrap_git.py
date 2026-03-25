"""Git-backed bootstrap helpers."""

from __future__ import annotations

from pathlib import Path
import subprocess


def read_git_identity() -> tuple[str, str]:
    """Read author identity from git config when available."""
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


def init_repository(target_dir: Path) -> None:
    """Initialize a git repository for a bootstrapped project."""
    subprocess.run(["git", "init", "--quiet"], cwd=target_dir, check=True)
    subprocess.run(["git", "add", "."], cwd=target_dir, check=True)
    subprocess.run(
        ["git", "commit", "--quiet", "-m", "feat: Initialize project from keystone template"],
        cwd=target_dir,
        check=True,
    )
