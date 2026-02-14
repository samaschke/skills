---
name: "autonomy"
description: "Activate when a subagent completes work and needs continuation check. Activate when a task finishes to determine next steps or when detecting work patterns in user messages. Governs automatic work continuation and queue management."
category: "process"
scope: "development"
subcategory: "orchestration"
tags:
  - autonomy
  - continuation
  - tracking
  - queue
version: "10.2.14"
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

## Autonomy Levels

### L1 - Guided
- Confirm before each action
- Wait for explicit user instruction
- No automatic continuation

### L2 - Balanced (Default)
- Add detected work to selected backend queue
- Confirm significant changes
- Continue routine tasks automatically

### L3 - Autonomous
- Execute without confirmation
- **Continue to next queued item on completion**
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
5. If yes → Add to selected backend queue, execute next pending item
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

Level stored in `autonomy.level` (L1/L2/L3)
