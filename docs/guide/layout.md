# Repository Layout

The command `stelion layout check` checks a repository against a layout that its consumer declares. Stelion imposes no layout: every area, kind, role, direction and path comes from the layout. Stelion ships default layouts, which a layout extends by name, and the schema of the format.

## 1. Layout

A layout is a YAML file of format `stelion:layout@1`, published as the JSON Schema [layout.schema.json](../../src/stelion/schemas/layout.schema.json). Every pattern is a glob anchored at the root of the repository: `**` as a whole segment matches any number of folders, `*` any text without `/`, and `?` one character other than `/`. A path lies within a glob when the path, or one of its folders, matches it.

A layout holds these sections, each optional:

| Section | Declares |
| --- | --- |
| `extends` | the layout that this layout completes: the name of a shipped layout, such as `project`, or a path relative to this file |
| `exclude` | the files outside every rule |
| `metadata` | the key of the metadata that names the role of a file, `role` by default |
| `areas` | each area by identifier, with the folder that holds it |
| `folders` | the kinds of folder: the glob of their folders, an optional condition on the metadata of a file of the folder, the kinds of file that they require, and the kind of their phases |
| `kinds` | the kinds of file: a pattern of their name, the files where the kind applies and those excepted, the kinds of folder that admit them, their role and their skeleton |
| `roles` | the roles admitted everywhere, the roles admitted in each area, and the areas that admit every role |
| `links` | the directions in which a file may not link, from one area into others |
| `retired` | the path prefixes that no file may hold, and that no text may store outside its records |
| `tree` | the entries admitted or required at the root, the files of given suffixes admitted only under given paths, the paths that Git must not track, and the largest size of a tracked file |

A layout merges over the layout that it extends. Entries with an `id`, and root entries by `name`, are merged by key, the extending layout replacing an entry of the same key. Lists of names are united, mappings are merged key by key, and a scalar replaces that of the base.

The shipped layout `project` holds the practices recommended for every project repository:

- its root entries;
- code under `src/` and `tests/`, and notebooks under `notebooks/`;
- `data/` and `config/local/` left untracked;
- a limit of 100 MiB per tracked file.

The shipped layout names no tool and no consumer.

## 2. Rules

Every finding has the level `error`. Its resource is the file, or the folder ending with `/`, relative to the root of the repository; its discriminator is the offending content.

| Identifier | Case |
| --- | --- |
| `folder/missing-kind` | a folder lacks a kind of file that its kind requires, both itself and in one of its phases |
| `kind/placement` | a file of a kind sits in a folder whose kind may not hold it |
| `kind/role` | a file of a kind declares another role than its kind |
| `kind/sections` | the level-2 headings of a file are no subsequence, in order, of the headings of its skeleton |
| `role/area` | a file declares a role that its area does not admit |
| `link/direction` | a file links into an area that its area may not link into |
| `path/retired` | a retired path exists, or a file outside its records stores it |
| `tree/unknown-root-entry` | a tracked root entry is absent from the layout |
| `tree/missing-root-entry` | a root entry that the layout requires is absent or untracked |
| `tree/misplaced` | a file of given suffixes lies outside the paths admitted for it, or in one of their exceptions |
| `tree/tracked` | Git tracks a path that the layout keeps untracked |
| `tree/oversized` | a tracked file exceeds the size limit of the layout |

A role that no area lists is admitted everywhere. A folder belongs to the first kind whose glob matches it, and a file to the first kind whose name pattern matches it. A link counts by the place that it names, whether or not a file exists there, so a broken link into a forbidden area is reported too.

The rules on files read the tracked files of the repository, or every file of a folder without Git. Three facts of a file come through the read package of Anagraphe, which owns their sources, their syntaxes and their resolution: its metadata, its links, and whether the shared exclusions of the repository leave it out. A file that the exclusions leave out escapes the rules on kinds, roles, links and retired paths, but not the rules of the tree. Anagraphe reads its configuration `anagraphe.yml` at the root of the check, in its subfolder `.config/`, or in its subfolder `config/`. A root that holds no such file is read without shared exclusions, and a root that holds the file at two of these places stops the check with status 2.

## 3. Command

```sh
stelion layout check --layout layout.yml
stelion layout check --layout specs/project.layout.yml --root projects/a-project --format sarif --output build/layout.sarif
```

The root is the folder given by `--root`, or by the environment variable `STELION_ROOT`, or the current folder. The option `--format` takes `text`, the default, or `sarif`, which writes a findings log in the profile of the gate Elenchos.

The exit status is 0 without finding, 1 with findings, and 2 when the check cannot run on an unreadable or invalid layout, or on an invalid configuration of Anagraphe. With `--format sarif`, the log then holds a failed run that states why.

The command needs the extra `layout`, which installs the read package of Anagraphe and `jsonschema`: `pip install "stelion[layout]"`.
