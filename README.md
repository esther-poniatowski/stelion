# stelion

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](#installation)
[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/stelion)](https://github.com/esther-poniatowski/stelion/commits/main)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.12-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL--3.0-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Cross-project synchronization framework and multi-project workspace manager.

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
at two levels:

1. **Workspace management** --- Discovers projects on disk, generates a unified
   VS Code workspace, a project inventory, an inter-project dependency graph,
   and a shared Conda environment from a single declarative manifest
   (`stelion.yml`). Bootstraps new projects from a template repository with
   placeholder substitution.

2. **Repository synchronization** (planned) --- Synchronizes shared files across
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
- **Ecosystem governance**: Ships authoritative standards (design principles,
  writing conventions, integration policy) and audit prompts as package data.
- **Cross-project coherence**: Keeps shared configuration files consistent while
  permitting local deviations.

---

## Features

### Workspace Management (implemented)

- [X] Discover projects by scanning directories for `pyproject.toml`.
- [X] Generate VS Code multi-root workspace files from discovered projects.
- [X] Generate project inventory (`projects.md`) from `pyproject.toml` metadata.
- [X] Generate structured dependency graph (`dependencies.yml` + `dependencies.md`).
- [X] Generate shared Conda environment from merged project environments.
- [X] Bootstrap new projects from a keystone template with placeholder substitution.
- [X] Register existing projects into workspace artifacts without full regeneration.
- [X] Detect drift between generated files and current project state.
- [X] Auto-generate manifest with sensible defaults on first run.
- [X] Ship ecosystem governance documents and VS Code defaults as package data.

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
Fill in the manifest's `categories`, `names_in_use`, and `integrations` sections,
then run:

```sh
stelion workspace init
```

Bootstrap a new project from the template:

```sh
stelion workspace new myproject "One-line description."
```

---

## Usage

### Workspace Commands

```sh
stelion workspace init [--manifest PATH] [--dry-run]
```

Initialize or regenerate a workspace. Generates `stelion.yml` with
auto-discovered projects when no manifest exists. With an existing manifest,
generates all workspace artifacts and copies reference documents from package
data.

```sh
stelion workspace sync [--target TARGET] [--force] [--dry-run]
```

Re-scan projects and update generated files. `--target` limits to a single
artifact (`workspace-file`, `projects`, `dependencies`, `environment`).

```sh
stelion workspace register <path>
```

Register an existing project (copy-pasted, imported, or manually created)
without running the full generation pipeline.

```sh
stelion workspace new <name> "<description>" [--no-git] [--dry-run]
```

Bootstrap a new project from the template: copy, substitute placeholders, rename
directories, initialize git, and register into workspace artifacts.

```sh
stelion workspace status
```

Show which generated files are out of date. Exit code 0 if all current, 1 if
drift detected.

### Global Commands

```sh
stelion info          # version and platform diagnostics
stelion --version     # version number
```

---

## Package Data

Stelion ships ecosystem governance documents and VS Code defaults as package
data under `src/stelion/data/`:

```text
data/
    standards/              # Authoritative rule definitions
        design-principles.md    # Architectural rules (referenced by audit-architecture)
        writing-standards.md    # Prose conventions (referenced by audit-documentation)
        integration-policy.md   # Integration mechanisms and version pinning
    audits/                 # Enforcement prompts
        audit-architecture.md   # Detects violations of design-principles
        audit-documentation.md  # Detects violations of writing-standards
    references/             # Other reference documents
        names.md                # Project naming conventions (Greek/Latin etymologies)
    vscode/                 # VS Code workspace defaults
        settings.json           # Ecosystem-standard editor settings
        extensions.json         # Recommended extensions
```

Each audit prompt references its corresponding standards file. The standards
define the rules; the audits define the detection methodology.

Governance documents are the single source of truth and live only here — they
are not copied into workspaces. The VS Code multi-root workspace includes
stelion as a folder, making all files navigable from the editor.

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
