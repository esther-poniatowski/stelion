# Submodule Synchronization

When multiple superprojects consume the same library as a git submodule, keeping
every submodule pointer in sync requires a repetitive sequence of operations
across repositories. The `stelion submodule sync` command automates this by
reading the dependency graph and propagating a commit to all replicas of a
dependency.

## Replicas

A dependency exists in up to three kinds of locations:

- **Local clone** --- the standalone repository where the library is developed.
- **Submodule instances** --- copies embedded in superprojects via `git
  submodule` (e.g. `geonexus/vendor/scholia`, `thoth/common/scholia`).
- **Remote** --- the upstream repository (e.g. GitHub).

The `--from` flag selects which replica is the **source** of the target commit.
All other replicas become **targets** and are updated automatically.

## Usage

```sh
stelion submodule sync <dependency> [--from local|<superproject>|remote]
                                    [--no-commit] [--dry-run]
                                    [--remote origin] [--branch main]
                                    [--manifest stelion.yml]
```

## Source Modes

### From local (default)

After committing changes in the local clone, propagate the current HEAD to all
superproject submodule pointers and push to the remote.

```sh
stelion submodule sync scholia
```

| Action | Target |
| --- | --- |
| Push | Remote (`origin/main`) |
| Update submodule pointer | Each superproject containing the dependency |

### From a superproject

After advancing a submodule within a specific superproject, propagate that
commit to the local clone, the remote, and all other superprojects.

```sh
stelion submodule sync scholia --from geonexus
```

| Action | Target |
| --- | --- |
| Fast-forward merge | Local clone |
| Push | Remote (`origin/main`) |
| Update submodule pointer | All superprojects except the source |

### From remote

After someone else has pushed to the remote, pull the change into the local
clone and update all superproject submodule pointers.

```sh
stelion submodule sync scholia --from remote
```

| Action | Target |
| --- | --- |
| Fetch + fast-forward merge | Local clone |
| Update submodule pointer | Each superproject containing the dependency |

## Options

`--dry-run`
:   Preview all planned updates without applying any changes. The output table
    shows what would be updated.

`--no-commit`
:   Update submodule pointers in superprojects without creating a commit for
    each pointer change. Useful when batching multiple submodule updates into a
    single manual commit.

`--remote NAME`
:   Remote name for fetch and push operations. Defaults to `origin`.

`--branch NAME`
:   Branch name for remote operations. Defaults to `main`.

## Execution Order

Within a single sync invocation, actions execute in a fixed order:

1. **Update local clone** (fetch + fast-forward merge)
2. **Push to remote**
3. **Update submodule pointers** (checkout + optional commit per superproject)

This ordering ensures the local repository is current before pushing, and
submodule pointer updates proceed independently of local or remote outcomes.

## Error Handling

Each action is wrapped individually. A failure in one replica (e.g. a dirty
working tree preventing a local merge, or a diverged remote rejecting a push)
is recorded in the outcome but does not abort the remaining actions. The final
output table highlights errors alongside successful updates.

## Prerequisites

The command reads the dependency graph from stelion's workspace context. For a
dependency to be syncable:

- It must appear as a `git_submodule` edge in `dependencies.yml`.
- Its superprojects must be listed in `dependencies.extra_scan_dirs` in
  `stelion.yml`.
- The local clone must be in the project inventory (discovered via
  `pyproject.toml` or custom markers).
