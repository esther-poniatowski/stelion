# INTERACTION AUDIT REPORT — stelion

**Date:** 2026-03-31
**Auditor posture:** Adversarial
**Scope:** Interaction boundaries only (coordination, data flows, sequencing, shared computation)

---

## 1. INTERACTION VERDICT

**Partially coordinated.**

The codebase employs a disciplined Clean Architecture with protocol-based dependency injection, a single composition root (`composition.py`) that wires all services, and explicit orchestration of the primary pipeline (manifest loading, discovery, graph construction, environment merge, generation). These structural choices prevent many classes of interaction defects. The `WorkspaceContext` dataclass serves as a shared intermediate result for the discovery/graph/environment pipeline, and the `WorkspaceServices` container prevents service construction duplication.

However, several coordination gaps exist at boundaries where the same data is consumed by multiple independent call sites, where filesystem reads are duplicated across subsystems with no shared cache, and where the composition root rebuilds the full workspace context redundantly in the registration workflow. The most consequential gap is the double reading of `environment.yml` files — once for shared environment construction and once for editable-pip dependency scanning — with no shared intermediate. Additionally, the `_parse_selection` helper is duplicated across adapter modules with no structural connection.

The interaction patterns scale linearly for most growth vectors (adding projects, adding generation targets, adding bulk operations). The exception is the dependency scanner interface, where adding scanners that read the same files as existing scanners will multiply redundant I/O without a shared-read layer.

---

## 2. EXECUTIVE FINDINGS

| # | Title | Severity | Primary Dimension | Secondary Dimensions | Boundary | Operational Consequence |
|---|---|---|---|---|---|---|
| 1 | Duplicated environment.yml reads across subsystems | High | Result Sharing | Consistency | `EditablePipDependencyScanner` / `CondaEnvironmentReader` via `build_dependency_graph` and `build_shared_environment` | Each project's environment.yml is parsed twice per pipeline execution; divergent parse logic could produce inconsistent dependency data |
| 2 | Redundant full workspace context rebuild during registration | High | Result Sharing | Sequencing | `register_workspace_project` calls `build_workspace_context` twice in `composition.py` | Every registration pays the cost of two full discovery + graph + environment scans; the first result is discarded |
| 3 | Duplicated `_parse_selection` helper across adapter modules | Medium | Consistency | — | `bulk_commands._parse_selection` / `comparison_commands._parse_selection` | Independent string-splitting logic for the same concept; a format change requires parallel edits |
| 4 | Generation target path computation duplicated across `target_paths` and `_build_targets` | Medium | Consistency | Result Sharing | `composition.target_paths` / `generation._build_targets` | Output path formulas are independently maintained; a manifest config change requires updates in two locations |
| 5 | Bulk adapter commands rebuild services and context independently | Medium | Result Sharing | Sequencing | `bulk_commands.workspace_exec` / `bulk_commands.workspace_commit` / `bulk_commands.workspace_push` | Each bulk command creates fresh services and re-discovers the full workspace, even when invoked in sequence |
| 6 | `generate_all` and `compute_drift` share structure but render independently | Low | Result Sharing | — | `generation.generate_all` / `generation.compute_drift` | Both build targets and render content through identical code paths; a sequential sync-then-status invocation renders every artifact twice |
| 7 | Superproject path resolution uses different lookup strategy than project discovery | Low | Scope Coordination | Consistency | `sync._resolve_superproject_dir` / `discovery.discover_projects` | Superprojects located by basename matching against `superproject_paths`, while projects discovered via marker files in `scan_dirs`; adding a superproject to the wrong config silently fails |

---

## 3. DETAILED FINDINGS

## F1: Duplicated environment.yml Reads Across Subsystems

- Severity: High
- Primary dimension: Result Sharing
- Secondary dimensions: Consistency
- Boundary: `EditablePipDependencyScanner` ↔ `CondaEnvironmentReader` via `build_dependency_graph` and `build_shared_environment` in `composition.build_workspace_context`
- Component A location: `src/stelion/workspace/infrastructure/dependency_scanners.py`, lines 14–41 (`EditablePipDependencyScanner.scan` calls `self._env_reader.read(project_dir)`)
- Component B location: `src/stelion/workspace/application/environment.py`, lines 11–26 (`build_shared_environment` calls `env_reader.read(project.path)`)
- Interaction description: Both `build_dependency_graph` and `build_shared_environment` are called sequentially in `build_workspace_context` (composition.py, lines 172–187). The dependency graph builder invokes `EditablePipDependencyScanner.scan()` for each project, which internally calls `CondaEnvironmentReader.read()` to parse `environment.yml`. Separately, `build_shared_environment` calls the same `CondaEnvironmentReader.read()` on every project to merge environments. The same file is read and parsed twice per project per pipeline invocation.
- Implicit assumption: Both subsystems assume the filesystem state of `environment.yml` is stable between their reads and that the parse logic in `CondaEnvironmentReader` produces consistent results across calls.
- Violated principle: §1 Result Sharing — when multiple consumers derive the same intermediate result from the same input, the computation must be performed once and shared.
- Operational consequence: For a workspace with N projects, there are N redundant YAML parse operations per pipeline invocation. More critically, the `EditablePipDependencyScanner` extracts pip dependency names by parsing the `pip_dependencies` field from `EnvironmentSpec`, while `merge_environments` filters out editable installs (`-e` lines). If the `CondaEnvironmentReader` parse logic changes (e.g., stricter validation), one subsystem may silently start producing different results from the other because there is no single shared `EnvironmentSpec` instance for each project.
- Growth scenario: Adding more dependency scanner types that need environment data (e.g., a conda-channel scanner) multiplies the redundant reads linearly.
- Evidence: `composition.py` line 131 creates `EditablePipDependencyScanner(env_reader)` with the same `CondaEnvironmentReader` instance, and `build_workspace_context` calls both `build_dependency_graph` (which invokes the scanner) and `build_shared_environment` (which calls `env_reader.read`) for the same set of projects.
- Remediation: Pre-compute a `dict[str, EnvironmentSpec | None]` by reading every project's environment once in `build_workspace_context`, then pass this map to both `build_dependency_graph` (adapting scanners to accept pre-read specs) and `build_shared_environment` (adapting it to accept specs instead of calling the reader).
- Why this coordination mechanism is the correct level: The environment specs are a shared intermediate result consumed by two independent subsystems. A pre-computed map is the minimal coordination that eliminates duplication without coupling the subsystems to each other. It does not require changing the scanner protocol — only adding an overload or a new protocol method that accepts a pre-read spec.
- Migration priority: before adding features

## F2: Redundant Full Workspace Context Rebuild During Registration

- Severity: High
- Primary dimension: Result Sharing
- Secondary dimensions: Sequencing
- Boundary: `register_workspace_project` calls `build_workspace_context` twice within the same operation in `composition.py`
- Component A location: `src/stelion/workspace/composition.py`, line 276 (first call: `ctx = build_workspace_context(manifest, services)`)
- Component B location: `src/stelion/workspace/composition.py`, line 284 (second call: `updated_ctx = build_workspace_context(effective_manifest, services)`)
- Interaction description: `register_workspace_project` first builds the full workspace context (discovery, graph, environment) to check whether the project is already known. After modifying the manifest's `extra_paths`, it rebuilds the entire context from scratch to verify the project is now discoverable and to regenerate all artifacts. The first context is used only for the `apply_registration` call and is then discarded.
- Implicit assumption: The second build will produce a superset of the first build's results, making the first build's discovery/graph/environment data redundant.
- Violated principle: §1 Result Sharing — the discovery, graph, and environment computation is performed twice.
- Operational consequence: Registration of a single project performs two full filesystem scans of all projects (marker detection, pyproject.toml parsing, environment.yml parsing, .gitmodules parsing), doubling the wall-clock time of the operation. For a workspace with many projects and slow I/O, this is directly user-visible.
- Growth scenario: As the number of projects grows, each redundant `build_workspace_context` call becomes more expensive (linear in project count for discovery, quadratic in theory for graph edges).
- Evidence: Lines 275–296 of `composition.py` show the sequential calls with no intermediate reuse.
- Remediation: Restructure `register_workspace_project` to build context once with the updated manifest. The pre-registration check can operate on the manifest alone (checking `extra_paths` membership) or on a lightweight discovery pass (just checking if the path is already known), avoiding the full graph and environment build. Only the post-registration context needs the full pipeline.
- Why this coordination mechanism is the correct level: The defect is redundant computation within a single orchestration function. The fix is sequencing: perform the registration check with minimal computation, then build the full context once with the final manifest state.
- Migration priority: before adding features

## F3: Duplicated `_parse_selection` Helper Across Adapter Modules

- Severity: Medium
- Primary dimension: Consistency
- Secondary dimensions: —
- Boundary: `bulk_commands._parse_selection` ↔ `comparison_commands._parse_selection`
- Component A location: `src/stelion/workspace/adapters/bulk_commands.py`, lines 29–41
- Component B location: `src/stelion/workspace/adapters/comparison_commands.py`, lines 54–66
- Interaction description: Both adapter modules define an identical `_parse_selection` function that converts CLI option strings (comma-separated names, regex pattern, git-only flag, comma-separated excludes) into keyword arguments for `select_projects`. The implementations are character-for-character identical.
- Implicit assumption: Both functions will be kept in sync when the selection format changes (e.g., adding a new filter, changing the delimiter from comma to semicolon).
- Violated principle: §4 Consistency — every fact must have exactly one authoritative declaration.
- Operational consequence: If a developer changes the name-splitting logic in one module (e.g., to trim whitespace or support glob patterns), the other module silently retains the old behavior. Users would get different selection semantics depending on whether they use `workspace exec` or `compare tree`.
- Growth scenario: Any new adapter command group (e.g., a future `stelion audit` subcommand) would need to copy the function a third time.
- Evidence: Both functions are identical: `tuple(names.split(",")) if names else ()` for names, `tuple(exclude.split(",")) if exclude else ()` for exclude, plus pattern and git_only passthrough.
- Remediation: Extract a single `parse_selection` function into a shared adapter utility module (e.g., `adapters/_selection.py`) and import it from both command modules.
- Why this coordination mechanism is the correct level: This is a duplicated fact (the CLI-to-domain conversion rule for project selection), not a shared computation. A single authoritative function is the minimal fix.
- Migration priority: next refactor cycle

## F4: Generation Target Path Computation Duplicated Across `target_paths` and `_build_targets`

- Severity: Medium
- Primary dimension: Consistency
- Secondary dimensions: Result Sharing
- Boundary: `composition.target_paths` ↔ `generation._build_targets`
- Component A location: `src/stelion/workspace/composition.py`, lines 251–265 (`target_paths` computes `manifest.manifest_dir / manifest.generate.workspace_file.output`, etc.)
- Component B location: `src/stelion/workspace/application/generation.py`, lines 54–86 (`_build_targets` computes `manifest.manifest_dir / manifest.generate.workspace_file.output`, etc.)
- Interaction description: Both functions independently compute the mapping from `GenerationArtifact` to output `Path` using the same formula: `manifest.manifest_dir / manifest.generate.<section>.output`. The `composition.target_paths` function is used by the CLI `workspace_init` dry-run path to display which files would be generated. The `generation._build_targets` function is used internally by `generate_all` and `compute_drift`.
- Implicit assumption: Both functions will be updated in lockstep when a new generation target is added or an output path formula changes.
- Violated principle: §4 Consistency — the path formula is a fact declared independently in two locations.
- Operational consequence: If a new generation artifact is added to `_build_targets` but not to `target_paths`, the dry-run preview of `workspace init` will omit the new artifact from its output, misleading the user about what would be generated.
- Growth scenario: Each new generation artifact requires updates in both locations. The divergence risk grows with the number of artifacts.
- Evidence: The four path computations in `target_paths` (lines 257–260) exactly mirror the four `GenerationTarget` constructors in `_build_targets` (lines 66–86).
- Remediation: Extract a `target_output_paths(manifest) -> dict[GenerationArtifact, Path]` function from `_build_targets` and have both `composition.target_paths` and `generation._build_targets` consume it. Alternatively, make `_build_targets` public and let `target_paths` derive from it.
- Why this coordination mechanism is the correct level: The output path formula is a single fact that should have one authoritative computation. A shared extraction function eliminates the duplication without changing the generation pipeline's structure.
- Migration priority: next refactor cycle

## F5: Bulk Adapter Commands Rebuild Services and Context Independently

- Severity: Medium
- Primary dimension: Result Sharing
- Secondary dimensions: Sequencing
- Boundary: `commands.py` (CLI router) ↔ `bulk_commands.workspace_exec` / `bulk_commands.workspace_commit` / `bulk_commands.workspace_push`
- Component A location: `src/stelion/workspace/adapters/commands.py`, lines 32–34 (`app.command("exec")(workspace_exec)`, etc.)
- Component B location: `src/stelion/workspace/adapters/bulk_commands.py`, lines 106–185 (each of `workspace_exec`, `workspace_commit`, `workspace_push` independently calls `create_services()`, `resolve_manifest()`, `build_workspace_context()`)
- Interaction description: Each bulk command independently creates `WorkspaceServices`, resolves the manifest, and builds the full `WorkspaceContext`. The `commands.py` module registers these functions as Typer subcommands but provides no mechanism to share the services or context between commands. The same pattern appears in `comparison_commands.py` and `submodule_commands.py`.
- Implicit assumption: Each command invocation is independent (true for the CLI), so redundant context construction is acceptable.
- Violated principle: §1 Result Sharing — while each CLI invocation is indeed independent, the pattern creates a structural expectation that services must be rebuilt per command. If a "batch mode" or programmatic API is introduced, this structure forces redundant computation.
- Operational consequence: Currently, each CLI invocation only runs one command, so the redundancy is not user-visible. However, the commands are registered as subcommands of the same Typer group, meaning the code structure implies they could be composed, but they cannot share state.
- Growth scenario: Adding new bulk operation types (e.g., `workspace pull`, `workspace lint`) multiplies the boilerplate and the number of locations where the service/context construction pattern must be replicated.
- Evidence: Lines 117–119 of `bulk_commands.py` (`workspace_exec`), lines 143–145 (`workspace_commit`), and lines 170–172 (`workspace_push`) all contain identical three-line sequences: `services = create_services()`, `m = resolve_manifest(Path(manifest))`, `ctx = build_workspace_context(m, services)`.
- Remediation: Introduce a shared `WorkspaceCommandContext` that is lazily constructed once per CLI invocation and threaded through commands via Typer's callback mechanism or a simple module-level factory. This preserves the current command-per-invocation model while eliminating the structural barrier to programmatic reuse.
- Why this coordination mechanism is the correct level: The services and context are genuinely shared across commands within a single session. A lazy factory or callback-injected context eliminates the boilerplate without introducing unnecessary coupling.
- Migration priority: opportunistically

## F6: `generate_all` and `compute_drift` Share Structure but Render Independently

- Severity: Low
- Primary dimension: Result Sharing
- Secondary dimensions: —
- Boundary: `generation.generate_all` ↔ `generation.compute_drift`
- Component A location: `src/stelion/workspace/application/generation.py`, lines 89–143 (`generate_all`)
- Component B location: `src/stelion/workspace/application/generation.py`, lines 146–179 (`compute_drift`)
- Interaction description: Both functions call `_build_targets` to construct the same `GenerationTarget` tuple, then iterate over the selected targets and call `target.render()` to produce content. If a user runs `stelion workspace sync --dry-run` (which calls `compute_drift`) followed by `stelion workspace sync` (which calls `generate_all`), every artifact is rendered twice. Within a single invocation, `run_drift_check` and `run_generate` are never called together, but the `workspace status` + `workspace sync` sequence is a common workflow.
- Implicit assumption: Rendering is cheap enough that duplication is acceptable.
- Violated principle: §1 Result Sharing — the rendered content is a shared intermediate result consumed by both "check" and "write" operations.
- Operational consequence: For expensive renderers (e.g., large workspace file generation), the double-render adds measurable latency. Currently the renderers are simple YAML/JSON serializers, so the cost is low but nonzero.
- Growth scenario: If renderers become more complex (e.g., template-based generation with filesystem reads), the duplication cost grows.
- Evidence: Both functions accept the same renderer parameters, build targets identically (lines 109–113 and 162–165), and iterate with the same selection logic (lines 115–116 and 166–167).
- Remediation: Introduce a "render-then-decide" pattern: a single function that renders all targets once and returns the rendered content alongside the target paths, then `generate_all` and `compute_drift` consume the pre-rendered content to decide whether to write or report drift.
- Why this coordination mechanism is the correct level: The rendering is a shared computation. A pre-render step eliminates the duplication while preserving the separate write-vs-check decision.
- Migration priority: opportunistically

## F7: Superproject Path Resolution Uses Different Lookup Strategy than Project Discovery

- Severity: Low
- Primary dimension: Scope Coordination
- Secondary dimensions: Consistency
- Boundary: `sync._resolve_superproject_dir` ↔ `discovery.discover_projects`
- Component A location: `src/stelion/workspace/application/sync.py`, lines 255–271 (`_resolve_superproject_dir` matches by `candidate.name == superproject_name` against `manifest.dependencies.superproject_paths`)
- Component B location: `src/stelion/workspace/application/discovery.py`, lines 12–60 (`discover_projects` scans `manifest.discovery.scan_dirs` for marker files)
- Interaction description: The project discovery system finds projects by scanning configured directories for marker files (`pyproject.toml`). The submodule sync system finds superprojects by matching directory basenames against a separate configuration (`dependencies.superproject_paths`). These two lookup strategies operate on overlapping concerns — both identify project directories — but use entirely independent configuration keys and matching logic.
- Implicit assumption: The user correctly configures `dependencies.superproject_paths` to point at the same directories that discovery would find, or at directories intentionally outside discovery's scope.
- Violated principle: §2 Scope Coordination — two components that select project directories operate with independent scope definitions.
- Operational consequence: A superproject referenced in dependency edges (discovered via `.gitmodules` scanning) may not be resolvable by `_resolve_superproject_dir` if its path is not listed in `superproject_paths`, even though it was successfully discovered by the project discovery system. The user sees a `SyncError: Superproject 'X' not found` even though `X` is a known project in the inventory.
- Growth scenario: Adding more superprojects requires manual synchronization of `dependencies.superproject_paths` with the actual directory layout.
- Evidence: `_resolve_superproject_dir` (sync.py, line 264) iterates `manifest.dependencies.superproject_paths` and matches by basename, while `discover_projects` (discovery.py, lines 36–52) iterates `manifest.discovery.scan_dirs` and matches by marker presence. The two config keys are independent.
- Remediation: Allow `_resolve_superproject_dir` to fall back to the project inventory (which is already available in the `WorkspaceContext`) by looking up the superproject name in `inventory.by_name()` and using its `path` attribute. The `superproject_paths` config would then serve as an override for superprojects outside the inventory, rather than the sole lookup mechanism.
- Why this coordination mechanism is the correct level: This is a scope coordination issue where two subsystems independently define how to locate project directories. Falling back to the inventory eliminates the gap for projects that are already discovered, while preserving the override for external superprojects.
- Migration priority: before adding features
