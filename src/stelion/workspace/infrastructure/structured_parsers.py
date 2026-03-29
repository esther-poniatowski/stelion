"""Structured-file parsers for cross-project comparison.

All parsers consume **text content** (not file paths) and return a
nested ``dict``.  The :class:`DispatchingParser` maps file extensions
to concrete parsers — the extension seam for new formats.
"""

from __future__ import annotations

import json
import tomllib

import yaml

from ..exceptions import ComparisonError


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


class DispatchingParser:
    """Route parsing to the correct backend based on file extension or hint.

    Parameters
    ----------
    parsers
        Mapping from extension (including dot, e.g. ``".toml"``) to a parser
        instance.
    """

    def __init__(self, parsers: dict[str, TomlParser | YamlParser | JsonParser]) -> None:
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
