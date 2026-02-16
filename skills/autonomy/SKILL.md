---
name: autonomy
description: "Activate when a subagent completes work and needs continuation check. Activate when a task finishes to determine next steps or when detecting work patterns in user messages. Governs automatic work continuation and queue management."
category: "process"
scope: "development"
subcategory: "orchestration"
tags:
  - autonomy
  - continuation
  - tracking
  - queue
version: "10.2.16"
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# Autonomy Skill

**Invoke automatically** after subagent completion or when deciding next actions.

## When to Invoke (Automatic)

| Trigger | Action |
|---------|--------|
| Subagent returns completed work | Check selected tracking backend for next item |
| Task finishes successfully | Update status, pick next pending item |
| Work pattern detected in user message | Create work items if L2/L3 |
| Multiple tasks identified | Queue all, parallelize if L3 |

## Acceptance Tests

| Test ID | Type | Prompt / Condition | Expected Result |
| --- | --- | --- | --- |
| AUT-T1 | Positive trigger | "Continue with autonomy after this item completes" | skill triggers |
| AUT-T2 | Positive trigger | "Run the next queued item automatically" | skill triggers |
| AUT-T3 | Negative trigger | "Explain what autonomy levels mean" | skill does not auto-dispatch work |
| AUT-T4 | Behavior | no system autonomy level in user ica-config | ask user to set system level (`L1`/`L2`/`L3`), persist choice |
| AUT-T5 | Behavior | no project autonomy level in project ica-config | ask user to set project level (`follow-system`/`L1`/`L2`/`L3`), persist choice |
| AUT-T6 | Behavior | project level is `follow-system` | effective level resolves to system level |
| AUT-T7 | Behavior | project level explicitly set | effective level uses project level override |

## Autonomy Level Configuration (MANDATORY)

Autonomy level MUST be resolved from `ica.config.json` (not tracking config).

Level values:
- `L1`
- `L2`
- `L3`

Project-only value:
- `follow-system`

Required keys:
- System (user) config key: `autonomy.system_level` (`L1` | `L2` | `L3`, default `L2`)
- Project config key: `autonomy.project_level` (`follow-system` | `L1` | `L2` | `L3`, default `follow-system`)

Resolution order:
1. Resolve user (system) config file:
   - `${ICA_HOME}/ica.config.json`
   - `$HOME/.codex/ica.config.json`
   - `$HOME/.claude/ica.config.json`
2. Resolve project config file:
   - `./ica.config.json` (project root)
3. Read `autonomy.system_level` from user config.
4. Read `autonomy.project_level` from project config.
5. Determine effective level:
   - if `autonomy.project_level` is `L1`/`L2`/`L3`, use that
   - if `autonomy.project_level` is `follow-system`, use `autonomy.system_level`

Bootstrap prompts (required if missing):
- If `autonomy.system_level` is missing:
  - ask: "No system autonomy level is configured. Set system autonomy level to `L2` (recommended), `L1`, or `L3`?"
  - persist in user `ica.config.json`
- If `autonomy.project_level` is missing:
  - ask: "No project autonomy level is configured. Set project autonomy level to `follow-system` (recommended), `L1`, `L2`, or `L3`?"
  - persist in project `ica.config.json`

Persistence rules:
- System level MUST be written to user `ica.config.json`.
- Project level MUST be written to project `ica.config.json`.
- If both are missing, ask and persist both before auto-dispatch.
- Effective default behavior after bootstrap is `L2` via `system_level=L2` and `project_level=follow-system`.

Example user `ica.config.json`:
```json
{
  "autonomy": {
    "system_level": "L2"
  }
}
```

Example project `ica.config.json`:
```json
{
  "autonomy": {
    "project_level": "follow-system"
  }
}
```

Compatibility:
- If legacy `autonomy.level` exists and `autonomy.system_level` is missing, treat legacy value as system level for this run and persist it as `autonomy.system_level`.

## Tracking Backend Selection (MANDATORY)

Resolve backend with config-first precedence:

1. Project config: `.agent/tracking.config.json`
2. Global config: `${ICA_HOME}/tracking.config.json`
3. Agent-home config fallback:
- `$HOME/.codex/tracking.config.json`
- `$HOME/.claude/tracking.config.json`
4. Auto-detect GitHub backend
5. Fallback: `.agent/queue/`

Provider values:
- `github`
- `linear` (future)
- `jira` (future)
- `file-based`

Detection pattern:

```bash
TRACKING_PROVIDER=""
for c in ".agent/tracking.config.json" \
         "${ICA_HOME:-}/tracking.config.json" \
         "$HOME/.codex/tracking.config.json" \
         "$HOME/.claude/tracking.config.json"; do
  if [ -n "$c" ] && [ -f "$c" ]; then
    TRACKING_PROVIDER="$(python3 - <<'PY' "$c"
import json,sys
cfg=json.load(open(sys.argv[1]))
it=cfg.get("issue_tracking",{})
print(it.get("provider","") if it.get("enabled",True) else "file-based")
PY
)"
    break
  fi
done

[ -z "$TRACKING_PROVIDER" ] && TRACKING_PROVIDER="file-based"
```

## Configuration Bootstrap (MANDATORY)

Before continuation or dispatch, ensure a persisted tracking configuration exists and is used:
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

If TDD skill is active (locally or globally), ask explicitly for this scope before auto-dispatch:
- "TDD is active. Apply TDD for this work scope? (yes/no)"

Persistence rule:
- If `tdd.enabled` is missing on first TDD-related invocation, ask for the default and persist it in the selected config file.
- Scope-level answer overrides stored default for the current run.

## Dispatch Trigger And Interrupt Policy (MANDATORY)

Resolve from ICA config hierarchy:
- `autonomy.dispatch_trigger` (`on_completion` | `immediate_if_idle`, default `on_completion`)
- `autonomy.interrupt_policy` (`p0_only` | `always_confirm` | `never_preempt`, default `p0_only`)

Policy behavior:
- `on_completion`: dispatch next item only after current `in_progress` item reaches terminal state (`completed` or `blocked`).
- `immediate_if_idle`: dispatch immediately only when no item is `in_progress`.
- `p0_only`: preempt only for `p0`/security/data-loss/production-outage.
- `always_confirm`: ask before any preemptive switch.
- `never_preempt`: never switch away from current `in_progress` item.

## Autonomy Levels

### L1 - Guided
- Confirm before each action
- Wait for explicit user instruction
- No automatic continuation

### L2 - Balanced (Default)
- Add detected work to selected backend queue
- Confirm significant changes
- Continue routine tasks automatically without interrupting active `in_progress` work

### L3 - Autonomous
- Execute without confirmation
- **Continue to next queued item on completion (non-preemptive)**
- Discover and queue related work
- Maximum parallel execution

## Continuation Logic (L3)

After work completes:
```
1. Run continuation pre-check gate on selected backend
   - Run `validate` skill checks for the just-finished work item
   - Run backend-aware tracking verification for the selected backend
   - If gate fails: mark item `blocked`, report blocker, STOP auto-continuation
2. Mark current item completed in selected backend
   - GitHub: update/close issue via github-issues-planning workflow
   - Local: rename file in .agent/queue/
3. Check: Are there pending items in selected backend?
4. Check: Did the work reveal new tasks?
5. If yes → Add to selected backend queue, run create + plan triage, then dispatch next pending item per dispatch trigger and interrupt policy
6. Before dispatching next item, run readiness gate:
   - next item is unblocked and has required fields (`type`, `priority`)
   - TDD phase ordering is respected when applicable (`RED` -> `GREEN` -> `REFACTOR`)
   - backend-aware tracking verification is still passing
7. If no more work → Report completion to user
```

## Validation And Check Gates (MANDATORY)

Autonomy must enforce gates on every transition:
- Pre-close gate: do not close/complete current item until validation + tracking checks pass.
- Pre-dispatch gate: do not auto-dispatch next item until readiness + dependency checks pass.
- Fail-closed behavior: any failed gate halts continuation and surfaces blocker details.

Human-friendly action mapping:
- **create** when new work is discovered
- **plan** when reprioritization/dependency updates are needed
- **run** when selecting and executing the next actionable item

## Work Detection

**Triggers queue addition:**
- Action verbs: implement, fix, create, deploy, update, refactor
- Role skill patterns: "developer implement X"
- Continuation: testing after implementation

**Direct response (no queue):**
- Questions: what, how, why, explain
- Status checks
- Simple lookups

## In-Progress Intake Rule (MANDATORY)

- If work is already `in_progress`, newly detected findings/comments are intake-only:
  - create/append items in selected backend
  - re-run planning/triage
  - do not dispatch these new items immediately
- Continue the active `in_progress` item first.
- Only preempt when interrupt policy allows; otherwise dispatch on completion.

## Queue Integration

Uses backend-aware tracking:
- GitHub backend: typed issues + state reports
- Linear/Jira backend: provider-native items (when supported)
- Local backend: `.agent/queue/` files

Local `.agent/queue/` remains cross-platform fallback:
- Claude Code: TodoWrite for display + queue for persistence
- Other agents: Queue files directly

See:
- `create-work-items` for creating newly discovered items
- `plan-work-items` for reprioritization and dependency refresh
- `run-work-items` for selecting and executing next actionable item
- canonical create/plan/run work-item skills for queue management
- `github-issues-planning` for issue lifecycle operations
- `github-state-tracker` for prioritized status retrieval

## Configuration

Resolved effective level comes from:
- `autonomy.system_level` in user `ica.config.json`
- `autonomy.project_level` in project `ica.config.json`
- `follow-system` means project uses system setting

Effective-level rule:
- `project_level` in (`L1`, `L2`, `L3`) overrides system level
- `project_level=follow-system` uses `system_level`
- if missing, bootstrap must ask and persist values before dispatch

Additional behavior keys:
- `autonomy.dispatch_trigger` (`on_completion` | `immediate_if_idle`)
- `autonomy.interrupt_policy` (`p0_only` | `always_confirm` | `never_preempt`)

## Validation Checklist

- [ ] Acceptance tests were defined before behavior changes
- [ ] Missing `autonomy.system_level` triggers user prompt and persistence
- [ ] Missing `autonomy.project_level` triggers user prompt and persistence
- [ ] `follow-system` correctly resolves to system level
- [ ] Effective level controls dispatch behavior without preempting active `in_progress` work
- [ ] `ica.config.json` files are updated at correct scopes (user vs project)
