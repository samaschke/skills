---
name: release
description: "Activate when user asks to release, bump version, cut a release, merge to main, or tag a version. Handles version bumping (semver), CHANGELOG updates, PR merging, git tagging, and GitHub release creation."
category: "process"
scope: "development"
subcategory: "release"
tags:
  - release
  - versioning
  - changelog
  - github
version: "10.2.17"
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# Release Skill

Handles the complete release workflow: version bump, CHANGELOG, merge, tag, and GitHub release.

## Triggering

Use this skill when the request requires release-specific git/version actions.

Use this skill when prompts include:
- release, cut a release, ship, publish, or tag a version
- bump version (`major`/`minor`/`patch`) and update changelog for release
- merge a release PR to `main`

Do not use this skill for:
- regular feature PR creation to `dev` (use `commit-pr`)
- implementation-only or planning-only requests
- explanation-only prompts with no release action request
- explain release strategy options

## Acceptance Tests

| Test ID | Type | Prompt / Condition | Expected Result |
| --- | --- | --- | --- |
| RLS-T1 | Positive trigger | "Cut a patch release and tag it" | skill triggers |
| RLS-T2 | Positive trigger | "Merge this release PR to main and publish notes" | skill triggers |
| RLS-T3 | Negative trigger | "Create a PR to dev for this feature" | skill does not trigger |
| RLS-T4 | Negative trigger | "Explain release strategy options" | skill does not trigger |
| RLS-T5 | Behavior | skill triggered for release flow | enforces release gates, worktree/branch policy, and explicit approval for non-draft publish |
| RLS-T6 | Behavior | missing `autonomy.system_level` in user `ica.config.json` | asks user, persists `autonomy.system_level`, then proceeds |
| RLS-T7 | Behavior | missing `autonomy.project_level` in project `ica.config.json` | asks user, persists `autonomy.project_level`, then proceeds |
| RLS-T8 | Behavior | project autonomy is `follow-system` | resolves effective autonomy and applies it to release confirmation behavior |
| RLS-T9 | Behavior | release PR missing `ICA-REVIEW-RECEIPT` | runs post-PR review loop, refreshes receipt for current head SHA, then re-checks gates |
| RLS-T10 | Behavior | release PR missing `ICA-SECURITY-REVIEW-RECEIPT` | runs post-PR security loop, refreshes receipt for current head SHA, then re-checks gates |
| RLS-T11 | Behavior | release PR has no required checks configured | treats checks gate as pass-with-note (`no required checks configured`) |
| RLS-T12 | Behavior | release flow reaches merge gate | requires current review+security receipts and checks result before merge |

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

Effective-level behavior for release:
- `L1`: require explicit confirmation for each release transition (version bump commit, PR merge, tag, publish)
- `L2`: standard release flow; explicit confirmation remains mandatory for larger-change release actions
- `L3`: automate mechanical release actions when gates pass and release automation is enabled, while still requiring explicit approval for non-draft publish

## Auto-Merge vs Agent Merge

This skill does NOT require GitHub "auto-merge" (`gh pr merge --auto`).
When automation is enabled, the **agent performs the merge itself** (runs `gh pr merge`) once the merge gates pass.

## When to Use

- User asks to "release", "cut a release", "ship it"
- User asks to "bump version" (major/minor/patch)
- User asks to "merge to main" after PR approval
- User asks to "tag a version" or "create a release"

## Prerequisites

Before releasing:
1. All changes committed and pushed
2. PR created and reviewed (ICA Stage 3 receipt is the required review gate by default)
3. Security review receipt exists and is current for release PR head SHA
4. Tests passing
5. No blocking review findings
6. `validate` checks pass for release scope
7. Backend-aware tracking verification passes
8. Worktree/branch policy resolved from ICA config (`git.worktree_branch_behavior`)
9. Effective autonomy level resolved from ICA config (`autonomy.system_level` + `autonomy.project_level`)
10. Explicit user confirmation for larger changes (release is always a larger change)

## Worktree + Branch Policy (ICA Config)

Read `git.worktree_branch_behavior` from `ica.config.json` hierarchy.

Allowed values:
- `always_new`
- `ask`
- `current_branch`

If missing:
- ask user which behavior to use
- persist in project/user `ica.config.json`

Release enforcement:
- if `always_new`, use a dedicated release worktree + branch before release actions
- if `ask`, ask before release actions and follow response
- even with `current_branch`, release remains a larger-change flow and requires explicit confirmation

## Validation And Check Gates (MANDATORY)

Pre-release gate:
- release request explicitly confirmed by user
- tests + reviewer + security review + validate all pass
- backend-aware tracking verification passes
- release PR target is `main`
- branch/worktree policy is satisfied for release scope
- autonomy level resolved and applied for release scope
- required checks are green (or no required checks are configured)

Pre-tag gate:
- release PR merged successfully
- local `main` is up to date and clean
- validate checks pass for release artifacts (version/changelog)
- autonomy level resolved and applied for release scope

Pre-publish gate:
- tag exists remotely
- release notes prepared and reviewed
- explicit user approval for non-draft publish (draft creation is safe-default)
- autonomy level resolved and applied for release scope

Fail-closed behavior:
- if any gate fails, STOP release progression and surface exact blocker.

## Automation Controls (Skills-Level)

These controls are driven by workflow configuration (AgentTask `workflow.*` and `ica.workflow.json`):
- `workflow.auto_merge=true`: standing approval to merge PRs once gates pass
- `workflow.release_automation=true`: automate the mechanical release steps (tag + GitHub release creation)

Safety defaults:
- Never auto-merge to `main` unless the user explicitly requested a release workflow.
- Never publish a non-draft GitHub release without explicit user approval (draft releases are OK).

Autonomy-level enforcement:
- `L1`: pause for explicit user confirmation at each release transition.
- `L2`: continue routine release steps after gates pass; keep explicit confirmations for larger-change actions.
- `L3`: may proceed through gated release steps automatically when workflow settings allow, but must still respect explicit-approval rules above.

## Pre-Release Receipt And Checks Loop (MANDATORY)

Before merge, release flow must verify receipts/checks for the current release PR head SHA.

If any receipt/check gate fails:
1. Run post-PR reviewer Stage 3 loop on the release PR branch.
2. Run post-PR security review loop on the release PR branch.
   - Preferred: `security-best-practices`
   - Escalation option: `security-engineer` for high-risk/complex findings
3. Push fixes when needed.
4. Re-run receipt and checks verification.

Required receipt outcomes for current head SHA:
- `ICA-REVIEW-RECEIPT`: `Findings: 0`, `Result: PASS`
- `ICA-SECURITY-REVIEW-RECEIPT`: `Findings: 0`, `Result: PASS`

Checks behavior:
- If required checks exist: all required checks must pass.
- If no required checks exist: record `no required checks configured` and treat checks gate as pass-with-note.

## Release Workflow

### Step 1: Verify Ready to Release

```bash
# Check PR status
gh pr status

# Verify PR is approved
gh pr view <PR-number> --json reviews

# Verify checks pass
CHECKS_OUTPUT=$(gh pr checks <PR-number> 2>&1 || true)
if echo "$CHECKS_OUTPUT" | rg -q "no checks reported"; then
  echo "No required checks configured; checks gate = pass-with-note."
else
  echo "$CHECKS_OUTPUT"
fi

# Verify this is a release PR (base should be main)
gh pr view <PR-number> --json baseRefName --jq .baseRefName

# Verify reviewer Stage 3 receipt exists (ICA-REVIEW-RECEIPT) and matches current head SHA
PR=<PR-number>
HEAD_SHA=$(gh pr view "$PR" --json headRefOid --jq .headRefOid)
RECEIPT=$(gh pr view "$PR" --json comments --jq '.comments | map(select(.body | contains("ICA-REVIEW-RECEIPT"))) | last | .body // ""')
echo "$RECEIPT" | rg -q "Reviewer-Stage: 3 \\(temp checkout\\)"
echo "$RECEIPT" | rg -q "Head-SHA: $HEAD_SHA"
echo "$RECEIPT" | rg -q "Result: PASS"

# Verify security review receipt exists (ICA-SECURITY-REVIEW-RECEIPT) and matches current head SHA
SEC_RECEIPT=$(gh pr view "$PR" --json comments --jq '.comments | map(select(.body | contains("ICA-SECURITY-REVIEW-RECEIPT"))) | last | .body // ""')
echo "$SEC_RECEIPT" | rg -q "Security-Reviewer-Stage: post-pr"
echo "$SEC_RECEIPT" | rg -q "Head-SHA: $HEAD_SHA"
echo "$SEC_RECEIPT" | rg -q "Result: PASS"
```

### Step 2: Determine Version Bump

Ask user if not specified:

| Type | When | Example |
|------|------|---------|
| `major` | Breaking changes | 1.0.0 → 2.0.0 |
| `minor` | New features, backward compatible | 1.0.0 → 1.1.0 |
| `patch` | Bug fixes, no new features | 1.0.0 → 1.0.1 |

### Step 3: Update VERSION File

```bash
# Read current version
CURRENT=$(cat src/VERSION 2>/dev/null || cat VERSION 2>/dev/null || echo "0.0.0")

# Calculate new version based on bump type
# For patch: increment last number
# For minor: increment middle, reset last to 0
# For major: increment first, reset others to 0
```

### Step 4: Update CHANGELOG

Add new section at top of CHANGELOG.md:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing features

### Fixed
- Bug fixes

### Removed
- Removed features
```

Derive changes from:
```bash
git log --oneline $(git describe --tags --abbrev=0 2>/dev/null || echo "HEAD~10")..HEAD
```

### Step 5: Commit Version Bump

```bash
# Re-run quality/validation gate before release commit
# - tests pass
# - reviewer has no blocking findings
# - security review has no blocking findings
# - validate checks pass
# - tracking verification passes

git add VERSION src/VERSION CHANGELOG.md
git commit -m "chore: Bump version to X.Y.Z"
git push
```

### Step 6: Merge PR

```bash
# Merge gate (required):
# - Reviewer Stage 3 receipt exists and matches head SHA (ICA-REVIEW-RECEIPT)
# - Security review receipt exists and matches head SHA (ICA-SECURITY-REVIEW-RECEIPT)
# - Required checks passing (or no required checks configured)
# - Validate checks pass
# - Backend-aware tracking verification passes
# - User explicitly approved the release/merge
#
# Only then merge the PR (squash or merge based on project preference)
gh pr merge <PR-number> --squash --delete-branch
```

Or if merge commit preferred:
```bash
gh pr merge <PR-number> --merge --delete-branch
```

### Step 7: Create Git Tag

```bash
# Checkout main after merge
git checkout main
git pull origin main

# Create annotated tag
git tag -a "vX.Y.Z" -m "Release vX.Y.Z"
git push origin "vX.Y.Z"
```

### Step 8: Create GitHub Release (if using GitHub)

```bash
# Default: create DRAFT release (safe). Publish only if user explicitly requests.
gh release create "vX.Y.Z" \
  --draft \
  --title "vX.Y.Z" \
  --notes "$(cat <<'EOF'
## What's Changed

### Added
- Feature 1
- Feature 2

### Fixed
- Bug fix 1

**Full Changelog**: https://github.com/OWNER/REPO/compare/vPREV...vX.Y.Z
EOF
)"
```

Or generate notes automatically:
```bash
gh release create "vX.Y.Z" --generate-notes
```

## Version File Locations

Check for VERSION in order:
1. `src/VERSION`
2. `VERSION`
3. `package.json` (for Node projects)
4. `pyproject.toml` (for Python projects)

## CHANGELOG Format

Follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [X.Y.Z] - YYYY-MM-DD

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security
```

## Safety Checks

Before any release action:
1. Confirm user approval for merge
2. Verify on correct branch
3. Check no uncommitted changes
4. Verify review and security receipts are current for PR head SHA
5. Verify required checks pass (or note `no required checks configured`)
6. Run `validate` checks for current release step
7. Run backend-aware tracking verification

## Integration

Works with:
- commit-pr skill - For version bump commit
- git-privacy skill - No AI attribution in release notes
- branch-protection skill - Respect branch rules
- reviewer skill - Verify no blocking findings

## Examples

### Patch Release
```
User: "Release a patch for the bug fixes"
→ Bump 1.2.3 → 1.2.4
→ Update CHANGELOG
→ Commit, merge, tag, release
```

### Minor Release
```
User: "Cut a minor release with the new features"
→ Bump 1.2.3 → 1.3.0
→ Update CHANGELOG
→ Commit, merge, tag, release
```

### Major Release
```
User: "Major release - we have breaking changes"
→ Bump 1.2.3 → 2.0.0
→ Update CHANGELOG (note breaking changes)
→ Commit, merge, tag, release
```

## Rollback

If release needs to be reverted:
```bash
# Delete the tag locally and remotely
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z

# Delete the GitHub release
gh release delete vX.Y.Z --yes

# Revert the merge commit if needed
git revert <merge-commit-sha>
```

## Validation Checklist

- [ ] Acceptance tests cover trigger behavior and release-gate behavior (including receipts/checks cases)
- [ ] Effective autonomy level is resolved before release transitions
- [ ] Pre-release gate includes reviewer + security + validate + tracking verification
- [ ] Receipt/checks loop auto-remediates missing/stale receipts before merge attempt
- [ ] Required checks gate handles both configured-checks and no-required-checks repos
- [ ] Non-draft publish still requires explicit approval

## Output Contract

When this skill runs, produce:
1. release scope confirmation (repo, PR, branch target, bump type)
2. autonomy resolution (`system_level`, `project_level`, effective level, and whether defaults were bootstrapped)
3. resolved branch/worktree policy (`git.worktree_branch_behavior`) and enforcement result
4. gate summary (tests, reviewer receipt, security receipt, validate, tracking verification, checks status)
5. pre-release loop status (auto-remediation attempts, receipt refresh result, checks-gate result)
6. version/changelog update summary
7. merge/tag/release results (PR merge status, tag, release URL/draft status)
8. explicit blocker details when any gate fails
