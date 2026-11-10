# CLI Reference

## Global Options

```
stelion [OPTIONS] COMMAND [ARGS]
```

| Option | Description |
| ------ | ----------- |
| `--version` / `-v` | Display the version and exit. |
| `--help` | Display the help message and exit. |

## Root and Settings File

Every command that reads the settings of a workspace takes two options:

| Option | Description |
| ------ | ----------- |
| `--root PATH` / `-r` | Root of the workspace: the folder from which Stelion finds its settings file and resolves the paths written in that file. |
| `--config PATH` / `-c` | Settings file. A file named by this option must exist. |

The root is the first of these answers: the option `--root`; the environment variable
`STELION_ROOT`; the nearest ancestor of the current folder that holds `stelion.yml`, in
`config/tools/` or at its own level; the current folder. A command can therefore run from any
subfolder of the workspace.

The settings file is `config/tools/stelion.yml` or `stelion.yml` below the root. When both exist,
the command stops with status 2 and names both files. Without any settings file, Stelion runs on
its canonical defaults. A path written in the settings file is relative to the root, so the file
moves between the root and `config/tools/` without an edit. A path given on the command line is
relative to the current folder.

## Exit Statuses

| Status | Meaning |
| ------ | ------- |
| 0 | Success. |
| 1 | A check found a problem (drift for `workspace status`), an operation failed in a project, or a confirmation was declined. |
| 2 | A usage or configuration error: an unknown option or value, an absent or invalid settings file, two competing settings files, or a confirmation required without a terminal and without `--yes`. |

## Workspace Commands

### `stelion workspace render-manifest`

Compose canonical defaults with a consumer overlay, validate the complete manifest and write it to the selected output.

```sh
stelion workspace render-manifest OVERLAY [--output/-o PATH] [--root/-r PATH] [--dry-run]
```

| Option | Description | Default |
| ------ | ----------- | ------- |
| `--output PATH` / `-o` | File that receives the complete manifest. The manifest is derived from the overlay, so an existing file is overwritten. | Standard output |
| `--root PATH` / `-r` | Root of the workspace that the manifest configures; it supplies the path-derived defaults, such as the workspace name, when the output is staged elsewhere. | Resolved root |
| `--dry-run` | Print the complete manifest without writing it. | Off |

### `stelion workspace init`

Initialize or regenerate a workspace. Without a settings file, the command writes `stelion.yml` at the root, with auto-discovered projects and consumer-agnostic defaults. With a settings file, the command generates all workspace artifacts.

```sh
stelion workspace init [--root/-r PATH] [--config/-c PATH] [--dry-run]
```

### `stelion workspace sync`

Re-scan projects and update generated files. The generated files are derived, so the command
overwrites each one whose content changes, and leaves the others untouched.

```sh
stelion workspace sync [--root/-r PATH] [--config/-c PATH] [--target/-t TARGET] [--dry-run]
```

| Option | Description | Default |
| ------ | ----------- | ------- |
| `--target TARGET` / `-t` | Limit to a single artifact (`workspace-file`, `projects`, `dependencies`, `environment`). | All |
| `--dry-run` | Show the drift without writing. | Off |

### `stelion workspace new`

Bootstrap a new project from the template: copy, substitute placeholders, rename
directories, and optionally initialize git.

```sh
stelion workspace new <name> "<description>" [--root/-r PATH] [--config/-c PATH] [--parent PATH] [--no-git] [--dry-run]
```

| Option | Description | Default |
| ------ | ----------- | ------- |
| `--parent PATH` | Folder that receives the new project, read from the current folder. It must be one of the discovery scan directories, so that the new project stays discoverable. | First scan directory |
| `--no-git` | Skip `git init`. | Off |
| `--dry-run` | Show the target folder without writing. | Off |

The command never overwrites an existing folder: a target that exists stops it with an error.

### `stelion workspace register`

Register an existing project and regenerate workspace artifacts. If the project sits
outside the configured scan roots, stelion records it in `discovery.extra_paths` and rewrites the
settings file in canonical form, which drops its comments. Before that rewrite, the command asks
for a confirmation on a terminal; `--yes` answers it, and without a terminal and without `--yes`
the command stops with status 2.

```sh
stelion workspace register <path> [--root/-r PATH] [--config/-c PATH] [--yes]
```

### `stelion workspace status`

Show which generated files are out of date. Exit code 0 if all current, 1 if drift
detected.

```sh
stelion workspace status [--root/-r PATH] [--config/-c PATH]
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
| `--root PATH` / `-r`, `--config PATH` / `-c` | Root and settings file (see [Root and Settings File](#root-and-settings-file)). |

The bulk commands perform the action that the command line states (a shell command, a commit of
the tracked changes, a push), so they ask for no confirmation.

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
                                    [--root/-r PATH] [--config/-c PATH]
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
stelion compare tree [--subtree/-s PATH] [--include GLOB] [--exclude-pattern GLOB]
                     [--instruction/-i FILE] [--format text|yaml] [--output/-o FILE]
                     [--names/-n a,b] [--pattern/-p REGEX] [--git-only]
                     [--exclude/-e x,y] [--root/-r PATH] [--config/-c PATH]
```

| Option | Description |
| ------ | ----------- |
| `--subtree PATH` / `-s` | Limit the scan to a subdirectory. |
| `--include GLOB` | Comma-separated glob patterns to include. |
| `--exclude-pattern GLOB` | Comma-separated glob patterns to exclude. |
| `--instruction FILE` / `-i` | Load comparison spec from a YAML instruction file. Mutually exclusive with target/filter options. |
| `--format FORMAT` | Format of the report: `text` or `yaml`. Default: `text`. |
| `--output FILE` / `-o` | Save report to a file instead of printing. YAML files (`.yml`/`.yaml`) force YAML format. |
| `--names a,b` / `-n` | Comma-separated project names to include. |
| `--pattern REGEX` / `-p` | Regex pattern to match project names. |
| `--git-only` | Only projects with a git repository. |
| `--exclude x,y` / `-e` | Comma-separated project names to exclude. |

### `stelion compare files`

Compare specific files across projects.

```sh
stelion compare files <paths...> [--granularity/-g survey|detail] [--reference PROJECT]
                      [--instruction/-i FILE] [--format text|yaml] [--output/-o FILE]
                      [--names/-n a,b] [--pattern/-p REGEX] [--git-only]
                      [--exclude/-e x,y] [--root/-r PATH] [--config/-c PATH]
```

| Option | Description | Default |
| ------ | ----------- | ------- |
| `--granularity` / `-g` | `survey` (variant grouping) or `detail` (unified diffs). | `survey` |
| `--reference PROJECT` | Reference project for detail-mode diffs. | None |
| `--instruction FILE` / `-i` | Load comparison spec from a YAML instruction file. Mutually exclusive with target/filter options. | None |
| `--format FORMAT` | Format of the report: `text` or `yaml`. | `text` |
| `--output FILE` / `-o` | Save report to a file instead of printing. YAML files (`.yml`/`.yaml`) force YAML format. | None |
| `--names a,b` / `-n` | Comma-separated project names to include. | None |
| `--pattern REGEX` / `-p` | Regex pattern to match project names. | None |
| `--git-only` | Only projects with a git repository. | Off |
| `--exclude x,y` / `-e` | Comma-separated project names to exclude. | None |

### `stelion info`

Display version and platform diagnostics.

```sh
stelion info
```
