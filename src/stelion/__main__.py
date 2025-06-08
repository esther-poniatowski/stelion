"""
Entry point for the `stelion` package, invoked as a module.

Usage
-----
To launch the command-line interface, execute::

    python -m stelion


See Also
--------
stelion.cli: Module implementing the application's command-line interface.
"""
from .cli import app

app()
