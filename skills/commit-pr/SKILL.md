---
name: commit-pr
description: "Activate when user asks to commit, push changes, create a PR, open a pull request, or submit changes for review. Activate when process skill reaches commit or PR phase. Provides commit message formatting and PR structure. PRs default to dev branch, not main. Works with git-privacy skill."
category: "process"
scope: "development"
subcategory: "version-control"
tags:
  - git
  - pull-request
  - commit
  - review
version: "10.2.18"
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# Git Commit and Pull Request Skill

This skill handles git commits and pull requests with specific formatting requirements.

## Triggering

Use this skill when the request requires commit, push, PR creation, or PR merge actions.

Use this skill when prompts include:
- commit or push the current changes
- create/open/update a pull request
- prepare changes for review and submit to `dev`
- merge an approved PR after gates pass

Do not use this skill for:
- explanation-only prompts with no git action request
- planning-only prompts without commit/PR intent
- release orchestration requests that should be handled by `release`

## Acceptance Tests

| Test ID | Type | Prompt / Condition | Expected Result |
| --- | --- | --- | --- |
| CPR-T1 | Positive trigger | "Commit these changes and push the branch" | skill triggers |
| CPR-T2 | Positive trigger | "Create a PR to dev with a summary and test plan" | skill triggers |
| CPR-T3 | Negative trigger | "Explain this PR feedback" | skill does not trigger |
| CPR-T4 | Negative trigger | "Plan work items for these findings" | skill does not trigger |
| CPR-T5 | Behavior | skill triggered for commit/PR | enforces prerequisites, branch/worktree policy, and no-AI-attribution commit/PR content |
| CPR-T6 | Behavior | missing `autonomy.system_level` in user `ica.config.json` | asks user, persists `autonomy.system_level`, then proceeds |
| CPR-T7 | Behavior | missing `autonomy.project_level` in project `ica.config.json` | asks user, persists `autonomy.project_level`, then proceeds |
| CPR-T8 | Behavior | project autonomy is `follow-system` | resolves effective autonomy and applies it to confirmation behavior for commit/push/PR/merge |
| CPR-T9 | Behavior | PR created to `dev` | automatically runs post-PR Stage 3 review loop and posts fresh review receipt for current head SHA |
| CPR-T10 | Behavior | security review enabled for scope | automatically runs security review loop, fixes findings, and posts fresh security receipt for current head SHA |
| CPR-T11 | Behavior | repo has no required checks configured | treats checks gate as pass-with-note (`no required checks configured`) instead of indefinite block |

## Autonomy Level Resolution (MANDATORY)

Resolve autonomy settings from `ica.config.json` hierarchy (not tracking config):
- user config:
  - `${ICA_HOME}/ica.config.json`
  - `$HOME/.codex/ica.config.json`
  - `$HOME/.claude/ica.config.json`
- project config:
  - `./ica.config.json`

Required keys:
- `autonomy.system_level`: `L1` | `L2` | `L3` (default `L2`)
- `autonomy.project_level`: `follow-system` | `L1` | `L2` | `L3` (default `follow-system`)

Bootstrap prompts (if missing):
- If `autonomy.system_level` missing:
  - ask: "No system autonomy level is configured. Set system autonomy level to `L2` (recommended), `L1`, or `L3`?"
  - persist in user `ica.config.json`
- If `autonomy.project_level` missing:
  - ask: "No project autonomy level is configured. Set project autonomy level to `follow-system` (recommended), `L1`, `L2`, or `L3`?"
  - persist in project `ica.config.json`

Compatibility:
- If legacy `autonomy.level` exists and `autonomy.system_level` is missing, treat legacy value as system level for this run and persist it as `autonomy.system_level`.

Effective level:
- if `project_level` is `L1`/`L2`/`L3`, use project level
- if `project_level` is `follow-system`, use system level

Effective-level behavior for this skill:
- `L1`: require explicit confirmation before each commit/push/PR/merge action
- `L2`: follow standard gated flow with confirmations for significant/high-impact actions
- `L3`: proceed automatically once all gates pass (except required explicit approvals for protected actions)

## PR TARGET BRANCH (CRITICAL)

**PRs go to `dev` by default, NOT `main`.**

```
feature/* → PR to dev   (default, normal workflow)
dev       → PR to main  (release only, requires explicit request)
```

### When to PR to main
- **ONLY** for releases (merging stable dev to main)
- **ONLY** when user explicitly says "release", "PR to main", or "merge to main"
- **NEVER** for regular feature work

### Default Behavior
```bash
# CORRECT - PR to dev (default)
gh pr create --base dev

# WRONG - PR to main (unless releasing)
gh pr create --base main  # DO NOT DO THIS!
```

## PREREQUISITES (MANDATORY)

**Before ANY commit or PR, you MUST:**

0. **Resolve effective autonomy level from ICA config**
   - Resolve `autonomy.system_level` + `autonomy.project_level` and effective level (`L1`/`L2`/`L3`)
   - If either key is missing: ask user and persist in `ica.config.json` at correct scope
   - Apply effective-level confirmation behavior for this run

1. **Resolve branch/worktree behavior from ICA config**
   - Read `git.worktree_branch_behavior` from `ica.config.json`
   - If missing: ask user, persist choice, then continue
   - If `always_new`: ensure changes are on a dedicated worktree + prefixed branch
   - Never commit implementation work directly on `main` or `dev`

2. **Run tests** - All tests must pass
3. **Run reviewer skill** - Must complete with no blocking findings
4. **Run security review** - Must complete with no blocking security findings
   - Prefer `security-best-practices` for supported stacks
   - Fallback: reviewer security-focused pass when stack is unsupported
5. **Fix all findings** - Auto-fix or get human decision
6. **Run validate skill checks** - Ensure completion criteria + state transition validity
7. **Run backend-aware tracking verification** for the selected backend
8. **Confirm larger changes explicitly** - Always ask before committing broad/high-impact changes

```
BLOCKED until prerequisites pass:
- git commit
- git push
- gh pr create
```

**If you skip these steps, you are violating the process.**

## Validation And Check Gates (MANDATORY)

Pre-commit gate:
- autonomy level resolved and applied for this scope
- tests pass
- reviewer has no blocking findings
- security review has no blocking findings
- `validate` checks pass
- backend-aware tracking verification passes

Pre-PR-create gate:
- pre-commit gate already passed for HEAD
- autonomy level resolved and applied for this scope
- branch target is valid (`dev` by default; `main` only for explicit release)
- backend tracking state is synchronized for items included in PR
- branch/worktree policy is satisfied (`always_new` requires dedicated worktree + prefixed branch)

Pre-merge gate:
- reviewer Stage 3 receipt is current and PASS
- security review receipt is current and PASS
- required checks are green (or no required checks are configured)
- `validate` checks pass for merge candidate
- backend-aware tracking verification passes
- explicit approval exists (or configured standing approval)
- autonomy level resolved and applied for merge scope

Fail-closed behavior:
- if any gate fails, STOP and do not commit/push/create-PR/merge.

## Worktree + Branch Policy (ICA Config)

Read `git.worktree_branch_behavior` from `ica.config.json` hierarchy.

Allowed values:
- `always_new`
- `ask`
- `current_branch`

If missing:
- ask user which behavior to use
- persist in project/user `ica.config.json`

Enforcement:
- for `always_new`, create and use a dedicated worktree + prefixed branch
- for `ask`, ask before commit/PR scope and honor response
- for `current_branch`, still enforce branch safety (`dev` default PR target, never feature work on `main`)

Large-change confirmation is mandatory regardless of policy.

Branch prefix resolution (no hardcoding):
- if `git.worktree_branch_prefix` is set, use it (examples: `agent/`, `claude/`, `cursor/`)
- else derive from the active agent runtime (`codex/`, `claude/`, `cursor/`, `gemini/`, `antigravity/`)
- if runtime cannot be determined, use agent-agnostic default `agent/`

Branch name template:
- `<resolved-prefix><short-scope-slug>-<YYYYMMDDHHMMSS>`

## CRITICAL RULES

**NEVER include any of the following in commits or PRs:**
- `Co-Authored-By:` lines for AI models or tools
- Any "Generated with" or "Generated by" footers
- Any indication of AI authorship or generation
- Tool URLs in attribution context

**You CAN include:**
- AI-related feature descriptions (e.g., "feat: Add GPT-4 integration")
- Bug fixes for AI components (e.g., "fix: AI inference timeout")
- Any legitimate technical content

## Commit Message Format

Use this format for commit messages:

```
<type>: <short description>

<optional body with more details>
```

### Commit Types
| Type | Usage |
|------|-------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `refactor` | Code refactoring |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |
| `style` | Formatting, missing semicolons, etc. |
| `perf` | Performance improvements |

### Example Commit Messages

```bash
# Simple commit
git commit -m "feat: Add user authentication endpoint"

# Commit with body (use HEREDOC)
git commit -m "$(cat <<'EOF'
fix: Resolve race condition in payment processing

The payment processor was not awaiting transaction confirmation
before updating order status. Added proper async handling.
EOF
)"
```

## Pull Request Format

When creating PRs with `gh pr create`:

```bash
# ALWAYS specify --base dev (unless releasing to main)
gh pr create --base dev --title "<type>: <title under 70 chars>" --body "$(cat <<'EOF'
## Summary
- Brief overview (1-3 bullets)

## Changes
- What was modified

## Test Plan
- [ ] Test case 1
- [ ] Test case 2

## Breaking Changes
- (if applicable)
EOF
)"
```

### Release PR (dev → main)
Only when explicitly releasing:
```bash
gh pr create --base main --title "release: v10.2.0" --body "$(cat <<'EOF'
## Release Summary
- Version: v10.2.0
- Changes since last release

## Verification
- [ ] Dev branch stable
- [ ] All tests passing
- [ ] Release notes updated
EOF
)"
```

### PR Title Guidelines
- Keep under 70 characters
- Use same type prefixes as commits
- Be descriptive but concise

### PR Body Sections
- **Summary**: Brief overview (1-3 bullet points)
- **Changes**: What was modified
- **Test Plan**: How to verify the changes
- **Breaking Changes**: (if applicable)

## Workflow

### For Commits:
1. Run `git status` to see changes
2. Run `git diff` to review what changed
3. Stage specific files (avoid `git add -A` for sensitive files)
4. Run pre-commit gate (`tests` + `reviewer` + `validate` + tracking verify)
5. Create commit with proper message format
6. Verify no AI attribution in message

### For Pull Requests:
1. Ensure all changes are committed
2. Push branch to remote if needed
3. Run `git log origin/dev..HEAD` to see all commits for the PR
4. Run pre-PR-create gate (`validate` + tracking verify + target-branch check)
5. Create PR with `gh pr create --base dev` (NOT main!)
6. Verify no AI attribution in title/body
7. Run automatic post-PR closed loop (MANDATORY):
   - Run reviewer Stage 3 in a fresh temp checkout
   - Run security review in the same fresh-head context
   - Auto-fix findings, push, and repeat until both receipts are PASS for current head SHA

## Post-PR Closed Loop (MANDATORY)

Immediately after PR creation (and after every push to PR branch), run this loop:
1. Checkout PR branch in a fresh temp workspace.
2. Run reviewer Stage 3 and fix findings automatically when safe.
3. Run security review and fix findings automatically when safe.
   - Preferred: `security-best-practices`
   - Escalation option: `security-engineer` for high-risk/complex issues
4. Push fixes to PR branch if any.
5. Re-run reviewer + security checks until both are clean.
6. Post/update receipts for current head SHA:
   - `ICA-REVIEW-RECEIPT` (`Findings: 0`, `Result: PASS`)
   - `ICA-SECURITY-REVIEW-RECEIPT` (`Findings: 0`, `Result: PASS`)
7. Evaluate required checks:
   - if required checks exist, they must be green
   - if no required checks exist, record `no required checks configured` and continue

### For Release PRs (dev → main):
1. Ensure dev is stable and tested
2. User must explicitly request release
3. Create PR with `gh pr create --base main`
4. Tag after merge: `git tag v10.2.0`

## Merging PRs (Gated, Required)

This skill may be used to merge PRs, but ONLY after the merge gates below are satisfied.

### Merge Gates (Required)

1. **Post-PR review receipt exists and matches current head SHA**
   - Reviewer skill Stage 3 MUST have posted an `ICA-REVIEW` / `ICA-REVIEW-RECEIPT` comment.
   - The comment MUST include:
     - `Reviewer-Stage: 3 (temp checkout)` (dedicated reviewer/subagent context)
     - `Reviewer-Agent: ... (subagent)` (must indicate subagent execution)
     - `Head-SHA: <sha>` matching the PR's current `headRefOid`
     - `Findings: 0` and `NO FINDINGS`
     - `Result: PASS`
2. **Post-PR security receipt exists and matches current head SHA**
   - Security review MUST have posted an `ICA-SECURITY-REVIEW-RECEIPT` comment.
   - The comment MUST include:
     - `Security-Reviewer-Stage: post-pr`
     - `Head-SHA: <sha>` matching the PR's current `headRefOid`
     - `Findings: 0` and `NO FINDINGS`
     - `Result: PASS`
3. **All required checks are green**
   - `gh pr checks <PR-number>` must show all required checks passing.
   - If no required checks exist, treat as pass-with-note (`no required checks configured`).
4. **Validation + tracking gate passes for merge candidate**
   - Run `validate` checks for release/merge readiness.
   - Run backend-aware tracking verification before merge.
5. **Approval to merge (one of the following)**
   - Default: explicit user approval in chat ("merge PR <N>", "LGTM", "approve", etc.).
   - Optional: `workflow.auto_merge=true` for the current AgentTask/workflow context.
     - This is a standing approval that allows the agent to merge once gates 1-2 pass.
     - Recommended: allow auto-merge ONLY for PRs targeting `dev` (never `main`).
   - If neither applies, STOP and wait.

### Optional Gate: Enforce GitHub-Style Approvals

By default this repo uses **self-review-and-merge**:
- PR is required (branch protection), but GitHub required approvals may remain at 0.
- Review is required via the **ICA Stage 3 receipt** (skills-level gate).

If you want to also enforce GitHub-style approvals (at least 1 `APPROVED` review), set:
- `workflow.require_github_approval=true`

Notes:
- GitHub forbids approving your own PR (server-side rule). For self-authored PRs, you need a second GitHub identity/bot
  if you want a GitHub `APPROVED` review.

### Enabling Auto-Merge (Recommended)

Auto-merge is controlled by the workflow configuration that drives AgentTasks:
- AgentTask field: `workflow.auto_merge`
- Workflow files (hierarchy): `./ica.workflow.json` or `~/.claude/ica.workflow.json` over `ica.workflow.default.json`

Minimal project workflow example (`ica.workflow.json`):
```json
{
  "medium": { "auto_merge": true },
  "large": { "auto_merge": true },
  "mega": { "auto_merge": true }
}
```

### Verify The Receipt (Copy/Paste)

```bash
PR=<PR-number>
HEAD_SHA=$(gh pr view "$PR" --json headRefOid --jq .headRefOid)

# Grab the most recent receipt body (if any)
RECEIPT=$(gh pr view "$PR" --json comments --jq '.comments | map(select(.body | contains("ICA-REVIEW-RECEIPT"))) | last | .body // ""')

echo "$RECEIPT" | rg -q "Reviewer-Stage: 3 \\(temp checkout\\)" || echo "Missing Stage 3 receipt"
echo "$RECEIPT" | rg -q "Reviewer-Agent:.*\\(subagent\\)" || echo "Missing Reviewer-Agent subagent marker"
echo "$RECEIPT" | rg -q "Head-SHA: $HEAD_SHA" || echo "Receipt is missing/stale for current head SHA"
echo "$RECEIPT" | rg -q "Findings: 0" || echo "Receipt does not indicate zero findings"
echo "$RECEIPT" | rg -q "NO FINDINGS" || echo "Receipt does not include NO FINDINGS marker"
echo "$RECEIPT" | rg -q "Result: PASS" || echo "Receipt does not indicate PASS"
```

**If any verification line fails:** DO NOT MERGE. Re-run reviewer Stage 3 and post a fresh receipt.

### Verify Security Receipt (Copy/Paste)

```bash
PR=<PR-number>
HEAD_SHA=$(gh pr view "$PR" --json headRefOid --jq .headRefOid)

SEC_RECEIPT=$(gh pr view "$PR" --json comments --jq '.comments | map(select(.body | contains("ICA-SECURITY-REVIEW-RECEIPT"))) | last | .body // ""')

echo "$SEC_RECEIPT" | rg -q "Security-Reviewer-Stage: post-pr" || echo "Missing security stage marker"
echo "$SEC_RECEIPT" | rg -q "Head-SHA: $HEAD_SHA" || echo "Security receipt is missing/stale for current head SHA"
echo "$SEC_RECEIPT" | rg -q "Findings: 0" || echo "Security receipt does not indicate zero findings"
echo "$SEC_RECEIPT" | rg -q "NO FINDINGS" || echo "Security receipt does not include NO FINDINGS marker"
echo "$SEC_RECEIPT" | rg -q "Result: PASS" || echo "Security receipt does not indicate PASS"
```

**If any verification line fails:** DO NOT MERGE. Re-run post-PR security review and post a fresh receipt.

### Verify Checks Gate (Required Checks Only)

```bash
PR=<PR-number>
CHECKS_OUTPUT=$(gh pr checks "$PR" 2>&1 || true)

if echo "$CHECKS_OUTPUT" | rg -q "no checks reported"; then
  echo "No required checks configured; checks gate = pass-with-note."
else
  echo "$CHECKS_OUTPUT"
fi
```

### Verify GitHub Approval (Copy/Paste)

```bash
PR=<PR-number>
REQUIRE_GH_APPROVAL=${REQUIRE_GH_APPROVAL:-false} # set to true if workflow.require_github_approval=true

PR_AUTHOR=$(gh pr view "$PR" --json author --jq .author.login)
GH_USER=$(gh api user --jq .login)
APPROVALS=$(gh pr view "$PR" --json reviews --jq '[.reviews[] | select(.state=="APPROVED")] | length')

if [ "$REQUIRE_GH_APPROVAL" = "true" ]; then
  if [ "$PR_AUTHOR" = "$GH_USER" ]; then
    echo "Self-authored PR ($GH_USER): GitHub forbids self-approval; approvals require a bot/second identity."
  else
    test "$APPROVALS" -ge 1 || echo "Missing GitHub APPROVED review"
  fi
fi
```

### Merge (Only After Approval)

```bash
gh pr merge <PR-number> --squash --delete-branch
```

## Examples

### Creating a Commit
```bash
# Stage files
git add src/auth/login.ts src/auth/types.ts

# Commit without any AI attribution
git commit -m "feat: Add login validation with rate limiting"
```

### Creating a PR
```bash
gh pr create --title "feat: Add user authentication" --body "$(cat <<'EOF'
## Summary
- Implements JWT-based authentication
- Adds login/logout endpoints
- Includes rate limiting for security

## Changes
- Added `src/auth/` module with authentication logic
- Updated API routes to include auth endpoints
- Added middleware for protected routes

## Test Plan
- [ ] Test login with valid credentials
- [ ] Test login with invalid credentials
- [ ] Verify rate limiting after 5 failed attempts
EOF
)"
```

## Output Contract

When this skill runs, produce:
1. autonomy resolution (`system_level`, `project_level`, effective level, and whether defaults were bootstrapped)
2. resolved branch/worktree policy (`git.worktree_branch_behavior`) and enforcement result
3. gate summary (tests, reviewer, security review, validate, tracking verification, checks status)
4. commit details (hash, message) when commit is performed
5. PR details (number/url/base/head/title) when PR is created/updated
6. post-PR loop status (review receipt, security receipt, checks gate result)
7. merge decision/status when merge is requested
8. any blocker with exact failed gate and required remediation

## Validation Checklist

- [ ] Acceptance tests cover positive, negative, and behavior cases (including post-PR and security-loop behavior)
- [ ] Effective autonomy level is resolved before commit/PR/merge actions
- [ ] Pre-commit gate includes tests + reviewer + security review + validate + tracking verification
- [ ] Post-PR closed loop runs automatically and posts fresh review/security receipts for current head SHA
- [ ] Required checks gate passes (or records `no required checks configured`)
- [ ] Merge remains fail-closed when any required gate or receipt is missing/stale

## Reminders

1. **No AI attribution** - Never add Co-Authored-By or Generated-with lines
2. **Be specific** - Describe what changed and why
3. **Keep it clean** - No unnecessary files (check .gitignore)
4. **Review first** - Always `git diff` before committing
