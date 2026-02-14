---
name: "ica-cli"
description: "Activate when users ask how to use, configure, verify, upgrade, or troubleshoot the ICA CLI (`ica`) after initial setup, including source management and day-2 operations."
category: "command"
scope: "system-management"
subcategory: "operations"
tags:
  - ica
  - cli
  - operations
  - troubleshooting
version: "10.2.14"
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# ICA CLI Operator

Use this skill when a user needs practical, command-level help with ICA CLI setup and operations.

## Scope

This is the **post-bootstrap** operations skill.
For first-time machine setup, use `ica-bootstrap` first, then use `ica-cli` for ongoing operations.

## When to Use

- User asks to install ICA or get `ica` working
- User asks how to configure targets, scope, modes, or config files
- User asks to verify installation status
- User asks to fix ICA CLI errors (`command not found`, config/scope issues, source/auth issues)

## Do Not Use

- Pure architecture/design questions with no CLI execution need
- General coding requests unrelated to ICA installation/configuration

## Operating Rules

1. Prefer deterministic commands and explicit flags over vague guidance.
2. Detect current state first, then change only what is necessary.
3. Use user language in explanations and provide copy/paste blocks.
4. Include platform-specific commands when needed (macOS/Linux vs Windows PowerShell).
5. After changes, always verify with `ica doctor` and `ica list` (or equivalent local CLI entrypoint).
6. For first-time setup requests, hand off to `ica-bootstrap` before continuing here.

## Workflow

### 1) Detect Environment and Current State

Run:

```bash
command -v ica || true
ica --help | head -n 40
ica doctor
ica list
```

If `ica` is not on `PATH`, continue with installation paths below.

### 2) Install ICA CLI

#### Recommended: Verified Bootstrap

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
ica launch --open=true
```

#### Alternative: Build and Run from Local Source Checkout

```bash
npm ci
npm run build:quick
node dist/src/installer-cli/index.js install --yes --targets=codex --scope=user --mode=symlink
```

Use this path when developing ICA itself or when bootstrap is not desired.

### 3) Configure Installation Correctly

Common flags:

- `--targets=claude,codex,cursor,gemini,antigravity`
- `--scope=user|project`
- `--project-path=/absolute/path` (optional for project scope; defaults to current directory)
- `--mode=symlink|copy`
- `--config-file=/path/to/ica.config.json`
- `--mcp-config=/path/to/mcp.json`
- `--env-file=/path/to/.env`

Examples:

```bash
# User-scope install for Codex only
ica install --yes --targets=codex --scope=user --mode=symlink

# Project-scope install for Claude + Codex
ica install --yes --targets=claude,codex --scope=project --project-path=/path/to/project --mode=symlink

# Non-interactive install with explicit config
ica install --yes --targets=codex --scope=user --config-file=/path/to/ica.config.json --mcp-config=/path/to/mcp.json
```

### 4) Manage Sources (Optional but Common)

```bash
ica sources list
ica sources add --repo-url=https://github.com/intelligentcode-ai/skills.git
ica sources refresh
ica catalog
```

If authentication is required:

```bash
ica sources auth --id=<source-id> --token=<pat-or-api-key>
```

### 5) Verify and Report

Verification commands:

```bash
ica --help | head -n 40
ica doctor
ica list
```

Expected outputs to confirm:

- CLI is executable
- Target homes resolved correctly for selected scope
- Managed assets are listed without errors
- Dashboard launches with `ica launch --open=true` when requested

## Troubleshooting

### `ica: command not found`

- Re-run bootstrap install and start a new shell session.
- If using source checkout, use `node dist/src/installer-cli/index.js ...` directly.

### Invalid or empty targets

- Use supported values only: `claude,codex,cursor,gemini,antigravity`.

### Symlink issues (permissions/policy)

- Retry with copy mode:

```bash
ica install --yes --targets=codex --scope=user --mode=copy
```

### Wrong scope or wrong project path

- Re-run `ica install` with explicit `--scope` and `--project-path`.

### Claude integration should be disabled

```bash
ica install --yes --targets=claude --scope=user --install-claude-integration=false
```

## Validation Checklist

- [ ] Frontmatter includes `name` and trigger-oriented `description`
- [ ] Directory name and frontmatter `name` both equal `ica-cli`
- [ ] Includes clear "When to Use" and "Do Not Use" boundaries
- [ ] Workflow is ordered and deterministic (detect -> install -> configure -> verify)
- [ ] Includes at least one concrete command example for install/configuration
- [ ] Includes troubleshooting guidance for common failures
- [ ] Includes explicit response contract for outputs

## Response Contract

When this skill is used, return:

1. Current state summary (`installed/not installed`, platform, scope, targets)
2. Commands executed (or recommended) in order
3. Verification result from `ica doctor` and `ica list`
4. Next corrective action if any check fails
