<a id="module-stelion.cli"></a>

<a id="command-line-interface"></a>

# Command-Line Interface

Command-line interface for the stelion package.

Defines commands available via `python -m stelion` or `stelion` if installed as a script.

Top-level commands:

- `info`: Display diagnostic information.
- `workspace`: Multi-project workspace management.
- `submodule`: Submodule synchronization commands.
- `compare`: Cross-project comparison commands.

> **See also**
>
> `typer.Typer`
> : Library for building CLI applications: [https://typer.tiangolo.com/](https://typer.tiangolo.com/)

<a id="stelion.cli.cli_info"></a>

### stelion.cli.cli_info()

Display version and platform diagnostics.

<a id="stelion.cli.main_callback"></a>

### stelion.cli.main_callback(version=<typer.models.OptionInfo object>)

Root command for the package command-line interface.

* **Parameters:**
  **version** ([*bool*](https://docs.python.org/3/builtins/functions.html#bool)) – If `True`, print the package version and exit.
