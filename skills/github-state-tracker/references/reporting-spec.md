# GitHub Reporting Spec

Use this format for consistent state-tracking outputs.

## Inputs

- Repository: `<owner>/<repo>`
- Issue source:
  - preferred: `gh issue list --json ...` via local script
  - fallback: GitHub MCP list/query tools through mcp-proxy
- Required labels:
  - `type/*`
  - `priority/*`
- Parent relation marker in body:
  - `Parent: #<number>`

## Required Outputs

1. Normalized JSON snapshot with:
- issue number/title/url/state
- type, priority, parent
- assignees, created/updated/closed timestamps

2. Markdown report with:
- totals by state
- totals by type
- totals by priority
- delta: new/closed/changed since previous snapshot
- prioritized open issue table

## Continuous Tracking Pattern

CLI-first (preferred for token efficiency):

```bash
<PYTHON> skills/github-state-tracker/scripts/gh_state_report.py \
  --snapshot-dir .agent/queue/github-state \
  --output-json .agent/queue/github-state/latest-export.json \
  --output-md summaries/github-state-report.md
```

The command above defaults to the current upstream repo. Add `--repo owner/repo` to target another project.
Set `<PYTHON>` as `python3` on macOS/Linux or `py -3` on Windows.

MCP fallback guidance:

```text
Use GitHub MCP list calls with bounded filters (state, since, labels, assignee),
then write normalized JSON and markdown report artifacts.
```

Run this on a schedule (for example hourly or daily) to track drift and planning movement.
