"""Extract ProjectMetadata from a project's pyproject.toml."""

from __future__ import annotations

import tomllib
import warnings
from pathlib import Path

from ..domain.project import ProjectMetadata


class PyprojectExtractor:
    """Read pyproject.toml and produce a ProjectMetadata instance."""

    def extract(self, project_dir: Path) -> ProjectMetadata:
        """Extract metadata from a project directory.

        Reads ``pyproject.toml`` for package metadata. Determines ``has_git``
        from the presence of a ``.git`` directory. If ``pyproject.toml`` is
        missing or contains invalid TOML, a warning is emitted and all fields
        derived from it fall back to their defaults; fields derivable from the
        filesystem (``has_git``, ``languages``, README description) are still
        populated normally.
        """
        has_git = (project_dir / ".git").is_dir()
        pyproject_path = project_dir / "pyproject.toml"

        data: dict = {}
        if not pyproject_path.exists():
            warnings.warn(
                f"{project_dir.name}: missing pyproject.toml, using defaults",
                stacklevel=2,
            )
        else:
            try:
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
            except tomllib.TOMLDecodeError as exc:
                warnings.warn(
                    f"{project_dir.name}: invalid TOML ({exc}), using defaults",
                    stacklevel=2,
                )

        project = data.get("project", {})
        name = project.get("name", project_dir.name)
        version = project.get("version", "0.0.0")
        description = project.get("description", "") or _readme_description(project_dir)
        urls = project.get("urls", {})
        homepage = urls.get("homepage")

        languages = _detect_languages(project_dir)

        return ProjectMetadata(
            name=name,
            path=project_dir,
            description=description,
            version=version,
            homepage=homepage,
            has_git=has_git,
            languages=languages,
        )


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


def _detect_languages(project_dir: Path) -> tuple[str, ...]:
    """Detect programming languages from source file extensions."""
    search_dir = project_dir / "src" if (project_dir / "src").is_dir() else project_dir
    found = []
    for ext, lang in _EXTENSION_MAP.items():
        try:
            if next(search_dir.rglob(f"*{ext}"), None) is not None:
                found.append(lang)
        except PermissionError:
            continue
    return tuple(found)
