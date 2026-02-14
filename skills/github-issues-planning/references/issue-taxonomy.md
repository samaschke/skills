# GitHub Issue Taxonomy

Use this reference to keep issue structure consistent across repositories.

## Required Labels

- Type labels:
  - `type/epic`
  - `type/story`
  - `type/bug`
  - `type/finding`
  - `type/work-item`
- Priority labels:
  - `priority/p0` (critical)
  - `priority/p1` (high)
  - `priority/p2` (medium)
  - `priority/p3` (low)

## Parent-Child Pattern

For child issues, include this line in body:

```text
Parent: #<issue-number>
```

For epic parents, keep a task list of linked children:

```markdown
- [ ] #123
- [ ] #124
- [ ] #125
```

## Example Commands

CLI-first (preferred for token efficiency):

```bash
<PYTHON> skills/github-issues-planning/scripts/gh_issue_create.py \
  --type epic \
  --title "Epic: GitHub planning workflow" \
  --priority p1
```

The command above defaults to the current upstream repo. Add `--repo owner/repo` to target another project.
Set `<PYTHON>` as `python3` on macOS/Linux or `py -3` on Windows.

MCP fallback:

```text
Use GitHub MCP tools like mcp__github__create_issue and mcp__github__update_issue.
Route through mcp-proxy for centralized auth and reduced token exposure.
```

```bash
<PYTHON> skills/github-issues-planning/scripts/gh_issue_create.py \
  --type story \
  --title "Story: Add reporting skill" \
  --priority p2 \
  --parent 123
```
