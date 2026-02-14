---
name: mcp-config
description: Activate when setting up MCP servers, resolving MCP tool availability, or configuring fallbacks for MCP-dependent features. Configures and troubleshoots MCP (Model Context Protocol) integrations.
version: 10.2.14
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# MCP Configuration Skill

Configure and resolve MCP (Model Context Protocol) tool integrations.

## Core Rule for GitHub Tracking

For GitHub planning/tracking operations, prefer `gh` CLI first for token efficiency.

Use GitHub MCP (`mcp__github__*`) only when:
- `gh` CLI is unavailable or not authenticated
- an MCP-only workflow is explicitly required
- brokered auth/routing through `mcp-proxy` is required

## When to Use

- Setting up MCP servers
- Resolving MCP tool availability
- Configuring fallbacks for MCP features
- Troubleshooting MCP connectivity

## Tracking Config Contract

Read issue-tracking provider settings in this order:
1. `.agent/tracking.config.json` (project)
2. `${ICA_HOME}/tracking.config.json` (global)
3. `$HOME/.codex/tracking.config.json` or `$HOME/.claude/tracking.config.json` (fallback)

Recommended minimal schema:

```json
{
  "issue_tracking": {
    "provider": "github",
    "enabled": true,
    "repo": "owner/repo",
    "transport": "gh-cli-preferred",
    "fallback": "file-based"
  }
}
```

Supported providers:
- `github`
- `linear` (future)
- `jira` (future)
- `file-based`

## MCP Integration Points

### Memory Integration
```json
{
  "memory": {
    "provider": "mcp__memory",
    "enabled": false,
    "fallback": "file-based"
  }
}
```

### Issue Tracking
```json
{
  "issue_tracking": {
    "provider": "github",
    "enabled": false,
    "transport": "gh-cli-preferred",
    "fallback": "file-based"
  }
}
```

### Documentation
```json
{
  "documentation": {
    "provider": "file-based",
    "enabled": true
  }
}
```

## Available MCP Tools

### Context7
- `mcp__Context7__resolve-library-id` - Find library documentation
- `mcp__Context7__query-docs` - Query library documentation

### GitHub
- `mcp__github__*` - GitHub API operations

### MCP Proxy
- `proxy.list_servers` - Discover configured upstreams
- `proxy.list_tools` - Enumerate tools for a server
- `proxy.call` - Call upstream tool with centralized auth

### Brave Search
- `mcp__brave-search__brave_web_search` - Web search
- `mcp__brave-search__brave_local_search` - Local search

### Memory
- `mcp__memory__*` - Knowledge graph operations

### Playwright
- `mcp__playwright__*` - Browser automation

### Sequential Thinking
- `mcp__sequential-thinking__sequentialthinking` - Structured analysis

## Fallback Configuration

When MCP tools are unavailable:
1. Check if fallback is configured
2. Use fallback provider
3. Log degraded capability
4. Continue with reduced functionality

## MCP Resolution Process

1. **Check availability** - Is the MCP server running?
2. **Verify configuration** - Are credentials valid?
3. **Test connectivity** - Can we reach the service?
4. **Prefer gh for GitHub** - If provider is `github`, check `gh auth status`
5. **Apply fallback** - Use alternative if unavailable

GitHub-specific order:
1. Try `gh` CLI path (`gh auth status`, then `gh issue ...`, `gh api ...`)
2. If unavailable, try `mcp__github__*` directly
3. If direct MCP is constrained, route via `mcp-proxy` (`proxy.call`)
4. If all fail, fallback to `file-based`

## Configuration Location

MCP servers are configured for Claude Code in `~/.claude.json`:
```json
{
  "mcpServers": {
    "server-name": {
      "command": "...",
      "args": ["..."]
    }
  }
}
```

Proxy upstream definitions:
- Project: `.mcp.json`
- User/global: `${ICA_HOME}/mcp-servers.json`

## Troubleshooting

- **Server not found**: Check `~/.claude.json` `mcpServers`
- **Connection failed**: Verify server is running
- **Auth error**: Check credentials/tokens
- **Timeout**: Increase timeout or check network
- **GitHub mode mismatch**: confirm `transport` and `gh auth status`
