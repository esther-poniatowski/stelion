"""Extract ProjectMetadata from a project's pyproject.toml."""

from __future__ import annotations

import tomllib
from pathlib import Path

from ..domain.project import ProjectMetadata


class PyprojectExtractor:
    """Read pyproject.toml and produce a ProjectMetadata instance."""

    def extract(self, project_dir: Path) -> ProjectMetadata:
        """Extract metadata from a project directory.

        Reads ``pyproject.toml`` for package metadata. Determines ``has_git``
        from the presence of a ``.git`` directory. Infers ``status`` from the
        version string and git state.
        """
        pyproject_path = project_dir / "pyproject.toml"
        has_git = (project_dir / ".git").is_dir()

        if not pyproject_path.exists():
            return ProjectMetadata(
                name=project_dir.name,
                path=project_dir,
                has_git=has_git,
            )

        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
        except tomllib.TOMLDecodeError:
            return ProjectMetadata(
                name=project_dir.name,
                path=project_dir,
                has_git=has_git,
            )

        project = data.get("project", {})
        name = project.get("name", project_dir.name)
        version = project.get("version", "0.0.0")
        description = project.get("description", "")
        urls = project.get("urls", {})
        homepage = urls.get("homepage")

        status = _infer_status(version, has_git)

        return ProjectMetadata(
            name=name,
            path=project_dir,
            description=description,
            version=version,
            status=status,
            homepage=homepage,
            has_git=has_git,
        )


def _infer_status(version: str, has_git: bool) -> str:
    """Infer a human-readable status string from version and git state."""
    if not has_git:
        return f"Pre-release (v{version}), no git repo"
    if version == "0.0.0":
        return f"Alpha (v{version}), active"
    return f"v{version}, active"
