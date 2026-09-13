# ugh-cloud

`ugh-cloud` is a Hermes Agent plugin for explicitly uploading skills from the active Hermes profile into reviewable GitHub pull requests under a per-agent namespace.

## Scope

The plugin supports:

- `/ugh skill upload <skill-id>`
- `/ugh skill upload all`
- `--to-agent <agent-name>` for a logical target agent
- one pull request per changed skill
- complete skill-directory uploads, including `SKILL.md`, references, templates, scripts, and assets
- deterministic add, patch, no-op, and explicit remove behavior

The plugin never modifies the curated `/skills/` catalog. It manages only `agents/<agent-name>/skills/` in the configured repository.

## Current status

The repository contains a working prototype. The next phase is a structure refactor that separates command parsing, skill discovery, synchronization planning, GitHub transport, and PR orchestration without changing the user-facing contract.

## Configuration

Configure the repository in the active Hermes profile:

    hermes config set plugins.entries.ugh-cloud.settings.github-repo owner/repository
    hermes config set plugins.entries.ugh-cloud.settings.agent-name Lyla

Optional exclusions:

    hermes config set plugins.entries.ugh-cloud.settings.exclude '["private/*"]'

Store the token outside normal configuration:

    UGH_CLOUD_GITHUB_TOKEN=github_pat_...

Required GitHub permissions are Contents: Read and write and Pull requests: Read and write.

## Repository model

    skills/<category>/<skill-id>/                 # curated/shared catalog; manual only
    agents/<agent-name>/skills/<category>/<id>/   # per-agent snapshots; plugin managed

## Development

Read `AGENTS.md` before changing code. Follow `ARCHITECTURE.md` for module boundaries. Use `CONTEXT.md` for current domain vocabulary and decisions; approved implementation work is tracked in GitHub Issues.

The user-facing behavior is defined by approved GitHub Issues and the command tests. Research evidence is under `.research/`.
