"""Domain models for project metadata and inventory."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


_GITHUB_URL_RE = re.compile(r"github\.com[:/](.+?)/(.+?)(?:\.git)?$")


class MetadataStatus(StrEnum):
    """Status of metadata extracted from a project directory."""

    CURRENT = "current"
    MISSING_PYPROJECT = "missing_pyproject"
    INVALID_PYPROJECT = "invalid_pyproject"


@dataclass(frozen=True)
class GithubSlug:
    """A validated GitHub owner/repo identifier."""

    owner: str
    repo: str

    @classmethod
    def parse(cls, raw: str) -> GithubSlug:
        """Parse an ``owner/repo`` string.

        Raises
        ------
        ValueError
            If the string is not exactly ``owner/repo`` with non-empty parts.
        """
        parts = raw.split("/")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError(
                f"GitHub identifier must be 'owner/repo', got: {raw!r}"
            )
        return cls(owner=parts[0], repo=parts[1])

    @classmethod
    def from_url(cls, url: str) -> GithubSlug | None:
        """Extract owner/repo from a GitHub URL.

        Accepts HTTPS (``https://github.com/owner/repo``) and SSH
        (``git@github.com:owner/repo.git``) formats.  Returns ``None``
        if the URL does not match a GitHub pattern.
        """
        match = _GITHUB_URL_RE.search(url)
        if not match:
            return None
        return cls(owner=match.group(1), repo=match.group(2))

    def __str__(self) -> str:
        return f"{self.owner}/{self.repo}"


@dataclass(frozen=True)
class ProjectMetadata:
    """Metadata extracted from a single project's pyproject.toml and filesystem."""

    name: str
    path: Path
    description: str = ""
    version: str = "0.0.0"
    homepage: str | None = None
    github: GithubSlug | None = None
    has_git: bool = False
    languages: tuple[str, ...] = ()
    status: MetadataStatus = MetadataStatus.CURRENT
    issue: str = ""


@dataclass(frozen=True)
class ProjectInventory:
    """Collection of discovered projects."""

    projects: tuple[ProjectMetadata, ...] = ()

    def by_name(self) -> dict[str, ProjectMetadata]:
        """Index projects by name."""
        return {p.name: p for p in self.projects}

    def by_path(self) -> dict[Path, ProjectMetadata]:
        """Index projects by their resolved filesystem path."""
        return {p.path.resolve(): p for p in self.projects}
