"""
The reader of a repository for the rules of a layout, through the read package of Anagraphe.

Anagraphe owns the metadata sources of a repository, the syntaxes and the resolution of its links,
and its shared exclusions. The rules of a layout therefore read them through `anagraphe-read`, a
dependency of the extra `layout` of Stelion, and implement none of them.
"""

from pathlib import Path
from typing import Any, Mapping, Sequence

from anagraphe_read import open_repository


class AnagrapheReader:
    """
    The metadata, references and exemptions of the files of one repository.

    The configuration of Anagraphe is the file ``config`` when it is given, else the file
    ``anagraphe.yml`` at one of the places of the root that Anagraphe accepts.

    Raises
    ------
    ValueError
        If the configuration of Anagraphe is invalid, or if ``config`` names no file.
    """

    def __init__(self, root: Path, config: Path | None = None) -> None:
        self._repository = open_repository(root, config=config)
        self._metadata: dict[str, Mapping[str, Any]] = {}

    def metadata(self, path: str) -> Mapping[str, Any]:
        """Return the metadata of a file, read through its declared metadata source."""
        if path not in self._metadata:
            self._metadata[path] = self._repository.metadata(path)
        return self._metadata[path]

    def references(self, path: str) -> Sequence[Any]:
        """Return the pointers of a file, each resolved to a path of the repository or None."""
        return self._repository.references(path)

    def exempt(self, path: str) -> bool:
        """Whether the shared exclusions of the repository leave a path out."""
        return self._repository.exempt(path)
