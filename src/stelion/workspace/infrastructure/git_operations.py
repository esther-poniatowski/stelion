"""Concrete git operations for submodule synchronization."""

from __future__ import annotations

import subprocess
from pathlib import Path

from ..exceptions import SyncError


class SubprocessGitOperations:
    """Git operations implemented via subprocess calls."""

    def head_commit(self, repo_dir: Path) -> str:
        """Read HEAD commit SHA from a repository."""
        return self._run(["git", "rev-parse", "HEAD"], cwd=repo_dir).strip()

    def submodule_commit(self, superproject_dir: Path, submodule_path: str) -> str:
        """Read the recorded commit SHA for a submodule in a superproject."""
        output = self._run(
            ["git", "ls-tree", "HEAD", submodule_path], cwd=superproject_dir,
        )
        parts = output.split()
        if len(parts) < 3:
            raise SyncError(
                f"Cannot read submodule commit for '{submodule_path}' "
                f"in {superproject_dir}."
            )
        return parts[2]

    def fetch_remote(self, repo_dir: Path) -> None:
        """Fetch from the default remote."""
        self._run(["git", "fetch"], cwd=repo_dir)

    def remote_head(self, repo_dir: Path, remote: str, branch: str) -> str:
        """Read the commit SHA of a remote tracking branch."""
        return self._run(
            ["git", "rev-parse", f"{remote}/{branch}"], cwd=repo_dir,
        ).strip()

    def update_submodule_pointer(
        self, superproject_dir: Path, submodule_path: str, commit: str,
    ) -> None:
        """Update a submodule to point at a specific commit."""
        submodule_dir = superproject_dir / submodule_path
        self._run(["git", "checkout", "--quiet", commit], cwd=submodule_dir)

    def commit_submodule_update(
        self, superproject_dir: Path, submodule_path: str,
        dependency: str, commit_short: str,
    ) -> None:
        """Stage and commit the submodule pointer change in the superproject."""
        self._run(["git", "add", submodule_path], cwd=superproject_dir)
        message = f"build: Update {dependency} submodule to {commit_short}"
        self._run(["git", "commit", "--quiet", "-m", message], cwd=superproject_dir)

    def is_clean(self, repo_dir: Path) -> bool:
        """Check whether the working tree has no uncommitted changes."""
        output = self._run(["git", "status", "--porcelain"], cwd=repo_dir)
        return output.strip() == ""

    def update_local_clone(self, repo_dir: Path, commit: str) -> str:
        """Update local clone to the target commit via fast-forward merge.

        Returns the old HEAD commit SHA.

        Raises
        ------
        SyncError
            If the working tree is dirty or fast-forward merge fails.
        """
        old = self.head_commit(repo_dir)
        if not self.is_clean(repo_dir):
            raise SyncError(
                f"Local repo at {repo_dir} has uncommitted changes. "
                f"Commit or stash before syncing."
            )
        self._run(["git", "fetch", "origin"], cwd=repo_dir)
        self._run(["git", "merge", "--ff-only", commit], cwd=repo_dir)
        return old

    def push_to_remote(self, repo_dir: Path, remote: str, branch: str) -> None:
        """Push the current HEAD to a remote branch."""
        self._run(["git", "push", remote, branch], cwd=repo_dir)

    @staticmethod
    def _run(cmd: list[str], cwd: Path) -> str:
        """Run a git command, raising SyncError on failure."""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, cwd=cwd,
            )
            return result.stdout
        except subprocess.CalledProcessError as exc:
            raise SyncError(
                f"Git command failed: {' '.join(cmd)}\n"
                f"cwd: {cwd}\n"
                f"stderr: {exc.stderr.strip()}"
            ) from exc
        except FileNotFoundError as exc:
            raise SyncError("Git is not installed or not on PATH.") from exc
