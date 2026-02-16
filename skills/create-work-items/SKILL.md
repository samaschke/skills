---
name: create-work-items
description: "Create and classify typed work items (epic, story, feature, bug, finding, work-item) in the configured tracking backend. Use when users ask to create/capture work or when actionable findings/comments are discovered from review, PR feedback, QA, regressions, or defect reports."
category: "process"
scope: "development"
subcategory: "planning"
tags:
  - work-items
  - planning
  - tracking
  - tdd
version: "10.2.15"
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# Create Work Items

Create typed work items and publish them to the active tracking backend.

## Triggering

Use this skill when the request requires creating or normalizing tracked work items.

Use this skill when prompts include:
- create tickets, issues, work items, findings, or backlog entries
- capture actionable findings/comments from review, PR feedback, QA, regression, or defect reports
- convert discovered implementation tasks into typed work items before planning/execution

Do not use this skill for:
- explanation-only prompts (no request to create tracked work)
- current backlog status only
- implementation-only prompts when existing planned items already cover the work

## Acceptance Tests

| Test ID | Type | Prompt / Condition | Expected Result |
| --- | --- | --- | --- |
| CWI-T1 | Positive trigger | "Create work items for these 4 review findings" | skill triggers |
| CWI-T2 | Positive trigger | "Capture these PR comments as bugs and findings" | skill triggers |
| CWI-T3 | Negative trigger | "Explain why the tests failed" | skill does not trigger |
| CWI-T4 | Negative trigger | "Show current backlog status only" | skill does not trigger |
| CWI-T5 | Behavior | skill triggered for actionable findings/comments | creates typed items with required fields and backend-aware output summary |

## Canonical Actionable Findings Definition

Treat these as actionable findings/comments:
- review findings
- PR comments requesting code/documentation changes
- QA findings
- regressions
- explicit defect reports

Do not create items for non-actionable commentary (questions, explanations, praise, status updates).

## When To Use

- User asks to create tickets/issues/work items
- New work is discovered during implementation or review
- Requirements must be captured before planning/execution

## Item Types

Supported item types:
- `epic`
- `story`
- `feature`
- `bug`
- `finding`
- `work-item`

## Backend Selection

Use canonical config-first backend routing:
1. `.agent/tracking.config.json`
2. `${ICA_HOME}/tracking.config.json`
3. `$HOME/.codex/tracking.config.json` or `$HOME/.claude/tracking.config.json`
4. Auto-detect GitHub
5. Fallback to `.agent/queue/`

## Configuration Bootstrap (MANDATORY)

Before creating items, ensure a persisted tracking configuration exists and is used:
1. If `.agent/tracking.config.json` exists, use it.
2. If project config is missing, ask explicitly:
   - "Use system tracking config for this project, or create a project-specific backend config?"
3. If the selected config file does not exist, ask for backend default (`github` or `file-based`) and create it.
4. Persist at least:
```json
{
  "issue_tracking": { "enabled": true, "provider": "github" },
  "tdd": { "enabled": false }
}
```
5. Use the persisted provider for this run (do not silently switch providers).
6. If user asks to change backend later, update the same config file and confirm the new active provider.

## TDD Confirmation Gate (MANDATORY)

If TDD skill is active (locally or globally), ask explicitly for this scope:
- "TDD is active. Apply TDD for this work scope? (yes/no)"

Persistence rule:
- If `tdd.enabled` is missing on first TDD-related invocation, ask for the default and persist it in the selected config file.
- Scope-level answer overrides stored default for the current run.

## Required Fields

Each created item should include:
- title
- type
- priority (`p0` to `p3` or local equivalent)
- description / acceptance notes
- optional parent

If fields are missing, ask focused clarification (short, bounded), then proceed.

## TDD Decomposition Rule (MANDATORY)

If TDD is being performed for the requested scope, you MUST create explicit work items for:
- `RED` - write/update failing test first
- `GREEN` - implement minimal code to make RED pass
- `REFACTOR` - cleanup and improve design with tests still green

These are required work items, not optional notes.

Required dependency order:
- `GREEN` blocked by `RED`
- `REFACTOR` blocked by `GREEN`

For GitHub backend:
- create these as separate child issues (typically `type/work-item`)
- use clear titles like `[RED] ...`, `[GREEN] ...`, `[REFACTOR] ...`
- create and verify native parent-child links

For file-based backend:
- create three separate `.agent/queue/` items with explicit phase markers

## Creation Rules

- GitHub backend:
  - Use `github-issues-planning` conventions for labels/types/priorities.
  - If parent is requested, include `Parent: #<id>` in body for traceability.
  - Create native GitHub parent-child relationship separately and verify it.
- File-based backend:
  - Create `.agent/queue/NNN-pending-<slug>.md` with structured fields.

## Output Contract

When this skill runs, return a concise creation summary with:
1. backend used
2. items created (ids/urls or filenames)
3. type/priority for each created item
4. parent + native-link verification status (if applicable)
5. TDD phase items created (`RED`/`GREEN`/`REFACTOR`) and dependency wiring status
