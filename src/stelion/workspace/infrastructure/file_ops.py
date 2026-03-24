"""File system operations: read, write, copy, hash."""

from __future__ import annotations

import hashlib
from pathlib import Path


class LocalFileReader:
    """Read file content from the local filesystem."""

    def read(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")


class LocalFileWriter:
    """Write file content to the local filesystem."""

    def write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


class SHA256Hasher:
    """Compute SHA-256 hash of string content for drift detection."""

    def hash_content(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
