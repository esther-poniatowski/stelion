"""Domain models for inter-project dependency tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .manifest import ManualEdge


class DependencyMechanism(Enum):
    """How one project depends on another."""

    EDITABLE_PIP = "editable pip install"
    CONDA = "conda"
    GIT_SUBMODULE = "git submodule"


@dataclass(frozen=True)
class DependencyEdge:
    """A resolved dependency between two projects."""

    dependent: str
    dependency: str
    mechanism: DependencyMechanism
    detail: str = ""


@dataclass(frozen=True)
class DependencyGraph:
    """Complete dependency graph: auto-detected and manual edges."""

    detected: list[DependencyEdge] = field(default_factory=list)
    manual: list[DependencyEdge] = field(default_factory=list)

    @property
    def all_edges(self) -> list[DependencyEdge]:
        """All resolved edges (detected + manual)."""
        return self.detected + self.manual

    def by_dependent(self) -> dict[str, list[DependencyEdge]]:
        """Group edges by their dependent project."""
        result: dict[str, list[DependencyEdge]] = {}
        for edge in self.all_edges:
            result.setdefault(edge.dependent, []).append(edge)
        return result

    def by_dependency(self) -> dict[str, list[DependencyEdge]]:
        """Group edges by their dependency (upstream) project."""
        result: dict[str, list[DependencyEdge]] = {}
        for edge in self.all_edges:
            result.setdefault(edge.dependency, []).append(edge)
        return result


def manual_edge_to_dependency_edge(edge: ManualEdge) -> DependencyEdge:
    """Convert a manifest ManualEdge to a resolved DependencyEdge."""
    mechanism_map = {
        "editable_pip": DependencyMechanism.EDITABLE_PIP,
        "conda": DependencyMechanism.CONDA,
        "git_submodule": DependencyMechanism.GIT_SUBMODULE,
    }
    mechanism = mechanism_map.get(edge.mechanism, DependencyMechanism.EDITABLE_PIP)
    return DependencyEdge(
        dependent=edge.dependent,
        dependency=edge.dependency,
        mechanism=mechanism,
        detail=edge.detail,
    )
