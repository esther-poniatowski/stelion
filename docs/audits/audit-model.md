# MODEL AUDIT REPORT — stelion

**Audit date:** 2026-03-31
**Auditor posture:** The code's abstractions are presumed to be arbitrary implementation choices that may or may not correspond to the problem's structure. This audit seeks to determine whether each abstraction has a domain justification and whether each domain concept has a code counterpart.

---

## 1. DOMAIN CONCEPT MAP

Derived from README.md and docs/guide/ files **before** reading source code.

### Entities

| Concept | Type | Essential Attributes | Relationships |
|---|---|---|---|
| **Workspace** | Entity | root directory, manifest path, set of projects, set of artifacts | Contains Projects, Manifest, Artifacts; governed by Manifest |
| **Manifest** | Entity | file path, discovery rules, template config, generation config, dependency config, ecosystem defaults | Governs Workspace; consumed by all generation and discovery processes |
| **Project** | Entity | name, path, description, version, language, git presence, homepage | Member of Workspace; participates in Dependencies; target of Bulk Operations and Comparisons |
| **Project Registry** | Entity | ordered collection of project metadata | Generated Artifact; derived from Project Inventory |
| **Dependency Graph** | Entity | set of directed edges between projects | Generated Artifact; derived from scanning projects |
| **Dependency Edge** | Relationship | dependent project, dependency project, integration mechanism, detail | Connects two Projects; classified by Integration Mechanism |
| **Integration Mechanism** | Classification | type: editable pip / conda / git submodule | Classifies Dependency Edges |
| **Workspace Artifact** | Classification | type: VS Code workspace, project registry, dependency graph, conda environment; output path, content | Generated from Workspace state; subject to Drift detection |
| **Drift** | Relationship (derived) | artifact, expected content, actual content, status (current/stale/missing) | Relates an Artifact to its on-disk state |
| **Template** | Entity | source directory, delimiters, exclude patterns, rename mappings | Used by Bootstrap process |
| **Placeholder Binding** | Relationship | placeholder key, resolved value | Connects Template to a new Project during bootstrapping |
| **Project Filter** | Process/Constraint | names, regex pattern, git-only flag, exclusion list | Selects a subset of Projects for operations |
| **Bulk Operation** | Process | operation type (exec/commit/push), command/message, filter | Applied across filtered Projects; produces Operation Outcomes |
| **Operation Outcome** | Entity | project, status (success/skipped/failed), detail, error | Result of one Bulk Operation on one Project |
| **Replica** | Entity | kind (local clone / submodule instance / remote), location, current commit | Location where a Dependency exists |
| **Submodule Instance** | Entity (specialization of Replica) | superproject name, superproject directory, submodule path within superproject | Embedding of a dependency in a superproject |
| **Superproject** | Entity | name, directory; contains one or more submodule instances | Consumes dependencies as git submodules |
| **Sync Propagation** | Process | dependency, source replica, target replicas, target commit | Propagates a commit from source to all targets |
| **Source Mode** | Classification | local / superproject / remote | Determines sync propagation direction |
| **Comparison Scope** | Entity | set of projects, target specification (tree or file) | Input to a Comparison operation |
| **Tree Comparison** | Process | scan project trees, match hierarchically, produce report | Consumes TreeSnapshots; produces TreeReport |
| **File Comparison** | Process | resolve paths, read content, dispatch to structured/unstructured diff | Consumes file contents; produces FileReport |
| **Matched Node** | Entity | canonical path, per-project resolved paths, presence/absence, match method, similarity, node type, children | Result of tree matching |
| **Match Quality** | Classification | exact / case-insensitive / fuzzy | How a node correspondence was established |
| **Variant Group** | Entity | set of projects with identical content, digest, line count | Groups projects in unstructured comparison |
| **Field Diff** | Entity | dotted path, per-project values | One field compared across projects in structured comparison |
| **Comparison Instruction** | Entity | project names, mode (tree/files), target spec | Declarative YAML specification for complex comparisons |
| **File Entry** | Entity | canonical path, per-project overrides, selectors, parser hint | One file within a Comparison Instruction |
| **Comparison Report** | Entity | projects, matches/results, summary | Output of any comparison operation |

---

## 2. MODEL VERDICT

**Classification: well-modeled**

The stelion codebase demonstrates strong correspondence between its domain concepts and code abstractions across all five functional areas. The domain layer contains explicit, immutable types for nearly every concept identified independently from the documentation: projects, manifests, dependencies, sync plans, comparison specifications, tree matches, field diffs, variant groups, and operation outcomes are all named, frozen dataclasses with typed relationships. Pure domain functions (tree matching, structured diffing, variant grouping) operate on domain types and return domain types. The separation between domain, application, and infrastructure layers preserves abstraction fidelity: infrastructure implements protocols, application orchestrates domain types, and CLI adapters translate between user input and domain objects.

The model is adequate for the system's current use cases. All implemented features (workspace management, submodule sync, bulk operations, cross-project comparison) have explicit domain representations.

The model will partially support planned extensions. The planned repository synchronization feature (token-level diffing, three-way merge, template substitution) will require new domain types, but the existing modeling discipline provides clear patterns for introducing them. However, a few modeling gaps exist that will create friction as the system evolves, primarily around the absence of a first-class Workspace aggregate and the ad-hoc derivation of project filtering.

---

## 3. EXECUTIVE FINDINGS

| # | Title | Severity | Primary Dimension | Secondary Dimension | Domain Concept | Mapping Category | Cost |
|---|---|---|---|---|---|---|---|
| 1 | No first-class Workspace entity | Medium | Concept Coverage | Relationship Coverage | Workspace | Domain gap | WorkspaceContext re-derived at every CLI entry point; no persistent aggregate to query |
| 2 | Project Filter is derived ad-hoc, not represented | Medium | Concept Coverage | Relationship Coverage | Project Filter | Domain gap | Filter logic duplicated across bulk and comparison adapters via parallel `_parse_selection` functions |
| 3 | Replica has no unified domain type | Medium | Concept Coverage | Abstraction Fidelity | Replica | Domain gap | Sync code infers replica kind from plan fields; no explicit collection of all replicas |
| 4 | Workspace Artifact lacks a first-class domain type | Low | Concept Coverage | — | Workspace Artifact | Domain gap | Generation target identity exists only in application layer; drift detection re-derives it |
| 5 | `_parse_selection` duplicated across adapters | High | Relationship Coverage | — | Project Filter (CLI parsing) | Domain gap | Identical function in `bulk_commands.py` and `comparison_commands.py`; divergence risk |
| 6 | Superproject not modeled as a distinct domain concept | Low | Concept Coverage | — | Superproject | Domain gap | Superproject resolution is procedural; superprojects exist only as string names and inferred paths |
| 7 | Placeholder Binding has no named type | Low | Concept Coverage | — | Placeholder Binding | Domain gap | Bindings are a plain `dict[str, str]`; template substitution semantics are implicit |

---

## 4. DETAILED FINDINGS

## F1: No First-Class Workspace Entity

- Severity: Medium
- Primary dimension: Concept Coverage
- Secondary dimension: Relationship Coverage
- Domain concept: Workspace (from concept map)
- Concept type: entity
- Code construct: `WorkspaceContext` in `composition.py` (partial representation)
- Mapping category: domain gap
- Ad-hoc derivation sites: `composition.py::build_workspace_context` called in every CLI command handler (`commands.py:workspace_init`, `commands.py:workspace_sync`, `commands.py:workspace_status`, `bulk_commands.py:workspace_exec`, `bulk_commands.py:workspace_commit`, `bulk_commands.py:workspace_push`, `submodule_commands.py:submodule_sync`, `comparison_commands.py:compare_tree`, `comparison_commands.py:compare_files_cmd`)
- Consumers affected: every CLI adapter function (9 call sites)
- Architectural cost: Every CLI entry point independently calls `resolve_manifest` then `build_workspace_context`, performing full discovery, graph construction, and environment merging from scratch. `WorkspaceContext` is close to a Workspace aggregate but lives in the composition root rather than the domain layer, and its construction is not cached or reusable. This forces every command to pay the full discovery cost and prevents workspace-level queries (e.g., "which artifacts are stale?") from being expressed as methods on the aggregate.
- Evidence: All 9 CLI command functions contain the pattern: `services = create_services()` → `m = resolve_manifest(Path(manifest))` → `ctx = build_workspace_context(m, services)`. WorkspaceContext captures manifest, inventory, graph, and environment but is defined in the composition module, not the domain layer.
- Remediation: Promote `WorkspaceContext` to a domain-layer aggregate (e.g., `domain/workspace.py::Workspace`) that owns the manifest, inventory, graph, and environment as a coherent unit. Provide a factory method that constructs it from infrastructure services. This makes the workspace a queryable domain object rather than a transient composition artifact.
- Domain justification for remediation: The workspace is the central entity of the problem domain; the manifest, project inventory, dependency graph, and shared environment are its constituent parts. Representing this aggregate explicitly in the domain layer reflects the domain structure and enables workspace-level operations (drift check, status queries) to be methods on the entity.
- Migration priority: next refactor cycle

## F2: Project Filter Derived Ad-Hoc, Not Represented

- Severity: Medium
- Primary dimension: Concept Coverage
- Secondary dimension: Relationship Coverage
- Domain concept: Project Filter (from concept map)
- Concept type: process / constraint
- Code construct: absent as a named type
- Mapping category: domain gap
- Ad-hoc derivation sites: `application/bulk.py::select_projects` receives filter parameters as individual keyword arguments; `bulk_commands.py::_parse_selection` and `comparison_commands.py::_parse_selection` independently convert CLI strings to these arguments
- Consumers affected: `bulk_commands.py` (3 commands), `comparison_commands.py` (2 commands), `composition.py::_run_bulk`, `composition.py::run_compare_trees`, `composition.py::run_compare_files`, `composition.py::_select_comparison_projects`
- Architectural cost: The filter concept is scattered across multiple function signatures as parallel keyword arguments (`names`, `pattern`, `git_only`, `exclude`). Adding a new filter criterion (e.g., "by language" or "by status") requires modifying every function signature in the chain. The filter cannot be inspected, logged, or tested as a unit.
- Evidence: `select_projects` in `application/bulk.py` takes 4 keyword arguments. `_run_bulk` in `composition.py` takes the same 4 and passes them through. `run_compare_trees` and `run_compare_files` also take the same 4. The two `_parse_selection` functions are identical copies.
- Remediation: Introduce a `ProjectFilter` dataclass in the domain layer capturing `names`, `pattern`, `git_only`, and `exclude` as a single typed object. `select_projects` would accept a `ProjectFilter` instead of four loose parameters. The CLI adapter would construct a `ProjectFilter` from user input in one place.
- Domain justification for remediation: A project filter is a domain constraint that governs which projects participate in an operation. It appears in the documentation as a named concept ("filter options") shared across bulk operations and comparison commands. Making it a first-class type reflects this domain structure.
- Migration priority: before adding features

## F3: Replica Has No Unified Domain Type

- Severity: Medium
- Primary dimension: Concept Coverage
- Secondary dimension: Abstraction Fidelity
- Domain concept: Replica (from concept map)
- Concept type: entity
- Code construct: absent as a unified type; partially represented by `SubmoduleTarget`, `PushSpec`, and the `local_dir` field on `SyncPlan`
- Mapping category: domain gap
- Ad-hoc derivation sites: `application/sync.py::plan_sync` assembles replica information into `SyncPlan` fields; `application/sync.py::execute_sync` dispatches to `_sync_local`, `_sync_remote`, `_sync_submodule` based on which `SyncPlan` fields are non-None
- Consumers affected: `plan_sync`, `execute_sync`, `_sync_local`, `_sync_remote`, `_sync_submodule`, `composition.py::run_submodule_sync`
- Architectural cost: The documentation defines a dependency as existing in "up to three kinds of locations" (local clone, submodule instances, remote). In the code, these are not represented as a collection of Replica objects. Instead, `SyncPlan` has separate fields (`local_dir: Path | None`, `push_spec: PushSpec | None`, `submodule_targets: tuple[SubmoduleTarget, ...]`), and `execute_sync` uses None-checks to determine which actions to take. Adding a fourth replica kind (e.g., a CI mirror) would require adding another optional field and another conditional branch.
- Evidence: `SyncPlan` in `domain/sync.py` has `local_dir: Path | None = None` and `push_spec: PushSpec | None = None` as separate optional fields rather than a unified replica collection. `execute_sync` tests each for None separately.
- Remediation: Introduce a `Replica` union type or protocol with variants `LocalReplica`, `SubmoduleReplica`, `RemoteReplica`, each carrying its specific attributes. `SyncPlan` would contain a `source: Replica` and `targets: tuple[Replica, ...]`. `execute_sync` would dispatch on replica kind via pattern matching.
- Domain justification for remediation: The replica is a core domain concept in submodule synchronization. The documentation explicitly names three replica kinds and describes sync as propagation from one replica to others. Making replicas first-class reflects this domain structure and makes the sync plan a collection of typed targets rather than a bag of optional fields.
- Migration priority: before adding features

## F4: Workspace Artifact Lacks a First-Class Domain Type

- Severity: Low
- Primary dimension: Concept Coverage
- Secondary dimension: —
- Domain concept: Workspace Artifact (from concept map)
- Concept type: classification / entity
- Code construct: `GenerationArtifact` enum in `application/generation.py` and `GenerationTarget` dataclass in the same file (application layer, not domain)
- Mapping category: domain gap
- Ad-hoc derivation sites: `generation.py::_build_targets` constructs `GenerationTarget` objects with render callables; `generation.py::compute_drift` re-derives the same target list; `composition.py::target_paths` re-derives output paths a third time
- Consumers affected: `generate_all`, `compute_drift`, `target_paths`, `workspace_init`, `workspace_sync`, `workspace_status`
- Architectural cost: The concept of a workspace artifact (a generated file with an identity, output path, and expected content) exists across generation and drift detection but is modeled only in the application layer, not the domain. `GenerationArtifact` (an enum) and `GenerationTarget` (a dataclass with a render callable) are application constructs. The target list is re-derived in three places. Drift detection and generation both independently construct the same list of targets.
- Evidence: `_build_targets` is called by both `generate_all` and `compute_drift`. `target_paths` in `composition.py` independently reconstructs the same path mapping. `GenerationTarget` includes a `render: Callable[[], str]` field, mixing infrastructure concerns into what should be a domain object.
- Remediation: Introduce a domain-layer `ArtifactSpec` type that captures the artifact identity and output path without the render callable. The render callable would be paired with it in the application layer. This separates the domain concept (what artifacts exist) from the infrastructure concern (how to render them).
- Domain justification for remediation: A workspace artifact is a domain concept: it has an identity (workspace-file, projects, dependencies, environment), an output path relative to the manifest, and a status (current, stale, missing). The documentation lists these as distinct generated outputs.
- Migration priority: opportunistically

## F5: `_parse_selection` Duplicated Across CLI Adapters

- Severity: High
- Primary dimension: Relationship Coverage
- Secondary dimension: —
- Domain concept: Project Filter (CLI-to-domain mapping)
- Concept type: relationship (alignment between CLI strings and domain filter)
- Code construct: `bulk_commands.py::_parse_selection` (lines 29–41) and `comparison_commands.py::_parse_selection` (lines 54–66)
- Mapping category: domain gap
- Ad-hoc derivation sites: `bulk_commands.py` line 29, `comparison_commands.py` line 54
- Consumers affected: `workspace_exec`, `workspace_commit`, `workspace_push` (via bulk), `compare_tree`, `compare_files_cmd` (via comparison)
- Architectural cost: The same CLI-string-to-filter-parameters derivation is implemented identically in two modules. If the filter semantics change (e.g., adding a new filter criterion), both must be updated. This is a relationship coverage defect: the mapping between CLI filter strings and domain filter parameters is a domain relationship that is derived in two independent locations.
- Evidence: Both functions are character-for-character identical: they split comma-separated names and exclude strings into tuples, pass through pattern and git_only. The duplication is invisible to a component audit (each function is internally correct).
- Remediation: Introduce a shared `ProjectFilter` domain type (see F2) and a single `parse_filter` function in a shared adapter utility. Both CLI modules would call the shared function, eliminating the duplicated derivation.
- Domain justification for remediation: The alignment between CLI filter strings and the domain filter concept is a domain relationship that should be computed once and consumed by all adapter commands.
- Migration priority: before adding features

## F6: Superproject Not Modeled as a Distinct Domain Concept

- Severity: Low
- Primary dimension: Concept Coverage
- Secondary dimension: —
- Domain concept: Superproject (from concept map)
- Concept type: entity
- Code construct: absent; resolved procedurally in `application/sync.py::_resolve_superproject_dir`
- Mapping category: domain gap
- Ad-hoc derivation sites: `application/sync.py::_resolve_superproject_dir` (iterates `manifest.dependencies.superproject_paths` and matches by directory basename); `SubmoduleTarget.superproject_name` and `SubmoduleTarget.superproject_dir` carry superproject attributes as strings/paths
- Consumers affected: `plan_sync`, `execute_sync`, `_sync_submodule`, submodule CLI adapter
- Architectural cost: A superproject is a domain concept that appears in the documentation, the dependency graph, and the submodule sync workflow. In the code, it has no dedicated type. Instead, superproject identity is distributed across `SubmoduleTarget.superproject_name` (a string), `SubmoduleTarget.superproject_dir` (a Path resolved at runtime), and `DependenciesConfig.superproject_paths` (raw strings). Resolving a superproject requires iterating configured paths and matching basenames, a derivation performed in `_resolve_superproject_dir`.
- Evidence: `_resolve_superproject_dir` iterates `manifest.dependencies.superproject_paths` and performs `candidate.name == superproject_name` matching. No `Superproject` type exists.
- Remediation: Introduce a `Superproject` domain type with `name: str` and `path: Path`, resolved once during workspace context construction and stored as a collection. `SubmoduleTarget` would reference a `Superproject` rather than carrying raw name + path fields.
- Domain justification for remediation: A superproject is a named domain entity in the submodule synchronization context. It has a name, a filesystem path, and contains one or more submodule instances. Making it explicit eliminates the procedural path-resolution derivation.
- Migration priority: opportunistically

## F7: Placeholder Binding Has No Named Type

- Severity: Low
- Primary dimension: Concept Coverage
- Secondary dimension: —
- Domain concept: Placeholder Binding (from concept map)
- Concept type: relationship
- Code construct: `dict[str, str]` returned by `application/bootstrap.py::build_placeholder_bindings`
- Mapping category: domain gap
- Ad-hoc derivation sites: `bootstrap.py::build_placeholder_bindings` (builds a plain dict); `bootstrap.py::bootstrap_project` (passes the dict to infrastructure services)
- Consumers affected: `bootstrap_project`, `substitute_in_directory`, `rename_paths` (infrastructure)
- Architectural cost: Template placeholder bindings carry semantic meaning (which placeholders map to which project values, with specific naming conventions like `package_name`, `repo_name`, `env_name` all mapping to the project name). This semantics is implicit in a `dict[str, str]`. The function `build_placeholder_bindings` encodes the convention that multiple placeholder keys map to the same value, but this convention is not inspectable or testable as a named type.
- Evidence: `build_placeholder_bindings` in `bootstrap.py` returns `dict[str, str]` with keys like `"package_name"`, `"repo_name"`, `"project_name"`, `"env_name"` all set to the same `name` value. The mapping convention is encoded procedurally, not declaratively.
- Remediation: Introduce a `PlaceholderBindings` dataclass (or a thin wrapper around a mapping) that makes the binding semantics explicit: which bindings come from the project name, which from ecosystem defaults, which from git identity. This type would be constructed by `build_placeholder_bindings` and consumed by the template engine.
- Domain justification for remediation: Placeholder bindings are the domain relationship between a template and a concrete project. They carry the semantics of what a template means when it says `{{ package_name }}`. Making this relationship a named type reflects the domain structure of template substitution.
- Migration priority: opportunistically

---

*7 findings reported (budget: 10). 0 phantom abstractions identified. 0 misaligned mappings identified. All defects are domain gaps of varying severity.*
