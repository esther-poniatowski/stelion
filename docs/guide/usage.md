# Usage

Stelion operates through four command groups: workspace management, submodule
synchronization, bulk operations, and cross-project comparison. Each group is
documented in detail in a dedicated guide.

For the exhaustive command registry, refer to [CLI Reference](cli-reference.md).

## Workspace Management

Initialize a workspace by scanning a directory for sibling projects:

```sh
stelion workspace init
```

The first run auto-discovers projects and writes `stelion.yml` at the root of the workspace with consumer-agnostic defaults. The settings file may move to `config/tools/stelion.yml` without an edit, since its paths are relative to the root. Every command finds the root from `--root`, else from the environment variable `STELION_ROOT`, else from the nearest ancestor of the current folder that holds the settings file, else from the current folder. The workspace directory supplies the default workspace name. A consumer must select any project template, license, account or channel values that its workflow requires. Subsequent runs regenerate all workspace artifacts from the manifest.

### Consumer overlays

A consumer overlay records only the values that differ from Stelion's canonical manifest. This boundary keeps output filenames, empty lists and objects, bundled editor settings and names derived from the workspace path under Stelion ownership.

Stelion applies four merge rules:

- an omitted field inherits its canonical value;
- a nonempty YAML object merges recursively;
- an empty YAML object clears the corresponding default object;
- a scalar or sequence replaces the corresponding default.

The YAML value `null` is invalid because an omitted field already inherits its default. Unknown fields and invalid values also fail before Stelion writes the complete manifest.

Render and validate an overlay with the following command:

```sh
stelion workspace render-manifest workspace.overlay.yml --output stelion.yml
```

Without `--output`, the manifest goes to the standard output. When the output is a staging file, the option `--root` supplies the final workspace directory for the path-derived defaults. The resulting `stelion.yml` is an ordinary complete manifest accepted by every workspace command.

Re-scan projects and update generated files:

```sh
stelion workspace sync
```

Bootstrap a new project from the template selected by the manifest:

```sh
stelion workspace new myproject "One-line description."
```

Register an existing project:

```sh
stelion workspace register ../myproject
```

Check which generated files have drifted:

```sh
stelion workspace status
```

## Submodule Synchronization

After committing changes in a library consumed as a git submodule, propagate the
commit to all replicas:

```sh
stelion submodule sync scholia --dry-run   # preview
stelion submodule sync scholia             # apply
```

The `--from` flag selects the source replica (local, a superproject name, or remote).
See [Submodule Sync](submodule-sync.md) for the full reference.

## Bulk Operations

Commit a shared change across all projects:

```sh
stelion workspace commit -m "chore: update CI config"
```

Push all git-enabled projects:

```sh
stelion workspace push --git-only
```

Run any shell command across a subset of projects:

```sh
stelion workspace exec "git status --short" --names stelion,morpha,glossa
```

All bulk commands accept filter options (`--names`, `--pattern`, `--git-only`,
`--exclude`) and `--dry-run`. See [Bulk Operations](bulk-operations.md) for the
full reference.

## Cross-Project Comparison

Compare directory structures:

```sh
stelion compare tree --names architekta,morpha,glossa --subtree docs/
```

Compare a specific configuration file field by field:

```sh
stelion compare files pyproject.toml --names architekta,morpha
```

For machine-parseable output, add `--format yaml`. For complex comparisons with
path overrides and field selectors, use a declarative instruction file:

```sh
stelion compare files --instruction compare-instructions.yml
```

See [Comparison](comparison.md) for the full reference.

## Next Steps

- [CLI Reference](cli-reference.md) — Full command registry and options.
- [Bulk Operations](bulk-operations.md) — exec, commit, push across projects.
- [Submodule Sync](submodule-sync.md) — Propagating commits across replicas.
- [Comparison](comparison.md) — Tree and file comparison commands.
- [Integration Policy](integration-policy.md) — Mechanisms, pinning, optional deps.
