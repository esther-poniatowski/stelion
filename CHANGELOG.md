# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- The command `stelion layout check`, which checks a repository against a layout that its consumer
  declares, in the new format `stelion:layout@1`, and reports twelve rules: missing kinds of file,
  the placement, role and sections of a kind of file, the roles admitted per area, the forbidden
  link directions between areas, the retired paths, and the root entries, placements, untracked
  paths and size limit of the tree. The report is text or a findings log in the profile of
  Elenchos. The package ships the schema of the format and the default layout `project`, which a
  layout extends by name.
- The extra `layout`, which installs the read package of Anagraphe and `jsonschema`, and the extra
  `test`, which installs Elenchos.
- The option `--anagraphe-config PATH` of `stelion layout check`, which names a configuration of
  Anagraphe kept outside the places that Anagraphe searches, such as `settings/anagraphe.yml`.
  The check then reads the metadata, links and shared exclusions declared in that file. A missing
  file stops the check with status 2. Without the option, the check is unchanged.

### Fixed

- `-v`/`--version` prints the version without a command. The option was not eager, so the command
  line stopped with "Missing command" and status 2.

### Changed

- The first commit of a bootstrapped project names the template that the manifest configures,
  the folder of `template.source`, instead of a fixed template name.
- **Breaking:** The extra `layout` requires `anagraphe-read` 0.5.0 at commit `107a80b`, and the
  extra `test` requires Elenchos at commit `33160b2`. Both pin Hodegos at `a151a28`, as Stelion
  does, so the extras install again. Therefore, `stelion layout check` reads `anagraphe.yml` at the
  root, in `.config/` or in `config/`, and no longer in `config/tools/`. A file left in
  `config/tools/` is ignored, so the repository is read without shared exclusions. A root that holds
  the file at two places stops the check with status 2.
- **Breaking:** Stelion requires Hodegos at commit `a151a28`. Therefore, Stelion searches
  `config/stelion.yml`, and no longer searches a folder that a file `hodegos.yml` lists. A file
  `hodegos.yml` left at the root is ignored, so an invalid one no longer stops a command. A root
  that holds both `config/stelion.yml` and another place of the file stops the command with
  status 2.
- **Breaking:** Hodegos locates the root of a command and the file `stelion.yml`, as its
  [specification](https://github.com/esther-poniatowski/hodegos/blob/main/docs/specification.md)
  states. The file lies at the root, in its subfolder `.config/`, or in its subfolder `config/`.
  Stelion no longer reads `config/tools/stelion.yml`: the option `--config` names a file kept in
  that folder or in any other folder. Hodegos reads `STELION_ROOT`, and the option `--root` no
  longer reads it. `workspace render-manifest` stops with status 2 when its root holds two competing
  configuration files. The places named in the next entry are replaced by these places.
- The command line follows the conventions shared by the tools of the workspace:
  - every command that reads the configuration file takes `-r`/`--root` and `-c`/`--config`; the
    root comes from `--root`, else `STELION_ROOT`, else the nearest ancestor holding `stelion.yml`
    in `config/tools/` or at its level, else the current folder;
  - the configuration file is read from `config/tools/stelion.yml` or `stelion.yml` below the root;
    two competing files stop the command with status 2; without a configuration file, Stelion runs
    on its canonical defaults;
  - the paths written in the configuration file are relative to the root, no longer to the folder of
    the file;
  - `workspace render-manifest` writes to the standard output without `--output`, and takes the
    final workspace from `--root`;
  - `workspace new --parent PATH`, read from the current folder, selects the scan directory that
    receives the new project;
  - `workspace register` asks for a confirmation before it rewrites an existing configuration file;
    `--yes` answers it, and without a terminal and without `--yes` the command stops with status 2;
  - `compare --format` takes `text` or `yaml`;
  - an absent or invalid configuration file is a configuration error, with status 2.

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
