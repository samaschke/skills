---
name: workflow
description: Activate when checking workflow step requirements, resolving workflow conflicts, or ensuring proper execution sequence. Applies workflow enforcement patterns and validates compliance.
version: 10.2.14
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# Workflow Skill

Apply workflow enforcement patterns and ensure proper execution sequence.

## When to Use

- Checking workflow step requirements
- Resolving workflow conflicts
- Ensuring proper execution sequence
- Validating workflow compliance

## Standard Workflow Steps

1. **Task** - Create AgentTask via Task tool
2. **Create Work Items** - Run `create-work-items` to define typed units (epic/story/feature/bug/finding/work-item)
3. **Plan Work Items** - Run `plan-work-items` to prioritize, dependency-map, and set parent/child relationships
4. **Review Plan** - Validate approach before execution
5. **Run Work Items** - Run `run-work-items` to execute selected actionable item(s)
6. **Review Execute** - Validate implementation
7. **Document** - Update documentation

## GitHub Relationship Rule

For GitHub backends, parent-child structure must be native GitHub relationships.

- `Parent: #123` issue body text is trace-only.
- Native relationship must be created via API/UI workflow.
- Planning step is incomplete until relationship is verified.

## Workflow Enforcement

When `enforcement.workflow.enabled` is true:
- Steps must be completed in order
- Skipping steps is blocked
- Each step has allowed tools

### Step Tool Restrictions

| Step | Allowed Tools |
|------|---------------|
| Task | Task |
| Plan | Plan, Read, Grep, Glob |
| Review Plan | Review, Read |
| Execute | Edit, Write, Bash, ... |
| Review Execute | Review, Read |
| Document | Document, Write, Edit |

## Workflow Resolution

### Conflict Resolution
When steps conflict:
1. Identify the blocking step
2. Complete required predecessor
3. Document resolution
4. Continue workflow

### Skip Justification
If skip is truly necessary:
1. Document reason for skip
2. Get explicit user approval
3. Note in completion summary
4. Flag for review

## Workflow Settings

Check workflow config:
```
/ica-get-setting enforcement.workflow.enabled
/ica-get-setting enforcement.workflow.steps
```

## Integration with AgentTasks

AgentTasks include workflow stage:
```yaml
agentTask:
  workflow:
    current_step: "Execute"
    completed_steps: ["Task", "Plan", "Review Plan"]
    remaining_steps: ["Review Execute", "Document"]
```

## Workflow Completion

Workflow is complete when:
- All required steps executed
- No blocking conditions remain
- Documentation updated
- Summary generated
