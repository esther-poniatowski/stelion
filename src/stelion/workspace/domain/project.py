"""Domain models for project metadata and inventory.

Classes
-------
MetadataStatus
    Status of metadata extracted from a project directory.
GithubSlug
    A validated GitHub owner/repo identifier.
ProjectMetadata
    Metadata extracted from a single project's pyproject.toml and filesystem.
ProjectInventory
    Collection of discovered projects.
"""

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
    """A validated GitHub owner/repo identifier.

    Attributes
    ----------
    owner : str
        GitHub user or organisation name.
    repo : str
        Repository name.
    """

    owner: str
    repo: str

    @classmethod
    def parse(cls, raw: str) -> GithubSlug:
        """Parse an ``owner/repo`` string.

        Parameters
        ----------
        raw : str
            String in ``owner/repo`` format.

        Returns
        -------
        GithubSlug
            Parsed slug with owner and repo populated.

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

        Parameters
        ----------
        url : str
            GitHub URL in HTTPS or SSH format.

        Returns
        -------
        GithubSlug | None
            Parsed slug, or ``None`` if the URL is not a GitHub URL.
        """
        match = _GITHUB_URL_RE.search(url)
        if not match:
            return None
        return cls(owner=match.group(1), repo=match.group(2))

    def __str__(self) -> str:
        return f"{self.owner}/{self.repo}"


@dataclass(frozen=True)
class ProjectMetadata:
    """Metadata extracted from a single project's pyproject.toml and filesystem.

    Attributes
    ----------
    name : str
        Project name from pyproject.toml.
    path : Path
        Filesystem path to the project root.
    description : str
        Short project description.
    version : str
        Declared version string.
    homepage : str | None
        Project homepage URL.
    github : GithubSlug | None
        Parsed GitHub owner/repo identifier.
    has_git : bool
        Whether the project directory is a git repository.
    languages : tuple[str, ...]
        Programming languages detected in the project.
    status : MetadataStatus
        Parsing status of the metadata extraction.
    issue : str
        Error or warning message from metadata extraction.
    """

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
    """Collection of discovered projects.

    Attributes
    ----------
    projects : tuple[ProjectMetadata, ...]
        Discovered project metadata entries.
    """

    projects: tuple[ProjectMetadata, ...] = ()

    def by_name(self) -> dict[str, ProjectMetadata]:
        """Index projects by name.

        Returns
        -------
        dict[str, ProjectMetadata]
            Mapping from project name to metadata.
        """
        return {p.name: p for p in self.projects}

    def by_path(self) -> dict[Path, ProjectMetadata]:
        """Index projects by their resolved filesystem path.

        Returns
        -------
        dict[Path, ProjectMetadata]
            Mapping from resolved path to metadata.
        """
        return {p.path.resolve(): p for p in self.projects}
