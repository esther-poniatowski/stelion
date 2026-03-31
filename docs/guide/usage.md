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

The first run auto-discovers projects and generates `stelion.yml` with sensible
defaults. Subsequent runs regenerate all workspace artifacts from the manifest.

Re-scan projects and update generated files:

```sh
stelion workspace sync
```

Bootstrap a new project from the template:

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
