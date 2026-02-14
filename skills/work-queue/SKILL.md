---
name: work-queue
description: Compatibility skill for legacy queue commands. Delegates to create-work-items, plan-work-items, and run-work-items while preserving .agent/queue fallback and config-driven tracking backend selection.
version: 10.2.14
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# Work Queue Skill

Compatibility layer for legacy queue phrasing.

Canonical skills:
- `create-work-items`
- `plan-work-items`
- `run-work-items`

Use this skill when users still ask for "work queue" directly.

## Tracking Backend Selection (MANDATORY)

Before queue operations, resolve backend in this strict order:

1. Project config: `.agent/tracking.config.json`
2. Global config: `${ICA_HOME}/tracking.config.json`
3. Agent-home fallback config:
- `$HOME/.codex/tracking.config.json`
- `$HOME/.claude/tracking.config.json`
4. Auto-detect GitHub (skills + auth)
5. Fallback: local `.agent/queue/`

No UI or CLI integration is required. The config file is the explicit agent signal.

## Tracking Config Contract

Supported minimal schema:

```json
{
  "issue_tracking": {
    "provider": "github",
    "enabled": true,
    "repo": "owner/repo",
    "fallback": "file-based"
  }
}
```

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

GH_READY=0
if [ "$TRACKING_PROVIDER" = "github" ] || [ -z "$TRACKING_PROVIDER" ]; then
  for d in "${ICA_HOME:-}" "$HOME/.codex" "$HOME/.claude"; do
    if [ -n "$d" ] && \
       [ -f "$d/skills/github-issues-planning/SKILL.md" ] && \
       [ -f "$d/skills/github-state-tracker/SKILL.md" ] && \
       gh auth status >/dev/null 2>&1; then
      TRACKING_PROVIDER="github"
      GH_READY=1
      break
    fi
  done
fi

[ -z "$TRACKING_PROVIDER" ] && TRACKING_PROVIDER="file-based"
```

Routing:
- `github`: use `github-issues-planning` + `github-state-tracker`
- `linear` / `jira`: use provider-specific skills when available (future), else fallback
- `file-based`: use `.agent/queue/`

Always fallback to `.agent/queue/` if configured backend is unavailable.

## When to Invoke (Automatic)

| Trigger | Action |
|---------|--------|
| Large task detected | Break down into work items |
| Work item completed | Check for next item |
| User asks "what's left?" | List remaining items |
| Multiple tasks identified | Queue for sequential/parallel execution |

## Directory Structure

```
.agent/
└── queue/
    ├── 001-pending-implement-auth.md
    ├── 002-pending-write-tests.md
    └── 003-completed-setup-db.md
```

## Setup (Automatic)

On first use, the skill ensures:

1. **Create directory**: `mkdir -p .agent/queue`
2. **Add to .gitignore** (if not present):
   ```
   # Agent work queue (local, not committed)
   .agent/
   ```
3. **If GitHub backend selected**:
- Validate with `gh auth status`.
- Resolve target repository (`--repo owner/repo` or current upstream).
4. **If non-file backend unavailable**:
- Log degraded mode and switch to `.agent/queue/`.

## Work Item Format

Each work item is a simple markdown file:

```markdown
# [Title]

**Status**: pending | in_progress | completed | blocked
**Priority**: high | medium | low
**Assignee**: developer | reviewer | etc.

## Description
What needs to be done.

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Notes
Any relevant context.
```

## File Naming Convention

```
NNN-STATUS-short-description.md
```

Examples:
- `001-pending-implement-auth.md`
- `002-in_progress-write-tests.md`
- `003-completed-setup-database.md`

## Operations

### Add Work Item
```bash
# Create new work item
echo "# Implement authentication" > .agent/queue/001-pending-implement-auth.md
```

GitHub backend equivalent:
```bash
# Use github-issues-planning skill workflow to create typed issue
# type/work-item + priority label + optional parent issue
# IMPORTANT: "Parent: #123" body text is trace-only.
# Create and verify native GitHub parent/child relationship separately.
```

### Update Status
```bash
# Rename to reflect status change
mv .agent/queue/001-pending-implement-auth.md .agent/queue/001-in_progress-implement-auth.md
```

### List Pending Work
```bash
ls .agent/queue/*-pending-*.md 2>/dev/null
```

GitHub backend equivalent:
```bash
# Use github-state-tracker to generate prioritized "open work" summary
```

### List All Work
```bash
ls -la .agent/queue/
```

### Complete Work Item
```bash
mv .agent/queue/001-in_progress-implement-auth.md .agent/queue/001-completed-implement-auth.md
```

GitHub backend equivalent:
```bash
# Update issue status labels / close issue through github-issues-planning workflow
```

## Platform Behavior

| Platform | Preferred Tracking | Fallback |
|----------|--------------------|----------|
| All agents | Configured provider (`github`/`linear`/`jira`) | `.agent/queue/` |
| Claude Code | TodoWrite display + selected backend | `.agent/queue/` persistence |
| Codex CLI | Selected backend | `.agent/queue/` |
| Gemini CLI | Selected backend | `.agent/queue/` |

## Workflow Integration

1. **PM breaks down story**:
- `provider=github` and ready → create GitHub typed issues
- For parent/child links on GitHub: create native relationship and verify it exists
- other provider unavailable or `provider=file-based` → create `.agent/queue/` files
2. **Agent picks next item**:
- GitHub issue in priority order or next pending local file
3. **Work completes**:
- close/update GitHub issue or rename local file to `completed`
4. **Autonomy skill checks**:
- continue using selected backend

## Queue Commands

Human-friendly action mapping:
- **create** -> add/classify work items
- **plan** -> prioritize/order/dependency-manage items
- **run** -> execute next actionable item(s)

Canonical delegation:
- `create` -> `create-work-items`
- `plan` -> `plan-work-items`
- `run` -> `run-work-items`

**Check queue status:**
```
What work is in the queue?
Show pending work items
```

**Add to queue:**
```
Add "implement login" to work queue
Queue these tasks: auth, tests, deploy
```

**Process queue:**
```
Work through the queue
Execute next work item
```

## Integration

Works with:
- autonomy skill - Automatic continuation through queue
- process skill - Quality gates between items
- pm skill - Story breakdown into queue items
- create-work-items skill - Typed item creation across backends
- plan-work-items skill - Prioritization, dependencies, hierarchy checks
- run-work-items skill - Next-item execution and state tracking
- github-issues-planning skill - Typed GitHub issue creation and hierarchy
- github-state-tracker skill - Continuous status/reporting and prioritization
