# Design Principles

Architectural rules for all projects in this ecosystem. Authoritative source
for structural standards enforced by the
[architecture audit prompt](../audits/audit-architecture.md).

---

## 1. Separation of Concerns

### 1.1 Architectural Layering

| Layer | Responsibility | May Depend On |
| --- | --- | --- |
| Domain | Pure business logic, typed models, validation, decisions | stdlib only |
| Application | Use-cases, orchestration, protocol definitions | Domain, Infrastructure via protocols |
| Infrastructure | Filesystem, config loading, subprocesses, I/O | Domain types, implements Application protocols |
| Adapters | CLI, editor integration, formatting, composition root | Application |

### 1.2 Layer Rules

- Domain code must be pure: no file reads, writes, subprocesses, environment
  access, or logging side effects.
- Application code sequences work, applies recovery behavior, and maps
  use-cases to domain and infrastructure calls.
- Infrastructure performs effects but does not own policy.
- Adapters are thin: parse external input, call application use-cases,
  format output.

### 1.3 Dependency Direction

- Adapters → Application → Domain
- Application → Infrastructure via protocol interfaces defined in the
  application layer.
- Infrastructure implements application-defined protocols and may depend on
  domain types.
- Never Domain → Infrastructure or Domain → Adapters.

### 1.4 Data Flow

Inward:

```text
Adapter input → Application request objects → Domain decisions
                                |
                                → Infrastructure effects
```

Outward:

```text
Domain/Application/Infrastructure diagnostics → Adapter formatter → stderr / JSON / editor
```

### 1.5 Responsibility Boundaries

Components must not mix:

- orchestration and business logic
- policy and mechanism
- I/O and transformation
- parsing and validation
- construction and execution
- configuration and runtime state
- persistence and domain logic
- interface adaptation and core computation
- selection logic and execution logic

Error handling must be owned by a layer boundary, not scattered across
layers.

A boundary that requires internal knowledge of its collaborator is not a
real boundary.

### 1.6 Boundary Smells

- a domain function that reads a file path
- a resolver that performs I/O as a side effect
- a config model that loads files from disk by itself
- a CLI command that reimplements orchestration logic
- an application module that imports a concrete infrastructure module
  instead of using a protocol

---

## 2. Redundancy

Duplication must be detected at every granularity and eliminated through the
correct abstraction mechanism:

- duplicated expressions, conditionals, and control-flow skeletons
- repeated imperative sequences or orchestration flows
- cloned helper logic or repeated object construction
- repeated validation, normalization, serialization, parsing, dispatch, or
  adaptation
- parallel class families encoding one underlying concept
- duplicated policy under different names
- conceptual duplication: structurally equivalent behavior with superficial
  naming differences

### 2.1 Absorbing Mechanisms

When eliminating duplication, name the correct mechanism: utility function,
domain object, policy object, strategy, higher-order function, template
method, pipeline stage, shared validator, factory, registry, typed
configuration object.

Do not recommend abstraction without naming the correct level of abstraction.
Distinguish true duplication from acceptable specialization and abstraction
opportunity from premature abstraction.

---

## 3. Modularity

Units must be independently understandable, independently reusable, and
minimally interdependent.

Prohibited patterns:

- monolithic modules and god objects
- orchestration classes accumulating global knowledge
- functions with too many phases
- excessive fan-in or fan-out
- hidden transitive dependencies
- cyclic or quasi-cyclic dependency graphs
- components requiring unrelated subsystems to be imported
- implicit optional dependencies that are effectively mandatory

Introduce intermediate abstractions to decompose overloaded units.

---

## 4. Data Objects and Contracts

### 4.1 Typed Boundaries

Do not pass raw dictionaries or loosely structured tuples across module
boundaries when a named type is warranted. Use dataclasses, TypedDicts, or
named tuples with clear semantics.

### 4.2 Dataclasses

Use `@dataclass(frozen=True)` for decision objects and inter-layer data.
Mutable containers inside frozen dataclasses must use
`field(default_factory=...)`.

### 4.3 Enumerations

Use `Enum` for closed sets. Do not spread magic strings through the
codebase.

### 4.4 Validation at Boundaries

Validate external inputs at system boundaries — adapter entry points,
configuration loaders, file parsers — using typed models with constraint
enforcement. Domain functions consume pre-validated data.

- Field-level constraints (type, range, pattern) for individual values.
- Model-level validators for cross-field invariants.

### 4.5 Contract Clarity

Public contracts must be explicit, structured, and reliable:

- No dictionaries standing in for domain objects.
- No string keys where structured types are required.
- No overloaded methods hiding qualitatively different modes.
- No return shapes varying implicitly with mode.
- No hidden side effects or order-dependent behavior.
- No implicit lifecycle rules.
- No booleans or strings selecting behavior that structured variants should
  represent.

---

## 5. Configuration

### 5.1 Configuration as Typed Data

Represent configuration as typed data objects — dataclasses, Pydantic
models, or structured OmegaConf containers — with explicit field types,
constraints, and defaults. Do not pass raw dictionaries or environment
variable strings through application code.

### 5.2 Loading and Precedence

Configuration loading belongs in the infrastructure layer. Precedence order:

```text
defaults → configuration files → environment variables → CLI overrides
```

### 5.3 Validation at Startup

Validate all configuration at application startup. Missing or invalid values
must raise exceptions immediately. No partial state propagation.

### 5.4 Environment Separation

Separate environment-specific settings into distinct configuration files or
profiles. Do not embed environment-conditional logic in application code.

### 5.5 Prohibited Patterns

- magic strings or literals embedded in logic
- sentinel values and scattered defaults
- hidden global state and implicit module-level settings
- environment access deep inside runtime logic
- long parameter lists that should become structured configuration objects
- configuration decisions split across multiple layers
- stringly-typed mode switching
- configuration bags represented as weakly structured dictionaries

Distinguish runtime state from static configuration. They must not share the
same role or representation.

---

## 6. Object Design and Flexibility

### 6.1 Prefer Functions for Pure Policy

Use standalone functions for pure transformations. Use classes only when an
object has real state or when a protocol is useful.

### 6.2 Protocols Over Deep Inheritance

Use `Protocol` for all infrastructure capabilities consumed by the
application layer. Protocols define capabilities through structural
subtyping.

Reserve abstract base classes (`ABC`) for enforced inheritance hierarchies or
shared initialization logic. Prefer protocols for capabilities; prefer ABCs
for type families.

### 6.3 Composition Over Inheritance

Favor composition and delegation. When multiple classes share orthogonal
behaviors:

- Base classes define shared initialization and core methods (is-a).
- Mixins provide supplementary functionality without shared initialization
  (has-a).
- Multiple inheritance requires explicit named arguments for correct MRO
  argument passing.

### 6.4 Generic Types

Use `TypeVar` and `Generic[T]` for type-safe reusable components. Prefer
bounded type variables (`TypeVar('T', bound=Base)`) when a minimum interface
is required.

### 6.5 Composition Root

All wiring of concrete infrastructure into application use-cases happens in a
single composition root module. This is the only module that imports both
application protocols and concrete infrastructure implementations.

### 6.6 No Hidden Singletons

Do not use global registries, mutable module-level caches, or service
locators. Pass dependencies explicitly.

### 6.7 Strategy Substitution

Behavior must be alterable through strategy substitution, policy injection,
or structured composition — not through source modification.

Prohibited patterns:

- `if`/`elif`, `match`, or type-switch logic encoding behavioral families
- branching on mode strings, flags, or sentinel values
- backend-specific logic embedded in generic layers
- algorithm selection hardcoded into reusable components
- subclassing where composition or protocol dispatch is more appropriate
- abstractions claiming generality while encoding one concrete use case
- policy embedded in low-level utilities or mechanisms

---

## 7. Extensibility

### 7.1 Open/Closed Principle

New behavior is added by introducing new implementations of existing
protocols, new pipeline steps, new handlers, or new decorated functions — not
by modifying existing code paths.

### 7.2 Extension via Decoration

Use decorators for cross-cutting concerns. Preserve function metadata with
`functools.wraps`. Document decorator ordering constraints.

### 7.3 Plugin Architecture

Use entry points (`importlib.metadata`) for plugin discovery and
registration. Access bundled resources through `importlib.resources`.

### 7.4 Pipeline and Chain Patterns

Each step implements a common interface, receives its predecessor's output,
and operates independently. Steps can be added, removed, or reordered
without modifying existing implementations.

### 7.5 Extension Seams

New variants, backends, policies, formats, stages, workflows, and entity
types must be introducible through stable extension seams.

Prohibited patterns:

- new cases requiring edits to several existing files
- central condition trees growing with every variant
- switch-on-type or switch-on-string dispatch
- rigid inheritance chains
- dispatchers or factories that must be edited for each new case
- missing registries, hooks, protocols, or composition seams

---

## 8. Diagnostics, Errors, and Robustness

### 8.1 Diagnostics as Data

User-facing diagnostics are structured records, not ad hoc formatted strings.

### 8.2 Formatting Boundary

Adapters own rendering. Domain and application code create diagnostics, not
print them.

### 8.3 Exceptions

- Project-specific exception hierarchies for unrecoverable failures.
- Explicit chaining: `raise NewError(...) from original_error`.
- Embed runtime state in exception messages through dedicated formatting
  methods.
- Exception groups and `except*` for batch validation.

### 8.4 Warning Management

Custom warning categories for domain-specific advisory conditions. Apply
warning filters in adapters only.

### 8.5 Error Recovery

Application-layer use-cases own recovery policy. Domain code raises
exceptions or returns error-carrying result types. Infrastructure reports
failures but does not decide whether to retry.

### 8.6 Logging

- Configure logging in adapters only.
- Never rely on logging side effects for core behavior.
- Never use `print()` for diagnostics in domain, application, or
  infrastructure code.
- Use dot-separated hierarchical logger names.
- For machine-parseable output, use structured logging (JSON format).

### 8.7 Invariant Protection

- No silent fallbacks or partial initialization.
- No mutable shared state without ownership clarity.
- No partial updates without rollback or containment.
- No side effects leaking across boundaries.
- No invalid states reachable by design.
- No temporal coupling or unclear failure modes.
- No raw implementation exceptions escaping domain boundaries.
- No best-effort behavior where deterministic policy is required.
- No hidden dependencies on process state, caches, initialization order, or
  environment.

---

## 9. Path and Subprocess Handling

### 9.1 Paths

- Use `pathlib.Path` everywhere.
- Keep distinct path categories in typed objects (source, workspace, build,
  output).

### 9.2 Subprocesses

- Use argument vectors, not shell command strings.
- Do not use `shell=True`.
- Keep subprocess invocation in infrastructure.
- Capture stdout/stderr for diagnostics.

---

## 10. Ease of Use

Public interfaces must support straightforward, declarative use at the
correct level of abstraction.

Prohibited patterns:

- multi-step setup ceremonies that should be encapsulated
- interfaces exposing mechanism instead of intent
- excessive boilerplate
- too many poorly grouped parameters
- poor defaults
- unclear entry points
- required call sequences that should be encapsulated in a lifecycle object
- APIs forcing callers to construct internal intermediate objects
- missing facades, builders, composition roots, or declarative entry points
