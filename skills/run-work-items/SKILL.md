---
name: "run-work-items"
description: "Activate when users ask to execute queued work. Selects next actionable item from the configured backend, runs implementation with process quality gates, and continuously updates item state until completion."
category: "process"
scope: "development"
subcategory: "execution"
tags:
  - work-items
  - execution
  - automation
  - quality-gates
version: "10.2.14"
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# Run Work Items

Execute the next actionable work item and maintain continuous state tracking.

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

## Output

Return:
- item executed
- result/status change
- test/review gate summary
- TDD phase evidence status when applicable
- next action (continue/blocked/done)
