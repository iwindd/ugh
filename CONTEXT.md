# Domain Context

## Purpose

`ugh-cloud` is a Hermes plugin that uploads skills from the active Hermes profile into per-agent paths in a GitHub repository through explicit, reviewable pull requests.

## Vocabulary

- Source: the active Hermes profile at command invocation time.
- Target agent: the logical destination selected by `--to-agent`, or the configured active agent name.
- Skill identity: `<category>/<skill-id>`.
- Curated catalog: remote `skills/`; never managed by this plugin.
- Agent snapshot: remote `agents/<agent>/skills/`; managed by this plugin.

## Accepted behavior

- The user invokes `/ugh skill upload`; there is no automatic post-creation upload.
- One changed skill produces at most one pull request.
- `all` is additive: target-only skills remain untouched.
- Identical content is a successful no-op.
- Conflicts are reported for the user to resolve; the plugin never force-pushes or resolves them automatically.
- GitHub Issues are the source of truth for approved implementation work.

## Current implementation seams

`command.py` parses the command, `config.py` reads plugin settings, `skills/` owns local discovery/snapshot/safety, `domain/` owns pure decisions, `github/` owns the remote adapter, and `orchestration/` owns the upload use case.

## Open decisions

- Whether to split the GitHub adapter into separate transport, Git Data, pull-request, and bootstrap modules.
- Whether to publish a package or keep the plugin profile-local.

Update this file when domain vocabulary or accepted decisions change. Put repository-wide rules in `AGENTS.md`, stable structure in `ARCHITECTURE.md`, and executable work in GitHub Issues.
