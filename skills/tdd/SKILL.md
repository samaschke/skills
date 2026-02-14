---
name: "tdd"
description: "Activate when user asks for Test-Driven Development, test-first implementation, red-green-refactor, or enforcing tests before code. Use for feature work, bug fixes, and refactors; treat TDD as the default rule unless the user explicitly waives it."
category: "process"
scope: "development"
subcategory: "workflow"
tags:
  - development
  - process
  - tdd
version: "10.2.15"
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# TDD Skill

General-purpose Test-Driven Development workflow for product code.

## Rule

For implementation work, TDD is the default.
- Do not start with production code changes.
- Start with a test plan, then failing tests (`RED`), then minimum code (`GREEN`), then cleanup (`REFACTOR`).
- Only skip TDD when the user explicitly says tests are out of scope.

## TDD Config Bootstrap (MANDATORY)

Persist TDD preference in the same tracking config hierarchy used by create/plan/run:
1. `.agent/tracking.config.json`
2. `${ICA_HOME}/tracking.config.json`
3. `$HOME/.codex/tracking.config.json` or `$HOME/.claude/tracking.config.json`

Behavior:
- If project config is missing, ask explicitly:
  - "Use system tracking config for this project, or create a project-specific backend config?"
- On first TDD invocation, if selected config file does not exist, create it.
- If `tdd.enabled` is missing, ask explicitly and persist:
  - "TDD is active. Set default TDD behavior to enabled for this scope/config? (yes/no)"
- Write/update:
```json
{
  "tdd": { "enabled": true }
}
```
- Scope-level decision always takes precedence over stored default for current run.
- If user asks to change default later, update `tdd.enabled` in the selected config file and confirm.

## When to Use

- User asks for TDD, test-first, or red-green-refactor
- Implementing a new feature with clear behavior
- Fixing a bug and preventing regression
- Refactoring code while preserving behavior
- Working in unfamiliar code where tests reduce risk

## When Not to Use

- One-off prototypes where tests are explicitly out of scope
- Tasks with no practical automated verification path
- Purely cosmetic edits where behavior does not change

## Core Loop: Red -> Green -> Refactor

1. **Define a single behavior slice**
   - Capture one user-visible outcome at a time.
   - Prefer smallest meaningful increment.

2. **Write a failing test first (`RED`)**
   - Add or update one focused test.
   - Run the narrowest command that executes the test.
   - Confirm it fails for the expected reason.

3. **Implement the minimum code to pass (`GREEN`)**
   - Change only what is needed to satisfy the test.
   - Avoid speculative abstractions.
   - Re-run the focused test, then nearby tests.

4. **Improve design without changing behavior (`REFACTOR`)**
   - Remove duplication and improve naming/structure.
   - Keep tests green after each small refactor step.

5. **Repeat**
   - Add the next failing test for the next behavior slice.
   - Continue until acceptance criteria are covered.

## Acceptance Tests (for this skill)

| Test ID | Type | Prompt / Condition | Expected Result |
| --- | --- | --- | --- |
| T1 | Positive trigger | "Implement this in TDD" | skill triggers |
| T2 | Positive trigger | "Write tests first, then code" | skill triggers |
| T3 | Positive trigger | "Red green refactor this bug fix" | skill triggers |
| T4 | Negative trigger | "Polish this dashboard layout" | skill does not trigger |
| T5 | Negative trigger | "Draft release notes only" | skill does not trigger |
| T6 | Behavior | skill triggered for code change | requires test plan + RED evidence before implementation |
| T7 | Behavior | bug fix workflow | regression test added first, initially failing |
| T8 | Behavior | completion | reports failing-to-passing evidence and final suite result |

## Test Planning Pattern (implementation work)

Before coding, define lightweight acceptance checks:

| Test ID | Type | Scenario | Expected Result |
| --- | --- | --- | --- |
| T1 | Happy path | valid input | expected output returned |
| T2 | Edge case | boundary input | stable, correct behavior |
| T3 | Error path | invalid input | safe, explicit failure |
| T4 | Regression | previously broken flow | bug stays fixed |

## Practical Rules

- Start with behavior, not internal implementation details.
- Use deterministic tests (no flaky timing/network dependencies).
- Keep tests readable (Arrange -> Act -> Assert).
- For bug fixes, write the regression test before the code fix.
- For legacy code, write characterization tests first, then refactor.
- Run full relevant test suite before finishing.
- Record the command/output proving the first failing test run.
- Record the command/output proving the final passing run.

## Validation Checklist

- [ ] Tests were written/updated before implementation changes
- [ ] First test run failed for expected reason
- [ ] Minimal implementation made tests pass
- [ ] Refactor preserved green test state
- [ ] New behavior and regression paths are covered
- [ ] Relevant suite passes end-to-end

## Output Contract

When this skill is used, produce:

1. Test plan (happy path, edge, error, regression)
2. Evidence of initial failing test(s)
3. Code change summary tied to passing tests
4. Final test results and residual risks (if any)
