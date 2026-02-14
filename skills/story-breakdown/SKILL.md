---
name: story-breakdown
description: Activate when user presents a large story or epic that needs decomposition. Activate when a task spans multiple components or requires coordination across specialists. Creates work items in selected tracking backend (config-driven), with .agent/queue/ fallback.
version: 10.2.14
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# Story Breakdown Skill

Break large stories into backend-aware work items.

## Tracking Backend Selection (MANDATORY)

Resolve tracking backend via config-first precedence:
1. `.agent/tracking.config.json`
2. `${ICA_HOME}/tracking.config.json`
3. `$HOME/.codex/tracking.config.json` or `$HOME/.claude/tracking.config.json`
4. Fallback: `.agent/queue/`

When backend is `github`, use `github-issues-planning` to create typed issue hierarchies.
When backend is unsupported/unavailable, use `.agent/queue/`.

## When to Break Down

- Multi-component scope
- Requires sequential execution phases
- Dependencies between work items
- More than 2-3 distinct tasks

## Breakdown Process

1. **Analyze scope** - Identify distinct work units
2. **Define items** - Create work item for each unit
3. **Set dependencies** - Note which items block others
4. **Assign roles** - Specify the role skill for execution (for example `developer`, `reviewer`)
5. **Add to queue** - Create items in selected backend (`github`/future provider/file-based)
6. **Canonical flow** - Use `create-work-items` for creation and `plan-work-items` for ordering/dependencies

## Work Item Creation

For file-based backend, create in `.agent/queue/`:

```markdown
# [Short Title]

**Status**: pending
**Priority**: high | medium | low
**Assignee**: developer | reviewer | etc.
**Blocks**: 002, 003 (optional)
**BlockedBy**: none | 001 (optional)

## Description
What needs to be done.

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

## Splitting Strategies

### By Component
- `001-pending-frontend-auth.md`
- `002-pending-backend-api.md`
- `003-pending-database-schema.md`

### By Phase
- `001-pending-core-functionality.md`
- `002-pending-error-handling.md`
- `003-pending-tests.md`

### By Domain
- `001-pending-authentication.md`
- `002-pending-data-processing.md`
- `003-pending-api-integration.md`

## Example Breakdown

Story: "Add user authentication"

```
.agent/queue/
├── 001-pending-setup-auth-database.md
├── 002-pending-implement-login-api.md
├── 003-pending-add-frontend-forms.md
└── 004-pending-write-auth-tests.md
```

GitHub backend equivalent:
- Parent epic issue: authentication initiative
- Child story/work-item issues linked via native GitHub parent-child relationship
- `Parent: #123` body text is trace-only and does not create the relationship
- Verify parent/child link exists before considering decomposition complete

With dependencies:
- 002 blocked by 001
- 003 blocked by 002
- 004 blocked by 002, 003

## Validation

Before execution:
- [ ] Each item has clear scope
- [ ] Dependencies are noted
- [ ] Roles assigned
- [ ] Success criteria defined
- [ ] No circular dependencies
