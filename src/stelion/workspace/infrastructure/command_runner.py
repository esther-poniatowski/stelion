"""Subprocess-based command runner for bulk operations."""

from __future__ import annotations

import subprocess
from pathlib import Path

from ..application.protocols import CommandResult


class SubprocessCommandRunner:
    """Run commands via subprocess with captured output."""

    def run(self, args: tuple[str, ...], cwd: Path) -> CommandResult:
        """Execute *args* in *cwd* and return the captured result.

        Parameters
        ----------
        args : tuple[str, ...]
            Command and arguments to execute.
        cwd : Path
            Working directory for the subprocess.

        Returns
        -------
        CommandResult
            Captured stdout, stderr, and return code.
        """
        proc = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True, check=False,
        )
        return CommandResult(proc.returncode, proc.stdout, proc.stderr)
