# Cross-Project Comparison

Stelion's comparison commands let you survey how directory structures and file
contents differ across projects. Unlike standard diff tools, they operate on
N projects simultaneously, infer file correspondences by similarity, and
produce reports with per-project presence information.

## Commands

### `stelion compare tree`

Compare the directory structure of selected projects.

```sh
stelion compare tree [--subtree PATH] [--include GLOB] [--exclude-pattern GLOB] [FILTERS]
```

| Option | Effect |
| --- | --- |
| `--subtree PATH` | Limit the scan to a subdirectory (e.g. `src/`, `docs/`) |
| `--include GLOB` | Comma-separated glob patterns for files to include (e.g. `*.py,*.toml`) |
| `--exclude-pattern GLOB` | Comma-separated glob patterns to exclude (e.g. `__pycache__,*.pyc`) |

Directories are matched first at each depth level, then files within matched
directories. This means a directory rename like `docs/guide/` to `docs/guides/`
appears as a single directory-level correspondence, not a list of unrelated fuzzy
file matches.

At each level, matching proceeds in three passes:

1. **Exact** --- identical names.
2. **Case-insensitive** --- same name modulo case.
3. **Fuzzy** --- similar names via `difflib.SequenceMatcher` (threshold: 0.6).

Each matched node reports which projects it is **present in** and which it is
**absent from**. There is no single status label --- a file may appear in any
subset of the selected projects.

#### Example

```sh
stelion compare tree --names architekta,morpha,glossa --subtree docs/
```

Output:

```text
                Architecture Comparison (docs/)
┌──────────────┬──────┬────────────┬────────┬────────┬───────┬────────────┐
│ Path         │ Type │ architekta │ morpha │ glossa │ Match │ Similarity │
├──────────────┼──────┼────────────┼────────┼────────┼───────┼────────────┤
│ docs/guide   │ dir  │     ✓      │   ✓    │   ✓    │ exact │            │
│ docs/adr     │ dir  │     ✓      │   ✓    │   ✗    │ exact │            │
│ docs/conf.py │ file │     ✓      │   ✓    │   ✓    │ exact │            │
└──────────────┴──────┴────────────┴────────┴────────┴───────┴────────────┘

Summary: 3 nodes — 2 in all, 1 in some, 0 unique  (2 dirs, 1 files)
```

### `stelion compare files`

Compare the contents of specific files across projects.

```sh
stelion compare files <paths...> [--granularity survey|detail] [FILTERS]
```

| Option | Effect |
| --- | --- |
| `<paths...>` | One or more relative file paths to compare |
| `--granularity survey` | (Default) Group projects by content identity, report pairwise similarity |
| `--granularity detail` | Unified diffs against a reference project (requires `--reference`) |
| `--reference PROJECT` | Reference project for detail-mode diffs |

The comparison strategy depends on the file type:

**Structured files** (`.toml`, `.yaml`, `.yml`, `.json`): Parsed into nested
dictionaries and compared field by field using dotted paths (e.g.
`project.version`, `tool.pytest.ini_options.testpaths`). Each field shows its
value per project, with absent fields marked explicitly.

**Unstructured files** (Markdown, plain text, etc.): In `survey` mode (default),
compared by **variant grouping** --- projects with identical content are grouped
together. Pairwise similarity scores show how much content diverges between
groups. In `detail` mode, unified diffs are computed from the `--reference`
project to every other project.

#### Example: structured comparison

```sh
stelion compare files pyproject.toml --names architekta,morpha
```

Output:

```text
╭─ pyproject.toml — differs ───────────────────────────────────╮
│ Field                │ architekta │ morpha                    │
│ project.name         │ architekta │ morpha                    │
│ project.version      │ 0.0.0      │ 0.0.0                    │
│ project.requires-py… │ >=3.12     │ >=3.12                   │
│ project.dependencies │ [grayskul… │ [pyyaml, …]              │
╰──────────────────────────────────────────────────────────────╯

Summary: 1 files — 0 identical, 1 different, 0 errors
```

#### Example: unstructured comparison

```sh
stelion compare files README.md --names architekta,morpha,glossa
```

Output:

```text
╭─ README.md — differs ─────────────────────────────────╮
│   Group 1: architekta (45 lines)                      │
│   Group 2: glossa (52 lines)                          │
│   Group 3: morpha (38 lines)                          │
│                                                       │
│   architekta ↔ glossa: 62.3%                          │
│   architekta ↔ morpha: 58.1%                          │
│   glossa ↔ morpha: 71.5%                              │
╰───────────────────────────────────────────────────────╯
```

#### Example: detail mode with reference

```sh
stelion compare files README.md --granularity detail --reference architekta --names architekta,morpha,glossa
```

Output:

```text
╭─ README.md — differs ───────────────────────────────────────╮
│ Reference: architekta                                       │
│                                                             │
│ architekta -> morpha                                        │
│ --- architekta                                              │
│ +++ morpha                                                  │
│ @@ -1,2 +1,2 @@                                            │
│  # Shared Title                                             │
│ -Architekta specific.                                       │
│ +Morpha specific.                                           │
│                                                             │
│ architekta -> glossa                                        │
│ (no changes)                                                │
│                                                             │
│ Similarities:                                               │
│ architekta ↔ glossa: 100.0%                                 │
│ architekta ↔ morpha: 78.3%                                  │
│ glossa ↔ morpha: 78.3%                                      │
╰─────────────────────────────────────────────────────────────╯
```

## Shared Options

Both commands share the project filter options used by bulk commands:

| Option | Effect |
| --- | --- |
| `--names a,b,c` | Restrict to named projects |
| `--pattern REGEX` | Match project names by regular expression |
| `--git-only` | Only projects with a git repository |
| `--exclude x,y` | Exclude named projects |
| `--format table` | (Default) Rich terminal table |
| `--format yaml` | Machine-parseable YAML output |
| `--instruction FILE` | Load comparison spec from a YAML instruction file |
| `--manifest PATH` | Path to workspace manifest (default: `stelion.yml`) |

At least 2 projects must be selected for comparison.

## Instruction Files

For complex comparisons, write a declarative YAML instruction file instead of
passing many CLI options. Use `--instruction FILE` to load it.

When `--instruction` is provided, it is the **sole source of truth** --- it is
mutually exclusive with target and filter CLI options.

### Tree mode

```yaml
projects: [architekta, morpha, glossa]

mode: tree
tree:
  subtree: src/
  include_patterns: ["*.py", "*.toml"]
  exclude_patterns: ["__pycache__", "*.pyc"]
```

### File mode

```yaml
projects: [architekta, morpha, glossa]

mode: files
files:
  granularity: survey
  entries:
    - canonical: pyproject.toml
      selectors: [project.name, project.version, project.dependencies]
    - canonical: README.md
    - canonical: .vscode/settings.json
      overrides:
        glossa: .vscode/project-settings.json
      parser_hint: json
```

For detail mode with a reference project:

```yaml
projects: [architekta, morpha, glossa]

mode: files
files:
  granularity: detail
  reference: architekta
  entries:
    - canonical: README.md
    - canonical: CONTRIBUTING.md
```

### Entry fields

| Field | Required | Description |
| --- | --- | --- |
| `canonical` | yes | Standard relative path for this file |
| `overrides` | no | `{project: actual_path}` for projects with a different filename |
| `selectors` | no | Dotted field paths to compare (empty = all fields) |
| `parser_hint` | no | Force a parser regardless of extension (e.g. `toml`, `yaml`, `json`) |

## Output Formats

### Terminal (default)

Rich tables and panels rendered to the terminal. Tree comparisons show a table
with presence indicators per project. File comparisons show per-file panels with
field-level or variant-level details.

### YAML (`--format yaml`)

Machine-parseable YAML written to stdout. Includes the full report structure:
matches, summaries, field diffs, variant groups, and pairwise similarities.

```sh
stelion compare tree --names architekta,morpha --format yaml > tree-report.yml
stelion compare files pyproject.toml --names architekta,morpha --format yaml > file-report.yml
```

## Error Handling

- **Missing files**: If a file cannot be read in one project, the error is
  recorded as an issue on the result. Other files and projects continue
  normally.
- **Parse errors**: If a structured file has invalid syntax, the parse error is
  recorded and the file is skipped for that project.
- **Fewer than 2 projects**: The command exits with an error if fewer than 2
  projects match the filters.
- **Conflicting options**: Providing `--instruction` together with target or
  filter options produces an error listing the conflicting options.
