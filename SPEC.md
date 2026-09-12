# ugh-cloud Plugin Specification

Status: Draft specification

## Problem Statement

Hermes profiles create and maintain skills locally. The user wants a reviewable GitHub backup workflow that uploads skills from the active Hermes profile into a target agent namespace in the `ugh-cloud` repository. Different agents may use the same skill ID with different content, so skills must remain isolated per agent. The workflow must be explicit and user-invoked; it must not silently upload, merge, poll, or modify curated skills.

## Solution

Build a Hermes plugin named `ugh-cloud`.

The plugin exposes the user-invoked command:

    /ugh skill upload <skill-id> [--to-agent <agent-name>] [--force]
    /ugh skill upload all [--to-agent <agent-name>]
    /ugh skill upload <category>/<skill-id> --remove [--to-agent <agent-name>] [--force]

The active Hermes profile is the source. The target agent is either the value of `--to-agent` or the configured display name of the active profile. If the target agent does not have a local Hermes profile, it is still a valid logical destination and the plugin creates its repository directory.

The plugin compares each source skill with the corresponding target-agent skill in GitHub and creates or updates one pull request per skill. The pull request targets `main`. The curated `/skills/` tree is never modified by this plugin.

## Repository Layout

The repository is organized as:

    ugh-cloud/
    ├── skills/
    │   └── <curated skills only>
    └── agents/
        └── <agent-name>/
            └── skills/
                └── <category>/
                    └── <skill-id>/
                        ├── SKILL.md
                        ├── references/
                        ├── templates/
                        ├── scripts/
                        └── assets/

`/skills/` is a manually curated/shared catalog and is out of scope for automatic upload.

`/agents/<agent-name>/skills/` contains the real per-agent skill snapshots. The category directory is preserved from the source profile.

## User Stories

1. As a Hermes user, I want to upload one skill explicitly, so that I can review it in GitHub before accepting it.
2. As a Hermes user, I want to upload all eligible skills from the active profile, so that I can back up a profile efficiently.
3. As a Hermes user, I want each changed skill to have its own pull request, so that skills can be reviewed and approved independently.
4. As a Hermes user, I want to send a skill from the active profile to a different logical agent, so that I can prepare another agent without switching profiles.
5. As a Hermes user, I want a target agent to exist only in GitHub, so that I can prepare its skills before creating its local Hermes profile.
6. As a Hermes user, I want the target agent name to appear in the PR title, so that the destination is obvious during review.
7. As a Hermes user, I want source profile information in the PR body, so that the origin of a skill is auditable.
8. As a Hermes user, I want a skill's category preserved, so that the repository remains navigable and duplicate IDs across categories remain unambiguous.
9. As a Hermes user, I want the complete skill directory uploaded, so that references, templates, scripts, and assets are not lost.
10. As a Hermes user, I want target-only skills left untouched during `all`, so that uploading from one profile does not delete unrelated target-agent skills.
11. As a Hermes user, I want unchanged content to be treated as success without a new commit, so that repeated uploads are idempotent.
12. As a Hermes user, I want an existing open PR updated when local content changes, so that repeated uploads do not create duplicate PRs.
13. As a Hermes user, I want merged PRs with later changes to produce a new PR, so that GitHub history remains intact.
14. As a Hermes user, I want closed unmerged PRs treated as history and not reopened, so that previous review decisions remain preserved.
15. As a Hermes user, I want conflicts reported without automatic resolution, so that I remain responsible for resolving review conflicts.
16. As a Hermes user, I want excluded skills protected from accidental upload, so that broad `all` operations remain controlled.
17. As a Hermes user, I want explicit `--force` confirmation to override an exclusion, so that exceptional uploads are deliberate.
18. As a Hermes user, I want suspicious secret files reported before upload, so that I can consciously decide whether exceptional content belongs in the PR.
19. As a Hermes user, I want GitHub credentials kept out of ordinary configuration and source files, so that the plugin does not expose the token.
20. As a Hermes user, I want no polling or webhook integration, so that the plugin stops after creating or updating the requested PRs.
21. As a Hermes user, I want duplicate skill IDs to require a qualified category/skill ID, so that the plugin never chooses an ambiguous source silently.
22. As a Hermes user, I want `all` to continue processing independent skills when one skill fails, so that one conflict or API error does not discard the whole batch.

## Command Contract

### Upload one skill

    /ugh skill upload <skill-id>

The skill ID may be a simple ID when unique in the active profile, or a qualified ID such as:

    /ugh skill upload software-development/computer-use

If a simple ID matches multiple categories, the command stops and lists the qualified choices.

### Upload to another agent

    /ugh skill upload computer-use --to-agent eve

The source remains the active profile. The target path is:

    agents/eve/skills/<category>/computer-use/

The PR title uses the target agent display name.

### Upload all

    /ugh skill upload all --to-agent eve

The plugin scans all skills in the active profile, applies configured exclusions, compares each skill independently, and creates at most one PR per changed skill. Skills that exist only in the target agent are not removed.

### Force

    /ugh skill upload <skill-id> --force

`--force` is per invocation. It does not change persistent exclusion configuration. It confirms exceptional upload of excluded or secret-warning content, after the plugin shows the affected paths and warnings.

## Pull Request Contract

### Actions

The action is determined by source-versus-target content:

- source exists, target absent: `add`
- source and target exist with different content: `patch`
- source and target content identical: successful no-op
- explicit removal workflow with target content present: `remove`
- `all` never removes target-only skills

### Titles

Use the target agent display name and singular `skill`:

    [Lyla] Request to add skill `computer-use`
    [Lyla] Request to patch skill `computer-use`
    [Lyla] Request to remove skill `computer-use`

### Commits

Use:

    chore(<agent-name>): <action> skill <skill-id>

Example:

    chore(eve): patch skill computer-use

### Branches

All pull requests target `main`. The deterministic branch format is:

    ugh-cloud/agents/<agent-name>/skills/<category>/<skill-id>

The target agent and skill identity determine branch reuse. Source profile is metadata, not branch identity.

### PR reuse

The logical identity of an upload is:

    (repository, target-agent, category, skill-id)

For an existing open PR with that identity:

- content differs: update the existing branch/PR
- content is identical: return successful no-op
- branch update has a conflict: stop and report the PR; do not force-push or resolve automatically

For a merged PR:

- content identical: successful no-op
- content differs: create a new branch/PR

For a closed, unmerged PR:

- leave the old PR unchanged
- create a new branch/PR
- include a link to the old PR when available

## PR Body

Every PR body includes:

    Source profile: <active profile>
    Target agent: <target agent>
    Skill: <category>/<skill-id>
    Action: add|patch|remove
    Command: <invoked command>

    Files:
    - SKILL.md
    - references/...
    - templates/...
    - scripts/...
    - assets/...

    Generated by: ugh-cloud
    Force upload: yes|no

The body may additionally include content checksums and the previous PR URL for traceability.

## Configuration and Secrets

The plugin configuration contains non-secret settings:

- `github-repo`: target repository in `owner/repository` form
- `agent-name`: display name for the active profile; if empty, fall back to the active profile name
- `exclude`: list of skill paths or glob patterns excluded from upload

The GitHub fine-grained Personal Access Token is not stored in `config.yaml`, the plugin manifest, the repository, or PR body. It is read from the profile secret mechanism or environment variable `UGH_CLOUD_GITHUB_TOKEN`.

Required GitHub permissions are limited to:

- Contents: Read and write
- Pull requests: Read and write

## Safety Rules

- Only the active profile's local skills are source input.
- `--to-agent` changes the destination only; it does not change the source profile.
- Only `agents/<target-agent>/skills/` is managed.
- `/skills/` is never changed by this plugin.
- Target-only skills are never removed by `all`.
- The plugin must reject path traversal and paths outside the active profile skill root.
- The plugin must detect and display likely secret files before upload.
- `--force` is required to proceed after an exclusion or secret warning, according to the approved workflow.
- The plugin must not force-push, merge PRs, poll PR status, or use webhooks.

## Implementation Decisions

- Implement as a profile-local Hermes plugin with `plugin.yaml` and `register(ctx)`.
- Register one user-invoked `ugh` command that parses `skill upload` arguments.
- Use the active Hermes home/profile for source discovery.
- Preserve category and copy the complete skill directory.
- Use GitHub REST API rather than requiring a local clone. If the repository has no commits, initialize the configured default branch (`main` for the agreed workflow) with a minimal `.gitkeep` commit through GitHub's Contents API before creating the skill branch; skill content must still enter through a pull request.
- Use deterministic target paths, branch names, titles, and commit messages.
- Compare complete directory content, not only `SKILL.md`.
- Keep PR creation/update independent per skill so batch failures do not abort unrelated uploads.
- Keep curated skills and per-agent snapshots separate.
- Use JSON string results at the Hermes tool/command boundary and convert expected failures into readable error results.

## Testing Decisions

Tests should verify external behavior rather than implementation details:

- command parsing for one skill, qualified IDs, `all`, `--to-agent`, and `--force`
- fallback from configured agent name to active profile name
- discovery of categories and complete skill directories
- rejection of ambiguous simple skill IDs
- exclusion handling and per-command force behavior
- secret-warning behavior
- add, patch, no-op, and explicit remove decisions
- target-only skills remaining untouched during `all`
- deterministic target paths, branch names, titles, and commit messages
- reuse of an open PR when content differs
- no-op success for identical open, merged, or current content
- new PR behavior after merged or closed-unmerged PRs
- conflict reporting without force-push
- independent handling of failures in `all`
- GitHub API error handling without leaking tokens
- path traversal and out-of-root protection

GitHub API calls should be tested through a fake HTTP transport or mock server. Tests must not require a real token, repository, or network access.

Before claiming completion, run:

    hermes plugins doctor "$HERMES_HOME/plugins/ugh-cloud" --ci
    hermes plugins list

Then exercise the command with a fake GitHub transport or a dry-run test fixture. A real GitHub PR should only be created after the user provides and confirms repository credentials.

## Out of Scope

- automatic hooks after skill creation
- automatic upload without `/ugh skill upload`
- polling GitHub PRs
- GitHub webhooks
- automatic merge or approval
- automatic conflict resolution
- force-pushing over remote changes
- modifying the curated `/skills/` catalog
- promoting a profile skill into `/skills/`
- deleting target-only skills during `all`
- synchronizing other Hermes profiles as source without an explicitly added source-profile feature
- storing or exposing GitHub tokens in ordinary configuration

## Further Notes

The first implementation should preserve the exact user-facing command and PR naming contract. The unresolved design detail is the final local mechanism for supplying `github-repo` and the token through the installed Hermes plugin settings/secret system; this must be verified against the current Hermes plugin configuration API before final implementation.
