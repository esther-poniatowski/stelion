# Getting Started

## Installation

Install stelion via pip:

```sh
pip install stelion
```

Or via conda:

```sh
conda install -c eresthanaconda stelion
```

## Quick Start

Initialize a workspace in a directory containing sibling projects:

```sh
cd dev/
stelion workspace init
```

Re-scan projects and update generated files:

```sh
stelion workspace sync
```

Limit a sync to a single artifact:

```sh
stelion workspace sync --target dependencies
```

After updating a library consumed as a git submodule, propagate the change to
all superprojects:

```sh
stelion submodule sync scholia --dry-run   # preview
stelion submodule sync scholia             # apply
```

See the [Submodule Synchronization](submodule-sync.md) guide for the full
reference.

Commit a change across all projects at once, then push:

```sh
stelion workspace commit -m "chore: update CI config" --dry-run   # preview
stelion workspace commit -m "chore: update CI config"             # apply
stelion workspace push --git-only
```

Run any shell command across a subset of projects:

```sh
stelion workspace exec "git status --short" --names stelion,morpha,glossa
```

Register an existing project and update workspace artifacts immediately:

```sh
stelion workspace register ../external/manual
```

See the [Bulk Operations](bulk-operations.md) guide for the full reference.
