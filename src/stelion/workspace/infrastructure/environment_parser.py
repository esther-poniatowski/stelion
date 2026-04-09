"""Parse Conda environment.yml files into EnvironmentSpec.

Classes
-------
CondaEnvironmentReader
    Read and parse a project's environment.yml.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from ..domain.environment import EnvironmentSpec


INVALID_ENVIRONMENT_MARKER = "<invalid-environment.yml>"


class CondaEnvironmentReader:
    """Read and parse a project's environment.yml."""

    def read(self, project_dir: Path) -> EnvironmentSpec | None:
        """Parse environment.yml from a project directory.

        Parameters
        ----------
        project_dir : Path
            Root directory of the project.

        Returns
        -------
        EnvironmentSpec | None
            Parsed environment, or ``None`` if the file does not exist.
        """
        env_path = project_dir / "environment.yml"
        if not env_path.exists():
            return None

        try:
            with open(env_path, encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
        except yaml.YAMLError as exc:
            return EnvironmentSpec(
                name=INVALID_ENVIRONMENT_MARKER,
                issues=(
                    f"{project_dir.name}: invalid environment.yml ({str(exc).splitlines()[0]})",
                ),
            )

        if not isinstance(raw, dict):
            return EnvironmentSpec(
                name=INVALID_ENVIRONMENT_MARKER,
                issues=(f"{project_dir.name}: environment.yml root must be a mapping",),
            )

        issues: list[str] = []
        name_raw = raw.get("name", "")
        name = name_raw if isinstance(name_raw, str) else INVALID_ENVIRONMENT_MARKER
        if name_raw != "" and not isinstance(name_raw, str):
            issues.append(f"{project_dir.name}: environment.yml field 'name' must be a string")

        channels = _coerce_str_sequence(
            raw.get("channels", ()),
            project_dir.name,
            "channels",
            issues,
        )
        deps: list[str] = []
        pip_deps: list[str] = []

        dependencies_raw = raw.get("dependencies", ())
        if dependencies_raw is None:
            dependencies_raw = ()
        if not isinstance(dependencies_raw, list):
            issues.append(
                f"{project_dir.name}: environment.yml field 'dependencies' must be a sequence"
            )
            dependencies_raw = []

        for item in dependencies_raw:
            if isinstance(item, str):
                deps.append(item)
            elif isinstance(item, dict) and "pip" in item:
                pip_deps.extend(
                    _coerce_str_sequence(
                        item.get("pip", ()),
                        project_dir.name,
                        "dependencies[].pip",
                        issues,
                    )
                )
            else:
                issues.append(
                    f"{project_dir.name}: environment.yml dependency entries must be strings or pip mappings"
                )

        return EnvironmentSpec(
            name=name,
            channels=tuple(channels),
            dependencies=tuple(deps),
            pip_dependencies=tuple(pip_deps),
            issues=tuple(issues),
        )


def _coerce_str_sequence(
    value: object,
    project_name: str,
    field: str,
    issues: list[str],
) -> tuple[str, ...]:
    """Return the valid string items from *value* and record structural issues.

    Parameters
    ----------
    value : object
        Raw value to coerce into a string sequence.
    project_name : str
        Project name used in diagnostic messages.
    field : str
        Field name used in diagnostic messages.
    issues : list[str]
        Mutable list to which structural issues are appended.

    Returns
    -------
    tuple[str, ...]
        Valid string items extracted from *value*.
    """
    if value is None:
        return ()
    if not isinstance(value, list):
        issues.append(f"{project_name}: environment.yml field '{field}' must be a sequence of strings")
        return ()
    result: list[str] = []
    for item in value:
        if isinstance(item, str):
            result.append(item)
        else:
            issues.append(f"{project_name}: environment.yml field '{field}' contains a non-string entry")
    return tuple(result)
