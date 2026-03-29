# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- **Submodule synchronization**: New `stelion submodule sync` command that
  propagates a commit across all replicas of a dependency (local clone,
  superproject submodule pointers, and remote). Supports three source modes
  (`--from local`, `--from <superproject>`, `--from remote`), dry-run
  inspection, and optional auto-commit. Per-action error resilience ensures
  failures in one replica do not abort the rest.
