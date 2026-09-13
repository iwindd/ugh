# Release

The canonical plugin version is `version` in `plugin.yaml`. Keep release tags in the form `vX.Y.Z` and move shipped entries from `Unreleased` into a dated version section before creating the release.

Before a release:

1. Run `python -m py_compile __init__.py command.py config.py domain/*.py skills/*.py github/*.py orchestration/*.py tests/*.py`.
2. Run `python -m unittest discover -s tests -v`.
3. Run `hermes plugins doctor . --ci`.
4. Review the staged diff for credentials and generated artifacts.
5. Create exactly one immutable version tag only after the release commit is reviewed.
6. Build a source archive from that tag, inspect its contents for secrets and generated artifacts, and publish the archive plus its SHA-256 checksum as release assets.
7. Create the GitHub Release as a draft for maintainer review. Publish it only after the assets, checksum, notes, tag, and commit have been read back and approved.

The release notes must document the Hermes-native installation and update commands. Use `hermes plugins install owner/repo --ref <40-character-commit-sha>` for reproducible pinning and `hermes plugins update <plugin-name>` for a managed update. Do not add a custom updater, polling, auto-enable, auto-restart, PyPI package, or release credential to CI.

Package publishing and automated release workflows are deferred until the distribution surface is defined.
