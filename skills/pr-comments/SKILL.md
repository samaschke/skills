---
name: pr-comments
description: Ensures pull request descriptions and commit messages are written for human reviewers — clear, professional, and without any AI attribution. This skill is automatically applied when creating PRs or commits. Use when the user says "review my PR description", "improve PR description", or "check commit message".
user-invocable: false
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# PR & Commit Quality Standards

This skill enforces quality standards for pull request descriptions and commit messages. It is background knowledge that Claude applies automatically when creating commits or PRs.

## CRITICAL: No AI Attribution

**NEVER include any of the following in commits, PRs, or comments:**
- `Co-Authored-By: Claude` or any Claude/AI attribution
- Any mention of "Claude", "Claude Code", "AI", "Assistant", "Anthropic", or "LLM"
- Any indication that code was AI-generated or AI-assisted
- Footer lines like "Generated with Claude Code"
- Emoji-heavy descriptions that signal AI authorship

## Pull Request Descriptions

### Structure

Every PR description must be written so a human reviewer can understand **what changed and why** without reading every line of code.

```markdown
## Summary
Brief explanation of what this PR accomplishes and WHY it was needed.
Not just "what files changed" but the motivation and context.

## Changes
- Specific, concrete descriptions of what was modified
- Group related changes together
- Mention files/modules by name when helpful
- Call out any non-obvious design decisions

## Test Plan
- [ ] How to verify this works
- [ ] Edge cases considered
- [ ] Manual testing steps if applicable
```

### Guidelines

1. **Lead with the WHY** — Reviewers need context, not just a list of file changes
2. **Be specific** — "Updated auth flow" is bad. "Added token refresh to prevent session expiry during long operations" is good
3. **Mention trade-offs** — If you chose approach A over B, briefly explain why
4. **Flag risks** — Call out anything reviewers should pay special attention to
5. **Keep it proportional** — A one-line fix needs a one-line description. A major refactor needs thorough explanation
6. **No filler** — Don't pad with obvious statements like "This PR improves the codebase"

### Bad Examples (avoid)

```
## Summary
This PR updates several files to improve functionality.

## Changes
- Updated file1.ts
- Updated file2.ts
- Added file3.ts
```

### Good Examples

```
## Summary
Fixes session timeout during long-running report generation. Users were
getting logged out mid-export because the auth token expired before the
report finished building.

## Changes
- Added background token refresh in `src/auth/token-manager.ts`
- Report generation now signals active usage to prevent idle timeout
- Added 30s grace period before hard session termination

## Test Plan
- [ ] Generate a report that takes >15min, verify no logout
- [ ] Verify normal session timeout still works for idle users
- [ ] Check token refresh doesn't create duplicate sessions
```

## Commit Messages

### Format

```
<type>: <concise description of what and why>

<optional body for context that doesn't fit in the subject line>
```

### Types
- `feat`: New feature or capability
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code restructuring without behavior change
- `test`: Test additions or fixes
- `chore`: Build, CI, dependency updates
- `perf`: Performance improvement

### Guidelines

1. **Subject line under 72 characters**
2. **Use imperative mood** — "Add feature" not "Added feature" or "Adds feature"
3. **Don't just describe the diff** — "fix: Prevent duplicate webhook delivery on retry" not "fix: Add check in webhook handler"
4. **Body explains WHY when non-obvious** — The diff shows what changed; the message explains the reasoning

## Azure DevOps PR Specifics

When creating PRs in Azure DevOps via `mcp__azureDevOps__create_pull_request`:

- **Title**: Use the same `<type>: <description>` format as commits
- **Description**: Use the Summary / Changes / Test Plan structure in markdown
- **Work Items**: Link related work items when available
- **Reviewers**: Add if the user specifies them

## Reminders

1. Write as if a teammate wrote it — natural, professional, no AI tells
2. Every description should answer: "If I came back to this in 6 months, would I understand what happened and why?"
3. Match the tone and style of existing PRs in the repository
