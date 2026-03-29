"""Loader for comparison instruction files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ..domain.comparison import (
    ComparisonSpec,
    FileTarget,
    FileTargetEntry,
    TreeTarget,
)
from ..exceptions import ComparisonError


class YamlSpecLoader:
    """Load and validate a comparison instruction YAML file.

    Follows the validation pattern of ``manifest_loader.py``.
    """

    def load(self, path: Path) -> ComparisonSpec:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ComparisonError(f"Could not read instruction file {path}: {exc}") from exc
        try:
            raw = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise ComparisonError(f"Invalid instruction YAML: {exc}") from exc

        if not isinstance(raw, dict):
            raise ComparisonError("Instruction file must be a YAML mapping.")

        return _parse_spec(raw, path)


def _parse_spec(raw: dict[str, Any], source: Path) -> ComparisonSpec:
    """Convert a raw YAML dict into a typed :class:`ComparisonSpec`."""
    project_names = _parse_string_sequence(raw.get("projects", ()), "projects")
    mode = _parse_required_string(raw.get("mode"), "mode")

    tree_raw = raw.get("tree")
    files_raw = raw.get("files")
    if tree_raw is not None and files_raw is not None:
        raise ComparisonError(
            f"Instruction file {source} specifies both 'tree' and 'files' sections. "
            "Use one or the other."
        )

    if mode == "tree":
        target = _parse_tree_target(_parse_optional_mapping(tree_raw, "tree"))
    elif mode == "files":
        target = _parse_file_target(_parse_optional_mapping(files_raw, "files"))
    else:
        raise ComparisonError(
            f"Instruction file {source} must specify 'mode' as 'tree' or 'files', got {mode!r}."
        )

    return ComparisonSpec(project_names=project_names, target=target)


def _parse_tree_target(raw: dict[str, Any]) -> TreeTarget:
    return TreeTarget(
        subtree=_parse_optional_string(raw.get("subtree"), "tree.subtree"),
        include_patterns=_parse_string_sequence(raw.get("include_patterns", ()), "tree.include_patterns"),
        exclude_patterns=_parse_string_sequence(raw.get("exclude_patterns", ()), "tree.exclude_patterns"),
    )


def _parse_file_target(raw: dict[str, Any]) -> FileTarget:
    entries_raw = _parse_required_sequence(raw.get("entries", []), "files.entries")
    if not entries_raw:
        raise ComparisonError("File target must specify at least one entry in 'entries'.")
    entries = tuple(_parse_file_entry(e) for e in entries_raw)
    granularity = _parse_optional_string(raw.get("granularity"), "files.granularity") or "survey"
    reference_project = _parse_optional_string(raw.get("reference"), "files.reference")
    try:
        return FileTarget(
            entries=entries,
            granularity=granularity,
            reference_project=reference_project,
        )
    except ValueError as exc:
        raise ComparisonError(str(exc)) from exc


def _parse_file_entry(raw: Any) -> FileTargetEntry:
    entry = _parse_required_mapping(raw, "files.entries[]")
    canonical = _parse_required_string(entry.get("canonical"), "files.entries[].canonical")
    overrides = _parse_string_mapping(entry.get("overrides", {}), "files.entries[].overrides")
    selectors = _parse_string_sequence(entry.get("selectors", ()), "files.entries[].selectors")
    parser_hint = _parse_optional_string(entry.get("parser_hint"), "files.entries[].parser_hint")
    if not canonical:
        raise ComparisonError("Each file entry must specify 'canonical'.")
    return FileTargetEntry(
        canonical=canonical,
        overrides=overrides,
        selectors=selectors,
        parser_hint=parser_hint,
    )


def _parse_optional_mapping(raw: Any, location: str) -> dict[str, Any]:
    if raw is None:
        return {}
    return _parse_required_mapping(raw, location)


def _parse_required_mapping(raw: Any, location: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ComparisonError(f"{location} must be a mapping.")
    return raw


def _parse_required_sequence(raw: Any, location: str) -> list[Any] | tuple[Any, ...]:
    if isinstance(raw, (str, bytes)) or not isinstance(raw, (list, tuple)):
        raise ComparisonError(f"{location} must be a sequence.")
    return raw


def _parse_string_sequence(raw: Any, location: str) -> tuple[str, ...]:
    items = _parse_required_sequence(raw, location)
    values: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, str):
            raise ComparisonError(f"{location}[{index}] must be a string.")
        values.append(item)
    return tuple(values)


def _parse_string_mapping(raw: Any, location: str) -> dict[str, str]:
    mapping = _parse_required_mapping(raw, location)
    values: dict[str, str] = {}
    for key, value in mapping.items():
        if not isinstance(key, str):
            raise ComparisonError(f"{location} keys must be strings.")
        if not isinstance(value, str):
            raise ComparisonError(f"{location}.{key} must be a string.")
        values[key] = value
    return values


def _parse_required_string(raw: Any, location: str) -> str:
    if not isinstance(raw, str) or not raw:
        raise ComparisonError(f"{location} must be a non-empty string.")
    return raw


def _parse_optional_string(raw: Any, location: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ComparisonError(f"{location} must be a string.")
    return raw
