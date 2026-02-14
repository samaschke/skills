# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

## [1.0.1] - 2026-02-14

### Changed
- Consolidated public skills catalog and removed obsolete/duplicate high-level skills.
- Established canonical high-level flow: `create-work-items` -> `plan-work-items` -> `run-work-items` + `process`.
- Kept `mcp-common` as internal foundational skill (`user-invocable: false`).
- Added bundled MCP core fallback for standalone `mcp-client` and `mcp-proxy` operation.
- Normalized skill frontmatter metadata fields across remaining public skills.
- Updated `README.md` and `skills.index.json` to match the consolidated canonical list.
- Hardened process guidance with explicit validation/check gate requirements across work-item execution, commits, PRs, and releases.
