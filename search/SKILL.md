---
name: search
description: Use this skill when the user asks to search for information, find documentation, look up something, or search across knowledge bases. Triggers on requests like "search for", "find docs about", "look up", "where can I find", "search wiki", "search notion".
---

# Cross-Platform Search Skill

This skill searches across multiple knowledge sources: **Azure DevOps Wiki** and **Notion**.

## Prerequisites

### Required MCP Servers
| Server | Tools | Purpose |
|--------|-------|---------|
| Azure DevOps MCP | `mcp__azureDevOps__search_wiki` | Search Azure DevOps wikis |
| Notion MCP | `mcp__notion__notion-search` | Search Notion workspace |

### Before Using This Skill

1. **Check tool availability**: Use `ToolSearch` to verify which sources are available
2. **Graceful degradation**: If only one source is available, search that source and inform user
3. **If no sources available**: Inform user which MCP servers need to be configured

### Availability Check
```
Before searching, determine available sources:

1. Call ToolSearch with query "azureDevOps wiki"
   - If found: Azure DevOps Wiki search is available
   - If not found: Set azure_available = false

2. Call ToolSearch with query "notion search"
   - If found: Notion search is available
   - If not found: Set notion_available = false

3. Based on availability:
   - Both available: Search both sources (default behavior)
   - Only Azure: Search Azure DevOps Wiki, note "Notion MCP not configured"
   - Only Notion: Search Notion, note "Azure DevOps MCP not configured"
   - Neither: Inform user "No search sources configured. Please configure Notion and/or Azure DevOps MCP servers."
```

### Setup Instructions
- **Notion MCP**: Requires Notion API key. See: https://developers.notion.com/docs/getting-started
- **Azure DevOps MCP**: Requires Azure DevOps PAT token with Wiki read permissions

## Available Search Sources

### 1. Azure DevOps Wiki
- **Tool**: `mcp__azureDevOps__search_wiki`
- **Default Organization**: value-ag
- **Default Project**: Software

### 2. Notion
- **Tool**: `mcp__notion__notion-search`
- **Supports**: Pages, databases, and connected sources (Slack, Google Drive, GitHub, Jira, etc.)

## Search Scopes

### Azure DevOps Wiki Scopes
| Scope | Description |
|-------|-------------|
| `all` | Search all wikis in the project |
| `project:<name>` | Limit to specific project (e.g., `project:Software`) |

### Notion Scopes
| Scope | Description |
|-------|-------------|
| `all` | Search entire Notion workspace |
| `page:<url-or-id>` | Search within a specific page and its children |
| `teamspace:<id>` | Search within a specific teamspace |
| `database:<url>` | Search within a specific database |
| `engineering-docs` | Shortcut for IT Operations Engineering Docs |

## How to Use

When the user requests a search, determine:
1. **What** they're searching for (the query)
2. **Where** they want to search (source and scope)

### Default Behavior
If the user doesn't specify a source:
- Search **both** Azure DevOps Wiki and Notion
- Present results from each source clearly separated

### User-Specified Scope Examples
- "Search wiki for deployment process" → Azure DevOps Wiki only
- "Search Notion for runbooks" → Notion only
- "Find info about VPN setup in engineering docs" → Notion, scoped to Engineering Docs
- "Search everywhere for authentication" → Both sources

## Implementation

### Search Azure DevOps Wiki
```json
{
  "searchText": "<query>",
  "projectId": "Software",
  "organizationId": "value-ag"
}
```

### Search Notion (All)
```json
{
  "query": "<query>",
  "query_type": "internal"
}
```

### Search Notion (Scoped to Engineering Docs)
```json
{
  "query": "<query>",
  "query_type": "internal",
  "page_url": "https://www.notion.so/2a257acbd749804892cbd19c1a5d79c4"
}
```

### Search Notion (Scoped to Page)
```json
{
  "query": "<query>",
  "query_type": "internal",
  "page_url": "<page-url-or-id>"
}
```

## Response Format

Present search results in a clear, organized format:

```markdown
## Search Results for "<query>"

### Azure DevOps Wiki
1. **[Page Title](url)** - Preview snippet...
2. **[Page Title](url)** - Preview snippet...

### Notion
1. **[Page Title](url)** - Preview snippet...
2. **[Page Title](url)** - Preview snippet...

---
*No results found in [source]* (if applicable)
```

## Asking for Clarification

If the search query is ambiguous, ask the user:
- Which source(s) to search (Wiki, Notion, or both)
- Any specific scope/area to limit the search
- Keywords to refine the search

## Common Searches

| User Request | Action |
|--------------|--------|
| "Search for runbook" | Both sources, look for runbook documentation |
| "Find deployment docs in wiki" | Azure DevOps Wiki only |
| "Search engineering docs for VPN" | Notion, scoped to Engineering Docs |
| "Look up incident reports" | Notion, category filter for Incident |
| "Find pipeline configuration" | Azure DevOps Wiki (likely CI/CD docs) |

## Tips

1. **Be thorough**: Search both sources unless explicitly limited
2. **Summarize results**: Don't just list links, provide context
3. **Offer to fetch**: If user needs details, offer to fetch the full page
4. **Suggest refinements**: If too many results, suggest narrowing the scope
