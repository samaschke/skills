---
name: "github-state-tracker"
description: "Retrieve, normalize, and report GitHub issue state continuously with prioritization and parent-child awareness. Use when users ask for GitHub issue status reports, backlog prioritization views, trend snapshots, or automated state tracking using gh CLI (preferred for token efficiency) with optional GitHub MCP fallback."
category: "process"
scope: "development"
subcategory: "tracking"
tags:
  - github
  - issues
  - reporting
  - automation
  - tracking
version: "1.0.0"
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# GitHub State Tracker

Collect and process issue data into actionable reports with priority ordering and parent-child context.

## Requirements (Mandatory)

- GitHub CLI installed and reachable in PATH (`gh --version`).
- GitHub authentication completed (`gh auth status`).
- Python 3 launcher selected:
  - macOS/Linux: `python3`
  - Windows (PowerShell/CMD): `py -3`
- Target repository available:
  - explicit `--repo owner/repo`, or
  - infer from current upstream repo via `gh repo view`.

## Triggering

Use this skill when the user asks for GitHub issue reporting, synchronization, or continuous state tracking.

Use this skill when requests include:
- Generate GitHub issue status reports with priorities
- Retrieve and process backlog items automatically
- Track issue state changes over time
- Build parent-child aware planning dashboards from GitHub Issues

Do not use this skill when the request is not about issue state analytics:
- Implement feature code changes
- Refactor test suites without reporting requirements
- Create static design mockups

## Acceptance Tests

| Test ID | Type | Prompt / Condition | Expected Result |
| --- | --- | --- | --- |
| GST-T1 | Positive trigger | "Generate a prioritized GitHub issue report" | Skill triggers |
| GST-T2 | Positive trigger | "Track issue state deltas daily from GitHub" | Skill triggers |
| GST-T3 | Negative trigger | "Fix lint errors in this module" | Skill does not trigger |
| GST-T4 | Negative trigger | "Write a CSS animation for cards" | Skill does not trigger |
| GST-T5 | Behavior | Skill is triggered for state tracking/reporting | Prefer gh with bounded queries; resolve target repo from user input or current upstream repo; optionally use MCP proxy + GitHub MCP tools; normalize type/priority/parent data; emit JSON snapshot and markdown report |

## Workflow

1. Choose transport (`gh` preferred).
- Preferred: use `gh` CLI and local report script for token-efficient retrieval and processing.
- Optional fallback: use GitHub MCP server calls when MCP is already configured or required by environment policy.
- Reference `skills/mcp-proxy/SKILL.md` for centralized auth handling.
- Reference `skills/mcp-config/SKILL.md` if MCP server setup is required.
- Reference `skills/mcp-client/SKILL.md` for dynamic tool discovery/calling.

2. Verify auth/tooling for selected transport.
- Set `<PYTHON>` launcher first:
  - macOS/Linux: `python3`
  - Windows: `py -3`
- CLI path (default): run `gh auth status` or `<PYTHON> skills/github-issues-planning/scripts/gh_preflight.py`.
- If CLI auth is missing, run `gh auth login` (correct command).
- MCP fallback path: ensure GitHub MCP server is reachable via MCP proxy.

3. Resolve the target project/repository.
- If the user specifies a target repo, use it.
- Otherwise default to current repo from `gh repo view --json nameWithOwner --jq .nameWithOwner`.
- If resolution fails, ask for `owner/repo` explicitly.

4. Create or update a snapshot.
- CLI path (default): run `<PYTHON> skills/github-state-tracker/scripts/gh_state_report.py --snapshot-dir <path> --output-md <path/report.md>`.
- Add `--repo <owner/repo>` only when targeting a repo different from current upstream.
- MCP fallback path: retrieve issues with narrow filters (state/label/assignee/time window), then feed normalized data into report generation.
- Use `--state all` to include open and closed items.

5. Use normalized fields for reporting.
- Type from `type/*` labels.
- Priority from `priority/*` labels.
- Parent from native GitHub relationship when available.
- If native relationship is unavailable, use issue body line `Parent: #<number>` as trace-only fallback and flag it as non-native.

6. Apply token-usage discipline.
- Request minimal fields needed for this report.
- Use bounded page sizes and `since`/incremental windows for recurring runs.
- Avoid pulling full issue timelines/comments unless the user explicitly asks.

7. Publish a concise report.
- Include totals by state, type, and priority.
- Include new, closed, and changed issues since prior snapshot.
- Call out untyped or unprioritized items explicitly.
- Confirm requirements status (`gh`, auth, Python launcher, target repo).
- Report resolved target repo and why (explicit vs inferred).

## MCP Proxy And Tool References

- Proxy skill: `skills/mcp-proxy/SKILL.md`
- MCP setup skill: `skills/mcp-config/SKILL.md`
- MCP invocation skill: `skills/mcp-client/SKILL.md`
- GitHub MCP tools to use on MCP path:
  - `mcp__github__list_issues`
  - `mcp__github__get_issue`
  - `mcp__github__search_issues`
  - `mcp__github__add_issue_comment`

## Example

```bash
<PYTHON> skills/github-state-tracker/scripts/gh_state_report.py \
  --snapshot-dir .agent/queue/github-state \
  --output-md summaries/github-issues-report.md
```

Add `--repo <owner/repo>` only when targeting a project other than the current upstream repo.
Set `<PYTHON>` as `python3` on macOS/Linux or `py -3` on Windows.

Detailed report format: `skills/github-state-tracker/references/reporting-spec.md`

## Validation Checklist

- [ ] Auth verified (MCP proxy or `gh auth status`)
- [ ] Target repo resolved (explicit input or current upstream)
- [ ] Snapshot JSON produced
- [ ] Markdown report produced
- [ ] Priority and type counts included
- [ ] Parent-child context extracted and source noted (native link vs trace-only marker)
- [ ] Delta section includes new/closed/changed totals
- [ ] Retrieval scope is bounded for token efficiency

## Output Contract

When this skill runs, produce:

1. Retrieval transport (MCP or CLI), command/tool, and source repository
2. Requirements status (`gh`, auth, Python launcher, target repo)
3. Snapshot artifact path(s)
4. Prioritized markdown report path
5. Delta summary (new/closed/changed)
6. Risk notes for untyped/unprioritized items
