# Stelion

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](#installation)
[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/stelion)](https://github.com/esther-poniatowski/stelion/commits/main)
[![Python](https://img.shields.io/badge/python-supported-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Tool that synchronizes files across repositories while preserving modifications specific to each project.

---

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

Distinct development projects often share configurations, environments, and tool settings.
Keeping files consistent while supporting customizations specific to each project is a recurring
challenge.

Standard approaches fall short:

- Duplicating files manually with targeted edits becomes unsustainable as projects evolve.
- Templates replicate files automatically but cannot handle precise adjustments specific to each project.
- `git` and similar tools cannot compare individual files across projects, and their diffs miss
  structural changes such as reordered blocks or substituted placeholders.

### Advantages

Stelion synchronizes files across repositories while preserving modifications specific to each
project:

- **Cross-project coherence**: Keeps shared configuration files consistent while permitting
  local deviations.
- **Template merging**: Tracks changes derived from instantiating templates to integrate updates
  meaningfully.
- **Precise diffing**: Detects divergences at the token level, including substituted placeholders
  and structural edits.

---

## Features

- [ ] Synchronize and adapt file versions across repositories.
- [ ] Configure mappings between local and remote versions across multiple repositories.
- [ ] Merge versions with standard conflict markers (three-way scheme).
- [ ] Compare file contents (diff) at line, word, or token level.
- [ ] Fill templates by replacing placeholders via configurable rules.
- [ ] Dry-run and verbose modes for safe inspection.
- [ ] Extend merge, diff and template strategies via plugins.

---

## Installation

### Using pip

Install from the GitHub repository:

```bash
pip install git+https://github.com/esther-poniatowski/stelion.git
```

### Using conda

Install from the eresthanaconda channel:

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

Display version and platform diagnostics:

```sh
stelion info
```

> [!NOTE]
> Stelion's CLI commands for merging templates, diffing, and synchronizing files are under
> active development. See the [Features](#features) section for the planned command set.

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
