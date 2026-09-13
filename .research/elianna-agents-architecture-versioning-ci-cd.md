# Research findings: agent guidance, architecture documentation, versioning, and CI/CD

Repository: `ugh-cloud` Hermes plugin
Research scope: AGENTS.md, ARCHITECTURE.md/code-structure documentation, versioning and release workflow, and GitHub CI/CD for a small Python Hermes plugin.

Evidence policy: primary documentation, specifications, and first-party repositories are preferred. Findings below distinguish direct source statements from repository-specific recommendations. External sources were retrieved 2026-09-13 unless a source carries its own version/date.

## Executive findings

1. `AGENTS.md` should remain a short, executable repository contract: orientation, commands, conventions, safety constraints, and completion gates. It should route to `SPEC.md`, `ARCHITECTURE.md`, and `REFACTOR-PLAN.md`, not duplicate them.
2. `ARCHITECTURE.md` should describe stable boundaries and dependency direction, while `REFACTOR-PLAN.md` describes migration sequence and temporary states. The current split is sound; the main improvement is to add an explicit invariants/verification section and keep the structure synchronized with the actual tree.
3. For this plugin, use SemVer for the plugin/package public contract, PEP 440-compatible metadata, immutable `vX.Y.Z` Git tags, and a human-maintained `CHANGELOG.md` with an `Unreleased` section. Do not infer releases solely from commit history.
4. Start with CI only: pull-request validation, push-to-`main` validation, and a manual or tag-gated release workflow after packaging exists. Do not publish a package until the project has a real `pyproject.toml`, defined distribution name, install contract, and a tested Hermes installation path.
5. CI should test the actual plugin without GitHub credentials or network, run the repository's mandatory checks, build/package-check artifacts when packaging is introduced, use least-privilege permissions, pin third-party actions, and make publishing a separate job gated on successful validation and an explicit release event.

## 1. AGENTS.md best practices

### Primary-source findings

The AGENTS.md project defines the file as a predictable Markdown location for coding-agent context and instructions, complementary to a human-oriented README. Its suggested content includes project overview, build/test commands, code style, security considerations, commit/PR guidance, and other information a new contributor needs.[1]

OpenAI Codex documents layered discovery: global guidance is combined with repository and nearer-directory guidance; files closer to the working directory occur later and can refine broader instructions. Codex also documents a default combined-size limit and fallback filenames.[2][3]

Claude Code documents `CLAUDE.md` as the project file for coding standards, architecture decisions, preferred libraries, and review checklists, loaded at session start. This is a parallel first-party model, not a claim that Claude Code consumes `AGENTS.md` by default.[4]

The Hermes documentation explicitly lists `AGENTS.md` among project context files, and the current Hermes repository uses its root `AGENTS.md` for repository orientation, contribution intent, quality expectations, and high-risk invariants.[6][9]

The OpenAI Agents Python repository provides a useful first-party example: its root `AGENTS.md` identifies repository structure, important files, development commands, tests, generated documentation boundaries, and contributor workflow.[5]

### Derived practice

An effective `AGENTS.md` is an operational router, not an encyclopedia:

- State the repository identity and the few directories/files that determine work.
- Give exact, copyable validation commands, including the expected success condition.
- State non-negotiable safety rules and scope boundaries in imperative language.
- Define what “done” means and which checks are mandatory before a PR.
- Point to source-of-truth documents rather than copying their content.
- Keep one rule in one place. Duplicated rules drift and create contradictory agent instructions.
- Use nested files only when a real directory boundary needs different rules; make nested files additive and local.
- Keep machine paths, credentials, personal preferences, and temporary debugging notes out of the tracked root file.
- Treat prose as guidance, not enforcement. Back critical constraints with tests, validators, permissions, repository settings, or hooks.
- Update the file when a repeated failure reveals a missing durable rule; remove stale rules rather than accumulating history.

### Assessment of the current `ugh-cloud` AGENTS.md

Strengths:

- It routes behavior, placement, refactor, Hermes API, and GitHub API work to the correct documents.
- It protects the central contract: active profile as source, `--to-agent` as destination, per-skill PRs, no curated-catalog mutation, no force-push/merge/polling/webhooks, and redacted errors.
- Its completion gates are concrete and include offline tests and plugin doctor.
- It keeps `__init__.py` thin and requires dependency injection around external effects.

Recommended maintenance:

- Add a short “Repository map” only if it can be kept synchronized with the actual tree; otherwise keep that detail in `ARCHITECTURE.md`.
- Add the eventual CI command(s) beside the local equivalents, so agents know the authoritative check rather than guessing from workflow YAML.
- State that `.research/` findings are evidence and recommendations, not runtime requirements.
- Add a release-documentation trigger once `CHANGELOG.md`, version metadata, or release workflows exist.
- Keep the file below the practical context budget; the current 53-line file is appropriately compact.

## 2. ARCHITECTURE.md and code-structure documentation

### What the documents should do

`ARCHITECTURE.md` should explain the system as it exists or the explicitly approved target state: responsibilities, boundaries, dependency direction, ownership, data/control flow, and high-value seams. It should answer “where does this behavior belong?” and “what may depend on what?”

`REFACTOR-PLAN.md` should explain the migration: current coupling, ordered steps, compatibility strategy, temporary adapters, and acceptance boundary. It should answer “how do we get there without breaking the contract?”

`SPEC.md` should remain the user-visible behavior contract. Release notes should describe shipped changes. `AGENTS.md` should tell an agent which of these to read and when.

This separation follows the repository's current design and the Hermes plugin boundary: Hermes documents standalone plugins as a manifest plus importable `register(ctx)` entry point, with commands/tools registered through the context.[7][8] Hermes also recommends additive compatibility for documented plugin behavior and keeping versioning local to boundaries that actually carry a wire or persisted format.[7]

### Documentation contents that are worth keeping

For each important module or package, document:

- responsibility and explicit non-responsibilities;
- allowed imports and dependency direction;
- side-effect boundary: filesystem, process, network, credentials, or Hermes runtime;
- input/output types or stable data shapes;
- error ownership and redaction expectations;
- the test seam and the fake/injected boundary used by tests;
- invariants that must survive refactoring;
- ownership of repository paths and generated files.

Prefer a compact dependency diagram plus a table of module responsibilities over prose that repeats implementation details. Link to the defining code and tests when useful, but do not turn the architecture document into a line-by-line index that becomes obsolete after every rename.

### Assessment of current architecture documents

The current `ARCHITECTURE.md` is directionally strong. It identifies the target tree, dependency direction, three core seams, and repository ownership. The current `REFACTOR-PLAN.md` correctly distinguishes registration, command parsing, pure planning, skill discovery/safety, GitHub transport, and orchestration, and it uses expand-and-contract migration rules.

Recommended additions:

1. Add an “Invariants” section containing the non-negotiable rules from `SPEC.md`: source is the active profile, destination is selected by `--to-agent`, only `agents/<target>/skills/` is managed, complete directories are preserved, and each changed skill has its own PR.
2. Add a small “Request lifecycle” sequence: command -> discovery/safety -> snapshot -> remote read -> pure plan -> GitHub mutation -> per-skill result.
3. Mark target-tree entries as “planned” until they exist, or add a current-versus-target table. This prevents agents from treating a future path as already implemented.
4. Define the contract of the fake GitHub gateway and the minimum cases it must simulate; the refactor plan already names these cases.
5. Record documentation ownership: `SPEC.md` for behavior, `ARCHITECTURE.md` for boundaries, `REFACTOR-PLAN.md` for migration, `AGENTS.md` for agent workflow, and `.research/` for rationale/evidence.
6. When packaging is introduced, document distribution files and installation surface separately from runtime module layout.

Do not add a framework, database, background scheduler, polling loop, or release automation to the architecture merely because another project uses one. The plugin's stated scope and current seams favor a standard-library core with injected external boundaries.

## 3. Versioning and release workflow

### Version semantics

SemVer 2.0.0 defines `MAJOR.MINOR.PATCH`: increment major for incompatible public API changes, minor for backward-compatible functionality, and patch for backward-compatible bug fixes. It also requires a declared public API and says released contents must not be modified; changes become a new release.[12]

Python package metadata must follow the Python version specification. PEP 440 defines the canonical public version form and ordering, including pre-, post-, and development releases.[11] PyPA notes that projects may choose SemVer or CalVer, but the choice is a maintainer policy; strict SemVer users should follow the SemVer rules.[10]

Recommendation: use `0.y.z` while the Hermes/plugin command and installation contract are still explicitly unstable, then `1.0.0` when that public contract is declared stable. Use patch for compatible fixes, minor for compatible command/config additions, and major for breaking command/config/plugin API changes. Use PEP 440-compatible versions in Python metadata; use `v0.1.0`, `v0.2.0`, etc. as Git tag names. The `v` prefix is a tag convention, not part of the SemVer core.[12]

The manifest currently says `0.1.0`, but it is not yet a package metadata source of truth. Decide later whether plugin manifest version, Python distribution version, and any runtime-reported version are single-sourced or deliberately independent. Do not maintain multiple editable literals without a check.

### Changelog

Keep a tracked `CHANGELOG.md` with reverse-chronological releases and an `Unreleased` section. Keep a changelog recommends grouping notable changes under categories such as Added, Changed, Deprecated, Removed, Fixed, and Security, linking release headings to comparisons, and recording user-relevant changes rather than dumping raw commit logs.[13]

GitHub Releases are useful publication metadata but are not a portable substitute for a repository changelog: GitHub describes releases as packages around Git tags with release notes and assets, and permits generated or manually written notes.[19][20] Recommendation: maintain the changelog in Git, then use the GitHub Release for the same version as the distribution point and concise release notes. The release body may be generated from PR labels only after labels and conventions are reliable; a maintainer should still review it.

### Tags, immutability, and release gates

A release should be created from a reviewed commit on `main`, after required CI checks pass. Create an annotated or GitHub release tag named `vX.Y.Z`; do not reuse or move a published tag. GitHub releases are based on tags that identify a repository point in history.[19]

Proposed sequence:

1. Merge a change that updates `CHANGELOG.md` and the authoritative version metadata.
2. Run all local and CI checks, including plugin doctor and offline/fake-transport tests.
3. Create the immutable `vX.Y.Z` tag on the exact reviewed commit.
4. Build the source distribution/wheel, if packaging is enabled, and inspect the artifact contents.
5. Create a draft GitHub Release, attach artifacts if appropriate, review generated/manual notes, then publish it.
6. Publish to a package index only from the release/tag workflow, after the build artifact has passed validation and the release gate.
7. Verify the tag, release, artifact, and installed package/version after publication.

For this repository, a package release is not yet justified by the current file set: there is no `pyproject.toml`, package layout, or declared installation/distribution contract in the inspected tree. Until that changes, use GitHub Releases/tags for repository milestones only and do not add PyPI publishing.

## 4. GitHub CI/CD design for this plugin

### Recommended workflows

A small initial setup should have two workflows, with a third added only when packaging exists:

1. `ci.yml` — pull requests to `main` and pushes to `main`; optionally `workflow_dispatch` for operator reruns. Run on Linux first because the plugin is Python and the acceptance commands are shell-oriented, but test Windows separately if native Windows path behavior is a supported contract.
2. `release.yml` — tag trigger for `v*.*.*`, or manual dispatch with a version input and explicit confirmation. It should depend on a successful build/test job and publish only the already-built artifact. A draft-release-first policy is safer than publishing directly.
3. `package.yml` or a release job inside `release.yml` — only after a real Python distribution is defined. Build with the PyPA-standard project metadata/build frontend,[14] inspect with `twine check` or equivalent, upload the artifact as a workflow artifact, and publish from a separate least-privilege job.

GitHub workflow files belong in `.github/workflows`; event filters can restrict branches, tags, and paths, and `workflow_dispatch` supports operator-controlled runs.[15] GitHub's Python guide recommends explicit Python setup, tests, matrices where useful, artifact storage for test/build outputs, and publishing after CI passes.[18]

### CI triggers and jobs

For `ci.yml`:

- `pull_request` targeting `main`: authoritative review gate; no write permissions and no secrets.
- `push` to `main`: post-merge verification and a stable signal for release readiness.
- `workflow_dispatch`: useful for diagnosis and explicit verification, but not a bypass around required checks.
- Do not use scheduled CI initially; add it only for a concrete need such as dependency or Hermes compatibility surveillance.
- Use concurrency per workflow/ref to cancel obsolete PR runs, but avoid canceling a run that is the release gate for a tag.

Jobs should be small and ordered by dependency:

- `quality`: compile the shipped modules and run the local test suite.
- `hermes-doctor`: run `hermes plugins doctor ... --ci` in a reproducible Hermes environment; if installing Hermes in CI is not yet standardized, make this a documented follow-up rather than a falsely green placeholder.
- `security/static`: validate no secrets or generated artifacts are tracked; add a linter/type checker only when its configuration is real and maintained.
- `build`: once packaging exists, build sdist/wheel, inspect filenames/metadata/contents, and upload artifacts for the release job.

The repository's current mandatory local checks are `python -m py_compile __init__.py github.py`, `python test_local.py`, and `hermes plugins doctor . --ci`. CI should invoke those exact checks initially, then migrate to the refactored test layout without silently dropping coverage.

### Permissions and action security

Set workflow-wide `permissions: contents: read` (or `permissions: {}` where feasible), then grant a narrower job only what it needs. GitHub documents least-privilege `GITHUB_TOKEN` permissions and specifically recommends limiting the token rather than relying on implicit defaults.[16][17]

The PR CI job needs no write token and should not receive release secrets. A release job that creates a GitHub Release needs `contents: write`; a PyPI Trusted Publishing job needs `id-token: write` and should not receive broad repository write permissions unless its release action requires them.[16][21]

Pin third-party actions to full commit SHAs where practical, or use a deliberately reviewed immutable version policy. GitHub's security guidance identifies SHA pinning as a mitigation against action-repository compromise and recommends auditing how actions handle source and secrets.[17] Enable Dependabot updates for pinned actions once workflows exist.

Never expose the plugin's GitHub PAT to CI unless a future integration explicitly requires it. Unit and integration tests must use fake HTTP transport/mock servers, as required by the repository specification. Do not run untrusted pull-request code with write-capable tokens or protected secrets.

### Packaging and release gate

Use `pyproject.toml` as the project metadata/build-system entry point when distribution is approved. The PyPA sample project demonstrates declaring build requirements, distribution name, PEP 440-compatible version, README, Python requirement, license, and project metadata there.[22] Build artifacts in CI using an isolated build command, then test the artifact rather than testing only the checkout.

If publishing to PyPI is eventually needed, prefer Trusted Publishing/OIDC over a long-lived API token. GitHub's Python guide presents Trusted Publishing for release-triggered publishing, and the PyPA publishing action requires `id-token: write`; its own documentation recommends separating build from publish and using artifacts between jobs.[18][21] TestPyPI is an appropriate non-production rehearsal target when the upload path needs validation.[23]

Release job gates should be explicit:

- event is a reviewed `vX.Y.Z` tag or an approved manual release;
- tag version equals the package/manifest version;
- all required CI jobs passed for the tagged commit;
- build artifact was produced by the gated build job, not rebuilt after approval;
- artifact metadata and contents pass checks;
- the target environment requires reviewer approval if the repository's governance warrants it;
- publishing is idempotently prevented for an already-published version;
- post-publish verification checks the release/tag and installable artifact.

### Hermes-specific CI considerations

Hermes documents project-local plugins as opt-in and third-party plugins as standalone repositories; the plugin's CI should therefore validate the standalone directory/manifest contract and the documented `register(ctx)` behavior rather than depending on undocumented internal imports.[7][8]

The current Hermes plugin documentation also describes opt-in plugin loading and warns that plugin Python code is in-process and not a sandbox. Keep tests offline, make external effects injectable, and ensure error paths redact tokens. These are especially important for a plugin that handles GitHub credentials and mutates remote branches/PRs.[8]

## Explicit recommendations

1. Keep `AGENTS.md` compact and retain its current router shape. Add only CI/release triggers and commands as those workflows become real.
2. Preserve the current document split: `SPEC.md` is behavior, `ARCHITECTURE.md` is stable structure, `REFACTOR-PLAN.md` is migration, `AGENTS.md` is agent workflow, and `.research/` is rationale.
3. Extend `ARCHITECTURE.md` with invariants, lifecycle sequence, current-versus-target status, and fake-gateway contract.
4. Adopt SemVer with PEP 440-compatible metadata; use `0.y.z` until the command/config/install contract is stable, then define `1.0.0` deliberately.
5. Add `CHANGELOG.md` with `Unreleased` before the first public release; do not generate it from raw Git history alone.
6. Use immutable `vX.Y.Z` tags and GitHub Releases tied to reviewed `main` commits. Never move a published tag.
7. Add PR/push CI now around the existing offline checks. Add release/package automation only after packaging metadata and an installation contract exist.
8. Use least-privilege workflow permissions, no secrets in PR CI, pinned action revisions, and Dependabot for action updates.
9. Separate build, test, and publish jobs. Publish only the exact artifact produced by the gated build job; prefer PyPI Trusted Publishing if PyPI becomes a target.
10. Treat `hermes plugins doctor . --ci`, offline fake-transport tests, compile checks, and secret/artifact scans as release gates. Do not create real GitHub PRs in CI.

## Unresolved decisions

- Is `ugh-cloud` intended to be installed only as a profile-local directory, or will it become a pip-distributed Hermes plugin? This determines whether `pyproject.toml`, wheel contents, entry points, and package publishing are needed.
- What exact Hermes versions are supported? CI needs a compatibility policy: one pinned Hermes version, a supported-version matrix, or a minimum-version contract.
- Should plugin manifest version, Python distribution version, and runtime version be single-sourced? If yes, which file is authoritative and how is drift checked?
- Is Windows native behavior part of the supported contract, requiring a Windows CI job for path/symlink semantics, or is Linux/WSL sufficient for this plugin?
- Should releases be tag-created manually by a maintainer, generated by a release-please-like tool, or driven by reviewed changelog/version PRs? Automation should not be adopted before the project chooses who approves the version bump.
- Does the repository need a package registry at all, or are GitHub tags/releases and Hermes plugin installation enough?
- If PyPI is chosen, what distribution name, trusted-publisher environment, release approvers, and artifact retention policy should be used?
- Which lint/type/security tools are acceptable? Add only tools with a committed configuration and a maintenance owner; do not turn speculative tool recommendations into CI failures.
- Should `hermes plugins doctor` run against a released Hermes build, the repository's current Hermes checkout, or a minimal fixture? The answer affects reproducibility and matrix cost.
- Should action references be pinned to full SHAs immediately, with a Dependabot policy, or use reviewed major tags during the prototype stage? The security preference is SHA pinning; the maintenance tradeoff is unresolved.

## Sources

[1] https://agents.md
[2] https://developers.openai.com/codex/guides/agents-md
[3] https://developers.openai.com/codex/customization/overview
[4] https://docs.anthropic.com/en/docs/claude-code/memory
[5] https://github.com/openai/openai-agents-python/blob/main/AGENTS.md
[6] https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files
[7] https://hermes-agent.nousresearch.com/docs/developer-guide/plugins
[8] https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/plugins.md
[9] https://github.com/NousResearch/hermes-agent/blob/main/AGENTS.md
[10] https://packaging.python.org/en/latest/discussions/versioning
[11] https://peps.python.org/pep-0440
[12] https://semver.org/spec/v2.0.0.html
[13] https://keepachangelog.com/en/1.1.0
[14] https://packaging.python.org/en/latest/tutorials/packaging-projects
[15] https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
[16] https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication
[17] https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
[18] https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python
[19] https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
[20] https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
[21] https://github.com/pypa/gh-action-pypi-publish
[22] https://github.com/pypa/sampleproject/blob/main/pyproject.toml
[23] https://packaging.python.org/en/latest/guides/using-testpypi
