# AGENTS.md

## Start here

Before changing this plugin, identify the work branch and read only the documents it triggers:

- Behavior or command contract change → read `CONTEXT.md` and the relevant GitHub Issue.
- Module placement or dependency change → read `ARCHITECTURE.md`.
- Hermes plugin API or registration change → read the Hermes plugin-development skill and the relevant official docs.
- GitHub API or token behavior change → read `.research/architecture-baseline.md` and verify the current GitHub documentation.

If a task triggers more than one branch, read all of its pointers before editing. Do not duplicate their content here.

## Working rules

1. Preserve the user-facing `/ugh skill upload` contract; approved behavior changes must be represented in the linked GitHub Issue before implementation.
2. Treat the active Hermes profile as the only source of local skills.
3. Treat `--to-agent` as the destination selector; never use it as a source selector.
4. Preserve category and the complete skill directory.
5. Manage only `agents/<target-agent>/skills/` in the remote repository.
6. Never modify the curated `skills/` catalog from this plugin.
7. Keep one pull request per changed skill, including when the user selects `all`.
8. Keep GitHub tokens in the profile secret/environment mechanism. Never place credentials in code, docs, tests, logs, or PR bodies.
9. Keep synchronization reviewable: no force-push, auto-merge, polling, webhook, or hidden upload.
10. Keep domain decisions pure and external effects behind injected boundaries.
11. Return actionable, redacted errors and isolate failures between skills in a batch.
12. Update tests and the relevant source-of-truth document when behavior changes.

## Done means

A change is complete only when:

- the relevant behavior is covered without requiring a real token or network;
- `python -m py_compile __init__.py command.py config.py domain/*.py skills/*.py github/*.py orchestration/*.py` passes;
- `python tests/test_local.py` passes;
- `hermes plugins doctor . --ci` passes;
- no generated artifacts or secrets are tracked; and
- the result matches the approved GitHub Issue, `CONTEXT.md`, and `ARCHITECTURE.md`.

Do not create real GitHub PRs as part of tests. Real remote verification is an explicit operator step after local checks pass.

## Change shape

Prefer a small vertical slice. For refactors, introduce the new seam, migrate callers while the old path still works, verify, then remove the old path. Keep `__init__.py` as plugin wiring; do not put command parsing, filesystem traversal, or GitHub requests there.

Use conventional commits:

    feat: ...
    fix: ...
    refactor: ...
    docs: ...
    test: ...
