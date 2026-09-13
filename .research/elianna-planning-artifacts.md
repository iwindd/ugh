# Planning artifacts for `ugh-cloud`

Research date: 2026-09-13

Status: Recommendation for repository workflow; no source code, existing documentation, configuration, issues, or pull requests were modified.

## Executive recommendation

Use a two-stage workflow:

1. Keep exploratory and implementation-detail plans in a local, gitignored `.hermes/plans/` workspace. Hermes officially provides this destination for plan-mode artifacts, uses timestamped Markdown files, and explicitly separates planning from execution.[4][5]
2. Once a direction is accepted, convert the plan into one or more GitHub Issues and attach those issues to a small Project only if sequencing, ownership, status, or cross-issue visibility is useful. GitHub positions Issues for ideas, tasks, bugs, and discussion, while Projects supplies synchronized table/board/roadmap views over issues and pull requests.[7][8]
3. Promote only durable repository knowledge into tracked files: user-visible behavior into `SPEC.md`, stable boundaries/invariants into `ARCHITECTURE.md`, and an approved, active migration sequence into `REFACTOR-PLAN.md`. Do not make a transient execution plan a tracked root document merely because it is detailed.

For `ugh-cloud`, this preserves the current document split described by the repository while preventing speculative designs, abandoned alternatives, and task-by-task execution notes from increasing the default agent context. The existing `SPEC.md` and `REFACTOR-PLAN.md` are source-of-truth documents, not disposable scratch notes; their presence is justified when they contain accepted behavior and an active migration contract.

## Decision criteria

The relevant distinction is not simply “local versus remote.” It is whether an artifact is:

- durable guidance that every agent should inherit;
- an accepted implementation commitment that needs review;
- a work item that needs an owner, status, or dependency links; or
- private, provisional reasoning that may be discarded.

Codex describes `AGENTS.md` as durable repository guidance, recommends keeping it small, and says task-specific Markdown can be referenced when the main file grows.[1][2][3]

Hermes similarly loads `AGENTS.md` as primary project context, progressively discovers narrower context, and warns that context files are subject to size limits and truncation.[4] Therefore, adding every plan to the automatically loaded context is the wrong default.

## Options compared

| Option | Agent discoverability | Version control and review | Stale-plan risk | Context load | Privacy | Turning a plan into implementation work |
|---|---|---|---|---|---|---|---|
| 1. External issue tracker / Projects | High after the agent is given repository access and an issue URL/number; not guaranteed during a local-only session | Strong discussion, ownership, labels, links, and status; not part of the Git diff | Medium: open issues can remain unresolved, but status, assignee, labels, and closure are visible | Low in the code workspace; context is fetched selectively | Depends on repository visibility and organization policy; private design details may still be exposed to collaborators | Direct: one accepted plan becomes an Issue; split into sub-issues; add to Project for sequencing. GitHub explicitly supports sub-issues for breaking large work into smaller units.[7] |
| 2. Gitignored local planning workspace (`.hermes/plans/`, `.scratch/`, or `.planning/`) | High for the active Hermes session when the path is supplied or plan mode creates it; low for a new agent unless the workflow points it there. Hermes plan mode specifically writes to `.hermes/plans/`.[5] | No shared review, no history in Git, and deletion is easy; local Git history is not a substitute for team review | High unless files carry status/expiry and are periodically triaged | Lowest default load if the directory is not an instruction file; avoids root-document bloat. A plan can be loaded on demand | Best for private hypotheses, credentials-adjacent notes, and rejected alternatives, provided secrets are never written there | Periodic review converts accepted items into Issues or a small reviewed PR that updates the source-of-truth docs |
| 3. Tracked `docs/plans/` area or a planning branch | High once an agent or contributor looks at the repository; a tracked index can improve navigation | Strong Git history and PR review; branch gives reviewability without landing the plan on `main` | Medium: history preserves stale plans unless status and owners are explicit; a branch can disappear or become detached from current `main` | Higher than option 2 if agents are told to read the area; lower than root-loaded `AGENTS.md` if not automatically referenced | Repository visibility applies; private branches still expose content to repository collaborators | A reviewed plan PR can become the implementation branch, or its checklist can be copied into Issues. GitHub describes pull requests as proposals that support discussion, review, checks, and later merge.[9] |

### Option 1: Issues and Projects

GitHub Issues are the best system of record for accepted work that needs accountability. The official documentation says Issues can track ideas, feedback, tasks, and bugs; they can be created to plan, discuss, and track work, and they integrate with Projects.[7] Projects adds custom fields, multiple views, status updates, and automation while keeping references synchronized with issues and pull requests.[8]

Strengths for this repository:

- An accepted refactor can become a parent Issue with sub-issues for command parsing, pure planning, discovery/snapshotting, GitHub adapters, and orchestration.
- Ownership and state are visible without loading planning prose into every coding session.
- The eventual implementation PR can link the Issue, giving a trace from decision to code review.
- Project fields can represent priority, milestone, risk, or “ready for implementation” without inventing repository files.

Costs and limits:

- Agents do not automatically receive the issue body in the local prompt. The session must be given the issue URL/number or use an approved GitHub integration.
- Issue prose is not a compile-time or repository checkout dependency; a detached plan can diverge from `main`.
- Projects are more operational machinery than a small plugin needs if there are only one or two active changes.
- This repository’s own `REFACTOR-PLAN.md` says not to publish GitHub Issues until the ticket breakdown is approved. That local rule is controlling for `ugh-cloud`.

Use Discussions only for genuinely open-ended design questions or community input. GitHub describes Discussions as a place for questions, information, announcements, and open-ended direction-setting, and its guidance distinguishes that conversational use from the more task-oriented Issue workflow.[10] For this small private implementation repository, Discussions are optional and should not become a second backlog.

### Option 2: Gitignored local planning workspace

A local planning directory is the best default for early reasoning. Hermes’s bundled plan workflow is unusually direct evidence: it says to plan only, avoid implementation and external actions, and save a concrete Markdown plan under `.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md`.[5] That gives agents a predictable write target without turning each intermediate plan into a repository-wide instruction file.

Use `.hermes/plans/` rather than inventing `.scratch/` when the artifact is created by Hermes plan mode. If the repository wants a generic local workspace for non-Hermes tools, `.scratch/plans/` or `.planning/` can be equivalent, but it should be explicitly gitignored and documented in the workflow—not silently assumed.

Strengths:

- No clutter in the normal tracked workspace and no accidental change to `SPEC.md` or `REFACTOR-PLAN.md`.
- Easy to record alternatives, assumptions, file-level steps, test commands, and unresolved questions before a decision exists.
- Lowest context cost: the plan is loaded when needed rather than placed in `AGENTS.md` or a root-level document that agents read routinely.
- Suitable for private research that should not be shared yet.

Risks and controls:

- A new agent cannot discover an ignored file reliably unless the task prompt, local workflow, or plan filename is supplied. Maintain a tiny local index or naming convention, and include an explicit expiry/status header.
- Gitignored does not mean secure. Never put tokens, personal data, or unredacted remote responses into plans. The repository’s AGENTS.md separately requires credentials to remain in the profile secret/environment mechanism.
- Add `Status`, `Owner`, `Created`, `Review-by`, and `Promotion target` fields. Delete or archive plans after promotion or expiry.
- Do not use a local plan as the only record after implementation begins if another contributor must understand the decision.

### Option 3: Tracked docs/plans or a planning branch

A tracked `docs/plans/` directory is appropriate when the plan itself is a reviewed deliverable: for example, a cross-cutting migration with explicit alternatives, a public design proposal, or a plan that must be reproducible by contributors without access to a personal workspace. A branch-based plan is a variant: review it through a PR, but do not merge it until the plan is accepted or it is intentionally retained as historical design context.

A tracked plan should have a stable identifier, status, owner, scope, decision date, links to Issues/PRs, and a clear archival rule. A `docs/plans/README.md` index is useful only if it remains maintained; otherwise it becomes another stale catalog.

The principal benefit is reviewability. GitHub’s pull-request documentation frames PRs as a place to propose, discuss, review, run checks on, and merge changes.[9] That makes a planning PR a good mechanism when the plan changes repository-wide contracts or when stakeholders need line-level review before implementation.

The principal drawback is semantic ambiguity: a tracked plan can look authoritative even when it is only a proposal. For `ugh-cloud`, `SPEC.md`, `ARCHITECTURE.md`, and `REFACTOR-PLAN.md` already have distinct meanings. Adding `docs/plans/` without a lifecycle policy would create competing sources of truth and increase agent search cost.

## Recommendation applied to `ugh-cloud`

Adopt this policy:

1. Local exploratory plan: write to `.hermes/plans/` with a timestamped slug. Include goal, current repository facts, assumptions, alternatives considered, exact likely files, tests, risks, open questions, status, owner, and review-by date. Do not edit source code or tracked docs while the design is still provisional.
2. Decision checkpoint: compare the plan with `AGENTS.md`, `SPEC.md`, `ARCHITECTURE.md`, `REFACTOR-PLAN.md`, and the relevant research evidence. Resolve contradictions before implementation. The root `AGENTS.md` should remain a compact router; Codex and Hermes both support scoped, progressive context rather than an ever-growing root file.[1][3][4]
3. Ticket promotion: after the scope and acceptance boundary are approved, create an Issue for each independently deliverable unit, or a parent Issue plus sub-issues when sequencing/dependencies matter. Attach to a Project only if status, ownership, dates, or cross-issue views add value. Do not create Issues merely to externalize unresolved brainstorming.
4. Documentation promotion: update the appropriate tracked source-of-truth file in the same reviewed change as the implementation when the plan establishes a durable contract. Link the Issue and plan provenance from the PR; do not copy the entire transient plan into the root.
5. Completion: close or update the Issue, mark the local plan `Promoted` or delete it, and remove stale alternatives. If a tracked design proposal remains useful after implementation, mark it `Accepted`, `Superseded`, or `Rejected` and link the resulting code/Issue rather than leaving “active” language.

This is deliberately not a new automation system. Hermes documents plugins as an extension surface, which supports keeping planning workflow outside the plugin runtime.[6] It respects the repository’s current out-of-scope rule against adding databases, schedulers, polling, or hidden GitHub behavior, and it keeps external effects behind the explicit operator workflow already required by the project.

## Exact promotion rule for tracked repository documentation

Promote a planning artifact into tracked repository documentation only when all of the following are true:

- The decision is accepted by the repository owner/maintainer, not merely proposed by an agent.
- The content changes a durable contract that a future agent or contributor must know without recovering a past conversation.
- The target source of truth is unambiguous:
  - `SPEC.md` for user-visible commands, behavior, safety rules, or acceptance criteria.
  - `ARCHITECTURE.md` for stable module responsibilities, dependency direction, ownership, seams, or invariants.
  - `REFACTOR-PLAN.md` for an approved, active migration sequence whose temporary states and acceptance boundary matter to implementation.
  - `AGENTS.md` only for concise repository-wide instructions, routing, mandatory checks, and non-negotiable rules that apply to every agent.
  - `.research/` for cited evidence and rationale that should remain available to later decisions.
- The content has a named owner, status, scope, and verification/expiry condition.
- The change can be reviewed as a focused PR and will not duplicate an existing source of truth.

Do not promote when the artifact is only a private hypothesis, an abandoned alternative, a task checklist that belongs in an Issue, a session transcript, or implementation detail that will be obsolete as soon as the code lands.

For `ugh-cloud`, an implementation plan should therefore remain local until its ticket breakdown and acceptance boundary are approved. It should enter tracked documentation in the same PR that adopts the decision, before or alongside code if agents need the contract to implement safely. The current repository rule that behavior changes require `SPEC.md` updates and that structure changes follow `ARCHITECTURE.md`/`REFACTOR-PLAN.md` makes this promotion boundary explicit; no separate “plan document” is required for every ticket.

## Confidence and evidence limits

- High confidence: Codex `AGENTS.md`, Hermes context files, and Hermes plan mode are described by first-party documentation.[1][4][5]
- High confidence: GitHub Issues and Projects are described by GitHub’s first-party documentation.[7][8]
- High confidence: GitHub pull requests and Discussions are described by GitHub’s first-party documentation.[9][10]
- Medium-to-high confidence: the repository fit of the recommended hybrid workflow, because it combines those documented mechanisms with the inspected `ugh-cloud` rules and current document split.
- The first-party `openai-agents-python` and `hermes-agent` repositories provide concrete examples of root `AGENTS.md` files used for contributor guidance and narrower routing, but examples are evidence of practice, not a universal requirement.[11][12]
- No claim is made that GitHub or Hermes automatically discovers arbitrary ignored planning directories. The recommendation treats `.hermes/plans/` as an explicit Hermes plan-mode destination and requires a workflow pointer for later sessions.[4][5]

## Sources

[1] OpenAI, “Custom instructions with AGENTS.md – Codex,” accessed 2026-09-13. https://developers.openai.com/codex/guides/agents-md

[2] OpenAI, “Codex manual,” accessed 2026-09-13. https://developers.openai.com/codex/codex-manual.md

[3] OpenAI, “Customization – Codex,” accessed 2026-09-13. https://developers.openai.com/codex/concepts/customization

[4] Nous Research, “Context Files | Hermes Agent,” accessed 2026-09-13. https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files

[5] Nous Research, “Plan — Write a markdown plan to .hermes/plans/; no execution,” bundled skill version 2.0.0, accessed 2026-09-13. https://hermes-agent.nousresearch.com/docs/user-guide/skills/bundled/software-development/software-development-plan

[6] Nous Research, “Build a Hermes Plugin,” accessed 2026-09-13. https://hermes-agent.nousresearch.com/docs/developer-guide/plugins

[7] GitHub, “About issues,” accessed 2026-09-13. https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues

[8] GitHub, “About Projects,” accessed 2026-09-13. https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects

[9] GitHub, “About pull requests,” accessed 2026-09-13. https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests

[10] GitHub, “About discussions,” accessed 2026-09-13. https://docs.github.com/en/discussions/collaborating-with-your-community-using-discussions/about-discussions

[11] OpenAI, `openai-agents-python`, root `AGENTS.md`, main branch, accessed 2026-09-13. https://github.com/openai/openai-agents-python/blob/main/AGENTS.md

[12] Nous Research, `hermes-agent`, root `AGENTS.md`, main branch, accessed 2026-09-13. https://github.com/NousResearch/hermes-agent/blob/main/AGENTS.md
