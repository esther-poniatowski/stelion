# Dependency edge schema

**Status**: Accepted

## Problem

The former dependency edge identified two projects. The record also stored a mechanism and an untyped detail. That record used transport as the semantic kind. However, a Git submodule could provide a build tool or incorporated content. A submodule could also identify a repository managed by a workspace.

The graph requires a consumer-independent schema. The schema must record why project A uses project B. The schema must also record its source and governing policy.

## Decision drivers

- **Exact semantics**: the kind must state why one project uses another.
- **Traceable sources**: each record must identify its source and whether Stelion found or received the edge.
- **Uniform queries**: automatic and manual edges must support the same graph methods.
- **Stable extension**: a new scanner or mechanism must retain the output structure.
- **Compatible manifests**: Stelion must continue to read existing manual edges.

## Considered designs

### Mechanism-only edges

The former design uses the mechanism as the edge kind. The structure is compact, but one `git_submodule` value cannot distinguish a tool from incorporated content.

### Separate records by role

A tagged union gives each semantic role its own record type. This design can enforce fields for one role, but it repeats the shared source fields. Each graph method must also handle several variants.

### Normalized edges

One record stores the shared properties:

- semantic kind;
- mechanism;
- source;
- version policy;
- optionality;
- provenance.

The `integration_path` field stores any path required by the mechanism.

## Decision

Stelion uses normalized dependency edges. Four semantic kinds form the initial vocabulary:

- `runtime/package` records imported or executed packages;
- `build/tooling` records tools that produce or maintain artifacts;
- `content/submodule` records incorporated project content;
- `workspace/containment` records repositories coordinated by a workspace.

A workspace includes a repository as a member. The workspace does not consume that repository as software. Therefore, `workspace/containment` requires `workspace_discovery` or `workspace_manifest`. Those mechanisms cannot represent the other kinds.

Each automatic source produces one edge. Stelion does not otherwise collapse records by endpoints because two sources can specify different policies. A manifest may refine every detected edge for a dependency name. Instead, when the manifest states an edge manually, Stelion replaces automatic records whose `dependent` and `dependency` values match.

The editable-pip, Git-submodule and workspace scanners emit required edges. A complete manual entry covers sources outside these scanners. Stelion maps a legacy `detail` value to `integration_path` and derives the new fields from the mechanism.

## Consequences

- Every generated edge defines the same properties without relying on its surrounding `edges` key or scanner.
- A `git_submodule` edge can represent a tool or content while retaining the same synchronization mechanism.
- The `provenance` field identifies how Stelion acquired the edge, not how Stelion updates the dependency.
- A kind override applies to every detected edge for one dependency name within a manifest.
- Separate variants would become preferable if the four roles later require different fields or lifecycle methods.
