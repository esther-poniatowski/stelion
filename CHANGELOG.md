# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- The command line follows the conventions shared by the tools of the workspace:
  - every command that reads the settings takes `-r`/`--root` and `-c`/`--config`; the root comes
    from `--root`, else `STELION_ROOT`, else the nearest ancestor holding `stelion.yml` in
    `config/tools/` or at its level, else the current folder;
  - the settings file is read from `config/tools/stelion.yml` or `stelion.yml` below the root; two
    competing files stop the command with status 2; without a settings file, Stelion runs on its
    canonical defaults;
  - the paths written in the settings file are relative to the root, no longer to the folder of
    the file;
  - `workspace render-manifest` writes to the standard output without `--output`, and takes the
    final workspace from `--root`;
  - `workspace new --parent PATH`, read from the current folder, selects the scan directory that
    receives the new project;
  - `workspace register` asks for a confirmation before it rewrites an existing settings file;
    `--yes` answers it, and without a terminal and without `--yes` the command stops with status 2;
  - `compare --format` takes `text` or `yaml`;
  - an absent or invalid settings file is a configuration error, with status 2.

### Removed

- `--manifest`/`-m` (replaced by `--config`/`-c` and `--root`/`-r`), `workspace new
  --destination`/`-d` (replaced by `--parent`), `workspace render-manifest --manifest-dir`
  (replaced by `--root`), `workspace sync --force` (the generated files are always rewritten when
  they change), the short forms `compare --format -f` and `compare files --reference -r`, and the
  format value `table` (replaced by `text`). The former names are rejected.

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
