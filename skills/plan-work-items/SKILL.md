---
name: plan-work-items
description: "Plan and prioritize existing typed work items with dependency and hierarchy validation. Use when users ask to sequence work, when new actionable findings/comments were captured, or when blockers/dependencies changed before execution."
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

## Triggering

Use this skill when the request requires ordering or validating tracked work before execution.

Use this skill when prompts include:
- prioritize, sequence, or structure backlog items
- re-plan after creating items from actionable findings/comments
- update dependencies or hierarchy after blockers/change requests

Do not use this skill for:
- explanation-only prompts without planning intent
- status-only prompts where no ordering/dependency change is requested
- direct implementation tasks that already have a valid actionable order

## Acceptance Tests

| Test ID | Type | Prompt / Condition | Expected Result |
| --- | --- | --- | --- |
| PWI-T1 | Positive trigger | "Prioritize these newly captured review findings" | skill triggers |
| PWI-T2 | Positive trigger | "Re-sequence backlog after adding 3 bugs" | skill triggers |
| PWI-T3 | Negative trigger | "Explain what this function does" | skill does not trigger |
| PWI-T4 | Negative trigger | "Only report current issue counts" | skill does not trigger |
| PWI-T5 | Behavior | skill triggered for findings-derived planning | returns actionable ordering, blocked list, dependency risks, and next item recommendation |

## Canonical Actionable Findings Definition

Treat these as actionable findings/comments:
- review findings
- PR comments requesting code/documentation changes
- QA findings
- regressions
- explicit defect reports

Do not create planning actions for non-actionable commentary (questions, explanations, praise, status updates).

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

## Output Contract

When this skill runs, return:
1. prioritized order
2. blocked vs actionable items
3. dependency risks
4. hierarchy verification status
5. TDD phase-chain status (`RED`/`GREEN`/`REFACTOR`)
6. recommended next item(s) for `run-work-items`
