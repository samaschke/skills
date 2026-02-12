# Intelligent Code Agents Skills

This repository is the standalone skills source for ICA.

## Layout

All skills live under:

- `skills/<skill-name>/SKILL.md`

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
version: <optional version string>
---
```

Notes:
- `category` is recommended so catalog grouping is stable.
- If `category` is omitted, ICA falls back to name-based inference and then defaults to `process`.
- `version` is optional but recommended for ICA-provided skills.

## Notes

- This repo is consumed by ICA as a source repository.
- If embedding another repository inside this repository, use the correct Git term: **submodule**.
