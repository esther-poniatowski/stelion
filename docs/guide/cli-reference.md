# CLI Reference

## Global Options

```
stelion [OPTIONS] COMMAND [ARGS]
```

| Option | Description |
| ------ | ----------- |
| `--version` / `-v` | Display the version and exit. |
| `--help` | Display the help message and exit. |

## Workspace Commands

### `stelion workspace init`

Initialize or regenerate a workspace. Generates `stelion.yml` with auto-discovered
projects when no manifest exists. With an existing manifest, generates all workspace
artifacts.

```sh
stelion workspace init [--manifest/-m PATH] [--dry-run]
```

### `stelion workspace sync`

Re-scan projects and update generated files.

```sh
stelion workspace sync [--manifest/-m PATH] [--target/-t TARGET] [--force] [--dry-run]
```

| Option | Description | Default |
| ------ | ----------- | ------- |
| `--manifest PATH` / `-m` | Path to workspace manifest. | `stelion.yml` |
| `--target TARGET` / `-t` | Limit to a single artifact (`workspace-file`, `projects`, `dependencies`, `environment`). | All |
| `--force` | Overwrite even if up to date. | Off |

### `stelion workspace new`

Bootstrap a new project from the template: copy, substitute placeholders, rename
directories, and optionally initialize git.

```sh
stelion workspace new <name> "<description>" [--manifest/-m PATH] [--destination/-d ROOT] [--no-git] [--dry-run]
```

### `stelion workspace register`

Register an existing project and regenerate workspace artifacts. If the project sits
outside the configured scan roots, stelion records it in `discovery.extra_paths`.

```sh
stelion workspace register <path> [--manifest/-m PATH]
```

### `stelion workspace status`

Show which generated files are out of date. Exit code 0 if all current, 1 if drift
detected.

```sh
stelion workspace status [--manifest/-m PATH]
```

## Bulk Commands

All bulk commands share the same filter options:

| Option | Description |
| ------ | ----------- |
| `--names a,b,c` / `-n` | Restrict to the named projects. |
| `--pattern REGEX` / `-p` | Match project names by regular expression. |
| `--git-only` | Only projects with a git repository. |
| `--exclude x,y` / `-e` | Exclude the named projects. |
| `--dry-run` | Preview without executing. |
| `--manifest PATH` | Path to `stelion.yml`. |

### `stelion workspace exec`

Run an arbitrary shell command in each project directory.

```sh
stelion workspace exec <command> [FILTER OPTIONS] [--dry-run]
```

### `stelion workspace commit`

Stage tracked changes and commit with a shared message.

```sh
stelion workspace commit -m <message> [FILTER OPTIONS] [--dry-run]
```

### `stelion workspace push`

Push the current branch to a remote in each project.

```sh
stelion workspace push [--remote origin] [--branch main] [FILTER OPTIONS] [--dry-run]
```

## Submodule Commands

### `stelion submodule sync`

Propagate a commit across all replicas of a dependency.

```sh
stelion submodule sync <dependency> [--from local|<superproject>|remote]
                                    [--no-commit] [--dry-run]
                                    [--manifest/-m PATH]
                                    [--remote origin] [--branch main]
```

| Option | Description | Default |
| ------ | ----------- | ------- |
| `--from` | Source replica: `local`, a superproject name, or `remote`. | `local` |
| `--no-commit` | Update submodule pointers without committing. | Off |
| `--manifest PATH` / `-m` | Path to workspace manifest. | `stelion.yml` |

## Comparison Commands

### `stelion compare tree`

Compare directory structures across projects.

```sh
stelion compare tree [--subtree/-s PATH] [--include GLOB] [--exclude-pattern GLOB]
                     [--instruction/-i FILE] [--format/-f FORMAT] [--output/-o FILE]
                     [--names/-n a,b] [--pattern/-p REGEX] [--git-only]
                     [--exclude/-e x,y] [--manifest PATH]
```

| Option | Description |
| ------ | ----------- |
| `--subtree PATH` / `-s` | Limit the scan to a subdirectory. |
| `--include GLOB` | Comma-separated glob patterns to include. |
| `--exclude-pattern GLOB` | Comma-separated glob patterns to exclude. |
| `--instruction FILE` / `-i` | Load comparison spec from a YAML instruction file. Mutually exclusive with target/filter options. |
| `--format FORMAT` / `-f` | Output format: `table` or `yaml`. Default: `table`. |
| `--output FILE` / `-o` | Save report to a file instead of printing. YAML files (`.yml`/`.yaml`) force YAML format. |
| `--names a,b` / `-n` | Comma-separated project names to include. |
| `--pattern REGEX` / `-p` | Regex pattern to match project names. |
| `--git-only` | Only projects with a git repository. |
| `--exclude x,y` / `-e` | Comma-separated project names to exclude. |
| `--manifest PATH` | Path to workspace manifest. Default: `stelion.yml`. |

### `stelion compare files`

Compare specific files across projects.

```sh
stelion compare files <paths...> [--granularity/-g survey|detail] [--reference/-r PROJECT]
                      [--instruction/-i FILE] [--format/-f FORMAT] [--output/-o FILE]
                      [--names/-n a,b] [--pattern/-p REGEX] [--git-only]
                      [--exclude/-e x,y] [--manifest PATH]
```

| Option | Description | Default |
| ------ | ----------- | ------- |
| `--granularity` / `-g` | `survey` (variant grouping) or `detail` (unified diffs). | `survey` |
| `--reference PROJECT` / `-r` | Reference project for detail-mode diffs. | None |
| `--instruction FILE` / `-i` | Load comparison spec from a YAML instruction file. Mutually exclusive with target/filter options. | None |
| `--format FORMAT` / `-f` | Output format: `table` or `yaml`. | `table` |
| `--output FILE` / `-o` | Save report to a file instead of printing. YAML files (`.yml`/`.yaml`) force YAML format. | None |
| `--names a,b` / `-n` | Comma-separated project names to include. | None |
| `--pattern REGEX` / `-p` | Regex pattern to match project names. | None |
| `--git-only` | Only projects with a git repository. | Off |
| `--exclude x,y` / `-e` | Comma-separated project names to exclude. | None |
| `--manifest PATH` | Path to workspace manifest. | `stelion.yml` |

### `stelion info`

Display version and platform diagnostics.

```sh
stelion info
```
