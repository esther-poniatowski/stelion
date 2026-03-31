# CLI Reference

## Global Options

```
stelion [OPTIONS] COMMAND [ARGS]
```

| Option | Description |
| ------ | ----------- |
| `--version` | Display the version and exit. |
| `--help` | Display the help message and exit. |

## Workspace Commands

### `stelion workspace init`

Initialize or regenerate a workspace. Generates `stelion.yml` with auto-discovered
projects when no manifest exists. With an existing manifest, generates all workspace
artifacts.

```sh
stelion workspace init [--manifest PATH] [--dry-run]
```

### `stelion workspace sync`

Re-scan projects and update generated files.

```sh
stelion workspace sync [--target TARGET] [--force] [--dry-run]
```

| Option | Description | Default |
| ------ | ----------- | ------- |
| `--target TARGET` | Limit to a single artifact (`workspace-file`, `projects`, `dependencies`, `environment`). | All |
| `--force` | Overwrite even if up to date. | Off |

### `stelion workspace new`

Bootstrap a new project from the template: copy, substitute placeholders, rename
directories, and optionally initialize git.

```sh
stelion workspace new <name> "<description>" [--destination ROOT] [--no-git] [--dry-run]
```

### `stelion workspace register`

Register an existing project and regenerate workspace artifacts. If the project sits
outside the configured scan roots, stelion records it in `discovery.extra_paths`.

```sh
stelion workspace register <path>
```

### `stelion workspace status`

Show which generated files are out of date. Exit code 0 if all current, 1 if drift
detected.

```sh
stelion workspace status
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
                                    [--remote origin] [--branch main]
```

| Option | Description | Default |
| ------ | ----------- | ------- |
| `--from` | Source replica: `local`, a superproject name, or `remote`. | `local` |
| `--no-commit` | Update submodule pointers without committing. | Off |

## Comparison Commands

### `stelion compare tree`

Compare directory structures across projects.

```sh
stelion compare tree [--subtree PATH] [--include GLOB] [--exclude-pattern GLOB] [FILTERS]
```

| Option | Description |
| ------ | ----------- |
| `--subtree PATH` | Limit the scan to a subdirectory. |
| `--include GLOB` | Comma-separated glob patterns to include. |
| `--exclude-pattern GLOB` | Comma-separated glob patterns to exclude. |

### `stelion compare files`

Compare specific files across projects.

```sh
stelion compare files <paths...> [--granularity survey|detail] [--reference PROJECT] [FILTERS]
```

| Option | Description | Default |
| ------ | ----------- | ------- |
| `--granularity` | `survey` (variant grouping) or `detail` (unified diffs). | `survey` |
| `--reference PROJECT` | Reference project for detail-mode diffs. | None |
| `--format table\|yaml` | Output format. | `table` |
| `--instruction FILE` | Load comparison spec from a YAML instruction file. | None |

### `stelion info`

Display version and platform diagnostics.

```sh
stelion info
```
