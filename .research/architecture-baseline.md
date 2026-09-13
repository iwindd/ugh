# Architecture Baseline Research

## Purpose

Capture primary-source constraints that shape the `ugh-cloud` refactor. This is a planning artifact, not an implementation guide for unrelated Hermes features.

## Hermes plugin contract

Hermes' official plugin documentation describes a standalone plugin as a directory with a manifest and an importable `register(ctx)` entry point. Tools and commands are registered through the plugin context. Plugin settings are namespaced under `plugins.entries.<plugin-id>.settings`, and runtime state belongs to the active profile.

Sources:

- Hermes Agent, Build a Hermes Plugin: https://hermes-agent.nousresearch.com/docs/developer-guide/plugins
- Hermes Agent, Adding Tools: https://hermes-agent.nousresearch.com/docs/developer-guide/adding-tools

Implication: keep `__init__.py` as registration/wiring only, and put behavior behind ordinary Python modules that can be tested without Hermes runtime objects.

## GitHub Git Data API

GitHub documents separate endpoints for references, commits, trees, and blobs. Creating a pull request requires a head branch and a base branch. GitHub also documents the repository Contents API as the supported file-creation path for an empty repository; a repository with no commits cannot be traversed through a normal branch ref or initialized by creating an empty Git tree.

Sources:

- GitHub REST API, Git database: https://docs.github.com/en/rest/git
- GitHub REST API, Git trees: https://docs.github.com/en/rest/git/trees
- GitHub REST API, Pull requests: https://docs.github.com/en/rest/pulls/pulls
- GitHub REST API, Repository contents: https://docs.github.com/en/rest/repos/contents

Implication: the GitHub adapter must own bootstrap, ref lookup, tree construction, commit creation, and PR operations. The orchestration layer must not construct HTTP requests directly.

## GitHub token permissions

Fine-grained personal access tokens are scoped to selected repositories and expose repository permissions individually. The plugin's operations require repository content write access and pull-request write access. Metadata read access is required by GitHub and is granted automatically for repository tokens.

Source:

- GitHub Docs, Managing your personal access tokens: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens

Implication: repository identity and token storage remain separate settings; the token must stay in the profile secret/env mechanism.

## Structure decision

The prototype's largest risk is responsibility coupling: command parsing, filesystem traversal, content hashing, GitHub API calls, branch reuse, and PR behavior are currently in two modules. The proposed decomposition follows the documented plugin registration seam and places the highest-value test seam at a GitHub gateway plus pure synchronization planner.

This avoids introducing a framework or database. The standard library is sufficient for local filesystem work, hashing, command parsing, and HTTP transport. A third-party dependency is deferred unless a later ticket demonstrates a concrete need.

## Deferred decisions

- Whether to use an installed `gh` fallback or require the configured token for every API operation.
- Whether to add a persistent local upload ledger; current behavior can derive identity from repository, target agent, category, skill ID, branch, and GitHub PR state.
- Whether to publish the plugin as a package after the local refactor is stable.
