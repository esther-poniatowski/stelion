"""Pure composition of workspace-manifest defaults and consumer overlays."""

from __future__ import annotations

from copy import deepcopy
from typing import Mapping

from ..exceptions import ManifestValidationError


def merge_manifest_mappings(
    base: Mapping[str, object],
    overlay: Mapping[str, object],
) -> dict[str, object]:
    """Merge a consumer overlay into a canonical manifest mapping.

    Nonempty nested mappings merge recursively. An empty mapping explicitly
    clears a default mapping. Every scalar and sequence replaces its default.
    Neither input is mutated.

    Parameters
    ----------
    base : Mapping[str, object]
        Canonical manifest values owned by Stelion.
    overlay : Mapping[str, object]
        Consumer-specific values that differ from the canonical defaults.

    Returns
    -------
    dict[str, object]
        Independent mapping containing the composed manifest values.
    """
    return _merge_manifest_mappings(base, overlay, ())


def _merge_manifest_mappings(
    base: Mapping[str, object],
    overlay: Mapping[str, object],
    path: tuple[str, ...],
) -> dict[str, object]:
    """Implement recursive overlay merging with field-path diagnostics."""
    merged = deepcopy(dict(base))
    for key, overlay_value in overlay.items():
        field_path = path + (key,)
        if overlay_value is None:
            raise ManifestValidationError(
                f"Manifest overlay value cannot be null: {'.'.join(field_path)}"
            )
        base_value = merged.get(key)
        if (
            isinstance(base_value, Mapping)
            and isinstance(overlay_value, Mapping)
            and overlay_value
        ):
            merged[key] = _merge_manifest_mappings(
                base_value,
                overlay_value,
                field_path,
            )
        else:
            merged[key] = deepcopy(overlay_value)
    return merged
