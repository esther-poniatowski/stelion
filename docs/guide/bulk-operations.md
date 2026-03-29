# Bulk Operations

When managing a multi-project workspace, routine git operations --- committing a
shared change, pushing all repositories, or running a diagnostic command ---
must be repeated in each project directory. The `stelion workspace` bulk commands
automate this by iterating over discovered projects and reporting per-project
outcomes.

## Commands

### exec

```sh
stelion workspace exec <command> [FILTER OPTIONS] [--dry-run] [--manifest PATH]
```

Run an arbitrary shell command in each project directory. The command is passed
to the shell (`sh -c`), so compound expressions and pipes work:

```sh
stelion workspace exec "git log --oneline -3"
stelion workspace exec "git stash list | head -5"
```

### commit

```sh
stelion workspace commit -m <message> [FILTER OPTIONS] [--dry-run] [--manifest PATH]
```

Stage tracked changes (`git add --update`) and commit with the given message.
Projects without a git repository or with a clean working tree are skipped
automatically. Untracked files are not staged --- use `exec "git add -A && git
commit -m '...'"` when untracked files must be included.

```sh
stelion workspace commit -m "chore: update CI configuration"
stelion workspace commit -m "build: bump dependency versions" --names stelion,morpha,glossa
```

### push

```sh
stelion workspace push [--remote origin] [--branch main] [FILTER OPTIONS] [--dry-run] [--manifest PATH]
```

Push the current branch to a remote in each project.

```sh
stelion workspace push
stelion workspace push --remote upstream --branch develop --git-only
```

## Filter Options

All bulk commands accept the same set of filter options to select a subset of
the discovered project inventory.

| Option | Description |
| --- | --- |
| `--names a,b,c` / `-n a,b,c` | Restrict to the named projects (comma-separated). Unknown names produce an error. |
| `--pattern REGEX` / `-p REGEX` | Match project names by Python regular expression (`re.search`). |
| `--git-only` | Only include projects that have a `.git` directory. |
| `--exclude x,y` / `-e x,y` | Exclude the named projects (comma-separated). |
| `--dry-run` | Preview planned operations without executing. |
| `--manifest PATH` | Path to `stelion.yml`. Defaults to `stelion.yml` in the current directory. |

Filters compose as an intersection: `--names a,b,c --git-only` selects only the
named projects that also have git. Projects are always processed in alphabetical
order.

If no filter is specified, all discovered projects are included.

## Output

Every bulk command prints a table with one row per project:

```
              exec: git log --oneline -1
┏━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Project    ┃ Status  ┃ Detail                               ┃
┡━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ architekta │ success │ 838983b docs: Rewrite project desc... │
│ glossa     │ success │ a1f2c3d feat: Add format command      │
│ morpha     │ failed  │ fatal: not a git repository           │
│ stelion    │ success │ d0b8141 docs: Add integration policy  │
└────────────┴─────────┴──────────────────────────────────────┘

exec: git log --oneline -1: 3 of 4 succeeded, 1 failed
```

Three statuses are possible:

| Status | Meaning |
| --- | --- |
| **success** | The operation executed and returned exit code 0. |
| **skipped** | The operation was not applicable (no git repo, clean working tree, or dry-run mode). |
| **failed** | The operation executed but returned a non-zero exit code. The error message is shown in the detail column. |

The CLI exits with code 0 if no project failed, and code 1 if any project
failed. Skipped projects are not counted as failures.

## Error Handling

Each project is processed independently. A failure in one project (e.g. a merge
conflict preventing a commit, or a rejected push) is recorded in the outcome
table but does not abort the remaining projects. This matches the behavior of
`stelion submodule sync`, where per-replica errors are captured without
short-circuiting the operation.

## Structured Operations vs. Generic exec

The `commit` and `push` commands provide validation that `exec` does not:

- **commit** checks for a git repository and a clean working tree before
  attempting the operation. Clean projects are skipped rather than producing a
  confusing "nothing to commit" error.
- **push** checks for a git repository before attempting the operation.

For operations beyond commit and push, use `exec` with the full shell command.
The structured commands exist for the most common workflows where validation and
clear skip-reporting improve the experience.

## Examples

Commit a shared change across all projects, excluding the workspace hub:

```sh
stelion workspace commit -m "chore: update license year" --exclude dev
```

Push all git-enabled projects whose names start with `s`:

```sh
stelion workspace push --pattern "^s" --git-only
```

Check the current branch across all projects:

```sh
stelion workspace exec "git branch --show-current"
```

Preview a bulk commit without executing:

```sh
stelion workspace commit -m "refactor: rename module" --dry-run
```
