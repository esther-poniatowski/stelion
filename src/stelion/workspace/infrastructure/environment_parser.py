"""Parse Conda environment.yml files into EnvironmentSpec."""

from __future__ import annotations

from pathlib import Path

import yaml

from ..domain.environment import EnvironmentSpec


class CondaEnvironmentReader:
    """Read and parse a project's environment.yml."""

    def read(self, project_dir: Path) -> EnvironmentSpec | None:
        """Parse environment.yml from a project directory.

        Returns None if the file does not exist.
        """
        env_path = project_dir / "environment.yml"
        if not env_path.exists():
            return None

        with open(env_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        name = raw.get("name", "")
        channels = raw.get("channels", [])
        deps: list[str] = []
        pip_deps: list[str] = []

        for item in raw.get("dependencies", []):
            if isinstance(item, str):
                deps.append(item)
            elif isinstance(item, dict) and "pip" in item:
                pip_deps.extend(item["pip"] or [])

        return EnvironmentSpec(
            name=name,
            channels=channels,
            dependencies=deps,
            pip_dependencies=pip_deps,
        )
