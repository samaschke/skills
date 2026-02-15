---
name: "process"
description: "Orchestrate the end-to-end development workflow with autonomous quality gates. Use when users ask to implement/run workflow phases, start or continue development, handle review/QA findings, or process actionable comments by routing through create-work-items -> plan-work-items -> run-work-items. Enforces TDD by default for implementation work and only pauses for genuine decisions."
category: "process"
scope: "development"
subcategory: "orchestration"
tags:
  - workflow
  - automation
  - tdd
  - review
version: "10.2.16"
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# Development Process

**AUTONOMOUS EXECUTION.** This process runs automatically. It only pauses when human input is genuinely required.

## Triggering

Use this skill when the request needs end-to-end orchestration of tracked development work.

Use this skill when prompts include:
- start, continue, or run development workflow phases
- implement/fix work that should be tracked and executed with gates
- handle actionable findings/comments from review, PR feedback, QA, regressions, or defect reports
- execute create -> plan -> run flow without manual per-skill invocation

Do not use this skill for:
- explanation-only prompts with no implementation or workflow action
- status-only prompts that only request reporting without execution
- isolated one-off questions unrelated to tracked development work

## Acceptance Tests

| Test ID | Type | Prompt / Condition | Expected Result |
| --- | --- | --- | --- |
| PRC-T1 | Positive trigger | "Address these 6 PR review comments end-to-end." | skill triggers |
| PRC-T2 | Positive trigger | "Start work on this bug and follow the workflow." | skill triggers |
| PRC-T3 | Negative trigger | "Explain why this check failed." | skill does not trigger |
| PRC-T4 | Negative trigger | "Show backlog summary only." | skill does not trigger |
| PRC-T5 | Behavior | skill triggered for actionable findings/comments | routes through create-work-items -> plan-work-items -> run-work-items using configured pipeline mode |

## Canonical Actionable Findings Definition

Treat these as actionable findings/comments:
- review findings
- PR comments requesting code/documentation changes
- QA findings
- regressions
- explicit defect reports

Do not create or run work for non-actionable commentary (questions, explanations, praise, status updates).

## Branch Workflow (CRITICAL)

```
main     ← STABLE ONLY (releases from dev)
  ↑
dev      ← INTEGRATION (all work merges here first)
  ↑
feature/* ← WHERE WORK HAPPENS
```

**ALL changes go to dev first. Main is ALWAYS stable.**

| Action | Target Branch |
|--------|---------------|
| Feature work | PR to `dev` |
| Bug fixes | PR to `dev` |
| Releases | PR from `dev` to `main` |

## Autonomous Principles

1. **Fix issues automatically** - Don't ask permission for obvious fixes
2. **Implement safe improvements automatically** - Low effort + safe = just do it
3. **Loop until clean** - Keep fixing until tests pass and no findings
4. **TDD by default** - RED -> GREEN -> REFACTOR before production code
5. **Only pause for genuine decisions** - Ambiguity, architecture, risk
6. **PR to dev by default** - Never PR to main unless releasing

## Work Management Actions (Human-Friendly)

Use these action names consistently:
- **create** - create typed work items (epic/story/feature/bug/finding/work-item)
- **plan** - prioritize, add dependencies, and establish parent/child structure
- **run** - execute next actionable item and update state continuously

Skill mapping:
- `create` -> `create-work-items` (with `pm` support as needed)
- `plan` -> `plan-work-items` (with `github-state-tracker` support as needed)
- `run` -> `run-work-items` (with `autonomy` + `parallel-execution` support as needed)

## Work-Item Pipeline Settings (ICA Config)

Read these values from `ica.config.json` hierarchy:
- `autonomy.work_item_pipeline_enabled` (default `true`)
- `autonomy.work_item_pipeline_mode` (`batch_auto` | `batch_confirm` | `item_confirm`, default `batch_auto`)

Mode behavior for actionable findings/comments:
- `batch_auto`: run full create -> plan -> run flow without additional confirmation
- `batch_confirm`: ask once for grouped confirmation, then run full flow
- `item_confirm`: confirm each candidate item before creation, then continue with plan -> run

## Workspace + Branch Isolation (ICA Config, MANDATORY)

Read `git.worktree_branch_behavior` from `ica.config.json` hierarchy.

Allowed values:
- `always_new` - always create a dedicated worktree + branch before implementation changes
- `ask` - ask per scoped work unit whether to create a dedicated worktree + branch
- `current_branch` - allow current branch workflow (still subject to large-change confirmation gate)

If `git.worktree_branch_behavior` is missing:
- ask explicitly which behavior to use for this project
- persist the chosen value in project `ica.config.json` (preferred) or user `ica.config.json`

Default branch naming when creating a new branch:
- `<resolved-prefix><short-scope-slug>-<YYYYMMDDHHMMSS>`

Branch prefix resolution (no hardcoding):
- if `git.worktree_branch_prefix` is set, use it (examples: `agent/`, `claude/`, `cursor/`)
- else derive from the active agent runtime (`codex/`, `claude/`, `cursor/`, `gemini/`, `antigravity/`)
- if runtime cannot be determined, use agent-agnostic default `agent/`

Mandatory behavior:
- if `always_new`, do not implement on the current branch; create and switch to the new worktree/branch first
- never perform implementation changes directly on `main` or `dev`
- if release work is requested, use a dedicated release worktree/branch before release actions

## Phase Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ WORK MANAGEMENT PHASE (AUTONOMOUS)                              │
│ create → plan → run-ready                                        │
│ Ensure typed items, priorities, dependencies, parent/child links │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ DEVELOPMENT PHASE (AUTONOMOUS)                                  │
│ Implement → Test → Review+Fix → Suggest+Implement → Loop        │
│ Pause only for: ambiguous requirements, architectural decisions │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ DEPLOYMENT PHASE (if applicable)                                │
│ Deploy → Test → Review+Fix → Commit                             │
│ Pause only for: deployment failures needing human intervention  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PR PHASE (to dev)                                               │
│ Create PR to dev → Review+Fix → WAIT for approval               │
│ Pause for: merge approval (ALWAYS requires explicit user OK)    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ RELEASE PHASE (dev → main, only when requested)                 │
│ Stabilize dev → Create release PR → Tag → WAIT for approval     │
│ Pause for: release approval (requires explicit "release" cmd)   │
└─────────────────────────────────────────────────────────────────┘
```

## Phase 0: Work Management (AUTONOMOUS)

### Step 0.1: Resolve Tracking Backend
```
Use create/plan/run config-first routing:
  1) .agent/tracking.config.json
  2) ${ICA_HOME}/tracking.config.json
  3) $HOME/.codex/tracking.config.json or $HOME/.claude/tracking.config.json
  4) auto-detect GitHub
  5) fallback to .agent/queue/
```

### Step 0.1a: Bootstrap Tracking Config (MANDATORY)
```
If project config is missing, ask explicitly:
  "Use system tracking config for this project, or create a project-specific backend config?"

If selected config file is missing:
  - ask for backend default (`github` or `file-based`)
  - create config file immediately
  - persist and use selected provider for the run

Minimum persisted shape:
{
  "issue_tracking": { "enabled": true, "provider": "github" },
  "tdd": { "enabled": false }
}

If user asks to change backend later:
  - update the same config file
  - confirm active provider after update
```

### Step 0.1b: TDD Activation Confirmation (MANDATORY)
```
If TDD skill is active (locally or globally):
  ask explicitly:
    "TDD is active. Apply TDD for this work scope? (yes/no)"

Persistence rules:
  - If `tdd.enabled` is missing in selected config, ask for default and persist it.
  - Scope-level answer overrides stored default for current run.
  - If user requests default change, update `tdd.enabled` in selected config.
```

### Step 0.1c: Resolve Work-Item Pipeline Mode (MANDATORY)
```
Resolve from ICA config hierarchy:
  - autonomy.work_item_pipeline_enabled (default true)
  - autonomy.work_item_pipeline_mode (default batch_auto)

When actionable findings/comments are detected:
  - If pipeline is disabled: do not auto-orchestrate; wait for explicit create/plan/run instruction
  - If enabled:
      batch_auto    -> proceed automatically
      batch_confirm -> ask once for grouped confirmation
      item_confirm  -> ask per item before creation
```

### Step 0.1d: Resolve Worktree/Branch Behavior (MANDATORY)
```
Resolve from ICA config hierarchy:
  - git.worktree_branch_behavior (always_new | ask | current_branch)

If missing:
  - ask user which behavior to use
  - persist in project or user ica.config.json

If value is always_new:
  - create a new worktree + prefixed branch before implementation
  - continue all implementation on that branch/worktree only

If value is ask:
  - ask for this work scope before implementation
  - if approved, create a new worktree + prefixed branch
```

### Step 0.2: create (Typed Work Items)
```
Invoke create-work-items.

Create or normalize work items as typed units:
  epic, story, feature, bug, finding, work-item

When actionable findings/comments are present and
`autonomy.work_item_pipeline_enabled=true`, this step is mandatory
even without an explicit "create" command.

If GitHub backend is active:
  - Use github-issues-planning workflow to create typed issues

If TDD is being performed for this scope:
  - MUST create explicit phase work items: RED, GREEN, REFACTOR
  - MUST plan them for execution in dependency order
```

### Step 0.3: plan (Priorities + Relationships)
```
Invoke plan-work-items.

Prioritize and define dependencies.

When actionable findings/comments were captured in Step 0.2, planning is
mandatory before any execution starts.

If parent/child hierarchy exists on GitHub:
  - Create native GitHub relationship (sub-issue/parent-child link)
  - Do NOT treat "Parent: #123" body text as a native link
  - Verify link exists before marking planning complete
```

### Step 0.4: run (Select + Execute Next Actionable Item)
```
Invoke run-work-items after create + plan are complete.

run-work-items MUST:
  - select the next unblocked actionable item
  - execute with process quality gates
  - update backend state transitions continuously
```

### Step 0.5: run-ready Check
```
Proceed to Phase 1 only when:
  - Next actionable item is identified
  - Blockers/dependencies are known
  - Tracking state is current
  - run-work-items has a selected next item
  - backend-aware tracking verification passes for the selected backend
  - if TDD is being performed: explicit RED/GREEN/REFACTOR items exist and are sequenced
```

### Step 0.6: Validation + Check Gate (MANDATORY)
```
Run `validate` skill before implementation starts.

Gate must confirm:
  - selected work item is typed and prioritized
  - dependency graph has no unresolved prerequisite for selected item
  - tracking backend state is synchronized
  - parent-child linkage is valid for backend in use
  - backend-aware tracking verification passes

Fail-closed:
  IF gate fails:
    - DO NOT start implementation
    - mark item blocked with concrete reason
    - route back to create/plan steps until gate passes
```

## Phase 1: Development (AUTONOMOUS)

### Step 1.0: Memory Check (AUTOMATIC)
```
BEFORE implementing, search memory:

  # Portable: resolve memory CLI location (prefers ICA_HOME when set)
  MEMORY_CLI=""
  for d in "${ICA_HOME:-}" "$HOME/.codex" "$HOME/.claude"; do
    if [ -n "$d" ] && [ -f "$d/skills/memory/cli.js" ]; then
      MEMORY_CLI="$d/skills/memory/cli.js"
      break
    fi
  done

  if [ -n "$MEMORY_CLI" ]; then
    node "$MEMORY_CLI" search "relevant keywords"
  elif [ -d "memory/exports" ]; then
    # Fallback: search shareable markdown exports (git-trackable)
    if command -v rg >/dev/null 2>&1; then
      rg -n "relevant keywords" memory/exports
    else
      grep -R "relevant keywords" memory/exports
    fi
  fi

IF similar problem solved before:
  - Review the solution
  - Apply or adapt it
  - Skip re-solving known problems

This step is SILENT - no user notification needed.
```

### Step 1.1: TDD Gate + Implement
```
Run tdd skill for implementation tasks:
  - Define a small test plan (happy path, edge, error, regression).
  - Write failing test first (RED) and record failing evidence.
  - Implement the minimum code change to pass (GREEN).
  - Refactor safely while tests stay green.

Only skip this step if the user explicitly says tests are out of scope.
```

### Step 1.2: Test Loop
```
Run tests
IF tests fail:
    Analyze failure
    Fix automatically if clear
    GOTO Step 1.2
IF tests pass:
    Continue to Step 1.3
```

### Step 1.3: Review + Auto-Fix
```
Run reviewer skill
- Finds: logic errors, regressions, security issues, file placement
- FIXES AUTOMATICALLY (don't ask permission)

IF fixes made:
    GOTO Step 1.2 (re-test)
IF needs human decision:
    PAUSE - present options, wait for input
IF clean:
    Continue to Step 1.4
```

### Step 1.4: Suggest + Auto-Implement
```
Run suggest skill
- Identifies improvements
- AUTO-IMPLEMENTS safe ones (low effort, no behavior change)
- PRESENTS risky ones to user

IF auto-implemented:
    GOTO Step 1.2 (re-test)
IF needs human decision:
    PAUSE - present suggestions, wait for input
    User chooses: implement some/all/none
    IF implementing: GOTO Step 1.2
IF clean or user says proceed:
    Continue to Phase 2 or 3
```

### Step 1.5: Memory Save (AUTOMATIC)
```
IF key decision was made (architecture, pattern, fix):
  # Portable: resolve memory CLI location (prefers ICA_HOME when set)
  MEMORY_CLI=""
  for d in "${ICA_HOME:-}" "$HOME/.codex" "$HOME/.claude"; do
    if [ -n "$d" ] && [ -f "$d/skills/memory/cli.js" ]; then
      MEMORY_CLI="$d/skills/memory/cli.js"
      break
    fi
  done

  if [ -n "$MEMORY_CLI" ]; then
    node "$MEMORY_CLI" write \
      --title "..." --summary "..." \
      --category "architecture|implementation|issues|patterns" \
      --importance "high|medium|low"
  else
    # Fallback: write a shareable export (no SQLite/embeddings).
    # Use a timestamp-based ID to avoid collisions.
    CATEGORY="architecture" # or implementation|issues|patterns
    SLUG="short-title-slug"
    TS="$(date -u +%Y%m%d%H%M%S)"
    mkdir -p "memory/exports/$CATEGORY"
    cat > "memory/exports/$CATEGORY/mem-$TS-$SLUG.md" << 'EOF'
---
id: mem-YYYYMMDDHHMMSS-short-title-slug
title: "..."
tags: []
category: architecture
importance: medium
created: YYYY-MM-DDTHH:MM:SSZ
---

# ...

## Summary
...
EOF
  fi

This step is SILENT - auto-saves significant decisions.
```

### Step 1.6: Completion Validation Gate (MANDATORY)
```
Before marking work complete:
  - run `validate` skill checks
  - verify test/review evidence is present
  - run backend-aware tracking verification
  - ensure work-item state transition is valid in selected backend

IF gate fails:
  - keep item in `in_progress` or move to `blocked` with reason
  - DO NOT mark complete
  - resolve failure, then re-run gate
```

**Exit:** Tests pass, no review findings, suggestions addressed

## Phase 2: Deployment (AUTONOMOUS)

Skip if no deployment required.

### Step 2.1: Deploy
```
Deploy to target environment
```

### Step 2.2: Test Loop
```
Run deployment tests
IF fail:
    Analyze and fix if clear
    GOTO Step 2.1
```

### Step 2.3: Review + Auto-Fix
```
Run reviewer skill
FIXES AUTOMATICALLY
IF fixes made: GOTO Step 2.2
```

### Step 2.4: Commit
```
Run commit-pr skill
Ensure git-privacy rules followed
```

**Exit:** Deployment tests pass, no findings, committed

## Phase 3: Pull Request (to dev)

**PRs go to `dev` branch, NOT `main`.**

### Step 3.1: Create PR to dev
```
Run commit-pr skill
MUST use: gh pr create --base dev
NEVER: gh pr create --base main (unless releasing)
```

### Step 3.2: Review + Auto-Fix (in temp folder)
```
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"
gh pr checkout <PR-number>

Run reviewer skill (post-PR stage)
- Run project linters (Ansible, HELM, etc.)
- FIXES AUTOMATICALLY
- Push fixes to PR branch

IF fixes made: GOTO Step 3.2 (re-review)
IF needs human: PAUSE
IF clean: Continue
```

**Required behavior (closed-loop):**
- Stage 3 MUST be executed by a dedicated reviewer subagent (recommended: a reviewer-only subagent via your Task/sub-agent mechanism).
- Reviewer Stage 3 MUST loop until the PR is clean:
  - If findings exist: fix + push commits to the PR branch, then restart Stage 3 in a fresh temp checkout.
  - When clean: post `ICA-REVIEW-RECEIPT` with `Findings: 0` and `NO FINDINGS` for the current head SHA.
  - Optional GitHub approvals (GitHub-style approvals mode):
    - Default is self-review-and-merge: **GitHub required approvals may remain at 0**, while ICA Stage 3 receipt remains
      the required review gate.
    - If `workflow.require_github_approval=true`, the reviewer subagent should also try to add a GitHub approval using
      `gh pr review <PR-number> --approve ...` (skip if already approved).
      - If PR author == current authenticated `gh` user: GitHub forbids approving your own PR (server-side rule). Skip.
        If repo rules require approvals, a second GitHub identity/bot is required for approvals.

### Step 3.3: Suggest + Auto-Implement
```
Run suggest skill on full PR diff
- AUTO-IMPLEMENTS safe improvements
- Push to PR branch
- PRESENTS risky ones to user

IF auto-implemented: GOTO Step 3.2 (re-review)
IF needs human: PAUSE, wait for decision
IF clean or user says proceed: Continue
```

### Step 3.4: Merge Approval (Default: Pause, Optional Auto-Merge)
Default behavior:
```
WAIT for explicit user approval
DO NOT merge without: "merge", "approve", "LGTM", or similar
```

Optional auto-merge (Skills-level standing approval):
- If `workflow.auto_merge=true` in the current AgentTask/workflow context
- AND the PR targets `dev`
- AND the reviewer Stage 3 ICA-REVIEW receipt exists for the current head SHA (PASS)
- AND the receipt includes `Findings: 0` and `NO FINDINGS`
- AND checks are green

Then the agent MAY proceed to merge without an additional chat approval.

**Never auto-merge to `main`** unless performing an explicitly requested release workflow.

**Exit:** No findings, suggestions addressed, user approved, merged to dev

## Phase 4: Release (dev → main)

**Only when user explicitly requests a release.**

### Step 4.1: Verify dev is stable
```
Ensure dev branch:
- All tests pass
- No pending critical issues
- User confirms ready for release
```

### Step 4.2: Create Release PR
```
gh pr create --base main --title "release: vX.Y.Z"
Include release notes and changelog
```

### Step 4.3: Await Release Approval
```
WAIT for explicit user approval
User must say "release", "merge to main", or similar
```

### Step 4.4: Tag and Publish
```
After merge to main:
git tag vX.Y.Z
git push origin vX.Y.Z
gh release create vX.Y.Z
```

**Exit:** Released to main, tagged, published

## Quality Gates (BLOCKING)

**These gates are MANDATORY. You CANNOT proceed without passing them.**

| Gate | Requirement | Blocked Actions |
|------|-------------|-----------------|
| Pre-implementation | Work item exists, prioritized, dependencies known, tracking backend updated | Start implementation |
| Pre-run transition | `validate` checks pass + backend-aware tracking verification passes | Move item to `in_progress` |
| Pre-commit | Tests pass + reviewer skill clean + `validate` checks pass + backend-aware tracking verification passes | `git commit`, `git push` |
| Pre-PR-create | target branch valid + `validate` checks pass + backend-aware tracking verification passes | `gh pr create` |
| Pre-deploy | Tests pass + reviewer skill clean | Deploy to production |
| Pre-complete transition | `validate` checks pass + state transition rules satisfied + tracking verification passes | Mark item `completed` |
| Pre-merge | reviewer Stage 3 PASS receipt + checks green + `validate` checks pass + backend-aware tracking verification passes + user approval | `gh pr merge` |
| Pre-release-publish | release PR merged + tag pushed + release validation checks pass + explicit publish approval (non-draft) | publish non-draft release |

### Gate Enforcement

```
IF attempting commit/push/PR without running reviewer skill:
  STOP - You are violating the process
  GO BACK to Step 1.3 (Review + Auto-Fix)
  DO NOT proceed until reviewer skill passes

IF attempting commit/push/PR/merge/release without validation + tracking checks:
  STOP - Transition gate failed
  RUN validate skill + backend-aware tracking verification
  DO NOT proceed until gate passes
```

**Skipping review is a process violation, not a shortcut.**

## When to Pause

**PAUSE for:**
- Architectural decisions affecting multiple components
- Ambiguous requirements needing clarification
- Multiple valid approaches with trade-offs
- High-risk changes that could break things
- Large changes (always ask before proceeding)
- **Merge approval** (always)

**DO NOT pause for:**
- Fixing typos, formatting, naming
- Adding missing error handling
- Fixing security vulnerabilities
- Moving misplaced files
- Removing unused code
- Extracting duplicated code
- Adding null checks

## Large-Change Confirmation Gate (MANDATORY)

You MUST ask for explicit confirmation before larger changes, regardless of other settings.

Treat as larger changes:
- cross-repository changes
- creation of new branches/worktrees or branch strategy changes
- broad refactors spanning multiple components
- release operations (merge to `main`, tagging, publishing)
- any change set with non-obvious blast radius

## Output Contract

When this skill runs, produce:
1. whether actionable findings/comments were detected and why
2. pipeline setting resolution (`work_item_pipeline_enabled`, `work_item_pipeline_mode`)
3. orchestration summary for create -> plan -> run (including any confirmations required by mode)
4. selected next actionable item and current state transition result
5. gate summary (validation, TDD phase status, tracking verification)
6. next action (`continue` / `blocked` / `done`)

## Commands

**Start (runs autonomously):**
```
process skill
```

**Force pause at every step (L1 mode):**
```
process skill with L1 autonomy
```

**Check status:**
```
Where am I in the process?
```
