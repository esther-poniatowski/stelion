# COMPONENT AUDIT REPORT — stelion

**Audit date:** 2026-03-31
**Auditor posture:** Adversarial — architecture is presumed defective until the code disproves it.
**Scope:** Component-level structural audit of all Python source under `src/stelion/`.

---

## 1. ARCHITECTURAL VERDICT

**Classification: serviceable but architecturally fragile**

The codebase demonstrates deliberate Clean Architecture layering with proper dependency direction, protocol-based DI at the application-infrastructure boundary, frozen dataclasses throughout the domain, and a single composition root. These are structural strengths that indicate intentional architectural investment. However, the composition root has grown into an oversized orchestration module that absorbs responsibilities belonging to both the application and adapter layers, generation use-cases accept exploded parameter lists instead of structured service objects, the sync use-case encodes behavioral variation through if/elif branching on enum values rather than strategy dispatch, and several infrastructure modules contain duplicated structural patterns. The architecture is fundamentally evolvable — the protocol seams, typed domain models, and layering provide genuine extension points — but continued feature growth without addressing the identified structural debts will progressively erode the layering that currently holds the system together.

---

## 2. EXECUTIVE FINDINGS

| # | Title | Severity | Primary Dimension | Secondary Dimensions | Structural Impact | Consequence Over Time |
|---|---|---|---|---|---|---|
| 1 | Composition root absorbs orchestration and facade logic | High | Separation of Concerns | Modularity | The composition module conflates DI wiring with multi-step orchestration workflows that belong in the application layer, creating a 500-line module with 20+ public functions. | Every new use-case requires editing composition.py; the module becomes a change bottleneck. |
| 2 | Exploded parameter lists in generation use-cases | High | Redundancy | Ease of Use, Modularity | `generate_all` and `compute_drift` accept 12 and 11 positional parameters respectively, with 8 renderer/IO parameters repeated identically across both signatures. | Adding a new generation target requires four coordinated edits for a single axis of variation. |
| 3 | Sync origin resolution uses branching instead of strategy dispatch | High | Flexibility | Extensibility | `plan_sync` contains an if/elif/else chain on `SyncOrigin` enum values, each branch with distinct parameter requirements and commit-resolution logic. | Adding a new sync origin requires modifying the core `plan_sync` function rather than registering a new strategy. |
| 4 | Duplicated project-selection and workspace-context setup in adapters | Medium | Redundancy | Ease of Use | `_parse_selection` is duplicated verbatim between `bulk_commands.py` and `comparison_commands.py`; the three-call context setup ceremony is repeated in every CLI command. | Every new command must reproduce the same boilerplate; inconsistencies silently diverge. |
| 5 | `DispatchingParser` constructor uses concrete union type instead of protocol | Medium | Flexibility | Extensibility | The `__init__` parameter is typed as a union of concrete parser classes, forcing source modification when a new parser is added. | A new file format requires editing the type annotation in the dispatcher. |
| 6 | Sync helper functions repeat the try/outcome/error pattern | Medium | Redundancy | Robustness | `_sync_local`, `_sync_remote`, and `_sync_submodule` each implement the same try-catch-to-SyncOutcome wrapping pattern. | Each new sync action must re-implement the same wrapping. |
| 7 | `VSCodeWorkspaceFileRenderer._load_settings` performs direct file I/O | Medium | Separation of Concerns | Robustness | When the manifest's vscode.source is not "defaults", the renderer opens a file from disk directly, bypassing the injected protocols. | The renderer becomes untestable without a real filesystem for non-default configs. |
| 8 | `_parse_selection` returns untyped dict instead of a structured model | Medium | Predictability | Modularity | Selection parameters are passed as a stringly-keyed dictionary splatted across the adapter-to-composition boundary. | A key name change silently passes the old key through without error. |
| 9 | Bulk adapter commands repeat the full workspace setup ceremony | Low | Redundancy | Ease of Use | Three bulk command functions follow identical structure differing only in the one composition-layer call. | Adding a new bulk operation requires copying the full ceremony again. |

---

## 3. DETAILED FINDINGS

## F1: Composition Root Absorbs Orchestration and Facade Logic

- Severity: High
- Primary dimension: Separation of Concerns
- Secondary dimensions: Modularity
- Location: `src/stelion/workspace/composition.py` (entire file, ~505 lines)
- Symptom: `composition.py` defines 20+ public functions (`run_generate`, `run_drift_check`, `run_submodule_sync`, `run_bulk_exec`, `run_bulk_commit`, `run_bulk_push`, `run_compare_trees`, `run_compare_files`, `register_workspace_project`, `initialize_workspace_manifest`, `build_workspace_context`, `target_paths`), four dataclasses (`WorkspaceServices`, `WorkspaceContext`, `WorkspaceRegistrationResult`, `ComparisonServices`), and a private helper `_run_bulk` — far exceeding the single responsibility of wiring concrete implementations to protocol interfaces.
- Violation: A composition root module must wire dependencies and nothing else. Functions like `register_workspace_project` (lines 268–296) contain multi-step orchestration logic: resolve manifest, build context, register project, check discoverability, conditionally write manifest, rebuild context, regenerate artifacts. This is application-layer orchestration, not wiring. Violates §1.5 (components must not mix construction and execution) and §6.5 (all wiring in composition root).
- Principle: Components must not mix construction and execution. All wiring happens in a single composition root module — these two rules require that the composition root only wires, while orchestration lives in application use-case modules.
- Root cause: The absence of application-layer facade use-cases for complex multi-step workflows forced the composition root to absorb that orchestration.
- Blast radius: Every adapter command imports composition.py and calls its facade functions. Every new workflow adds another public function to this module. The adapters layer is structurally coupled to composition.py's growing surface.
- Future break scenario: When a new workspace workflow is added (e.g. workspace migration, workspace diff, workspace merge), it will be added as yet another function in composition.py, further bloating the module.
- Impact: The composition root's single-responsibility guarantee is already compromised. The module is the most-imported, most-changed file in the workspace package.
- Evidence: `register_workspace_project` (lines 268–296) performs 7 orchestration steps including conditional I/O and error-handling. `run_submodule_sync` (lines 304–328) resolves targets, plans, and executes — three-phase orchestration. `_run_bulk` (lines 406–424) selects projects and delegates execution. None of these are wiring.
- Remediation: Extract orchestration functions into dedicated application-layer use-case modules. `register_workspace_project` becomes an application use-case in `application/registration.py`. `run_submodule_sync` already has its logic in `application/sync.py` but composition.py re-orchestrates it. `run_compare_trees`/`run_compare_files` should move into `application/comparison.py`. The composition root retains only `create_services`, `create_bootstrap_services`, `create_manifest_init_services`, `create_comparison_services`, and `resolve_manifest`.
- Why this remediation is the correct abstraction level: The problem is misplaced orchestration logic, not missing abstraction. The application layer already exists and already hosts similar use-cases (e.g. `bootstrap.py`, `generation.py`). Moving the orchestration there restores the composition root to its architectural role without introducing new abstractions.
- Migration priority: before adding features

## F2: Exploded Parameter Lists in Generation Use-Cases

- Severity: High
- Primary dimension: Redundancy
- Secondary dimensions: Ease of Use, Modularity
- Location: `src/stelion/workspace/application/generation.py` lines 89–103 (`generate_all`) and lines 146–158 (`compute_drift`); `src/stelion/workspace/composition.py` lines 206–227 (`run_generate`) and lines 230–248 (`run_drift_check`)
- Symptom: `generate_all` accepts 12 parameters; `compute_drift` accepts 11 parameters. Eight of these are identical across both functions: `manifest`, `inventory`, `graph`, `environment`, `render_workspace_file`, `render_projects_yaml`, `render_dependency_yaml`, `render_environment`. The callers in composition.py pass them identically in both call-sites.
- Violation: The four renderer parameters are a cohesive unit — they are always passed together, never independently varied, and are all protocol-typed callables serving the same purpose. Their repetition across two function signatures is structural duplication. Violates §2 (Redundancy) and §5.5 (long parameter lists that should become structured configuration objects).
- Principle: Duplication must be detected at every granularity and eliminated through the correct abstraction mechanism.
- Root cause: The generation module lacks a typed service container for the renderer protocols. `WorkspaceServices` in composition.py already groups them, but `generation.py` does not accept it because it avoids importing from the composition layer.
- Blast radius: Both `generate_all` and `compute_drift` in generation.py; both `run_generate` and `run_drift_check` in composition.py; the `_build_targets` internal helper. Five call-sites are affected by the same parameter shape.
- Future break scenario: Adding a fifth generation target (e.g. a Makefile or CI config) requires adding a new renderer parameter to both `generate_all` and `compute_drift`, their shared helper `_build_targets`, and both composition-layer call-sites — five coordinated signature changes.
- Impact: High friction for extending the generation system and error-prone consistency maintenance between the two parallel function signatures.
- Evidence: `generate_all` signature (lines 89–103): `manifest, inventory, graph, environment, render_workspace_file, render_projects_yaml, render_dependency_yaml, render_environment, writer, reader, hasher, force, selected_targets`. `compute_drift` signature (lines 146–158): same minus `writer` and `force`.
- Remediation: Introduce a frozen dataclass `GenerationServices` in the application layer grouping the four renderer protocols plus `FileReader`, `FileWriter`, and `FileHasher`. Also introduce a `GenerationContext` frozen dataclass grouping `manifest`, `inventory`, `graph`, `environment`. Both `generate_all` and `compute_drift` then accept `(ctx: GenerationContext, services: GenerationServices, ...)`, reducing to 3–4 parameters. This is the typed service container pattern already used by `BootstrapServices` and `ManifestInitServices`.
- Why this remediation is the correct abstraction level: The codebase already uses this exact pattern (frozen-dataclass service containers) in `BootstrapServices` and `ManifestInitServices`. This is not premature abstraction; it is consistent application of an established project idiom.
- Migration priority: before adding features

## F3: Sync Origin Resolution Uses Branching Instead of Strategy Dispatch

- Severity: High
- Primary dimension: Flexibility
- Secondary dimensions: Extensibility
- Location: `src/stelion/workspace/application/sync.py` lines 52–118 (`plan_sync`)
- Symptom: `plan_sync` contains an `if origin == SyncOrigin.LOCAL: ... elif origin == SyncOrigin.SUPERPROJECT: ... elif origin == SyncOrigin.REMOTE: ... else: raise` chain spanning 50 lines. Each branch has distinct logic for determining `target_commit`, `source_label`, `submodule_targets`, `update_local`, and `push_spec`.
- Violation: The three branches are three distinct strategies for resolving a sync source. They share the same output shape (`SyncPlan`) but differ in precondition validation, commit-resolution mechanism, and push/local update policy. Violates §6.7 (behavior alterable through strategy substitution) and §7.1 (new behavior via new implementations, not source modification).
- Principle: Behavior must be alterable through strategy substitution, not through source modification.
- Root cause: The `SyncOrigin` enum represents the axis of variation but the variation logic is encoded as conditional branching rather than dispatched to origin-specific strategy objects.
- Blast radius: `plan_sync` is the central planning function for submodule sync. The `_parse_origin` adapter helper in `submodule_commands.py` also uses conditional logic, creating a parallel dispatch chain.
- Future break scenario: Adding a new sync origin (e.g. `SyncOrigin.TAG` or `SyncOrigin.PR`) requires modifying the `plan_sync` function body, the `SyncOrigin` enum, and the adapter `_parse_origin` helper — three files modified for a single new variant.
- Impact: The sync planning function is the most complex single function in the application layer. Its branching structure makes it difficult to test each origin strategy independently.
- Evidence: Lines 67–76 (LOCAL branch), 78–93 (SUPERPROJECT branch), 95–106 (REMOTE branch). Each branch independently constructs a `SyncPlan` with different field assignments.
- Remediation: Define a `SyncOriginResolver` protocol with a single method `resolve(dependency, targets, inventory, git, ...) -> SyncPlan`. Implement `LocalOriginResolver`, `SuperprojectOriginResolver`, `RemoteOriginResolver` as concrete classes. The composition root wires the appropriate resolver based on the CLI argument. `plan_sync` becomes a thin delegation.
- Why this remediation is the correct abstraction level: The three branches share no logic — they are genuinely different strategies producing the same output type. Strategy extraction via protocol is the correct mechanism because each branch has distinct preconditions.
- Migration priority: before adding features

## F4: Duplicated Project-Selection and Workspace-Context Setup in Adapters

- Severity: Medium
- Primary dimension: Redundancy
- Secondary dimensions: Ease of Use
- Location: `src/stelion/workspace/adapters/bulk_commands.py` lines 29–41 (`_parse_selection`); `src/stelion/workspace/adapters/comparison_commands.py` lines 54–66 (identical `_parse_selection`); all CLI command functions across 4 adapter modules
- Symptom: `_parse_selection` is duplicated verbatim between `bulk_commands.py` and `comparison_commands.py`. Additionally, every CLI command independently performs the three-step ceremony: `create_services() -> resolve_manifest(Path(manifest)) -> build_workspace_context(m, services)`.
- Violation: Identical helper functions across two modules. Identical multi-step initialization sequences across 8 CLI commands. Violates §2 (Redundancy).
- Principle: Duplication must be detected at every granularity.
- Root cause: The adapter layer lacks a shared CLI utility module for common option parsing and workspace resolution.
- Blast radius: All 8 CLI command functions across 4 adapter modules. Any change to project selection logic or workspace setup requires editing every command.
- Future break scenario: Adding a new selection filter (e.g. `--language`) requires modifying `_parse_selection` in both files and every command that uses it.
- Impact: Moderate — the duplication is mechanical but affects every adapter function.
- Evidence: `bulk_commands.py:29-41` and `comparison_commands.py:54-66` are character-identical functions. The `create_services -> resolve_manifest -> build_workspace_context` sequence appears in 8 command functions.
- Remediation: Extract `_parse_selection` into a shared adapter utility module (e.g. `adapters/_cli_common.py`). Extract the three-step workspace resolution into a shared helper `resolve_workspace_context(manifest: Path) -> tuple[WorkspaceContext, WorkspaceServices]`.
- Why this remediation is the correct abstraction level: These are identical imperative sequences, not conceptually different operations that happen to look similar. A shared utility function is the minimum sufficient mechanism.
- Migration priority: next refactor cycle

## F5: `DispatchingParser` Constructor Uses Concrete Union Type Instead of Protocol

- Severity: Medium
- Primary dimension: Flexibility
- Secondary dimensions: Extensibility
- Location: `src/stelion/workspace/infrastructure/structured_parsers.py` line 172
- Symptom: `DispatchingParser.__init__` accepts `parsers: dict[str, TomlParser | YamlParser | JsonParser | MarkdownSectionParser]`. The type annotation enumerates all concrete parser classes.
- Violation: The dispatcher's purpose is to route parsing to the correct backend based on extension. Its interface should accept any object satisfying a parser protocol, not a closed union of concrete types. Violates §6.2 (use Protocol for infrastructure capabilities) and §7.5 (new variants via stable extension seams).
- Principle: Use Protocol for all infrastructure capabilities consumed by the application layer. New variants must be introducible through stable extension seams.
- Root cause: No local `ContentParser` protocol exists for individual format parsers. The `StructuredParser` protocol in `application/protocols.py` models the dispatching parser itself, not the individual backends.
- Blast radius: `DispatchingParser` in `structured_parsers.py`; `create_comparison_services` in `composition.py`.
- Future break scenario: Adding INI file comparison support requires: (1) implementing an `IniParser` class, (2) modifying the type annotation on `DispatchingParser.__init__` to include `IniParser` in the union, (3) registering it in `create_comparison_services`. Step 2 is source modification to an existing class.
- Impact: The dispatcher is architecturally designed as a registry-dispatch pattern but its type signature undercuts the openness.
- Evidence: Line 172: `dict[str, TomlParser | YamlParser | JsonParser | MarkdownSectionParser]`. The parsers are used only via `.parse(content)` — a structural protocol is already satisfied but not declared.
- Remediation: Define a `ContentParser` protocol with a single method `def parse(self, content: str) -> dict: ...`. Change the `DispatchingParser.__init__` signature to `parsers: dict[str, ContentParser]`. The existing concrete parsers already structurally satisfy this protocol.
- Why this remediation is the correct abstraction level: This is a protocol extraction — the smallest change that opens the extension seam. The concrete parsers need no modification.
- Migration priority: next refactor cycle

## F6: Sync Helper Functions Repeat the Try/Outcome/Error Pattern

- Severity: Medium
- Primary dimension: Redundancy
- Secondary dimensions: Robustness
- Location: `src/stelion/workspace/application/sync.py` lines 156–182 (`_sync_local`), 184–211 (`_sync_remote`), 214–252 (`_sync_submodule`)
- Symptom: All three helper functions follow the same structural skeleton: (1) try to read the current ref, (2) compare with target, (3) if equal return not-applied outcome, (4) if dry_run return not-applied outcome, (5) perform the action, (6) return applied outcome, (7) except SyncError return error outcome. The try/except wrapping, the dry-run short-circuit, and the SyncOutcome construction logic are replicated.
- Violation: Structural duplication at the control-flow skeleton level. The three functions differ only in the action performed, the OutcomeKind, and the label computation. Violates §2 (duplicated control-flow skeletons must be absorbed).
- Principle: Duplicated expressions, conditionals, and control-flow skeletons must be absorbed.
- Root cause: The three sync targets are modeled as separate helper functions rather than as parameterized invocations of a common sync-action template.
- Blast radius: The three functions in `sync.py` and the `execute_sync` function that calls them.
- Future break scenario: Adding a new sync action (e.g. syncing a worktree or a mirror) requires copying the same skeleton again.
- Impact: The tripled skeleton increases maintenance cost and creates risk of inconsistency in error handling.
- Evidence: `_sync_local` (lines 156–182), `_sync_remote` (lines 184–211), `_sync_submodule` (lines 214–252): all follow try/compare/dry-run/action/except. The structural shape is identical; only the action body differs.
- Remediation: Extract a higher-order helper function `_execute_sync_action(kind: OutcomeKind, label: str, current_ref_fn: Callable, action_fn: Callable, target_ref: str, dry_run: bool) -> SyncOutcome` that encapsulates the try/compare/dry-run/action/except skeleton. Each caller passes only the differing parts.
- Why this remediation is the correct abstraction level: The three functions share a control-flow skeleton but differ in the action body. A higher-order function is the correct mechanism for absorbing control-flow duplication without unnecessary class hierarchies.
- Migration priority: next refactor cycle

## F7: `VSCodeWorkspaceFileRenderer._load_settings` Performs Direct File I/O

- Severity: Medium
- Primary dimension: Separation of Concerns
- Secondary dimensions: Robustness
- Location: `src/stelion/workspace/infrastructure/renderers/vscode.py` lines 36–46 (`_load_settings`) and lines 48–55 (`_load_extensions`)
- Symptom: When `manifest.vscode.uses_defaults()` is false, `_load_settings` calls `open(source_path, encoding="utf-8")` directly, performing filesystem I/O that bypasses the injected `PackageDataLoader` and the `FileReader` protocol used elsewhere in the system.
- Violation: The renderer's constructor accepts a `PackageDataLoader` for the default case, but for the custom-source case, it opens files directly. This creates an asymmetry where one code path is testable via injection and the other requires a real filesystem. Violates §1.2 (infrastructure performs effects but does not own policy) and §1.5 (do not mix I/O and transformation).
- Principle: Infrastructure performs effects but does not own policy. Components must not mix I/O and transformation.
- Root cause: The `VSCodeWorkspaceFileRenderer` was designed with only the `PackageDataLoader` injection point, not a general `FileReader` for custom source paths.
- Blast radius: `VSCodeWorkspaceFileRenderer` in `vscode.py`; any test exercising the non-default VS Code configuration path.
- Future break scenario: If VS Code settings sources are extended to support remote URLs or database-backed configs, the direct `open()` call will need ad hoc replacement.
- Impact: The renderer is partially testable — the default path works through injection, but the custom path does not.
- Evidence: Line 41–42: `source_path = manifest.manifest_dir / manifest.vscode.source; with open(source_path, encoding="utf-8") as f:`. Contrast with the default path at line 39 which uses `self._loader.load_json(...)`.
- Remediation: Accept a `FileReader` protocol in the constructor alongside the `PackageDataLoader`. In the non-default path, use `reader.read(source_path)` followed by `json.loads(text)` instead of `open()` + `json.load()`. This aligns the custom path with the project's established I/O delegation pattern.
- Why this remediation is the correct abstraction level: The `FileReader` protocol already exists in `application/protocols.py` and is used for exactly this purpose throughout the codebase. Injecting it is the minimal change that eliminates the direct I/O.
- Migration priority: opportunistically

## F8: `_parse_selection` Returns Untyped Dict Instead of Structured Model

- Severity: Medium
- Primary dimension: Predictability
- Secondary dimensions: Modularity
- Location: `src/stelion/workspace/adapters/bulk_commands.py` lines 29–41; `src/stelion/workspace/adapters/comparison_commands.py` lines 54–66
- Symptom: Both `_parse_selection` functions return `dict[str, Any]`, which is then splatted as `**selection` into composition-layer functions. The dict keys (`names`, `pattern`, `git_only`, `exclude`) are implicit — the compiler cannot verify that the keys match the expected keyword arguments.
- Violation: The selection parameters are a cohesive domain concept passed as a stringly-keyed dictionary across the adapter-to-composition boundary. Violates §4.1 (do not pass raw dictionaries across module boundaries) and §4.5 (no string keys where structured types are required).
- Principle: Do not pass raw dictionaries across module boundaries when a named type is warranted.
- Root cause: The project selection filters were added incrementally without introducing a typed container.
- Blast radius: All bulk commands and comparison commands that use `_parse_selection` followed by `**` splatting. 7 call-sites across 3 adapter modules.
- Future break scenario: Renaming `git_only` to `git_repos_only` in the application layer would silently pass the old key through the dict without error.
- Impact: The implicit contract between the adapter's dict construction and the composition layer's keyword parameters is fragile.
- Evidence: `bulk_commands.py` line 122: `result = run_bulk_exec(ctx, command, dry_run=dry_run, **selection)` where `selection` is a dict. `comparison_commands.py` line 163: `report = run_compare_trees(ctx, cmp_services, target, **selection)`.
- Remediation: Introduce a frozen dataclass `ProjectSelectionCriteria` with fields `names: tuple[str, ...]`, `pattern: str | None`, `git_only: bool`, `exclude: tuple[str, ...]`. The `_parse_selection` function returns this typed object. Composition-layer functions accept it as a single parameter.
- Why this remediation is the correct abstraction level: This is a typed domain record introduction, following the project's own established pattern (every other cross-boundary data transfer uses frozen dataclasses).
- Migration priority: next refactor cycle

## F9: Bulk Adapter Commands Repeat the Full Workspace Setup Ceremony

- Severity: Low
- Primary dimension: Redundancy
- Secondary dimensions: Ease of Use
- Location: `src/stelion/workspace/adapters/bulk_commands.py` lines 106–185 (`workspace_exec`, `workspace_commit`, `workspace_push`)
- Symptom: All three bulk command functions follow identical structure: (1) `create_services()`, (2) `resolve_manifest(Path(manifest))`, (3) `build_workspace_context(m, services)`, (4) `_parse_selection(...)`, (5) try/except WorkspaceError wrapping, (6) `_print_bulk_result(result, dry_run)`, (7) conditional `raise typer.Exit(1)`. The only variation is the single line that calls `run_bulk_exec`, `run_bulk_commit`, or `run_bulk_push`.
- Violation: The three functions are near-identical templates differing only in the one composition-layer call. The 15-line ceremony around that call is repeated three times. Violates §2 (repeated imperative sequences must be absorbed).
- Principle: Repeated imperative sequences and orchestration flows must be absorbed.
- Root cause: Each Typer command must be a separate function for CLI registration, but the boilerplate around the varying call is not factored out.
- Blast radius: The three bulk commands in `bulk_commands.py`.
- Future break scenario: Adding a new bulk operation (e.g. `workspace pull`) requires copying the full ceremony again.
- Impact: Low — the duplication is mechanical and the blast radius is contained within one file.
- Evidence: `workspace_exec` (lines 106–129), `workspace_commit` (lines 132–155), `workspace_push` (lines 158–185) share identical setup/teardown wrapping.
- Remediation: Extract a shared helper `_run_bulk_command(manifest: Path, selection: dict, dry_run: bool, operation_factory: Callable[..., BulkResult]) -> None` that handles the workspace setup, error wrapping, result printing, and exit-code logic. Each command becomes a thin wrapper.
- Why this remediation is the correct abstraction level: This is a higher-order function extraction for a repeated imperative sequence. The three commands genuinely differ only in the operation they invoke.
- Migration priority: opportunistically
