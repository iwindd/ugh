# Architecture

## Purpose

`ugh-cloud` is a profile-local Hermes plugin. The user invokes `/ugh skill upload`; the plugin discovers skills from the active profile, plans a synchronization, and uses GitHub pull requests as the review boundary.

## Current structure

    ugh-cloud/
    ├── plugin.yaml
    ├── __init__.py                 # Hermes registration only
    ├── command.py                  # command parsing and result formatting
    ├── config.py                   # plugin context settings and source root
    ├── domain/
    │   ├── __init__.py
    │   ├── models.py                # immutable domain data types
    │   └── planning.py              # pure add/patch/no-op/remove decisions
    ├── skills/
    │   ├── __init__.py
    │   ├── discovery.py             # category-aware source discovery
    │   ├── snapshot.py              # complete skill-directory snapshots
    │   └── safety.py                # exclusions and secret warnings
    ├── github/
    │   ├── __init__.py              # public GitHub adapter boundary
    │   └── client.py                # authenticated REST, Git Data, and PR operations
    ├── orchestration/
    │   ├── __init__.py
    │   └── uploader.py              # upload use-case boundary
    ├── tests/
    │   └── test_local.py            # offline command smoke test
    ├── .research/                   # cited research evidence
    ├── CONTEXT.md                   # working domain context
    ├── docs/agents/                 # issue tracker and context consumer rules
    ├── AGENTS.md
    ├── ARCHITECTURE.md
    └── README.md

## Dependency direction

    plugin entry point
        -> command
        -> orchestration
            -> domain
            -> skills
            -> github adapter

`domain/` and `skills/` do not import Hermes APIs or perform network calls. `github/` owns authentication, HTTP, Git Data operations, pull-request lifecycle, bootstrap, and remote errors. `command.py` is the only boundary that reads raw Hermes command input and context. `orchestration/` coordinates the use case without becoming a second command parser.

## Core invariants

- The active Hermes profile is the only local source.
- `--to-agent` selects the destination, never the source.
- Skill identity preserves `<category>/<skill-id>`.
- The curated remote `skills/` catalog is never modified.
- Only `agents/<target>/skills/` is managed.
- `all` is additive and never deletes target-only skills.
- Identical content is a successful no-op.
- One changed skill creates or updates at most one pull request.
- Tokens stay in the active profile secret/environment mechanism.
- No force-push, auto-merge, polling, webhook, or automatic conflict resolution.

## Test seams

- `domain.planning.action_for` is pure and deterministic.
- `skills.discovery` can run against a temporary profile tree.
- `skills.snapshot` and `skills.safety` can be tested without a network or token.
- `command.handle_ugh` accepts a fake context and an injected upload boundary.
- `github.client` is the external side-effect boundary and must be replaced by a fake transport for API tests.

## Documentation ownership

- `AGENTS.md`: compact repository rules, triggers, and completion gates.
- `CONTEXT.md`: evolving vocabulary, accepted decisions, and unresolved questions.
- GitHub Issues: approved implementation work and acceptance criteria.
- `.research/`: cited evidence and recommendations, not runtime requirements.
- `docs/adr/`: durable decisions that are difficult to reverse.
