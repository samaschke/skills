---
name: github-issues-planning
description: Plan and structure GitHub Issues work for epics, stories, bugs, findings, and work-items with consistent labels, priorities, and parent-child links. Use when users ask to set up GitHub planning/tracking, create typed issues, define issue hierarchies, or enforce issue taxonomy via gh CLI (preferred for token efficiency) with optional GitHub MCP fallback.
category: process
scope: development
subcategory: planning
tags:
  - github
  - issues
  - planning
  - prioritization
  - tracking
version: 1.0.0
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# GitHub Issues Planning

Establish a repeatable GitHub-native planning model with typed issues, explicit priorities, and parent-child relationships.

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

Use this skill when the user asks for GitHub issue planning or taxonomy work.

Use this skill when requests include:
- Create GitHub epics, stories, bugs, findings, or work-items
- Set up issue labels and priorities for planning/tracking
- Define parent-child issue relationships in GitHub
- Use gh CLI to create and organize project issues

Do not use this skill when requests are unrelated to issue planning:
- Fix implementation code bugs without issue management changes
- Perform UI design-only work
- Configure CI runners or deployment infrastructure

## Acceptance Tests

| Test ID | Type | Prompt / Condition | Expected Result |
| --- | --- | --- | --- |
| GIP-T1 | Positive trigger | "Set up GitHub issue taxonomy for epics and stories" | Skill triggers |
| GIP-T2 | Positive trigger | "Create a bug issue with priority and parent in GitHub" | Skill triggers |
| GIP-T3 | Negative trigger | "Fix this TypeScript null check bug" | Skill does not trigger |
| GIP-T4 | Negative trigger | "Create a landing page hero section" | Skill does not trigger |
| GIP-T5 | Behavior | Skill is triggered for GitHub planning/tracking | Prefer gh CLI/scripts for token efficiency; resolve target repo from user input or current upstream repo; optionally use MCP proxy + GitHub MCP tools; enforce labels/priorities/parent-child linkage; communicate requirements and platform-specific run commands clearly; verify native parent/child links |

## Workflow

1. Select transport first (`gh` preferred).
- Preferred: use `gh` CLI and local helper scripts for token-efficient execution.
- Optional fallback: use GitHub MCP tools when MCP is already configured or required by environment policy.
- Reference `skills/mcp-proxy/SKILL.md` for centralized auth and token handling.
- Reference `skills/mcp-config/SKILL.md` if MCP server discovery/config is needed.
- Reference `skills/mcp-client/SKILL.md` when discovering/calling MCP tools dynamically.

2. Verify prerequisites for the chosen transport.
- Set `<PYTHON>` launcher first:
  - macOS/Linux: `python3`
  - Windows: `py -3`
- CLI path (default): run `<PYTHON> skills/github-issues-planning/scripts/gh_preflight.py`.
- If CLI auth is missing, run `gh auth login` (correct command) or `<PYTHON> skills/github-issues-planning/scripts/gh_preflight.py --auto-login`.
- MCP fallback path: ensure GitHub MCP server is available and authenticated via MCP proxy.
- Never ask for raw tokens in chat; use interactive login/proxy flows only.

3. Resolve the target project/repository.
- If the user specifies a target repo, use it.
- Otherwise default to the current repo from `gh repo view --json nameWithOwner --jq .nameWithOwner`.
- If resolution fails, ask for `owner/repo` explicitly.

4. Align issue taxonomy before creating items.
- Use these type labels: `type/epic`, `type/story`, `type/bug`, `type/finding`, `type/work-item`.
- Use these priority labels: `priority/p0`, `priority/p1`, `priority/p2`, `priority/p3`.
- Optional lifecycle labels: `status/backlog`, `status/in-progress`, `status/done`.

5. Create typed issues deterministically.
- CLI path (default): run `<PYTHON> skills/github-issues-planning/scripts/gh_issue_create.py --type <epic|story|bug|finding|work-item> --title \"...\" --priority <p0|p1|p2|p3> --parent <issue-number-optional>`.
- Add `--repo <owner/repo>` only when targeting a repo different from current upstream.
- MCP fallback path: use GitHub MCP issue creation/update tools with explicit type/priority labels and optional parent marker.
- Use dry-run and minimal field selection for sensitive repos.

6. Enforce explicit TDD phase work items when applicable.
- If TDD is being performed for the scoped implementation, create explicit issues for:
  - `[RED] ...`
  - `[GREEN] ...`
  - `[REFACTOR] ...`
- These MUST be separate work items (usually `type/work-item`) and MUST be executed in order.
- Link each phase natively to the parent story/feature/bug item, and capture dependency order:
  - `GREEN` blocked by `RED`
  - `REFACTOR` blocked by `GREEN`

7. Encode parent-child relationship correctly.
- Always include `Parent: #<number>` in child issue body when `--parent` is provided for human traceability.
- Treat body marker as trace text only; it is not a native GitHub relationship.
- Create native GitHub parent-child relationship via GitHub UI or API workflow supported by your environment.
- Verify native link exists before reporting hierarchy creation success.
- For epic parents, you may additionally maintain a child checklist in the epic body.

8. Apply token-usage discipline.
- Fetch only required fields (avoid large body payloads unless parent parsing is required).
- Bound retrieval sizes (`per_page`/`limit`) and scope (`state`, labels, assignee) before broad queries.
- Prefer incremental sync (`since`-style filters) for repeated runs.

9. Return a concise planning summary.
- Confirm requirements status (`gh`, auth, Python launcher, target repo).
- Report created issue URL/number.
- Report resolved target repo and why (explicit vs inferred).
- Report issue type, priority, and parent reference.
- Report TDD phase issue creation and execution-order wiring status when applicable.
- Report whether MCP or CLI transport was used and why.

## MCP Proxy And Tool References

- Proxy skill: `skills/mcp-proxy/SKILL.md`
- MCP setup skill: `skills/mcp-config/SKILL.md`
- MCP invocation skill: `skills/mcp-client/SKILL.md`
- GitHub MCP tools to use when on MCP path:
  - `mcp__github__create_issue`
  - `mcp__github__update_issue`
  - `mcp__github__list_issues`
  - `mcp__github__get_issue`
  - `mcp__github__add_issue_comment`

## Issue Conventions

| Concept | GitHub Representation |
| --- | --- |
| Epic | Issue with `type/epic` label |
| Story | Issue with `type/story` label |
| Bug | Issue with `type/bug` label |
| Finding | Issue with `type/finding` label |
| Work-Item | Issue with `type/work-item` label |
| Priority | `priority/p0` (highest) to `priority/p3` |
| Parent-child | Native GitHub parent-child link (required) + optional `Parent: #<number>` body marker |

Detailed examples: `skills/github-issues-planning/references/issue-taxonomy.md`

## Validation Checklist

- [ ] `gh` CLI installed
- [ ] MCP proxy path validated, or `gh auth status` succeeds (fallback)
- [ ] Target repo resolved (explicit input or current upstream)
- [ ] Issue has one valid type label
- [ ] Issue has one valid priority label
- [ ] Parent trace marker is present when requested
- [ ] Native GitHub parent-child relationship is created and verified when requested
- [ ] Explicit TDD phase issues (`RED`/`GREEN`/`REFACTOR`) exist when TDD applies
- [ ] TDD phase dependencies enforce `RED -> GREEN -> REFACTOR`
- [ ] Retrieval/creation scope is bounded for token efficiency
- [ ] Final response includes issue URL and metadata summary

## Output Contract

When this skill runs, produce:

1. Transport status (MCP or CLI + auth state)
2. Requirements status (`gh`, auth, Python launcher, target repo)
3. Exact command(s) used (or dry-run command)
4. Created/updated issue IDs and URLs
5. Type/priority/parent-child summary (including native-link verification status)
6. Any blockers (missing permissions, missing repo access, auth failures)
