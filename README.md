# Intelligent Code Agents Skills

A practical, portable skills catalog for local coding agents.
Use it with ICA for managed installs, or use it standalone in your own workflow.

## Contribute a Skill

Contributions happen directly in this repository.

- Submit your custom skill as a pull request: [Create Pull Request](https://github.com/intelligentcode-ai/skills/pulls)
- Before submitting, follow: [How to Contribute](https://github.com/intelligentcode-ai/skills#how-to-contribute)

## Agent Bootstrap Prompt (Fastest Start)

Paste this into a local coding agent to bootstrap setup quickly:

```text
Bootstrap ICA for this local environment.

Your task:
1) Download and install this skill file into your own native skill storage (using your runtime's normal skill conventions):
   https://raw.githubusercontent.com/intelligentcode-ai/skills/master/skills/ica-bootstrap/SKILL.md
2) Immediately execute the installed `ica-bootstrap` skill.
3) Let `ica-bootstrap` complete end-to-end setup, including:
   - ICA CLI installation
   - skills source registration/refresh
   - installation of `ica-cli`
   - verification (`ica doctor`, `ica list`)

Behavior requirements:
- Do the work directly on this machine.
- Do not ask me where skill folders are.
- Do not ask me to confirm routine steps.
- Ask only if credentials, permissions, or security policy block execution.
- If a command fails, diagnose and retry with the safest fallback automatically.

Final output:
- What you installed
- What you executed
- Current ICA health/status
- Exact blocker only if setup is still not complete
```

Canonical prompt source:
- `skills/ica-bootstrap/assets/INITIAL_PROMPT.md`

## Layout

All skills live under:

- `skills/<skill-name>/SKILL.md`

## Canonical Workflow Skills

The canonical high-level execution flow is:

- `create-work-items`
- `plan-work-items`
- `run-work-items`
- `process` (orchestration + quality gates)

GitHub tracking specialization:

- `github-issues-planning` for hierarchy/taxonomy creation
- `github-state-tracker` for prioritized state/reporting

Tracking verification is backend-aware (not GitHub-hardcoded):

- Resolve provider from tracking config.
- For `github`, verify native parent-child linkage and item state before transitions.
- For `file-based`, verify `.agent/queue` state and naming integrity before transitions.
- Apply equivalent checks on macOS, Linux, and Windows.

## Hidden Foundational Skills

Some skills are foundational/internal and not intended for direct invocation.
Example:

- `mcp-common` (`user-invocable: false`)

These remain installable dependencies/foundations for related public skills.

Optional per-skill resources:

- `skills/<skill-name>/references/`
- `skills/<skill-name>/scripts/`
- `skills/<skill-name>/assets/`

## SKILL Frontmatter Contract

Each `SKILL.md` should include frontmatter:

```yaml
---
name: <skill-name>
description: <short behavior summary>
category: <role|command|process|enforcement|meta>
scope: <optional broad domain>
subcategory: <optional narrow grouping>
tags:
  - <optional tag>
  - <optional tag>
version: <version string>
author: <author name>
contact-email: <maintainer email>
website: <optional website url>
---
```

Notes:
- `category` is required so catalog grouping is stable.
- If `category` is omitted, ICA falls back to name-based inference and then defaults to `process`.
- `version` is required for contributed skills.
- `author` and `contact-email` are required for contributed skills.
- `website` is optional.
- `scope`, `subcategory`, and `tags` are optional but strongly recommended for filtering/grouping in UIs.

## Metadata for Filtering

Use these fields to support broader, non-development catalogs and better UI filtering:

- `scope`: broad domain
  - examples: `development`, `system-management`, `social-media`, `operations`, `marketing`
- `category`: primary classification within a scope
  - examples: `command`, `process`, `role`, `enforcement`, `meta`
- `subcategory`: optional finer grouping
  - examples: `installation`, `release`, `monitoring`, `publishing`
- `tags`: optional free-form keywords
  - examples: `onboarding`, `tdd`, `ci`, `security`

Suggested convention:
- Keep `scope`, `category`, and `subcategory` lowercase with hyphens.
- Keep tags short, lowercase, and stable over time.

## Root Skill Index (Performance)

This repository may include a root `skills.index.json` file to accelerate catalog loading.

- Purpose: avoid parsing every `SKILL.md` on each catalog refresh.
- Source of truth: `skills/*/SKILL.md` files.
- Index role: derived cache for fast discovery/filtering.
- Expected shape:
  - top-level: `version`, `generatedAt`, `skills[]`
  - per skill: `name`, `description`, `category`, optional `scope`, `subcategory`, `tags`, `version`, `author`, `contactEmail`, `website`

If index entries and `SKILL.md` differ, maintainers may regenerate the index during review.

## How to Contribute

Contributions are welcome through pull requests.

Contribution policy:

- Submit **custom skills only** via PR.
- Each PR is reviewed and may be:
  - accepted and merged
  - dismissed/rejected with feedback
- Keep each PR focused (prefer one skill per PR).
- Contributions must be compatible with this repository's MIT license.
- Contributions that require a different or additional license are not accepted.

Required structure:

- Add skills under `skills/<skill-name>/SKILL.md`
- Use lowercase, hyphenated folder and skill names
- Include frontmatter aligned with the enhanced ICA spec:
  - `name` (required)
  - `description` (required)
  - `category` (required)
  - `scope` (optional, recommended)
  - `subcategory` (optional)
  - `tags` (optional)
  - `version` (required)
  - `author` (required)
  - `contact-email` (required)
  - `website` (optional)

Recommended additions:

- `skills/<skill-name>/assets/` for prompt snippets or examples
- `skills/<skill-name>/references/` for optional deep documentation
- `skills/<skill-name>/scripts/` for deterministic helper scripts

PR checklist:

- [ ] Skill is custom and self-contained
- [ ] File path follows `skills/<skill-name>/SKILL.md`
- [ ] Frontmatter includes `name`, `description`, `category`, `version`, `author`, `contact-email` (and optional `website`)
- [ ] Frontmatter includes meaningful filter metadata (`scope`/`subcategory`/`tags`) when applicable
- [ ] Trigger language is specific (does not over-trigger)
- [ ] Instructions are ordered, actionable, and testable
- [ ] Includes validation checklist and at least one concrete example
- [ ] Contribution is MIT-compatible and does not introduce conflicting license terms

By submitting a contribution, you confirm that:

- you have the right to contribute the content
- you license your contribution under this repository's MIT license
- you are not adding code/content with conflicting license restrictions

## Notes

- ICA can consume this repo as a skill source, but ICA is not required to use these skills.
- If embedding another repository inside this repository, use the correct Git term: **submodule**.

## License and Warranty Disclaimer

This repository is licensed under the MIT License. See `LICENSE`.

All skills and related assets are provided **"AS IS"**, without warranties of any kind, express or implied, including merchantability, fitness for a particular purpose, and noninfringement.

No additional grants are provided beyond the MIT license terms, including no service, support, maintenance, certification, indemnity, or trademark grants.

To the maximum extent permitted by law, authors and contributors are not liable for any claim, damages, or other liability arising from, out of, or in connection with the skills or their use.
