# stelion

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](docs/guide/installation.md)
[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/stelion)](https://github.com/esther-poniatowski/stelion/commits/main)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.12-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL--3.0-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Keeps multiple Python projects consistent within a shared workspace.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Overview

Stelion manages consistency across a multi-project Python ecosystem. The tool operates
at four levels:

1. **Workspace management** — discovers projects on disk, generates a unified VS Code
   workspace, a project registry, a dependency graph, and a shared Conda environment
   from a single declarative manifest (`stelion.yml`). Bootstraps new projects from a
   template repository with placeholder substitution.
2. **Submodule synchronization** — propagates a commit across all replicas of a
   dependency: local clone, superproject submodule pointers, and remote.
3. **Bulk operations** — runs commands across all or a filtered subset of discovered
   projects, including structured git operations (commit, push) with per-project
   outcome reporting.
4. **Cross-project comparison** — compares directory structures or file contents across
   selected projects with hierarchical matching, variant grouping, and structured
   field-level diffing.

### Motivation

Distinct development projects often share configurations, environments, and tool
settings. Keeping files consistent while supporting project-specific adjustments is
a recurring challenge:

- Duplicating files manually with targeted edits becomes unsustainable as projects
  evolve.
- Templates replicate files automatically but cannot handle precise adjustments specific
  to each project.
- Standard diff tools cannot compare individual files across projects, and their diffs
  miss structural changes such as reordered blocks or substituted placeholders.

### Advantages

- **Workspace generation** — a single `stelion.yml` manifest drives the creation of
  VS Code workspace files, project indexes, dependency graphs, and shared Conda
  environments.
- **Project bootstrapping** — new projects inherit their structure from a template
  repository with automated placeholder substitution and registration.
- **Bulk operations** — commit, push, or run arbitrary commands across all projects
  (or a filtered subset) in a single invocation.
- **Cross-project comparison** — compare directory layouts or specific files (TOML,
  YAML, JSON, Markdown) across projects with hierarchical matching, variant grouping,
  and structured field-level diffing.

---

## Features

### Workspace Management (implemented)

- [X] Discover projects by scanning directories for `pyproject.toml`.
- [X] Generate VS Code multi-root workspace files from discovered projects.
- [X] Generate project registry (`projects.yml`) with description, status, and language.
- [X] Generate structured dependency graph (`dependencies.yml`).
- [X] Generate shared Conda environment from merged project environments.
- [X] Bootstrap new projects from a keystone template with placeholder substitution.
- [X] Register existing projects and persist discovery config when needed.
- [X] Detect drift between generated files and current project state.
- [X] Auto-generate manifest with sensible defaults on first run.

### Submodule Synchronization (implemented)

- [X] Propagate a commit from a local repo to all superproject submodule pointers and
  the remote.
- [X] Propagate a commit from one superproject's submodule to the local clone, the
  remote, and all other superprojects.
- [X] Fetch and propagate a remote HEAD to the local clone and all superproject pointers.
- [X] Dry-run mode, optional auto-commit, per-action error resilience.

### Bulk Operations (implemented)

- [X] Run arbitrary shell commands in each project directory.
- [X] Stage tracked changes and commit across projects with a shared message.
- [X] Push the current branch to a remote across projects.
- [X] Filter by name, regex, git presence, or exclusion list; dry-run mode.
- [X] Tabular outcome reporting with per-project status.

### Cross-Project Comparison (implemented)

- [X] Compare directory structures with hierarchical matching (exact, case-insensitive,
  fuzzy).
- [X] Compare structured files (TOML, YAML, JSON) field by field with dotted-path
  diffing.
- [X] Compare unstructured files (Markdown, text) via variant grouping and pairwise
  similarity.
- [X] Declarative YAML instruction files for complex comparisons.
- [X] Output as Rich terminal tables or machine-parseable YAML.

### Repository Synchronization (planned)

- [ ] Synchronize and adapt file versions across repositories.
- [ ] Three-way merge with conflict markers; configurable template substitution.
- [ ] Extensible merge, diff, and template strategies via plugins.

---

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

---

## Documentation

| Guide | Content |
| ----- | ------- |
| [Installation](docs/guide/installation.md) | Prerequisites, pip/conda/source setup |
| [Usage](docs/guide/usage.md) | Workflows and command overview |
| [CLI Reference](docs/guide/cli-reference.md) | Full command registry and options |
| [Bulk Operations](docs/guide/bulk-operations.md) | exec, commit, push across projects |
| [Submodule Sync](docs/guide/submodule-sync.md) | Propagating commits across replicas |
| [Comparison](docs/guide/comparison.md) | Tree and file comparison commands |
| [Integration Policy](docs/guide/integration-policy.md) | Mechanisms, pinning, optional dependencies |

Full API documentation and rendered guides are also available at
[esther-poniatowski.github.io/stelion](https://esther-poniatowski.github.io/stelion/).

---

## Contributing

Contribution guidelines are described in [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Acknowledgments

### Authors

**Author**: @esther-poniatowski

For academic use, the GitHub "Cite this repository" feature generates citations in
various formats. The [citation metadata](CITATION.cff) file is also available.

### Third-Party Dependencies

- **[PyYAML](https://pyyaml.org/)** — YAML configuration parsing.
- **[Typer](https://typer.tiangolo.com/)** — CLI interface.
- **[Rich](https://rich.readthedocs.io/)** — Terminal output formatting.

---

## License

This project is licensed under the terms of the
[GNU General Public License v3.0](LICENSE).
