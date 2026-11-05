"""Domain models for inter-project dependency tracking."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .manifest import ManualEdge


class DependencyKind(StrEnum):
    """Semantic role that one project has for another."""

    RUNTIME_PACKAGE = "runtime/package"
    BUILD_TOOLING = "build/tooling"
    CONTENT_SUBMODULE = "content/submodule"
    WORKSPACE_CONTAINMENT = "workspace/containment"


class DependencyMechanism(StrEnum):
    """Mechanism that realizes a dependency edge."""

    EDITABLE_PIP = "editable_pip"
    CONDA = "conda"
    GIT_SUBMODULE = "git_submodule"
    WORKSPACE_DISCOVERY = "workspace_discovery"
    WORKSPACE_MANIFEST = "workspace_manifest"


class EdgeProvenance(StrEnum):
    """Origin of the assertion represented by an edge."""

    AUTOMATIC = "automatic"
    MANUAL = "manual"


@dataclass(frozen=True)
class DependencyEdge:
    """A resolved and evidenced relation between two projects."""

    dependent: str
    """Name of the downstream project."""
    dependency: str
    """Name of the upstream project."""
    kind: DependencyKind
    """Semantic role of the dependency."""
    mechanism: DependencyMechanism
    """Mechanism that realizes the relation."""
    source_declaration: str
    """Configuration declaration from which the edge was derived."""
    version_policy: str
    """Rule selecting the dependency version or commit."""
    optional: bool
    """Whether the dependent can operate without this relation."""
    provenance: EdgeProvenance
    """Whether a scanner found the edge or the manifest asserted it."""
    integration_path: str = ""
    """Path or target used by the integration mechanism, when applicable."""

    def __post_init__(self) -> None:
        if not self.source_declaration:
            raise ValueError("Dependency edges require a source declaration.")
        if not self.version_policy:
            raise ValueError("Dependency edges require a version or commit policy.")
        validate_kind_mechanism(self.kind, self.mechanism)


def validate_kind_mechanism(
    kind: DependencyKind,
    mechanism: DependencyMechanism,
) -> None:
    """Validate the boundary between workspace membership and consumption edges.

    Parameters
    ----------
    kind : DependencyKind
        Semantic role of the edge.
    mechanism : DependencyMechanism
        Integration mechanism that realizes the edge.

    Raises
    ------
    ValueError
        If a workspace mechanism and workspace-containment kind do not coincide.
    """
    workspace_mechanisms = {
        DependencyMechanism.WORKSPACE_DISCOVERY,
        DependencyMechanism.WORKSPACE_MANIFEST,
    }
    is_containment = kind is DependencyKind.WORKSPACE_CONTAINMENT
    uses_workspace_mechanism = mechanism in workspace_mechanisms
    if is_containment != uses_workspace_mechanism:
        raise ValueError(
            "Workspace-containment edges require a workspace mechanism, and "
            "workspace mechanisms cannot represent consumption edges."
        )


@dataclass(frozen=True)
class DependencyGraph:
    """Complete dependency graph: auto-detected and manual edges."""

    detected: tuple[DependencyEdge, ...] = ()
    """Edges discovered automatically from project configuration files."""
    manual: tuple[DependencyEdge, ...] = ()
    """Edges declared explicitly in the workspace manifest."""

    @property
    def all_edges(self) -> tuple[DependencyEdge, ...]:
        """All resolved edges (detected + manual).

        Returns
        -------
        tuple[DependencyEdge, ...]
            Concatenation of detected and manual edges.
        """
        return self.detected + self.manual

    def by_dependent(self) -> dict[str, list[DependencyEdge]]:
        """Group edges by their dependent project.

        Returns
        -------
        dict[str, list[DependencyEdge]]
            Mapping from dependent project name to its edges.
        """
        result: dict[str, list[DependencyEdge]] = {}
        for edge in self.all_edges:
            result.setdefault(edge.dependent, []).append(edge)
        return result

    def by_dependency(self) -> dict[str, list[DependencyEdge]]:
        """Group edges by their dependency (upstream) project.

        Returns
        -------
        dict[str, list[DependencyEdge]]
            Mapping from dependency project name to its edges.
        """
        result: dict[str, list[DependencyEdge]] = {}
        for edge in self.all_edges:
            result.setdefault(edge.dependency, []).append(edge)
        return result

    def dependents_of(self, name: str) -> list[str]:
        """Project names that directly depend on the given project.

        Parameters
        ----------
        name : str
            Upstream project name.

        Returns
        -------
        list[str]
            Names of projects that depend on *name*.
        """
        return [e.dependent for e in self.all_edges if e.dependency == name]

    def dependencies_of(self, name: str) -> list[str]:
        """Project names that the given project directly depends on.

        Parameters
        ----------
        name : str
            Downstream project name.

        Returns
        -------
        list[str]
            Names of upstream projects that *name* depends on.
        """
        return [e.dependency for e in self.all_edges if e.dependent == name]

    def affected_projects(self, name: str) -> set[str]:
        """All project names connected to the given project by any edge.

        Parameters
        ----------
        name : str
            Project name to look up.

        Returns
        -------
        set[str]
            Union of dependents and dependencies of *name*.
        """
        return {e.dependent for e in self.all_edges if e.dependency == name} | {
            e.dependency for e in self.all_edges if e.dependent == name
        }

    def edges_involving(self, name: str) -> list[DependencyEdge]:
        """All dependency edges that reference the given project.

        Parameters
        ----------
        name : str
            Project name to look up.

        Returns
        -------
        list[DependencyEdge]
            Edges where *name* appears as dependent or dependency.
        """
        return [
            e for e in self.all_edges if e.dependent == name or e.dependency == name
        ]


def manual_edge_to_dependency_edge(edge: ManualEdge) -> DependencyEdge:
    """Convert a manifest ManualEdge to a resolved DependencyEdge.

    Parameters
    ----------
    edge : ManualEdge
        Manually declared edge from the workspace manifest.

    Returns
    -------
    DependencyEdge
        Resolved edge with a validated mechanism.

    Raises
    ------
    ValueError
        If the mechanism string does not match a known ``DependencyMechanism``.
    """
    try:
        mechanism = DependencyMechanism(edge.mechanism)
    except ValueError as exc:
        known = ", ".join(mechanism.value for mechanism in DependencyMechanism)
        raise ValueError(
            f"Unknown dependency mechanism '{edge.mechanism}' on edge "
            f"'{edge.dependent} -> {edge.dependency}'. "
            f"Known mechanisms: {known}"
        ) from exc
    try:
        kind = DependencyKind(edge.kind)
    except ValueError as exc:
        known = ", ".join(kind.value for kind in DependencyKind)
        raise ValueError(
            f"Unknown dependency kind '{edge.kind}' on edge "
            f"'{edge.dependent} -> {edge.dependency}'. Known kinds: {known}"
        ) from exc
    return DependencyEdge(
        dependent=edge.dependent,
        dependency=edge.dependency,
        kind=kind,
        mechanism=mechanism,
        source_declaration=edge.source_declaration,
        version_policy=edge.version_policy,
        optional=edge.optional,
        provenance=EdgeProvenance.MANUAL,
        integration_path=edge.integration_path,
    )
