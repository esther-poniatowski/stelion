"""Concrete bulk operation implementations.

Classes
-------
ShellOperation
    Run an arbitrary shell command in each project directory.
GitCommitOperation
    Stage tracked changes and commit, skipping clean working trees.
GitPushOperation
    Push the current branch to a remote.
"""

from __future__ import annotations

from ..application.protocols import CommandRunner
from ..domain.bulk import OutcomeStatus, ProjectOutcome
from ..domain.project import ProjectMetadata


class ShellOperation:
    """Run an arbitrary shell command in each project directory.

    Parameters
    ----------
    command : str
        Shell command string to execute.
    runner : CommandRunner
        Backend used to invoke shell processes.
    """

    def __init__(self, command: str, runner: CommandRunner) -> None:
        self._command = command
        self._runner = runner

    @property
    def label(self) -> str:
        """Human-readable label describing this operation.

        Returns
        -------
        str
            Formatted label prefixed with ``exec:``.
        """
        return f"exec: {self._command}"

    def __call__(self, project: ProjectMetadata, *, dry_run: bool) -> ProjectOutcome:
        if dry_run:
            return ProjectOutcome(
                project.name, project.path,
                OutcomeStatus.SKIPPED, f"would run: {self._command}",
            )
        result = self._runner.run(("sh", "-c", self._command), project.path)
        if result.return_code != 0:
            return ProjectOutcome(
                project.name, project.path,
                OutcomeStatus.FAILED, "", result.stderr.strip(),
            )
        return ProjectOutcome(
            project.name, project.path,
            OutcomeStatus.SUCCESS, result.stdout.strip(),
        )


class GitCommitOperation:
    """Stage tracked changes and commit, skipping clean working trees.

    Parameters
    ----------
    message : str
        Commit message to use.
    runner : CommandRunner
        Backend used to invoke git processes.
    """

    def __init__(self, message: str, runner: CommandRunner) -> None:
        self._message = message
        self._runner = runner

    @property
    def label(self) -> str:
        """Human-readable label describing this operation.

        Returns
        -------
        str
            Formatted label prefixed with ``commit:``.
        """
        return f"commit: {self._message}"

    def __call__(self, project: ProjectMetadata, *, dry_run: bool) -> ProjectOutcome:
        if not project.has_git:
            return ProjectOutcome(
                project.name, project.path,
                OutcomeStatus.SKIPPED, "no git repository",
            )
        status = self._runner.run(("git", "status", "--porcelain"), project.path)
        if status.return_code != 0:
            return ProjectOutcome(
                project.name, project.path,
                OutcomeStatus.FAILED, "", status.stderr.strip(),
            )
        if not status.stdout.strip():
            return ProjectOutcome(
                project.name, project.path,
                OutcomeStatus.SKIPPED, "working tree clean",
            )
        if dry_run:
            return ProjectOutcome(
                project.name, project.path,
                OutcomeStatus.SKIPPED, f"would commit: {self._message}",
            )
        add_result = self._runner.run(("git", "add", "--update"), project.path)
        if add_result.return_code != 0:
            return ProjectOutcome(
                project.name, project.path,
                OutcomeStatus.FAILED, "", add_result.stderr.strip(),
            )
        result = self._runner.run(
            ("git", "commit", "-m", self._message), project.path,
        )
        if result.return_code != 0:
            return ProjectOutcome(
                project.name, project.path,
                OutcomeStatus.FAILED, "", result.stderr.strip(),
            )
        summary = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "committed"
        return ProjectOutcome(
            project.name, project.path,
            OutcomeStatus.SUCCESS, summary,
        )


class GitPushOperation:
    """Push the current branch to a remote.

    Parameters
    ----------
    remote : str
        Remote name (e.g. ``"origin"``).
    branch : str
        Branch to push.
    runner : CommandRunner
        Backend used to invoke git processes.
    """

    def __init__(self, remote: str, branch: str, runner: CommandRunner) -> None:
        self._remote = remote
        self._branch = branch
        self._runner = runner

    @property
    def label(self) -> str:
        """Human-readable label describing this operation.

        Returns
        -------
        str
            Formatted label prefixed with ``push:``.
        """
        return f"push: {self._remote}/{self._branch}"

    def __call__(self, project: ProjectMetadata, *, dry_run: bool) -> ProjectOutcome:
        if not project.has_git:
            return ProjectOutcome(
                project.name, project.path,
                OutcomeStatus.SKIPPED, "no git repository",
            )
        if dry_run:
            return ProjectOutcome(
                project.name, project.path,
                OutcomeStatus.SKIPPED,
                f"would push to {self._remote}/{self._branch}",
            )
        result = self._runner.run(
            ("git", "push", self._remote, self._branch), project.path,
        )
        if result.return_code != 0:
            return ProjectOutcome(
                project.name, project.path,
                OutcomeStatus.FAILED, "", result.stderr.strip(),
            )
        # git push writes progress to stderr
        detail = result.stderr.strip() or "up to date"
        return ProjectOutcome(
            project.name, project.path,
            OutcomeStatus.SUCCESS, detail,
        )
