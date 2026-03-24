"""New project bootstrapping use-case.

Copies a template project, substitutes placeholders, renames directories
and files, and optionally initializes a git repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..domain.manifest import TemplateConfig, EcosystemDefaults


@dataclass(frozen=True)
class BootstrapResult:
    """Outcome of bootstrapping a new project."""

    name: str
    target_dir: Path
    placeholders_replaced: int
    files_renamed: int
    git_initialized: bool


def build_placeholder_bindings(
    name: str,
    description: str,
    defaults: EcosystemDefaults,
    author_name: str = "",
    author_email: str = "",
) -> dict[str, str]:
    """Build the placeholder-to-value mapping for template substitution.

    Parameters
    ----------
    name
        Project name (used as package_name, repo_name, env_name, project_name).
    description
        One-line project description.
    defaults
        Ecosystem-level defaults from the manifest.
    author_name
        Author full name (typically from git config).
    author_email
        Author email (typically from git config).
    """
    bindings = {
        "{{ package_name }}": name,
        "{{ repo_name }}": name,
        "{{ project_name }}": name,
        "{{ env_name }}": name,
        "{{ description }}": description,
        "{{ github_user }}": defaults.github_user,
        "{{ channel_name }}": defaults.channel_name,
        "{{ license }}": defaults.license,
    }
    if author_name:
        bindings["{{ author_name }}"] = author_name
        first = author_name.split()[0] if author_name.split() else ""
        last = author_name.split()[-1] if author_name.split() else ""
        bindings["{{ first_name }}"] = first
        bindings["{{ last_name }}"] = last
    if author_email:
        bindings["{{ email }}"] = author_email
        bindings["{{ contact@example.com }}"] = author_email
    return bindings
