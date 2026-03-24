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
                description=_readme_description(project_dir),
                status=_infer_status("0.0.0", has_git),
                has_git=has_git,
                languages=_detect_languages(project_dir),
            )

        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
        except tomllib.TOMLDecodeError:
            return ProjectMetadata(
                name=project_dir.name,
                path=project_dir,
                description=_readme_description(project_dir),
                status=_infer_status("0.0.0", has_git),
                has_git=has_git,
                languages=_detect_languages(project_dir),
            )

        project = data.get("project", {})
        name = project.get("name", project_dir.name)
        version = project.get("version", "0.0.0")
        description = project.get("description", "") or _readme_description(project_dir)
        urls = project.get("urls", {})
        homepage = urls.get("homepage")

        status = _infer_status(version, has_git)
        languages = _detect_languages(project_dir)

        return ProjectMetadata(
            name=name,
            path=project_dir,
            description=description,
            version=version,
            status=status,
            homepage=homepage,
            has_git=has_git,
            languages=languages,
        )


def _infer_status(version: str, has_git: bool) -> str:
    """Infer a human-readable status string from version and git state."""
    if not has_git:
        return f"Pre-release (v{version}), no git repo"
    if version == "0.0.0":
        return f"Alpha (v{version}), active"
    return f"v{version}, active"


def _readme_description(project_dir: Path) -> str:
    """Extract the first descriptive line from a project README as fallback."""
    readme = project_dir / "README.md"
    if not readme.exists():
        return ""
    in_comment = False
    for line in readme.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if "<!--" in stripped:
            in_comment = True
        if in_comment:
            if "-->" in stripped:
                in_comment = False
            continue
        if not stripped or stripped.startswith("#") or stripped.startswith("[![") or stripped == "---":
            continue
        return stripped
    return ""


_EXTENSION_MAP: dict[str, str] = {
    ".py": "Python",
    ".tex": "LaTeX",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".rs": "Rust",
    ".go": "Go",
    ".sh": "Shell",
}


def _detect_languages(project_dir: Path) -> list[str]:
    """Detect programming languages from source file extensions."""
    search_dir = project_dir / "src" if (project_dir / "src").is_dir() else project_dir
    found = []
    for ext, lang in _EXTENSION_MAP.items():
        try:
            if next(search_dir.rglob(f"*{ext}"), None) is not None:
                found.append(lang)
        except PermissionError:
            continue
    return found
