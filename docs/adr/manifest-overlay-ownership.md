# Manifest overlay ownership

**Status**: Accepted

## Problem

A complete consumer-owned manifest repeats Stelion's schema and generic defaults. Each default change then requires synchronized edits in Stelion and every consumer. However, Stelion must remain independent of consumer paths, repositories and policies.

The design must assign one owner to each manifest value while preserving a reviewable complete `stelion.yml` at the workspace boundary.

## Decision drivers

- **Single ownership**: Stelion must define each generic default and merge rule once.
- **Consumer independence**: Stelion must not import or name a downstream consumer.
- **Reviewability**: the consumer must produce a complete manifest before generating workspace files.
- **Validation**: unknown fields, invalid types and ambiguous null values must fail before output is written.

## Considered designs

### Complete consumer manifest

Each consumer stores the complete `stelion.yml`. The file remains usable without running Stelion first, but it duplicates generic defaults and schema structure.

### Static base manifest

Stelion ships a base YAML file that consumers merge with their configuration. The base file makes defaults visible, but it duplicates the typed default factory inside Stelion.

### Typed defaults with overlays

Stelion serializes its typed default model, merges a consumer overlay and parses the result through the normal manifest validator. The consumer stores only its policy and values that can vary between hosts.

## Decision

Stelion composes typed defaults with consumer overlays. The path of the workspace determines its default name, exclusion and shared-environment name. Stelion also supplies generic output filenames, empty lists and objects, and bundled editor settings. When a workflow needs them, the consumer must declare its template source and ecosystem policy, including its license, account and channel.

An omitted field inherits its default. A nonempty YAML object merges recursively, while an empty YAML object clears the corresponding default object. A scalar or sequence replaces its default. Stelion rejects the YAML value `null` because an omitted field already inherits its default.

The command `stelion workspace render-manifest` validates and serializes the complete manifest. The option `--manifest-dir` identifies the final workspace when the output path belongs to a temporary stage.

## Consequences

- Stelion owns the manifest language, defaults, merge semantics and validation.
- Each consumer owns a portable overlay and interpolates any values that vary between hosts before Stelion composes the manifest.
- The complete rendered manifest remains the operational input for workspace generation and drift checks.
- If a consumer must run without Stelion, it stores a complete manifest instead of using the overlay route.
