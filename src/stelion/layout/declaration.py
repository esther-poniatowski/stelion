"""
Reading of a layout declaration, the format `stelion:layout@1`.

A consumer declares the layout of its repositories: Stelion imposes none. The schema of the format
is `stelion/schemas/layout.schema.json`, and Stelion ships default layouts under `stelion/layouts/`,
which a layout extends by name.

Functions
---------
load_layout(path) -> Layout
    Read a layout, merge the layouts that it extends, and check it.
glob_regex(pattern) -> re.Pattern
    Compile a glob anchored at the root of a repository.
within(path, patterns) -> bool
    Whether a path, or one of its folders, matches a glob.

Classes
-------
Layout, FolderKind, FileKind, Placement, RootEntry, Retired, Forbidden
    The checked content of a layout.
LayoutError
    A layout that cannot be read, breaks its schema, or names what it lacks.
"""

import json
import re
from dataclasses import dataclass, field
from functools import cache
from importlib.resources import files
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

import yaml
from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

LAYOUT_FORMAT = "stelion:layout@1"
"""Contract identifier of a layout declaration."""


class LayoutError(Exception):
    """A layout that cannot be read, breaks its schema, or names a kind or an area it lacks."""


@cache
def glob_regex(pattern: str) -> re.Pattern[str]:
    """
    Compile a glob anchored at the root of a repository.

    `**` as a whole segment matches any number of folders, `*` any text without `/`, and `?` one
    character other than `/`. A final `/` is ignored, so that a glob names a folder.

    Examples
    --------
    >>> bool(glob_regex("a/**/b.md").fullmatch("a/x/y/b.md"))
    True
    >>> bool(glob_regex("a/**").fullmatch("a"))
    False
    >>> bool(glob_regex("*.template").fullmatch("log.md.template"))
    True
    """
    parts = pattern.strip("/").split("/")
    expression = ""
    for index, part in enumerate(parts):
        last = index == len(parts) - 1
        if part == "**":
            expression += ".*" if last else "(?:[^/]+/)*"
            continue
        for character in part:
            expression += {"*": "[^/]*", "?": "[^/]"}.get(character, re.escape(character))
        if not last:
            expression += "/"
    return re.compile(expression)


def within(path: PurePosixPath, patterns: Sequence[str]) -> bool:
    """
    Whether a path relative to the root, or one of its folders, matches one of the globs.

    Examples
    --------
    >>> within(PurePosixPath("src/pkg/a.py"), ["src/**"])
    True
    >>> within(PurePosixPath("a/b.py"), ["src/**"])
    False
    >>> within(PurePosixPath("archive/x/a.md"), ["archive"])
    True
    """
    candidates = [path, *(parent for parent in path.parents if parent != PurePosixPath("."))]
    return any(
        glob_regex(pattern).fullmatch(candidate.as_posix())
        for candidate in candidates
        for pattern in patterns
    )


@dataclass(frozen=True)
class FolderKind:
    """A kind of folder: the folders that it matches, and the kinds of file that it requires."""

    identifier: str
    match: str
    exclude: tuple[str, ...] = ()
    when: Mapping[str, Any] | None = None
    requires: tuple[str, ...] = ()
    phases: str | None = None


@dataclass(frozen=True)
class FileKind:
    """A kind of file named by a fixed pattern."""

    identifier: str
    name: re.Pattern[str]
    admitted: tuple[str, ...]
    within: tuple[str, ...] = ()
    role: str | None = None
    skeleton: str | None = None
    exceptions: tuple[str, ...] = ()


@dataclass(frozen=True)
class Forbidden:
    """A direction in which a file may not link, from one area into others."""

    identifier: str
    source: str
    targets: tuple[str, ...]
    reason: str = ""


@dataclass(frozen=True)
class Retired:
    """A retired path prefix, and the files that may still store it."""

    prefix: str
    retained_in: frozenset[str] = frozenset()


@dataclass(frozen=True)
class RootEntry:
    """An entry admitted at the root of a repository."""

    name: str
    folder: bool = False
    required: bool = False


@dataclass(frozen=True)
class Placement:
    """Files of given suffixes, admitted only under given paths."""

    identifier: str
    suffixes: frozenset[str]
    allowed: tuple[str, ...]
    exceptions: tuple[str, ...] = ()

    def misplaced(self, path: PurePosixPath) -> bool:
        """Whether a file of the suffixes lies outside the admitted paths, or in an exception."""
        if path.suffix not in self.suffixes:
            return False
        return not within(path, self.allowed) or within(path, self.exceptions)


@dataclass(frozen=True)
class Layout:  # pylint: disable=too-many-instance-attributes
    """A checked layout, merged with the layouts that it extends."""

    path: Path
    exclude: tuple[str, ...] = ()
    role_key: str = "role"
    areas: Mapping[str, str] = field(default_factory=dict)
    folders: tuple[FolderKind, ...] = ()
    kinds: tuple[FileKind, ...] = ()
    roles_everywhere: frozenset[str] = frozenset()
    roles_by_area: Mapping[str, frozenset[str]] = field(default_factory=dict)
    open_areas: frozenset[str] = frozenset()
    forbidden: tuple[Forbidden, ...] = ()
    retired: tuple[Retired, ...] = ()
    root: tuple[RootEntry, ...] = ()
    placements: tuple[Placement, ...] = ()
    untracked: tuple[str, ...] = ()
    max_file_bytes: int | None = None

    def area_of(self, path: PurePosixPath) -> str | None:
        """Return the area holding a path: the first area whose folder holds it."""
        for area, folder in self.areas.items():
            if within(path, [folder]):
                return area
        return None


@cache
def _schema() -> dict[str, Any]:
    """Return the packaged schema of a layout, read once."""
    schema: dict[str, Any] = json.loads(
        files("stelion").joinpath("schemas/layout.schema.json").read_text("utf-8")
    )
    return schema


def _read(path: Path) -> dict[str, Any]:
    """Read one layout file and check it against the schema, without its parents."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
        raise LayoutError(f"{path}: the layout cannot be read: {error}") from error
    errors = list(Draft202012Validator(_schema()).iter_errors(raw))
    if errors:
        first = min(errors, key=lambda error: list(error.absolute_path))
        where = "/".join(str(step) for step in first.absolute_path)
        raise LayoutError(f"{path}: /{where}: {first.message}")
    data: dict[str, Any] = raw
    return data


def _parent(path: Path, name: str) -> Path:
    """Return the file of the layout that a layout extends: a shipped layout, or a path."""
    shipped = files("stelion").joinpath(f"layouts/{name}.yml")
    if "/" not in name and not name.endswith((".yml", ".yaml")) and shipped.is_file():
        return Path(str(shipped))
    return (path.parent / name).resolve()


def _by_id(base: list[Any], extra: list[Any]) -> list[Any]:
    """Merge two lists of entries keyed by `id`, those of `extra` replacing those of `base`."""
    merged = {entry["id"]: entry for entry in base}
    merged.update({entry["id"]: entry for entry in extra})
    return list(merged.values())


def _union(base: list[Any], extra: list[Any]) -> list[Any]:
    """Unite two lists of names, in the order of the base then of the extension."""
    return [*base, *(item for item in extra if item not in base)]


def merge(base: Mapping[str, Any], extra: Mapping[str, Any]) -> dict[str, Any]:
    """
    Merge a layout over the layout that it extends.

    Lists of entries with an `id`, and root entries by `name`, are merged by key, the extending
    layout replacing an entry of the same key. Lists of names are united. Mappings are merged key
    by key, and a scalar of the extending layout replaces that of the base.

    Examples
    --------
    >>> merge({"exclude": ["a"], "tree": {"max_file_mib": 1}}, {"exclude": ["b"], "tree": {}})
    {'exclude': ['a', 'b'], 'tree': {'max_file_mib': 1}}
    """
    merged: dict[str, Any] = dict(base)
    for key, value in extra.items():
        old = merged.get(key)
        if isinstance(old, dict) and isinstance(value, dict):
            merged[key] = merge(old, value)
        elif isinstance(old, list) and isinstance(value, list):
            if key == "root":
                kept = {entry["name"]: entry for entry in old}
                kept.update({entry["name"]: entry for entry in value})
                merged[key] = list(kept.values())
            elif all(isinstance(item, dict) and "id" in item for item in old + value):
                merged[key] = _by_id(old, value)
            else:
                merged[key] = _union(old, value)
        else:
            merged[key] = value
    return merged


def _resolved(path: Path, seen: tuple[Path, ...] = ()) -> dict[str, Any]:
    """Read a layout and the chain of layouts that it extends, merged from the base."""
    if path in seen:
        raise LayoutError(f"{path}: the layout extends itself through {seen[-1]}")
    data = _read(path)
    name = data.get("extends")
    if name is None:
        return data
    parent = _parent(path, name)
    if not parent.is_file():
        raise LayoutError(f"{path}: the extended layout {name} is absent")
    merged = merge(_resolved(parent, (*seen, path)), data)
    merged.pop("extends", None)
    return merged


def _check(layout: Layout) -> None:
    """Raise `LayoutError` when the layout names a kind or an area that it does not declare."""
    folders = {kind.identifier for kind in layout.folders}
    files_kinds = {kind.identifier for kind in layout.kinds}
    for folder in layout.folders:
        for required in folder.requires:
            if required not in files_kinds:
                raise LayoutError(
                    f"folder kind {folder.identifier} requires {required}, no kind of file"
                )
        if folder.phases is not None and folder.phases not in folders:
            raise LayoutError(
                f"folder kind {folder.identifier} has phases {folder.phases}, no kind"
            )
    for kind in layout.kinds:
        for admitted in kind.admitted:
            if admitted not in folders:
                raise LayoutError(
                    f"kind {kind.identifier} is admitted in {admitted}, no kind of folder"
                )
    areas = set(layout.areas)
    named = {*layout.roles_by_area, *layout.open_areas}
    named |= {rule.source for rule in layout.forbidden}
    named |= {target for rule in layout.forbidden for target in rule.targets}
    for area in sorted(named - areas):
        raise LayoutError(f"the layout names the area {area}, which it does not declare")


def load_layout(path: Path) -> Layout:
    """
    Read a layout, merge the layouts that it extends, and check it.

    Parameters
    ----------
    path : Path
        The YAML file of the layout.

    Returns
    -------
    Layout
        The merged and checked layout.

    Raises
    ------
    LayoutError
        If a file of the chain cannot be read or breaks the schema, the chain loops, a name pattern
        is invalid, or the layout names a kind or an area that it does not declare.
    """
    data = _resolved(path.resolve())
    roles = data.get("roles", {})
    tree = data.get("tree", {})
    try:
        kinds = tuple(
            FileKind(
                entry["id"],
                re.compile(entry["name"]),
                tuple(entry["in"]),
                tuple(entry.get("within", ())),
                entry.get("role"),
                entry.get("skeleton"),
                tuple(entry.get("except", ())),
            )
            for entry in data.get("kinds", [])
        )
    except re.error as error:
        raise LayoutError(f"{path}: a name pattern of a kind is invalid: {error}") from error
    limit = tree.get("max_file_mib")
    layout = Layout(
        path=path.resolve(),
        exclude=tuple(data.get("exclude", ())),
        role_key=data.get("metadata", {}).get("role", "role"),
        areas=dict(data.get("areas", {})),
        folders=tuple(
            FolderKind(
                entry["id"],
                entry["match"],
                tuple(entry.get("exclude", ())),
                entry.get("when"),
                tuple(entry.get("requires", ())),
                entry.get("phases"),
            )
            for entry in data.get("folders", [])
        ),
        kinds=kinds,
        roles_everywhere=frozenset(roles.get("everywhere", ())),
        roles_by_area={area: frozenset(names) for area, names in roles.get("by_area", {}).items()},
        open_areas=frozenset(roles.get("open", ())),
        forbidden=tuple(
            Forbidden(entry["id"], entry["from"], tuple(entry["to"]), entry.get("reason", ""))
            for entry in data.get("links", {}).get("forbidden", [])
        ),
        retired=tuple(
            Retired(entry["prefix"], frozenset(entry.get("retained_in", ())))
            for entry in data.get("retired", [])
        ),
        root=tuple(
            RootEntry(entry["name"], entry.get("folder", False), entry.get("required", False))
            for entry in tree.get("root", [])
        ),
        placements=tuple(
            Placement(
                entry["id"],
                frozenset(entry["suffixes"]),
                tuple(entry["allowed"]),
                tuple(entry.get("except", ())),
            )
            for entry in tree.get("placements", [])
        ),
        untracked=tuple(tree.get("untracked", ())),
        max_file_bytes=int(limit * 1024 * 1024) if limit is not None else None,
    )
    try:
        _check(layout)
    except LayoutError as error:
        raise LayoutError(f"{path}: {error}") from error
    return layout
