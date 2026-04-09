"""File system operations: read, write, copy, hash.

Classes
-------
LocalFileReader
    Read file content from the local filesystem.
LocalFileWriter
    Write file content to the local filesystem.
SHA256Hasher
    Compute SHA-256 hash of string content for drift detection.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


class LocalFileReader:
    """Read file content from the local filesystem."""

    def read(self, path: Path) -> str:
        """Read the full text content of a file.

        Parameters
        ----------
        path : Path
            File to read.

        Returns
        -------
        str
            UTF-8 decoded file content.
        """
        return path.read_text(encoding="utf-8")


class LocalFileWriter:
    """Write file content to the local filesystem."""

    def write(self, path: Path, content: str) -> None:
        """Write text content to a file, creating parent directories as needed.

        Parameters
        ----------
        path : Path
            Destination file path.
        content : str
            Text to write.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


class SHA256Hasher:
    """Compute SHA-256 hash of string content for drift detection."""

    def hash_content(self, content: str) -> str:
        """Compute a SHA-256 hex digest of *content*.

        Parameters
        ----------
        content : str
            Text to hash.

        Returns
        -------
        str
            Hexadecimal SHA-256 digest.
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
