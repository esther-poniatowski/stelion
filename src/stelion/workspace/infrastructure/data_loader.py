"""Load bundled package data resources via importlib.resources."""

from __future__ import annotations

import json
from importlib import resources
from typing import Any


class StelionDataLoader:
    """Load files from the stelion.data package."""

    _PACKAGE = "stelion.data"

    def load_text(self, resource_path: str) -> str:
        """Load a text resource from the data directory.

        Parameters
        ----------
        resource_path : str
            Dot-separated or slash-separated path relative to stelion/data/.
            Examples: ``"references/design-principles.md"``,
            ``"vscode/settings.json"``.

        Returns
        -------
        str
            UTF-8 decoded text content of the resource.
        """
        parts = resource_path.replace("\\", "/").split("/")
        subpackage = ".".join([self._PACKAGE] + parts[:-1])
        filename = parts[-1]
        ref = resources.files(subpackage).joinpath(filename)
        return ref.read_text(encoding="utf-8")

    def load_json(self, resource_path: str) -> Any:
        """Load and parse a JSON resource from the data directory.

        Parameters
        ----------
        resource_path : str
            Slash-separated path relative to stelion/data/.

        Returns
        -------
        Any
            Deserialized JSON content.
        """
        text = self.load_text(resource_path)
        return json.loads(text)
