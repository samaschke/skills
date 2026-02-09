---
name: commit-pr
description: Use this skill when the user asks to commit changes, create a git commit, make a PR, create a pull request, push changes, or any git commit/PR related task. This skill overrides default commit behavior.
---

# Git Commit and Pull Request Skill

This skill handles git commits and pull requests with specific formatting requirements.

## Prerequisites

### Required Tools
| Tool | Purpose | Required |
|------|---------|----------|
| `git` | Version control | Yes |
| `gh` (GitHub CLI) | Create GitHub PRs | For GitHub repos |
| Azure DevOps MCP | Create Azure DevOps PRs | For Azure DevOps repos |

### Before Using This Skill

1. **Verify git is available**: Run `git --version` via Bash
2. **For GitHub PRs**: Check if `gh` CLI is installed (`gh --version`)
3. **For Azure DevOps PRs**: Verify `mcp__azureDevOps__create_pull_request` is available via ToolSearch

### Availability Check
```
Before creating PRs:

For GitHub:
1. Run: gh --version
2. If not found: Inform user "GitHub CLI (gh) is not installed. Install via: winget install GitHub.cli"
3. If found but not authenticated: "Run 'gh auth login' to authenticate"

For Azure DevOps:
1. Call ToolSearch with query "azureDevOps pull_request"
2. If not found: "Azure DevOps MCP server is not configured"
3. If found: Proceed with mcp__azureDevOps__create_pull_request
```

### Setup Instructions
- **GitHub CLI**: `winget install GitHub.cli` then `gh auth login`
- **Azure DevOps MCP**: Configure in Claude Code MCP settings with PAT token

## CRITICAL RULES

**NEVER include any of the following in commits or PRs:**
- `Co-Authored-By: Claude` or any Claude attribution
- Any mention of "Claude", "Claude Code", "AI", "Assistant", or "Anthropic"
- Any indication that code was AI-generated or AI-assisted
- Footer lines like "Generated with Claude Code"

## Commit Message Format

Use this format for commit messages:

```
<type>: <short description>

<optional body with more details>
```

### Commit Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `style`: Formatting, missing semicolons, etc.
- `perf`: Performance improvements

### Example Commit Messages

```bash
# Simple commit
git commit -m "feat: Add user authentication endpoint"

# Commit with body (use HEREDOC)
git commit -m "$(cat <<'EOF'
fix: Resolve race condition in payment processing

The payment processor was not properly awaiting the transaction
confirmation before updating the order status. Added proper
async/await handling.
EOF
)"
```

## Pull Request Format

When creating PRs with `gh pr create`:

```bash
gh pr create --title "<type>: <short title>" --body "$(cat <<'EOF'
## Summary
- Bullet point 1
- Bullet point 2

## Changes
- Description of changes

## Test Plan
- [ ] Test case 1
- [ ] Test case 2
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
4. Create commit with proper message format
5. **DO NOT add any Co-Authored-By or AI attribution**

### For Pull Requests:
1. Ensure all changes are committed
2. Push branch to remote if needed
3. Run `git log main..HEAD` to see all commits for the PR
4. Create PR with `gh pr create`
5. **DO NOT add any "Generated with" footer or AI attribution**

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

## Reminders

1. **No AI attribution** - Never mention Claude, AI, or automated generation
2. **Be specific** - Describe what changed and why
3. **Keep it clean** - No unnecessary files (check .gitignore)
4. **Review first** - Always `git diff` before committing
