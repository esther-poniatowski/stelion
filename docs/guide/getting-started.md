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

After updating a library consumed as a git submodule, propagate the change to
all superprojects:

```sh
stelion submodule sync scholia --dry-run   # preview
stelion submodule sync scholia             # apply
```

See the [Submodule Synchronization](submodule-sync.md) guide for the full
reference.
