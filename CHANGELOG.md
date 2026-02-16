# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

## [1.1.3] - 2026-02-16

### Changed
- Added explicit system/project autonomy-level resolution (`autonomy.system_level`, `autonomy.project_level`) with `follow-system` handling across `autonomy`, `process`, `commit-pr`, and `release`.
- Hardened process orchestration to avoid preempting in-progress work when new findings arrive; findings are captured, triaged, and prioritized before selecting the next work item.
- Enforced post-PR review and security receipt loops in `commit-pr`, including pass-with-note behavior when no required checks are configured.
- Enforced pre-release review/security receipt loops in `release` with current head-SHA verification before merge.
- Normalized skill metadata names for validator compatibility in planning/work execution skills.

## [1.1.2] - 2026-02-15

### Removed
- Removed the unintended `e2e-skill-publisher-20260215085923` artifact from the published skills catalog.

## [1.1.0] - 2026-02-15

### Added
- Introduced configurable work-item pipeline automation in `process` for actionable findings (`create -> plan -> run`) with `batch_auto`, `batch_confirm`, and `item_confirm` modes.
- Added worktree/branch behavior controls (`always_new`, `ask`, `current_branch`) to process-oriented skill flows.

### Changed
- Persisted and enforced TDD defaults through tracking configuration bootstrap behavior.
- Added explicit trigger contracts (`Triggering`, `Acceptance Tests`, `Output Contract`) for `commit-pr` and `release`.
- Removed hardcoded `codex/*` branch naming from process rules and replaced it with agent-agnostic branch-prefix resolution.

## [1.0.1] - 2026-02-14

### Changed
- Consolidated public skills catalog and removed obsolete/duplicate high-level skills.
- Established canonical high-level flow: `create-work-items` -> `plan-work-items` -> `run-work-items` + `process`.
- Kept `mcp-common` as internal foundational skill (`user-invocable: false`).
- Added bundled MCP core fallback for standalone `mcp-client` and `mcp-proxy` operation.
- Normalized skill frontmatter metadata fields across remaining public skills.
- Updated `README.md` and `skills.index.json` to match the consolidated canonical list.
- Hardened process guidance with explicit validation/check gate requirements across work-item execution, commits, PRs, and releases.
