"""Project registration use-case.

Registers an existing project into workspace artifacts without regenerating
everything. Used for copy-pasted, imported, or manually created projects.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..domain.project import ProjectMetadata
from .protocols import MetadataExtractor


@dataclass(frozen=True)
class RegistrationResult:
    """Outcome of registering a project."""

    project: ProjectMetadata
    files_updated: tuple[str, ...]


def register_project(
    project_dir: Path,
    extractor: MetadataExtractor,
) -> ProjectMetadata:
    """Extract metadata from a project directory for registration.

    The caller (CLI adapter) is responsible for updating the workspace file,
    projects index, and dependency graph with the returned metadata.
    """
    if not project_dir.is_dir():
        raise FileNotFoundError(f"Project directory does not exist: {project_dir}")

    return extractor.extract(project_dir)
