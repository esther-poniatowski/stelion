"""Structured-file parsers for cross-project comparison.

All parsers consume **text content** (not file paths) and return a
nested ``dict``.  The :class:`DispatchingParser` maps file extensions
to concrete parsers — the extension seam for new formats.
"""

from __future__ import annotations

import json
import tomllib
from typing import Protocol

import yaml

from ..exceptions import ComparisonError


class ContentParser(Protocol):
    """Protocol for parsing text content into a dict."""

    def parse(self, content: str) -> dict: ...


class TomlParser:
    """Parse TOML text into a dict."""

    def parse(self, content: str) -> dict:
        try:
            return tomllib.loads(content)
        except tomllib.TOMLDecodeError as exc:
            raise ValueError(f"Invalid TOML: {exc}") from exc


class YamlParser:
    """Parse YAML text into a dict."""

    def parse(self, content: str) -> dict:
        try:
            result = yaml.safe_load(content)
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML: {exc}") from exc
        if not isinstance(result, dict):
            raise ValueError(f"Expected YAML mapping, got {type(result).__name__}")
        return result


class JsonParser:
    """Parse JSON text into a dict."""

    def parse(self, content: str) -> dict:
        try:
            result = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON: {exc}") from exc
        if not isinstance(result, dict):
            raise ValueError(f"Expected JSON object, got {type(result).__name__}")
        return result


class MarkdownSectionParser:
    """Parse Markdown into a nested dict keyed by header text.

    The H1 title (``# Project``) is discarded — it always varies across
    projects.  Text before the first H2 header is stored under
    ``_preamble``.  Leaf sections hold their body text as the value.
    Sections with both body text and subsections store the body under a
    ``_body`` key.

    Example::

        ## Overview            →  {"Overview": {"Motivation": "...", "Advantages": "..."}}
        ### Motivation
        ...
        ### Advantages
        ...
        ## Features            →  {"Features": "- [X] item\\n..."}
    """

    def parse(self, content: str) -> dict:
        sections = _split_sections(content)
        return _build_section_tree(sections)


def _split_sections(content: str) -> list[tuple[int, str, str]]:
    """Split Markdown into ``(level, title, body)`` triples."""
    sections: list[tuple[int, str, list[str]]] = []
    current: tuple[int, str, list[str]] | None = None

    for line in content.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#") and (stripped[len(stripped) - len(stripped.lstrip("#")):].strip()):
            hashes = len(stripped) - len(stripped.lstrip("#"))
            title = stripped[hashes:].strip()
            if current is not None:
                sections.append(current)
            current = (hashes, title, [])
        elif current is not None:
            current[2].append(line)
        else:
            # Text before the first header.
            if sections or current:
                pass
            else:
                current = (0, "_preamble", [line])

    if current is not None:
        sections.append(current)

    return [(level, title, "\n".join(body).strip()) for level, title, body in sections]


def _build_section_tree(sections: list[tuple[int, str, str]]) -> dict:
    """Build a nested dict from a flat list of ``(level, title, body)``."""
    root: dict = {}
    # Stack of (level, dict_node) — the dict where children should be added.
    stack: list[tuple[int, dict]] = [(0, root)]

    for level, title, body in sections:
        # The H1 title is always the project name — skip it.
        if level == 1:
            continue

        # Preamble (text before any header).
        if level == 0:
            if body:
                root["_preamble"] = body
            continue

        # Pop stack back to find the correct parent.
        while len(stack) > 1 and stack[-1][0] >= level:
            stack.pop()

        parent = stack[-1][1]
        parent[title] = body
        # Push a placeholder dict in case this section has children.
        # If children arrive, they will be inserted into this dict;
        # otherwise the string value stays.
        child_dict: dict = {}
        stack.append((level, child_dict))
        # We'll reconcile string vs dict in the finalization pass.
        parent[f"\x00{title}"] = child_dict  # hidden key for child accumulation

    # Reconcile: for each section that got children, merge body + children.
    _reconcile(root)
    return root


def _reconcile(d: dict) -> None:
    """Merge child-accumulation dicts into their parent entries."""
    keys = [k for k in d if not k.startswith("\x00")]
    for key in keys:
        child_key = f"\x00{key}"
        child_dict = d.pop(child_key, None)
        if child_dict is None:
            continue
        _reconcile(child_dict)
        if child_dict:
            # This section has subsections — promote to dict.
            body = d[key]
            if body:
                child_dict["_body"] = body
            d[key] = child_dict
    # Clean up any remaining hidden keys (shouldn't happen, but be safe).
    for k in [k for k in d if k.startswith("\x00")]:
        d.pop(k)


class DispatchingParser:
    """Route parsing to the correct backend based on file extension or hint.

    Parameters
    ----------
    parsers
        Mapping from extension (including dot, e.g. ``".toml"``) to a parser
        instance.
    """

    def __init__(self, parsers: dict[str, ContentParser]) -> None:
        self._parsers = parsers

    def parse(self, content: str, *, extension: str = "", hint: str | None = None) -> dict:
        """Parse *content* using the parser identified by *hint* or *extension*.

        Parameters
        ----------
        content
            Raw file text.
        extension
            File extension including the dot (e.g. ``".toml"``).
        hint
            Parser name override (e.g. ``"toml"``), takes precedence over
            *extension*.
        """
        key = f".{hint}" if hint else extension.lower()
        parser = self._parsers.get(key)
        if parser is None:
            raise ComparisonError(
                f"No parser registered for {key!r}. "
                f"Registered extensions: {', '.join(sorted(self._parsers))}"
            )
        return parser.parse(content)
