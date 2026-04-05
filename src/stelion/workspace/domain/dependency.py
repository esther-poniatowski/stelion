"""Domain models for inter-project dependency tracking."""

from __future__ import annotations

from dataclasses import dataclass
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

    detected: tuple[DependencyEdge, ...] = ()
    manual: tuple[DependencyEdge, ...] = ()

    @property
    def all_edges(self) -> tuple[DependencyEdge, ...]:
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

    def dependents_of(self, name: str) -> list[str]:
        """Project names that directly depend on the given project."""
        return [e.dependent for e in self.all_edges if e.dependency == name]

    def dependencies_of(self, name: str) -> list[str]:
        """Project names that the given project directly depends on."""
        return [e.dependency for e in self.all_edges if e.dependent == name]

    def affected_projects(self, name: str) -> set[str]:
        """All project names connected to the given project by any edge."""
        return {
            e.dependent for e in self.all_edges if e.dependency == name
        } | {
            e.dependency for e in self.all_edges if e.dependent == name
        }

    def edges_involving(self, name: str) -> list[DependencyEdge]:
        """All dependency edges that reference the given project."""
        return [
            e for e in self.all_edges
            if e.dependent == name or e.dependency == name
        ]


def manual_edge_to_dependency_edge(edge: ManualEdge) -> DependencyEdge:
    """Convert a manifest ManualEdge to a resolved DependencyEdge.

    Raises
    ------
    ValueError
        If the mechanism string does not match a known ``DependencyMechanism``.
    """
    mechanism_map = {
        "editable_pip": DependencyMechanism.EDITABLE_PIP,
        "conda": DependencyMechanism.CONDA,
        "git_submodule": DependencyMechanism.GIT_SUBMODULE,
    }
    if edge.mechanism not in mechanism_map:
        known = ", ".join(sorted(mechanism_map))
        raise ValueError(
            f"Unknown dependency mechanism '{edge.mechanism}' on edge "
            f"'{edge.dependent} -> {edge.dependency}'. "
            f"Known mechanisms: {known}"
        )
    return DependencyEdge(
        dependent=edge.dependent,
        dependency=edge.dependency,
        mechanism=mechanism_map[edge.mechanism],
        detail=edge.detail,
    )
