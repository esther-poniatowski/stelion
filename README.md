# stelion

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](#installation)
[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/stelion)](https://github.com/esther-poniatowski/stelion/commits/main)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.12-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL--3.0-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Keeps multiple Python projects consistent within a shared workspace.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Package Data](#package-data)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Overview

Stelion manages consistency across a multi-project Python ecosystem. It operates
at three levels:

1. **Workspace management** --- Discovers projects on disk, generates a unified
   VS Code workspace, a project registry (YAML), a structured dependency graph
   (YAML), and a shared Conda environment from a single declarative manifest
   (`stelion.yml`). Bootstraps new projects from a template repository with
   placeholder substitution.

2. **Submodule synchronization** --- Propagates a commit across all replicas of
   a dependency: local clone, superproject submodule pointers, and remote.
   Supports local, superproject, and remote sources with optional auto-commit
   and dry-run inspection.

3. **Bulk operations** --- Runs commands across all or a filtered subset of
   discovered projects. Includes generic shell execution and structured git
   operations (commit, push) with per-project outcome reporting.

4. **Repository synchronization** (planned) --- Synchronizes shared files across
   repositories while preserving project-specific modifications. Supports
   token-level diffing, three-way merge with conflict markers, and configurable
   template substitution.

### Motivation

Distinct development projects often share configurations, environments, and tool
settings. Keeping files consistent while supporting project-specific adjustments
is a recurring challenge:

- Duplicating files manually with targeted edits becomes unsustainable as
  projects evolve.
- Templates replicate files automatically but cannot handle precise adjustments
  specific to each project.
- Standard diff tools cannot compare individual files across projects, and their
  diffs miss structural changes such as reordered blocks or substituted
  placeholders.

### Advantages

- **Workspace generation**: A single `stelion.yml` manifest drives the creation
  of VS Code workspace files, project indexes, dependency graphs, and shared
  Conda environments.
- **Project bootstrapping**: New projects inherit their structure from a template
  repository with automated placeholder substitution and registration.
- **Bulk operations**: Commit, push, or run arbitrary commands across all projects
  (or a filtered subset) in a single invocation.
- **Cross-project coherence**: Keeps shared configuration files consistent while
  permitting local deviations.

---

## Features

### Workspace Management (implemented)

- [X] Discover projects by scanning directories for `pyproject.toml`.
- [X] Generate VS Code multi-root workspace files from discovered projects.
- [X] Generate project registry (`projects.yml`) with description, status, and language detection.
- [X] Generate structured dependency graph (`dependencies.yml`).
- [X] Generate shared Conda environment from merged project environments.
- [X] Bootstrap new projects from a keystone template with placeholder substitution.
- [X] Register existing projects into workspace artifacts and persist discovery config when needed.
- [X] Detect drift between generated files and current project state.
- [X] Auto-generate manifest with sensible defaults on first run.
- [X] Ship VS Code workspace defaults as package data.

### Submodule Synchronization (implemented)

- [X] Propagate a commit from a local repo to all superproject submodule pointers and the remote.
- [X] Propagate a commit from one superproject's submodule to the local clone, the remote, and all other superprojects.
- [X] Fetch and propagate a remote HEAD to the local clone and all superproject submodule pointers.
- [X] Dry-run mode for safe inspection of planned updates.
- [X] Optional auto-commit of submodule pointer changes in each superproject.
- [X] Per-action error resilience: failures in one replica do not abort the rest.

### Bulk Operations (implemented)

- [X] Run an arbitrary shell command in each project directory.
- [X] Stage tracked changes and commit across projects with a shared message.
- [X] Push the current branch to a remote across projects.
- [X] Filter target projects by name, regex pattern, git presence, or exclusion list.
- [X] Dry-run mode for safe inspection of planned operations.
- [X] Per-project error resilience: failures in one project do not abort the rest.
- [X] Tabular outcome reporting with per-project status (success, skipped, failed).

### Repository Synchronization (planned)

- [ ] Synchronize and adapt file versions across repositories.
- [ ] Configure mappings between local and remote versions.
- [ ] Merge versions with standard conflict markers (three-way scheme).
- [ ] Compare file contents (diff) at line, word, or token level.
- [ ] Fill templates by replacing placeholders via configurable rules.
- [ ] Dry-run and verbose modes for safe inspection.
- [ ] Extend merge, diff, and template strategies via plugins.

---

## Installation

### Using pip

```bash
pip install git+https://github.com/esther-poniatowski/stelion.git
```

### Using conda

```bash
conda install stelion -c eresthanaconda
```

### From source

```bash
git clone https://github.com/esther-poniatowski/stelion.git
cd stelion
conda env create -f environment.yml
conda activate stelion
pip install -e .
```

---

## Quick Start

Initialize a workspace in a directory containing sibling projects:

```sh
cd dev/
stelion workspace init
```

This auto-discovers projects and generates `stelion.yml` with sensible defaults.
Fill in the manifest's `names_in_use` and `integrations` sections, then run:

```sh
stelion workspace init
```

Bootstrap a new project from the template:

```sh
stelion workspace new myproject "One-line description."
```

Then register it into the generated workspace artifacts:

```sh
stelion workspace register ../myproject
```

---

## Usage

### Workspace Commands

```sh
stelion workspace init [--manifest PATH] [--dry-run]
```

Initialize or regenerate a workspace. Generates `stelion.yml` with
auto-discovered projects when no manifest exists. With an existing manifest,
generates all workspace artifacts.

```sh
stelion workspace sync [--target TARGET] [--force] [--dry-run]
```

Re-scan projects and update generated files. `--target` limits to a single
artifact (`workspace-file`, `projects`, `dependencies`, `environment`).

```sh
stelion workspace register <path>
```

Register an existing project (copy-pasted, imported, or manually created)
and immediately regenerate workspace artifacts. If the project sits outside the
configured scan roots, Stelion records it in `discovery.extra_paths`.

```sh
stelion workspace new <name> "<description>" [--destination ROOT] [--no-git] [--dry-run]
```

Bootstrap a new project from the template: copy, substitute placeholders, rename
directories, and optionally initialize git. Then use `stelion workspace register`
to add it to generated workspace artifacts.

```sh
stelion workspace status
```

Show which generated files are out of date. Exit code 0 if all current, 1 if
drift detected.

### Bulk Commands

```sh
stelion workspace exec <command> [--names a,b,c] [--pattern REGEX] [--git-only] [--exclude x,y] [--dry-run]
```

Run an arbitrary shell command in each project directory. Compound commands work
via shell expansion (e.g. `"git add -A && git status"`).

```sh
stelion workspace commit -m <message> [--names a,b,c] [--pattern REGEX] [--git-only] [--exclude x,y] [--dry-run]
```

Stage tracked changes (`git add --update`) and commit in each project. Projects
with a clean working tree or no git repository are skipped automatically.

```sh
stelion workspace push [--remote origin] [--branch main] [--names a,b,c] [--pattern REGEX] [--git-only] [--exclude x,y] [--dry-run]
```

Push the current branch to a remote in each project.

All bulk commands share the same filter options:

| Option | Effect |
| --- | --- |
| `--names a,b,c` | Restrict to the named projects |
| `--pattern REGEX` | Match project names by regular expression |
| `--git-only` | Only projects with a git repository |
| `--exclude x,y` | Exclude the named projects |
| `--dry-run` | Preview without executing |

### Submodule Commands

```sh
stelion submodule sync <dependency> [--from local|<superproject>|remote] [--no-commit] [--dry-run]
```

Propagate a commit across all replicas of `<dependency>`. The `--from` flag
selects the source: `local` (default) uses the standalone repo's HEAD, a
superproject name reads from that superproject's submodule pointer, and `remote`
fetches and uses the remote HEAD. All other replicas are updated automatically:
submodule pointers in superprojects, the local clone, and the remote.

### Global Commands

```sh
stelion info          # version and platform diagnostics
stelion --version     # version number
```

---

## Package Data

Stelion ships VS Code workspace defaults as package data under
`src/stelion/data/`:

```text
data/
    vscode/                 # VS Code workspace defaults
        settings.json           # Ecosystem-standard editor settings
        extensions.json         # Recommended extensions
```

Quality governance (design principles, writing standards, audit prompts, AI
agent templates) is provided by [eutaxis](https://github.com/esther-poniatowski/eutaxis).
Research organization (note types, contracts, registries, epistemic rules) is
provided by [gnomon](https://github.com/esther-poniatowski/gnomon).

---

## Documentation

- [User Guide](https://esther-poniatowski.github.io/stelion/guide/)
- [API Documentation](https://esther-poniatowski.github.io/stelion/api/)

> [!NOTE]
> Documentation can also be browsed locally from the [`docs/`](docs/) directory.

---

## Contributing

Please refer to the [contribution guidelines](CONTRIBUTING.md).

---

## Acknowledgments

**Author**: @esther-poniatowski

For academic use, please cite using the GitHub "Cite this repository" feature or
refer to the [citation metadata](CITATION.cff).

### Third-Party Dependencies

- **[PyYAML](https://pyyaml.org/)** --- YAML configuration parsing
- **[Typer](https://typer.tiangolo.com/)** --- CLI interface
- **[Rich](https://rich.readthedocs.io/)** --- Terminal output formatting

---

## License

This project is licensed under the terms of the [GNU General Public License v3.0](LICENSE).
