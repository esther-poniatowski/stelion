"""
The rules of a layout, checked on one repository.

The rules read the tracked files of the repository, and read the metadata, the references and the
exemptions of its files through a `Reader`. The reader of a repository is
`stelion.layout.anagraphe.AnagrapheReader`, which reads them through the read package of
Anagraphe, since Anagraphe owns the metadata sources, the link syntaxes and the exemptions.

Functions
---------
check_layout(layout, root, reader) -> list[Finding]
    Check every rule of a layout on the repository at `root`.

Classes
-------
Rule, Finding
    A rule of a layout, and one of its violations.
Reader
    The port through which the rules read the metadata, references and exemptions of files.
"""

import importlib.resources
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterator, Mapping, Protocol, Sequence

from .declaration import FileKind, Layout, glob_regex, within


@dataclass(frozen=True)
class Rule:
    """A rule of a layout: its identifier and its description."""

    identifier: str
    description: str


MISSING_KIND = Rule("folder/missing-kind", "A folder lacks a kind of file that its kind requires.")
KIND_PLACEMENT = Rule(
    "kind/placement", "A file of a kind sits in a folder whose kind may not hold it."
)
KIND_ROLE = Rule("kind/role", "A file of a kind declares another role than its kind.")
KIND_SECTIONS = Rule("kind/sections", "The level-2 headings of a file do not follow its skeleton.")
ROLE_AREA = Rule("role/area", "A file declares a role that its area does not admit.")
LINK_DIRECTION = Rule(
    "link/direction", "A file links into an area that its area may not link into."
)
RETIRED_PATH = Rule("path/retired", "A retired path exists, or is stored outside its records.")
UNKNOWN_ROOT_ENTRY = Rule("tree/unknown-root-entry", "A root entry is absent from the layout.")
MISSING_ROOT_ENTRY = Rule(
    "tree/missing-root-entry", "A root entry that the layout requires is absent."
)
MISPLACED = Rule(
    "tree/misplaced", "A file of given suffixes lies outside the paths admitted for it."
)
TRACKED = Rule("tree/tracked", "Git tracks a path that the layout keeps untracked.")
OVERSIZED = Rule("tree/oversized", "A tracked file exceeds the size limit of the layout.")

RULES = (
    MISSING_KIND,
    KIND_PLACEMENT,
    KIND_ROLE,
    KIND_SECTIONS,
    ROLE_AREA,
    LINK_DIRECTION,
    RETIRED_PATH,
    UNKNOWN_ROOT_ENTRY,
    MISSING_ROOT_ENTRY,
    MISPLACED,
    TRACKED,
    OVERSIZED,
)
"""Every rule of a layout, in the order of the specification."""

_HEADING = re.compile(r"^## (.+?)\s*$")
_FENCE = re.compile(r"^(```|~~~)")
_URL = re.compile(r"(?:https?|ftp)://[^\s<>)\]]+")
_ABSOLUTE = re.compile(r"(?<![\w.])/(?:[^\s`'\"<>()[\]]+/)+[^\s`'\"<>()[\]]*")


class Reader(Protocol):
    """The port through which the rules read what the owner of addressing reads."""

    def metadata(self, path: str) -> Mapping[str, Any]:
        """Return the metadata of a file, empty when it holds none."""

    def references(self, path: str) -> Sequence[Any]:
        """Return the pointers of a file, each with `named`, `raw`, `line` and `column`."""

    def exempt(self, path: str) -> bool:
        """Whether the shared exclusions of the repository leave a path out."""


@dataclass(frozen=True)
class Finding:
    """
    One violation of a rule of a layout.

    Attributes
    ----------
    rule : Rule
        The rule broken.
    path : str
        The file, or the folder ending with `/`, relative to the root of the repository.
    discriminator : str
        The offending content: a kind, a role, a target, a prefix or an entry.
    message : str
        The explanation.
    position : tuple[int, int] | None
        The line and the column of the offending text, None for a whole file or folder.
    """

    rule: Rule
    path: str
    discriminator: str
    message: str
    position: tuple[int, int] | None = None


def tracked_files(root: Path) -> list[PurePosixPath]:
    """Return the files that Git tracks below the root, or every file of a folder without Git."""
    completed = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, capture_output=True, check=False
    )
    if not completed.returncode and (root / ".git").exists():
        names = [name for name in completed.stdout.decode("utf-8").split("\0") if name]
    else:
        names = [
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and ".git" not in path.relative_to(root).parts
        ]
    return sorted(PurePosixPath(name) for name in names)


def headings(text: str) -> list[str]:
    """
    Return the level-2 headings of a Markdown text, outside fenced code.

    Examples
    --------
    >>> headings("## Parts\\n```\\n## Not one\\n```\\n## Notes\\n")
    ['Parts', 'Notes']
    """
    found, fenced = [], False
    for line in text.splitlines():
        if _FENCE.match(line):
            fenced = not fenced
        elif not fenced and (match := _HEADING.match(line)):
            found.append(match.group(1))
    return found


def follows(sections: Sequence[str], skeleton: Sequence[str]) -> bool:
    """
    Whether headings form a subsequence of the headings of a skeleton, in order.

    Examples
    --------
    >>> follows(["Parts", "Notes"], ["Parts", "Excluded", "Notes"])
    True
    >>> follows(["Notes", "Parts"], ["Parts", "Notes"])
    False
    """
    position = 0
    for section in sections:
        try:
            position = list(skeleton).index(section, position) + 1
        except ValueError:
            return False
    return True


class _Check:  # pylint: disable=too-few-public-methods
    """The rules of one layout, checked on the files of one repository."""

    def __init__(self, layout: Layout, root: Path, reader: Reader) -> None:
        self.layout = layout
        self.root = root
        self.reader = reader
        self.tracked = [path for path in tracked_files(root) if not within(path, layout.exclude)]
        self.files = [path for path in self.tracked if not reader.exempt(path.as_posix())]
        self.folders = self._classify()

    def run(self) -> list[Finding]:
        """Return the findings of every rule, in the order of the rules."""
        return [
            *self._kinds(),
            *self._roles(),
            *self._links(),
            *self._retired(),
            *self._root_entries(),
            *self._tree(),
        ]

    # --- Kinds of folder and of file -------------------------------------------------------------

    def _classify(self) -> dict[PurePosixPath, str]:
        """Map each folder of a declared kind to its kind, the first matching kind winning."""
        candidates = sorted({parent for path in self.files for parent in path.parents})
        kinds: dict[PurePosixPath, str] = {}
        for kind in self.layout.folders:
            pattern = glob_regex(kind.match)
            for folder in candidates:
                if folder in kinds or folder == PurePosixPath("."):
                    continue
                if not pattern.fullmatch(folder.as_posix()) or within(folder, kind.exclude):
                    continue
                if kind.when is not None:
                    data = self.reader.metadata((folder / kind.when["file"]).as_posix())
                    if data.get(kind.when["key"]) != kind.when["equals"]:
                        continue
                kinds[folder] = kind.identifier
        return kinds

    def _kind_of(self, path: PurePosixPath) -> FileKind | None:
        """Return the kind of a file: the first kind whose pattern and scope match it."""
        for kind in self.layout.kinds:
            if (
                kind.name.match(path.name)
                and (not kind.within or within(path, kind.within))
                and not within(path, kind.exceptions)
            ):
                return kind
        return None

    def _kinds(self) -> Iterator[Finding]:
        """Report the placement, role and sections of each file of a kind, then missing kinds."""
        held: dict[PurePosixPath, set[str]] = {folder: set() for folder in self.folders}
        for path in self.files:
            kind = self._kind_of(path)
            if kind is None:
                continue
            folder_kind = self.folders.get(path.parent)
            shown = folder_kind or "no kind"
            if folder_kind not in kind.admitted:
                yield Finding(
                    KIND_PLACEMENT,
                    path.as_posix(),
                    kind.identifier,
                    f"a file of kind {kind.identifier} sits in a folder of kind {shown}",
                )
                continue
            held[path.parent].add(kind.identifier)
            yield from self._kind_content(path, kind)
        yield from self._missing(held)

    def _kind_content(self, path: PurePosixPath, kind: FileKind) -> Iterator[Finding]:
        """Report the role and the sections of a file of a kind, in an admitted folder."""
        if kind.role is not None:
            role = self.reader.metadata(path.as_posix()).get(self.layout.role_key)
            if role != kind.role:
                yield Finding(
                    KIND_ROLE,
                    path.as_posix(),
                    kind.identifier,
                    f"kind {kind.identifier} declares role {kind.role}, the file declares {role}",
                )
        if kind.skeleton is not None:
            sections = headings(self._text(path))
            skeleton = headings(self._skeleton(kind.skeleton))
            if not follows(sections, skeleton):
                yield Finding(
                    KIND_SECTIONS,
                    path.as_posix(),
                    kind.identifier,
                    f"the headings {sections} do not follow the skeleton {skeleton}",
                )

    def _missing(self, held: Mapping[PurePosixPath, set[str]]) -> Iterator[Finding]:
        """Report each kind that a folder requires, held neither by it nor by each phase."""
        for spec in self.layout.folders:
            for folder, folder_kind in self.folders.items():
                if folder_kind != spec.identifier:
                    continue
                phases = [
                    sub
                    for sub, sub_kind in self.folders.items()
                    if spec.phases is not None and sub_kind == spec.phases and sub.parent == folder
                ]
                for required in spec.requires:
                    met = required in held[folder] or (
                        bool(phases) and all(required in held[phase] for phase in phases)
                    )
                    if not met:
                        yield Finding(
                            MISSING_KIND,
                            f"{folder.as_posix()}/",
                            required,
                            f"no file of kind {required}, in the folder or in each of its phases",
                        )

    def _skeleton(self, reference: str) -> str:
        """Read a skeleton: a path from the root, or a resource of an installed package."""
        package, separator, resource = reference.partition(":")
        if separator:
            return importlib.resources.files(package).joinpath(resource).read_text("utf-8")
        return (self.root / reference).read_text(encoding="utf-8")

    def _text(self, path: PurePosixPath) -> str:
        """Read the text of a file of the repository, empty when it cannot be read."""
        try:
            return (self.root / path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return ""

    # --- Roles and links between areas -----------------------------------------------------------

    def _admits(self, area: str | None, role: str) -> bool:
        """Whether an area admits a role, as the section roles of the layout states."""
        layout = self.layout
        listed = role in layout.roles_everywhere or any(
            role in roles for roles in layout.roles_by_area.values()
        )
        if not listed or role in layout.roles_everywhere:
            return True
        if area is None:
            return False
        return area in layout.open_areas or role in layout.roles_by_area.get(area, frozenset())

    def _roles(self) -> Iterator[Finding]:
        """Report each file whose role its area does not admit."""
        layout = self.layout
        if not (layout.roles_everywhere or layout.roles_by_area):
            return
        for path in self.files:
            role = self.reader.metadata(path.as_posix()).get(layout.role_key)
            if not isinstance(role, str):
                continue
            area = layout.area_of(path)
            if not self._admits(area, role):
                yield Finding(
                    ROLE_AREA,
                    path.as_posix(),
                    role,
                    (
                        f"role {role} is not admitted in the area {area}"
                        if area is not None
                        else f"role {role} is not admitted outside every area"
                    ),
                )

    def _links(self) -> Iterator[Finding]:
        """Report each link from an area into an area that it may not link into."""
        rules = {rule.source: rule for rule in self.layout.forbidden}
        if not rules:
            return
        for path in self.files:
            rule = rules.get(self.layout.area_of(path) or "")
            if rule is None:
                continue
            for pointer in self.reader.references(path.as_posix()):
                # The place that a link names decides its direction, whether or not a file exists
                # there; a broken link is reported by Anagraphe as broken besides.
                if pointer.named is None:
                    continue
                target_area = self.layout.area_of(PurePosixPath(pointer.named))
                if target_area in rule.targets:
                    yield Finding(
                        LINK_DIRECTION,
                        path.as_posix(),
                        pointer.raw,
                        f"links into {target_area}, which {rule.source} may not link into "
                        f"(rule {rule.identifier})",
                        (pointer.line, pointer.column),
                    )

    # --- Retired paths ---------------------------------------------------------------------------

    def _retired(self) -> Iterator[Finding]:
        """Report each retired path that exists, and each text storing one outside its records."""
        own = self._own_path()
        for retired in self.layout.retired:
            if (self.root / retired.prefix.rstrip("/")).exists():
                yield Finding(
                    RETIRED_PATH, retired.prefix, retired.prefix, "the retired path exists"
                )
            stored = re.compile(r"(?<![\w.-])" + re.escape(retired.prefix))
            for path in self.files:
                name = path.as_posix()
                if name in retired.retained_in or name == own:
                    continue
                cleaned = _ABSOLUTE.sub("", _URL.sub("", self._text(path)))
                for number, line in enumerate(cleaned.splitlines(), start=1):
                    match = stored.search(line)
                    if match:
                        yield Finding(
                            RETIRED_PATH,
                            name,
                            retired.prefix,
                            f"stores {retired.prefix}",
                            (number, match.start() + 1),
                        )

    def _own_path(self) -> str | None:
        """Return the path of the layout below the root, None when the layout lies outside."""
        try:
            return self.layout.path.relative_to(self.root.resolve()).as_posix()
        except ValueError:
            return None

    # --- Tree ------------------------------------------------------------------------------------

    def _root_entries(self) -> Iterator[Finding]:
        """Report the required root entries that are absent, and the undeclared ones."""
        if not self.layout.root:
            return
        names = sorted({path.parts[0] for path in self.tracked})
        for entry in self.layout.root:
            pattern = glob_regex(entry.name)
            if entry.required and not any(pattern.fullmatch(name) for name in names):
                yield Finding(
                    MISSING_ROOT_ENTRY,
                    entry.name,
                    entry.name,
                    "required by the layout, and absent or untracked",
                )
        for name in names:
            if not any(glob_regex(entry.name).fullmatch(name) for entry in self.layout.root):
                folder = (self.root / name).is_dir()
                yield Finding(
                    UNKNOWN_ROOT_ENTRY,
                    f"{name}/" if folder else name,
                    name,
                    "not a root entry of the layout",
                )

    def _tree(self) -> Iterator[Finding]:
        """Report the misplaced, wrongly tracked and oversized tracked files."""
        for path in self.tracked:
            name = path.as_posix()
            placement = next(
                (item for item in self.layout.placements if item.misplaced(path)), None
            )
            if placement is not None:
                yield Finding(
                    MISPLACED,
                    name,
                    placement.identifier,
                    f"a file of {placement.identifier} outside the paths admitted for it",
                )
            if within(path, self.layout.untracked):
                yield Finding(
                    TRACKED, name, name, "tracked, although the layout keeps it untracked"
                )
            limit = self.layout.max_file_bytes
            source = self.root / path
            if (
                limit is not None
                and source.is_file()
                and not source.is_symlink()
                and source.stat().st_size > limit
            ):
                yield Finding(OVERSIZED, name, name, "larger than the size limit of the layout")


def check_layout(layout: Layout, root: Path, reader: Reader) -> list[Finding]:
    """
    Check every rule of a layout on the repository at `root`.

    Parameters
    ----------
    layout : Layout
        The checked layout.
    root : Path
        The root of the repository.
    reader : Reader
        The reader of the metadata, references and exemptions of the files of the repository.

    Returns
    -------
    list[Finding]
        The findings, rule by rule in the order of `RULES`, then file by file.
    """
    return _Check(layout, root, reader).run()
