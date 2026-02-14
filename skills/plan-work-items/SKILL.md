---
name: "plan-work-items"
description: "Activate when users ask to plan, prioritize, or structure existing work items. Orders backlog by priority and dependencies, validates parent-child hierarchy, and prepares run-ready next actions."
category: "process"
scope: "development"
subcategory: "planning"
tags:
  - work-items
  - planning
  - prioritization
  - dependencies
version: "10.2.15"
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# Plan Work Items

Prioritize and structure work items so execution can proceed deterministically.

## When To Use

- User asks to prioritize or sequence work
- Parent/child hierarchy must be validated
- Dependencies/blockers need explicit management

## Planning Workflow

1. Load current backlog from active backend.
2. Normalize item types and priorities.
3. Build dependency graph (blocks/blocked-by).
4. Enforce TDD phase chain only when TDD is being performed (`RED` -> `GREEN` -> `REFACTOR`).
5. Identify actionable next set (unblocked, highest priority).
6. Publish planning result back to backend.

## Configuration Bootstrap (MANDATORY)

Before planning, ensure a persisted tracking configuration exists and is used:
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

## TDD Planning Gate (MANDATORY)

When TDD is being performed for the scoped work:
- explicit `RED`, `GREEN`, `REFACTOR` work items MUST exist
- they MUST be dependency-linked in that order
- planning is NOT complete until this chain is present and actionable ordering respects it

If the chain is missing:
- create missing phase items via `create-work-items`
- re-run planning pass

## Parent/Child Rule (GitHub)

- `Parent: #123` in issue body is trace-only.
- Native GitHub parent-child relationship must exist for hierarchy to be valid.
- Verify native relationship before marking planning complete.

## Planning Output

Return:
- prioritized order
- blocked vs actionable items
- dependency risks
- hierarchy verification status
- TDD phase-chain status (`RED`/`GREEN`/`REFACTOR`)
- recommended next item(s) for `run-work-items`
