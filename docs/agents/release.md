# Release

The canonical plugin version is `version` in `plugin.yaml`. Keep release tags in the form `vX.Y.Z` and keep `CHANGELOG.md` updated under `Unreleased` before a release.

Before a release:

1. Run `python -m py_compile __init__.py command.py config.py domain/*.py skills/*.py github/*.py orchestration/*.py tests/*.py`.
2. Run `python -m unittest discover -s tests -v`.
3. Run `hermes plugins doctor . --ci`.
4. Review the staged diff for credentials and generated artifacts.
5. Create an immutable version tag only after the user approves the release.

Package publishing and automated release workflows are deferred until the distribution surface is defined.
