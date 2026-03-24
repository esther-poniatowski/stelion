"""Domain models and logic for Conda environment specifications."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EnvironmentSpec:
    """Parsed content of a Conda environment.yml file."""

    name: str = ""
    channels: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    pip_dependencies: tuple[str, ...] = ()


def merge_environments(specs: list[EnvironmentSpec], name: str) -> EnvironmentSpec:
    """Merge multiple environment specs into one, de-duplicating entries.

    Channels and dependencies are unioned in encounter order. Pip editable
    installs (lines starting with ``-e``) are excluded from the shared
    environment since they contain machine-specific paths.
    """
    seen_channels: dict[str, None] = {}
    seen_deps: dict[str, None] = {}
    seen_pip: dict[str, None] = {}

    for spec in specs:
        for ch in spec.channels:
            seen_channels.setdefault(ch, None)
        for dep in spec.dependencies:
            seen_deps.setdefault(dep, None)
        for pip_dep in spec.pip_dependencies:
            if pip_dep.strip().startswith("-e"):
                continue
            seen_pip.setdefault(pip_dep, None)

    return EnvironmentSpec(
        name=name,
        channels=tuple(seen_channels),
        dependencies=tuple(seen_deps),
        pip_dependencies=tuple(seen_pip),
    )
