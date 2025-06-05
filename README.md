# Stelion

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](#installation)
[![Maintenance](https://img.shields.io/maintenance/yes/2025)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/architekta)](https://github.com/esther-poniatowski/architekta/commits/main)
[![Python](https://img.shields.io/badge/python-supported-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

---

Repository synchronizer toolset for cross-project consistency and project-specific
adjustments via configurable mappings, fine-grained diffs, and template-based substitution.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Support](#support)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Overview

### Motivation

Distinct development projects often share common configurations, development environments, and tool
settings. A recurring challenge is to maintain consistency across these projects while supporting
project-specific customizations.

Standard approaches remain limited:

- Manual duplication across projects with targeted edits is error-prone and unsustainable as
  projects evolve.
- Template-based synchronization partially automates replication but does not accommodate
  fine-grained, project-specific adjustments.
- Comparing or merging *individual* files across projects is not supported by standard version
  control systems (e.g., `git`), and their line-based diffing fails to capture structural or
semantic differences (e.g., reordering, token-level edits, placeholder substitutions).

These limitations hinder the ability to propagate updates across repositories, track divergence from
a reference template, and integrate external modifications selectively.

### Advantages

This tool introduces a controlled, file-level synchronization mechanism across multiple
repositories, while preserving project-specific modifications.

It provides the following benefits:

- **Cross-project coherence with flexibility**: Ensures consistency across shared configuration
  files across repositories while permitting local deviations.
- **Template-aware merging**: Tracks changes derived from template instantiation, enabling
  meaningful integration of updates.
- **Fine-grained difference analysis**: Detects divergences at the token level (including
  placeholder substitutions) and structural edits, allowing precise inspection of relevant changes.

---

## Features

- [ ] Synchronize and adapt file versions across repositories.
- [ ] Configure mappings between local and remote versions across multiple repositories.
- [ ] Merge versions with standard conflict markers (three-way scheme).
- [ ] Compare file contents (diff) at various granularity (line, word, token).
- [ ] Fill templates via configurable placeholder replacement.
- [ ] Dry-run and verbose modes for safe inspection.
- [ ] Extend merge, diff and template strategies via plugins.

---

## Installation

To install the package and its dependencies, use one of the following methods:

### Using Pip Installs Packages

Install the package from the GitHub repository URL via `pip`:

```bash
pip install git+https://github.com/esther-poniatowski/stelion.git
```

### Using Conda

Install the package from the private channel eresthanaconda:

```bash
conda install stelion -c eresthanaconda
```

### From Source

1. Clone the repository:

      ```bash
      git clone https://github.com/esther-poniatowski/stelion.git
      ```

2. Create a dedicated virtual environment:

      ```bash
      cd stelion
      conda env create -f environment.yml
      ```

---

## Usage

### Command Line Interface (CLI)

To display the list of available commands and options:

```sh
stelion --help
```

### Programmatic Usage

To use the package programmatically in Python:

```python
import stelion
```

---

## Configuration

### Environment Variables

|Variable|Description|Default|Required|
|---|---|---|---|
|`VAR_1`|Description 1|None|Yes|
|`VAR_2`|Description 2|`false`|No|

### Configuration File

Configuration options are specified in YAML files located in the `config/` directory.

The canonical configuration schema is provided in [`config/default.yaml`](config/default.yaml).

```yaml
var_1: value1
var_2: value2
```

---

## Documentation

- [User Guide](https://esther-poniatowski.github.io/stelion/guide/)
- [API Documentation](https://esther-poniatowski.github.io/stelion/api/)

> [!NOTE]
> Documentation can also be browsed locally from the [`docs/`](docs/) directory.

## Support

**Issues**: [GitHub Issues](https://github.com/esther-poniatowski/stelion/issues)

**Email**: `{{ contact@example.com }}`

---

## Contributing

Please refer to the [contribution guidelines](CONTRIBUTING.md).

---

## Acknowledgments

### Authors & Contributors

**Author**: @esther-poniatowski

**Contact**: `{{ contact@example.com }}`

For academic use, please cite using the GitHub "Cite this repository" feature to
generate a citation in various formats.

Alternatively, refer to the [citation metadata](CITATION.cff).

### Third-Party Dependencies

- **[Library A](link)** - Purpose
- **[Library B](link)** - Purpose

---

## License

This project is licensed under the terms of the [GNU General Public License v3.0](LICENSE).
