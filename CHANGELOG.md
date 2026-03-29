# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- **Cross-project comparison**: New `stelion compare` command group with two
  subcommands:
  - `stelion compare tree` --- Compares directory structures across projects
    with hierarchical matching (directories first, then files within). Uses
    three-pass matching (exact, case-insensitive, fuzzy) and reports per-project
    presence/absence for every matched node.
  - `stelion compare files` --- Compares file contents across projects.
    Structured files (TOML, YAML, JSON) are diffed field by field with dotted
    paths. Unstructured files are compared by variant grouping with pairwise
    similarity scores.
  - Declarative YAML instruction files for complex comparisons with path
    overrides, field selectors, and parser hints.
  - Both terminal (Rich tables) and machine-parseable (YAML) output formats.
  - Per-file error resilience: read or parse failures do not abort other files.
- **Submodule synchronization**: New `stelion submodule sync` command that
  propagates a commit across all replicas of a dependency (local clone,
  superproject submodule pointers, and remote). Supports three source modes
  (`--from local`, `--from <superproject>`, `--from remote`), dry-run
  inspection, and optional auto-commit. Per-action error resilience ensures
  failures in one replica do not abort the rest.
