<a id="workspace-adapters"></a>

# Workspace Adapters

CLI adapters exposing workspace use-cases as Typer commands.

<a id="module-stelion.workspace.adapters.commands"></a>

<a id="commands"></a>

## Commands

Typer command group for workspace management.

<a id="stelion.workspace.adapters.commands.workspace_init"></a>

### stelion.workspace.adapters.commands.workspace_init(manifest=<typer.models.OptionInfo object>, dry_run=<typer.models.OptionInfo object>)

Initialize or regenerate a workspace from its manifest.

* **Parameters:**
  * **manifest** (*Path*) – Path to the workspace manifest file.
  * **dry_run** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Preview actions without writing.

<a id="stelion.workspace.adapters.commands.workspace_sync"></a>

### stelion.workspace.adapters.commands.workspace_sync(manifest=<typer.models.OptionInfo object>, target=<typer.models.OptionInfo object>, dry_run=<typer.models.OptionInfo object>, force=<typer.models.OptionInfo object>)

Re-scan projects and update generated workspace files.

* **Parameters:**
  * **manifest** (*Path*) – Path to the workspace manifest file.
  * **target** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Single generation target to sync.
  * **dry_run** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Preview without writing.
  * **force** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Overwrite even if current.

<a id="stelion.workspace.adapters.commands.workspace_register"></a>

### stelion.workspace.adapters.commands.workspace_register(path=<typer.models.ArgumentInfo object>, manifest=<typer.models.OptionInfo object>)

Register an existing project into workspace artifacts.

* **Parameters:**
  * **path** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Path to the project directory.
  * **manifest** (*Path*) – Path to the workspace manifest file.

<a id="stelion.workspace.adapters.commands.workspace_new"></a>

### stelion.workspace.adapters.commands.workspace_new(name=<typer.models.ArgumentInfo object>, description=<typer.models.ArgumentInfo object>, manifest=<typer.models.OptionInfo object>, destination=<typer.models.OptionInfo object>, dry_run=<typer.models.OptionInfo object>, no_git=<typer.models.OptionInfo object>)

Bootstrap a new project from the template.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Project name (lowercase, underscores).
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – One-line project description.
  * **manifest** (*Path*) – Path to the workspace manifest file.
  * **destination** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Target discovery root relative to the manifest.
  * **dry_run** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Preview without writing.
  * **no_git** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Skip git init.

<a id="stelion.workspace.adapters.commands.workspace_status"></a>

### stelion.workspace.adapters.commands.workspace_status(manifest=<typer.models.OptionInfo object>)

Show which generated files are out of date.

* **Parameters:**
  **manifest** (*Path*) – Path to the workspace manifest file.

<a id="module-stelion.workspace.adapters.bulk_commands"></a>

<a id="bulk-commands"></a>

## Bulk Commands

Typer commands for bulk operations across workspace projects.

<a id="stelion.workspace.adapters.bulk_commands.workspace_exec"></a>

### stelion.workspace.adapters.bulk_commands.workspace_exec(command=<typer.models.ArgumentInfo object>, names=<typer.models.OptionInfo object>, pattern=<typer.models.OptionInfo object>, git_only=<typer.models.OptionInfo object>, exclude=<typer.models.OptionInfo object>, dry_run=<typer.models.OptionInfo object>, manifest=<typer.models.OptionInfo object>)

Run an arbitrary shell command in each project directory.

* **Parameters:**
  * **command** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Shell command to run in each project.
  * **names** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Comma-separated project names to include.
  * **pattern** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Regex pattern to match project names.
  * **git_only** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Only include projects with a git repository.
  * **exclude** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Comma-separated project names to exclude.
  * **dry_run** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Preview without executing.
  * **manifest** (*Path*) – Path to the workspace manifest.

<a id="stelion.workspace.adapters.bulk_commands.workspace_commit"></a>

### stelion.workspace.adapters.bulk_commands.workspace_commit(message=<typer.models.OptionInfo object>, names=<typer.models.OptionInfo object>, pattern=<typer.models.OptionInfo object>, git_only=<typer.models.OptionInfo object>, exclude=<typer.models.OptionInfo object>, dry_run=<typer.models.OptionInfo object>, manifest=<typer.models.OptionInfo object>)

Stage tracked changes and commit across projects.

* **Parameters:**
  * **message** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Commit message to use.
  * **names** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Comma-separated project names to include.
  * **pattern** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Regex pattern to match project names.
  * **git_only** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Only include projects with a git repository.
  * **exclude** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Comma-separated project names to exclude.
  * **dry_run** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Preview without executing.
  * **manifest** (*Path*) – Path to the workspace manifest.

<a id="stelion.workspace.adapters.bulk_commands.workspace_push"></a>

### stelion.workspace.adapters.bulk_commands.workspace_push(remote=<typer.models.OptionInfo object>, branch=<typer.models.OptionInfo object>, names=<typer.models.OptionInfo object>, pattern=<typer.models.OptionInfo object>, git_only=<typer.models.OptionInfo object>, exclude=<typer.models.OptionInfo object>, dry_run=<typer.models.OptionInfo object>, manifest=<typer.models.OptionInfo object>)

Push the current branch to a remote across projects.

* **Parameters:**
  * **remote** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Remote name to push to.
  * **branch** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Branch to push.
  * **names** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Comma-separated project names to include.
  * **pattern** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Regex pattern to match project names.
  * **git_only** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Only include projects with a git repository.
  * **exclude** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Comma-separated project names to exclude.
  * **dry_run** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Preview without executing.
  * **manifest** (*Path*) – Path to the workspace manifest.

<a id="module-stelion.workspace.adapters.comparison_commands"></a>

<a id="comparison-commands"></a>

## Comparison Commands

Typer commands for cross-project comparison.

<a id="stelion.workspace.adapters.comparison_commands.compare_tree"></a>

### stelion.workspace.adapters.comparison_commands.compare_tree(subtree=<typer.models.OptionInfo object>, include=<typer.models.OptionInfo object>, exclude_pattern=<typer.models.OptionInfo object>, names=<typer.models.OptionInfo object>, pattern=<typer.models.OptionInfo object>, git_only=<typer.models.OptionInfo object>, exclude=<typer.models.OptionInfo object>, instruction=<typer.models.OptionInfo object>, fmt=<typer.models.OptionInfo object>, output=<typer.models.OptionInfo object>, manifest=<typer.models.OptionInfo object>)

Compare directory structures across projects.

* **Parameters:**
  * **subtree** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Limit scan to a subdirectory.
  * **include** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Comma-separated include glob patterns.
  * **exclude_pattern** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Comma-separated exclude glob patterns.
  * **names** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Comma-separated project names to include.
  * **pattern** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Regex pattern to match project names.
  * **git_only** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Only include projects with a git repository.
  * **exclude** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Comma-separated project names to exclude.
  * **instruction** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Path to instruction YAML file.
  * **fmt** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Output format (`"table"` or `"yaml"`).
  * **output** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Save report to a file instead of printing.
  * **manifest** (*Path*) – Path to the workspace manifest.

<a id="stelion.workspace.adapters.comparison_commands.compare_files_cmd"></a>

### stelion.workspace.adapters.comparison_commands.compare_files_cmd(paths=<typer.models.ArgumentInfo object>, granularity=<typer.models.OptionInfo object>, reference=<typer.models.OptionInfo object>, names=<typer.models.OptionInfo object>, pattern=<typer.models.OptionInfo object>, git_only=<typer.models.OptionInfo object>, exclude=<typer.models.OptionInfo object>, instruction=<typer.models.OptionInfo object>, fmt=<typer.models.OptionInfo object>, output=<typer.models.OptionInfo object>, manifest=<typer.models.OptionInfo object>)

Compare specific files across projects.

* **Parameters:**
  * **paths** ([*list*](https://docs.python.org/3/library/stdtypes.html#list) *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Relative file paths to compare across projects.
  * **granularity** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Comparison granularity (`"survey"` or `"detail"`).
  * **reference** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Reference project for detail-mode diffs.
  * **names** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Comma-separated project names to include.
  * **pattern** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Regex pattern to match project names.
  * **git_only** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Only include projects with a git repository.
  * **exclude** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Comma-separated project names to exclude.
  * **instruction** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Path to instruction YAML file.
  * **fmt** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Output format (`"table"` or `"yaml"`).
  * **output** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *None*) – Save report to a file instead of printing.
  * **manifest** (*Path*) – Path to the workspace manifest.

<a id="module-stelion.workspace.adapters.submodule_commands"></a>

<a id="submodule-commands"></a>

## Submodule Commands

Typer command group for submodule operations.

<a id="stelion.workspace.adapters.submodule_commands.submodule_sync"></a>

### stelion.workspace.adapters.submodule_commands.submodule_sync(dependency=<typer.models.ArgumentInfo object>, from_source=<typer.models.OptionInfo object>, no_commit=<typer.models.OptionInfo object>, dry_run=<typer.models.OptionInfo object>, manifest=<typer.models.OptionInfo object>, remote=<typer.models.OptionInfo object>, branch=<typer.models.OptionInfo object>)

Propagate a commit across all replicas of a submodule dependency.

* **Parameters:**
  * **dependency** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the dependency to synchronize.
  * **from_source** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Sync source: `"local"`, `"remote"`, or a superproject name.
  * **no_commit** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Update submodule pointers without committing.
  * **dry_run** ([*bool*](https://docs.python.org/3/library/functions.html#bool)) – Preview updates without applying.
  * **manifest** (*Path*) – Path to the workspace manifest.
  * **remote** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Remote name (for remote origin).
  * **branch** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Branch name (for remote origin).
