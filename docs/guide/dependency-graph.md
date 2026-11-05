# Dependency graph

The dependency graph draws an edge from project A to project B and records the source that justifies it. Each edge stores its semantic kind separately from its mechanism. As a result, the same mechanism can serve several kinds: a Git submodule can provide either a build tool or incorporated content.

## Edge kinds

The edge kind states how project B serves project A.

| Kind | Role |
| --- | --- |
| `runtime/package` | supplies a package imported or executed by the dependent |
| `build/tooling` | supplies a tool that builds, checks, generates or maintains artifacts |
| `content/submodule` | supplies source, documentation, LaTeX or other incorporated content |
| `workspace/containment` | the workspace coordinates the dependency as a managed member |

A `workspace/containment` edge says that a workspace manages a member repository. The edge does not say that the workspace imports or executes the member. Therefore, this kind uses `workspace_discovery` or `workspace_manifest`. Those mechanisms cannot represent the other kinds.

## Edge fields

Every generated record defines the same properties.

| Field | Meaning |
| --- | --- |
| `dependent` | project that holds the edge |
| `dependency` | project that supplies the package, tool, content or member repository |
| `kind` | semantic role of the dependency |
| `source_declaration` | configuration entry or file section that justifies the edge |
| `mechanism` | integration method |
| `version_policy` | rule that selects the package release, checkout or commit |
| `optional` | whether project A can operate without project B |
| `provenance` | whether a scanner found the edge or the manifest stated it |
| `integration_path` | path or target used by the mechanism |

The `automatic` value states that a scanner found the edge. This value does not imply that Stelion updates the dependency automatically.

## Detected sources

Stelion currently reads three sources.

| Declaration | Default kind | Mechanism | Version policy | Status |
| --- | --- | --- | --- | --- |
| editable pip entry in `environment.yml` | `runtime/package` | `editable_pip` | `workspace_checkout` | required, automatic |
| known-project entry in `.gitmodules` | `content/submodule` | `git_submodule` | `pinned_commit` | required, automatic |
| project selected by workspace discovery | `workspace/containment` | `workspace_discovery` | `workspace_checkout` | required, automatic |

The manifest can refine a scanner's default kind by dependency name:

```yaml
integrations:
  canonical_mechanisms:
    ktisma:
      type: tool
      mechanism: git_submodule
      edge_kind: build/tooling
```

The manifest keys overrides by dependency name. The `ktisma` override applies to every detected edge. One dependency can serve different roles across consumers. In that case, the manifest must state each exceptional endpoint pair manually. A manual edge replaces every automatic edge whose `dependent` and `dependency` values match. Automatic records for the other endpoint pairs remain unchanged.

## Manual assertions

When no scanner reads the source, the manifest must state a complete edge. The entry supplies the semantic kind and every policy field:

```yaml
dependencies:
  manual_edges:
    - dependent: analysis
      dependency: morpha
      kind: runtime/package
      source_declaration: environment.yml:dependencies
      mechanism: conda
      version_policy: ">=0.2,<0.3"
      optional: false
      integration_path: morpha
```

Stelion writes `provenance: manual` for this record. An edge that manually includes a workspace member uses `kind: workspace/containment` with `mechanism: workspace_manifest`.

## Generated records

The generated `dependencies.yml` stores automatic and manual assertions under one `edges` key. Each record is self-contained:

```yaml
edges:
  - dependent: techne
    dependency: ktisma
    kind: build/tooling
    source_declaration: '.gitmodules:submodule "vendor/ktisma"'
    mechanism: git_submodule
    version_policy: pinned_commit
    optional: false
    provenance: automatic
    integration_path: vendor/ktisma
```

When a legacy manual edge uses `detail`, Stelion continues to read it. Stelion maps `detail` to `integration_path`. Stelion also derives the missing kind and version policy from the mechanism. The next rendered manifest uses the canonical fields.
