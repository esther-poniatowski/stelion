# Integration Policy

Guidelines for integrating packages across a multi-project ecosystem. Governs
the choice of integration mechanism, version pinning strategy, optional
dependency patterns, and integration module design.

## 1. Integration Mechanisms

### 1.1 Decision Matrix

| Criterion | Editable pip install | Conda channel | Git submodule |
| --------- | -------------------- | ------------- | ------------- |
| Library type | Python package | Python package | Non-Python (LaTeX), zero-dep tools |
| Consumer type | Research / active development | Teaching / production | Any |
| Update frequency | Continuous (source changes reflect immediately) | Release-gated | Manual (`git submodule update`) |
| Reproducibility | Low (floating, machine-specific paths) | High (channel-pinned) | Medium (commit-pinned if disciplined) |
| Portability | Low (absolute paths in `environment.yml`) | High (channel name only) | High (repository URL) |
| Best for | Rapid iteration during active co-development | Stable consumption of released packages | Vendoring non-pip-installable artifacts |

### 1.2 When to Use Each Mechanism

**Editable pip install** (`pip install -e <path>`):

- The consumer and the library are under active co-development.
- The consumer needs source changes reflected immediately without rebuilds.
- Both projects live on the same machine (single-developer workflow).
- Declare in `environment.yml` under the `pip:` section.

**Conda channel** (`conda install -c <channel> <package>`):

- The library has published releases on a conda channel.
- The consumer does not need bleeding-edge changes.
- Reproducibility across machines matters (teaching environments, shared labs).
- Declare in `environment.yml` under `dependencies:`.

**Git submodule** (`git submodule add <url> vendor/<name>`):

- The library is not a Python package (LaTeX packages, build toolkits).
- The library has zero external dependencies and is invoked as a standalone tool.
- The consumer needs a vendored snapshot that travels with the repository.
- Declare in `.gitmodules`; place in `vendor/` (tools) or `common/` (shared content).

### 1.3 Submodule Directory Conventions

- `vendor/` -- standalone tools invoked by the consumer.
- `common/` -- shared content included into the consumer's source tree.

Use `vendor/` as the default. Use `common/` only when the submodule provides content
that is directly `\input`-ed or `\usepackage`-d from the consumer's source tree.

## 2. Version Pinning

### 2.1 Guidelines by Consumer Type

| Consumer type | Editable pip | Conda | Git submodule |
| ------------- | ------------ | ----- | ------------- |
| Research (active dev) | Floating (no version pin) | N/A | Floating (update frequently) |
| Teaching / production | N/A | Pin to channel version | Pin to tagged commit or release |
| Library (optional dep) | N/A | N/A | N/A (use `TYPE_CHECKING` imports) |

### 2.2 Rules

- **Research consumers** may use floating versions for all ecosystem packages. The
  development pace makes strict pinning counterproductive.
- **Teaching and production consumers** should pin conda packages to the channel version
  at environment creation time. Use `conda-lock` if multi-machine reproducibility is
  required.
- **Git submodules** should be updated explicitly with `git submodule update --remote`
  and committed. The commit hash in the parent repository serves as the version pin.
- **Never leave submodules floating** in production or teaching repositories. Always
  commit submodule updates as discrete changes with descriptive messages.

## 3. Optional Dependencies

### 3.1 When to Declare

Declare optional dependencies in `pyproject.toml` under `[project.optional-dependencies]`
when:

- A library provides integration modules for another ecosystem package.
- The integration is meaningful to external users (not just internal development).
- The dependency is importable at runtime (not just `TYPE_CHECKING`).

### 3.2 When NOT to Declare

Do not declare optional dependencies when:

- The integration is experimental or undocumented.
- The dependency is only used in tests (use dev extras instead).
- The consumer installs the library through a different mechanism (e.g., editable pip
  in an `environment.yml`).

## 4. Integration Module Pattern

### 4.1 Structure

Cross-library integrations should use a dedicated `integration/` subpackage within the
consuming library:

```
src/<package>/
    integration/
        __init__.py
        <library_a>.py
        <library_b>.py
```

Each integration module bridges the consuming library's domain with the external
library's API. The `integration/` package is part of the consuming library's source
tree, not a separate package.

### 4.2 Import Strategy

Use `TYPE_CHECKING` guards for type annotations and lazy runtime imports for actual
usage:

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from <external>.io import ExternalType

class IntegrationHandler:
    def process(self, data: ExternalType, path: Path) -> None:
        from <external>.io import get_handler  # lazy runtime import
        handler = get_handler(path.suffix)
        handler.process(data, path)
```

This pattern ensures:

- **No hard dependency**: the consuming library installs and works without the external
  library present.
- **Type safety**: type checkers resolve annotations via the `TYPE_CHECKING` block.
- **Graceful degradation**: runtime `ImportError` can be caught and logged, or the
  integration module can simply remain unused.

### 4.3 Testing Integration Modules

Integration tests should:

- Live in `tests/test_<package>/test_integration/`.
- Mock the external library to avoid adding it as a test dependency.
- Include at least one test that exercises the lazy import path.
- Include at least one test that exercises the graceful degradation path (import failure).

## 5. Redundancy and Consistency

### 5.1 Single Declaration Rule

Each library should be declared in exactly one location per consumer:

- Python packages: `environment.yml` (pip section) **or** `environment.yml`
  (dependencies section). Never both.
- Submodules: `.gitmodules` only.
- Never declare the same library in both `pyproject.toml` dependencies and
  `environment.yml` unless one is an optional dependency and the other is a concrete
  install for a specific environment.

### 5.2 Path Conventions for Editable Installs

Editable pip installs in `environment.yml` use absolute or relative paths:

```yaml
pip:
  - -e ../morpha[dev]
```

Absolute paths are acceptable for single-developer workflows. If portability becomes a
requirement, switch to relative paths from the consumer's root.
