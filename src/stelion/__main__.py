"""
Command-line entry point for the `stelion` package.

Usage
-----
To invoke the package::

    python -m stelion


See Also
--------
stelion.cli: Command-line interface module for the package.
"""
from .cli import app

app()
