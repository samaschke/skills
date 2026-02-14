---
name: "ica-bootstrap"
description: "Activate when users need first-time ICA setup from scratch: install ICA CLI, configure sources, install baseline skills (including `ica-cli`), verify health, and hand off to day-2 CLI usage."
category: "command"
scope: "system-management"
subcategory: "installation"
tags:
  - ica
  - bootstrap
  - installation
  - onboarding
version: "10.2.14"
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# ICA Bootstrap

Use this skill only for first-time or broken-environment setup. This skill bootstraps ICA so users can then use `ica-cli` for regular operations.

## When to Use

- User says "set up ICA from scratch"
- User has no working `ica` command
- User wants a one-shot onboarding flow with minimal technical steps
- User asks to install ICA + skills for IDE/desktop agent usage

## Do Not Use

- Routine CLI usage questions (use `ica-cli`)
- Feature development unrelated to ICA installation

## Operating Rules

1. Default to minimal user input and safe automatic retries.
2. Ask user only when credentials, policy restrictions, or explicit target choices are required.
3. Prefer verified bootstrap first; use source-build fallback only if needed.
4. Verify at every phase and stop only on true blockers.
5. Ensure `ica-cli` is installed as the final handoff skill.

## Workflow

### 1) Detect Platform and Preconditions

Run:

```bash
uname -s 2>/dev/null || true
command -v ica || true
command -v git || true
command -v curl || true
command -v node || true
command -v npm || true
```

### 2) Install ICA CLI (Verified Bootstrap)

macOS/Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/intelligentcode-ai/intelligent-code-agents/main/scripts/bootstrap/install.sh | bash
```

Windows PowerShell:

```powershell
iwr https://raw.githubusercontent.com/intelligentcode-ai/intelligent-code-agents/main/scripts/bootstrap/install.ps1 -UseBasicParsing | iex
```

Then run:

```bash
ica install
```

If bootstrap is blocked, fallback to local source method:

```bash
npm ci
npm run build:quick
node dist/src/installer-cli/index.js install --yes --targets=codex --scope=user --mode=symlink
```

### 3) Configure Skills Source

```bash
ica sources list
ica sources add --repo-url=https://github.com/intelligentcode-ai/skills.git
ica sources refresh
ica catalog
```

If source already exists, skip add and continue.

### 4) Install Baseline Skills and Targets

Use safe defaults unless user specifies otherwise:

- Targets: `codex`
- Scope: `user`
- Mode: `symlink` (fallback to `copy` if symlink fails)
- Baseline skill: `ica-cli`

Example:

```bash
ica install --yes --targets=codex --scope=user --mode=symlink --skills=ica-cli
```

On symlink failure:

```bash
ica install --yes --targets=codex --scope=user --mode=copy --skills=ica-cli
```

### 5) Verify and Handoff

```bash
ica --help | head -n 40
ica doctor
ica list
```

Successful handoff criteria:

- `ica` command works
- `ica doctor` reports healthy setup or only non-blocking warnings
- skills source is registered
- `ica-cli` is installed and available for ongoing use

## Troubleshooting

### `ica` still not found

- Open a new terminal/session and re-check `command -v ica`.
- Use local entrypoint fallback: `node dist/src/installer-cli/index.js ...`.

### Source auth required

```bash
ica sources auth --id=<source-id> --token=<pat-or-api-key>
ica sources refresh --id=<source-id>
```

### CLI installation partially succeeded

```bash
ica doctor
ica sync --yes
ica list
```

## Validation Checklist

- [ ] Frontmatter is specific and trigger-oriented for first-time setup
- [ ] Workflow is deterministic and executable end-to-end
- [ ] Includes verified bootstrap and local fallback
- [ ] Installs skills source and baseline `ica-cli` skill
- [ ] Includes verification and explicit handoff criteria
- [ ] Includes troubleshooting for common blockers

## Response Contract

When this skill runs, output:

1. Current state (what is already installed)
2. Commands executed (or exact commands required from user)
3. Verification status (`ica doctor`, `ica list`)
4. Handoff status ("ready for `ica-cli`" or exact blocker and fix)
