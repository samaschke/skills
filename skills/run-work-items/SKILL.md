---
name: run-work-items
description: "Execute the next actionable work item from the configured backend with process quality gates and continuous state updates. Use when users ask to run queued work, continue after planning, or execute actionable findings/comments already captured in the backlog."
category: "process"
scope: "development"
subcategory: "execution"
tags:
  - work-items
  - execution
  - automation
  - quality-gates
version: "10.2.15"
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# Run Work Items

Execute the next actionable work item and maintain continuous state tracking.

## Triggering

Use this skill when the request requires executing planned work items in priority/dependency order.

Use this skill when prompts include:
- run or execute queued/planned work items
- continue with the next actionable item after planning
- execute backlog items created from actionable findings/comments

Do not use this skill for:
- explanation-only prompts without execution intent
- planning-only prompts that still need dependency ordering first
- create new issues for these comments

## Acceptance Tests

| Test ID | Type | Prompt / Condition | Expected Result |
| --- | --- | --- | --- |
| RWI-T1 | Positive trigger | "Run the next actionable item from this plan" | skill triggers |
| RWI-T2 | Positive trigger | "Execute these queued findings after planning" | skill triggers |
| RWI-T3 | Negative trigger | "Explain why this bug happened" | skill does not trigger |
| RWI-T4 | Negative trigger | "Create new issues for these comments" | skill does not trigger |
| RWI-T5 | Behavior | skill triggered for planned findings backlog | selects next unblocked item, runs quality gates, and updates backend state |

## Canonical Actionable Findings Definition

Treat these as actionable findings/comments:
- review findings
- PR comments requesting code/documentation changes
- QA findings
- regressions
- explicit defect reports

Do not run execution for non-actionable commentary (questions, explanations, praise, status updates).

## When To Use

- User asks to run/execute work items
- Backlog has actionable items and execution should continue
- Autonomy loop needs next-step dispatch

## Execution Workflow

1. Load prioritized plan from active backend.
2. Enforce TDD phase order when applicable (`RED` -> `GREEN` -> `REFACTOR`).
3. Select next actionable unblocked item.
4. Run pre-execution validation/check gates.
5. Execute with `process` quality gates (`tdd`, test loop, review loop).
6. Run post-execution validation/check gates.
7. Update state continuously (`in_progress`, `blocked`, `completed`).
8. On completion, re-evaluate next actionable item.

## Configuration Bootstrap (MANDATORY)

Before execution, ensure a persisted tracking configuration exists and is used:
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

## Validation And Check Gates (MANDATORY)

Pre-execution gate:
- Validate item readiness (`type`, `priority`, dependency status, backend state sync).
- Run `validate` skill checks before moving item to `in_progress`.
- Run backend-aware tracking verification for the selected backend.

Post-execution gate:
- Re-run `validate` skill checks before completion.
- Confirm TDD evidence status for current phase (`RED` failing first, `GREEN` pass, `REFACTOR` pass after cleanup) when applicable.
- Re-run backend-aware tracking verification before selecting next item.

If any gate fails:
- do NOT advance to next item
- set item state to `blocked` with reason
- route to `create-work-items` + `plan-work-items` when missing prerequisites are detected

## TDD Execution Gate (MANDATORY)

If TDD is being performed for the work scope:
- you MUST execute explicit `RED`, `GREEN`, `REFACTOR` items in order
- you MUST NOT skip directly to implementation/refactor without completed prior phase

Phase completion expectations:
- `RED`: failing test evidence captured for target behavior
- `GREEN`: minimal implementation passes targeted tests
- `REFACTOR`: design cleanup completed with tests still passing

If chain items are missing, stop run selection and route back to `create-work-items` + `plan-work-items`.

## Backend State Updates

- GitHub backend: update labels/state/closure on issue.
- File-based backend: rename `.agent/queue/` status prefix.

## Continuation Rules

- If actionable items remain, continue automatically per autonomy level.
- If only blocked items remain, report blockers and stop.
- If no items remain, report completion.

## Output Contract

When this skill runs, return:
1. item executed
2. result/status change
3. test/review gate summary
4. TDD phase evidence status when applicable
5. next action (`continue` / `blocked` / `done`)
