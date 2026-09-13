# AGENTS.md Research

## Scope

This note compares primary-source guidance for agent instruction files and derives rules for `ugh-cloud`.

## Sources

- AGENTS.md format: https://github.com/agentsmd/agents.md/blob/main/README.md
- AGENTS.md website: https://agents.md/
- OpenAI Codex project instructions: https://developers.openai.com/codex/guides/agents-md/
- Claude Code memory/instruction files: https://docs.anthropic.com/en/docs/claude-code/memory
- Hermes project context files: https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files

## Findings

### 1. AGENTS.md is an instruction file, not a project encyclopedia

The AGENTS.md project describes the file as a predictable place for coding-agent context and instructions. Its minimal example focuses on development environment tips, testing instructions, and PR instructions.

Decision: keep repository-wide rules, commands, conventions, and completion gates in `AGENTS.md`; keep detailed architecture and accepted product behavior in linked documents.

### 2. Scope follows the directory being worked on

OpenAI Codex documents a hierarchy: global instructions, then project-root instructions, then instructions in directories between the project root and current working directory. More specific files are loaded later and therefore refine or override broader guidance. Codex also supports `AGENTS.override.md` and a configured fallback filename list.

Decision: write the root `AGENTS.md` for repository-wide rules. Put specialized rules close to specialized code only when the repository grows enough to justify them. Do not put plugin implementation details in the root file if a narrower document can carry them.

### 3. Instruction files are merged, so contradictions are expensive

Codex concatenates applicable instruction files from broad scope to narrow scope. Claude Code documents the same general model for its `CLAUDE.md` files: files are loaded by directory scope and concatenated rather than treated as a single replacement file.

Decision: maintain one source of truth per rule. Root `AGENTS.md` should point to `SPEC.md` and `ARCHITECTURE.md` instead of copying their contents. Nested instruction files must state only local additions.

### 4. Specific, verifiable instructions outperform general advice

Claude Code's official guidance recommends concise, specific, well-structured instructions; examples include build commands, conventions, project layout, always-do rules, and common workflows. It also recommends keeping instructions short and moving path-specific rules into scoped files when they grow.

Decision: write imperative rules with observable completion criteria. Prefer `Run X and verify Y` over `Keep the project healthy`. Prefer a small number of high-value rules over generic reminders.

### 5. Context size is a reliability constraint

Codex documents a default combined project-instruction limit of 32 KiB and advises splitting instructions across nested directories when the limit is reached. Claude Code recommends keeping a `CLAUDE.md` under 200 lines and using path-scoped rules for larger projects.

Decision: keep `AGENTS.md` short. Use pointers for branch-specific documents and split local rules by directory only when there is a real scope boundary.

### 6. Instruction files are guidance, not hard enforcement

Claude Code explicitly distinguishes behavioral instructions from enforced settings and hooks. An agent may fail to follow prose; deterministic enforcement belongs in tooling, tests, permissions, or hooks.

Decision: put quality expectations in `AGENTS.md`, but also encode critical requirements in tests, plugin doctor checks, `.gitignore`, and runtime validation. Do not describe a prose rule as a security boundary.

### 7. Personal preferences and project rules should be separated

Claude Code distinguishes project instructions shared through version control from local/personal instruction files. Codex likewise supports global and project scopes.

Decision: keep `ugh-cloud/AGENTS.md` limited to repository rules that every contributor/agent should follow. Keep machine-specific paths, tokens, and personal preferences outside the repository.

## Applied structure for ugh-cloud

The current root document should remain a compact router:

- `SPEC.md` for user-visible behavior and constraints
- `ARCHITECTURE.md` for module boundaries and dependency direction
- `REFACTOR-PLAN.md` for the active code-structure migration
- `.research/` for evidence and rationale

`AGENTS.md` should contain only the triggers that decide which document to read, the non-negotiable repository rules, the completion checks, and the change-shape guidance.

## Recommendations

1. Keep the root `AGENTS.md` below 200 lines and preferably much shorter.
2. Start each pointer with the condition that triggers it.
3. Use imperative, testable wording.
4. Remove duplicated commands when the package/tool configuration is the authoritative source.
5. Add nested `AGENTS.md` files only for genuinely narrower directory rules.
6. Review the file whenever commands, architecture, or quality gates change.
7. Treat `.gitignore`, tests, and plugin doctor as enforcement companions, not as content to duplicate in prose.
