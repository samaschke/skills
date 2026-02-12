---
name: engineering-docs
description: Use this skill when the user asks to create a runbook, document an approach, create a guide, generate a post mortem, or add any documentation to the IT Operations Engineering Docs in Notion. Triggers on requests like "create a runbook", "document this", "write a post mortem", "add to engineering docs", "create documentation for".
---

# Engineering Docs Creator

This skill creates documentation entries in the **IT Operations > Engineering Docs** database in Notion.

## Prerequisites

### Required MCP Server
- **Notion MCP Server** must be configured and running

### Required Tools
| Tool | Purpose |
|------|---------|
| `mcp__notion__notion-search` | Search for existing docs |
| `mcp__notion__notion-fetch` | Fetch page details |
| `mcp__notion__notion-create-pages` | Create new documentation |

### Before Using This Skill

1. **Check tool availability**: Use `ToolSearch` with query `"notion"` to verify Notion tools are loaded
2. **If tools are missing**: Inform the user that the Notion MCP server needs to be configured
3. **Setup instructions**: The Notion MCP server requires a Notion API key. See: https://developers.notion.com/docs/getting-started

### Availability Check
```
Before proceeding, verify the Notion MCP tools are available:
1. Call ToolSearch with query "notion create"
2. If mcp__notion__notion-create-pages is NOT found:
   - Inform user: "The Notion MCP server is not configured. Please add it to your Claude Code MCP settings."
   - Do NOT attempt to create documentation
3. If found: Proceed with the skill
```

## Database Information

- **Database URL**: https://www.notion.so/2a257acbd749804892cbd19c1a5d79c4
- **Data Source ID**: `2a257acb-d749-8025-a4b2-000b3bf734d4`

## Available Properties

When creating pages, use these properties:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `Doc name` | title | Yes | The document title (e.g., "Runbook: XYZ") |
| `Category` | multi_select | Yes | JSON array of categories |
| `Status` | status | No | "Draft", "In Review", "Published", "Outdated" |
| `Summary` | text | Yes | Brief description of the document |
| `Author` | person | No | Auto-set by Notion |

## Available Categories

Use one or more of these categories (as JSON array):
- `Runbook` - Step-by-step operational procedures
- `Operations` - General operations documentation
- `Guide` - How-to guides and tutorials
- `Incident` - Incident reports
- `Infrastructure` - Infrastructure documentation
- `Architecture` - Architecture decisions and diagrams
- `Tech Spec` - Technical specifications
- `Best Practices` - Best practice guidelines
- `Backup & DR` - Backup and disaster recovery
- `Monitoring` - Monitoring and alerting
- `Security` - Security documentation
- `Maintenance` - Maintenance procedures
- `Environment` - Environment configurations
- `Access` - Access and permissions
- `Workflows` - Workflow documentation
- `Permissions` - Permission matrices

## Document Templates

### Runbook Template

Title format: `Runbook: [Action/System Name]`
Categories: `["Runbook", "Operations"]`

Content structure:
```markdown
# Overview
Brief description of what this runbook accomplishes.

# Prerequisites
- **Prerequisite 1** - Description
- **Prerequisite 2** - Description

# Step-by-Step Instructions
1. **Step Title**
   Detailed instructions for this step.
   `command or path here`

2. **Step Title**
   Detailed instructions for this step.

## Side Notes / Background Information
Optional additional context or troubleshooting tips.
```

### Post Mortem Template

Title format: `Postmortem: [Incident Title]`
Categories: `["Incident", "Operations"]`

Content structure:
```markdown
# Incident Summary
| Field | Value |
|-------|-------|
| Date | YYYY-MM-DD |
| Duration | X hours |
| Severity | High/Medium/Low |
| Services Affected | List services |

# Timeline
- **HH:MM** - Event description
- **HH:MM** - Event description

# Root Cause
Description of what caused the incident.

# Impact
Description of the impact on users/systems.

# Resolution
How the incident was resolved.

# Action Items
- [ ] Action item 1
- [ ] Action item 2

# Lessons Learned
Key takeaways from this incident.
```

### Guide Template

Title format: `Guide: [Topic Name]` or `[Topic Name] Guide`
Categories: `["Guide"]` (add relevant secondary categories)

Content structure:
```markdown
# Overview
What this guide covers and who it's for.

# Prerequisites
What you need before starting.

# Instructions
## Section 1
Content...

## Section 2
Content...

# Troubleshooting
Common issues and solutions.

# Related Documentation
Links to related docs.
```

## How to Create a Document

Use the Notion MCP tool `mcp__notion__notion-create-pages` with:

```json
{
  "parent": {"data_source_id": "2a257acb-d749-8025-a4b2-000b3bf734d4"},
  "pages": [{
    "properties": {
      "Doc name": "Title here",
      "Category": "[\"Category1\", \"Category2\"]",
      "Status": "Published",
      "Summary": "Brief summary of the document content."
    },
    "content": "Markdown content here..."
  }]
}
```

## Important Notes

1. **Always use the correct data source ID**: `2a257acb-d749-8025-a4b2-000b3bf734d4`
2. **Category must be a JSON array string**: `"[\"Runbook\"]"` not `["Runbook"]`
3. **Don't include the title in the content** - it's set via the `Doc name` property
4. **Set Status to "Published"** unless the user specifies otherwise
5. **Write a meaningful Summary** - this appears in list views
6. **Follow existing naming conventions**:
   - Runbooks: `Runbook: [Name]`
   - Post Mortems: `Postmortem: [Name]`
   - Guides: `Guide: [Name]` or `[Name] Guide`
   - Workflows: `Workflow: [Name]`

## Example: Creating a Runbook

```
User: "Create a runbook for restarting the payment service"

1. Gather information about the procedure from the user
2. Use the Runbook template structure
3. Create the page with:
   - Doc name: "Runbook: Payment Service Restart"
   - Category: ["Runbook", "Operations"]
   - Status: "Published"
   - Summary: Brief description
   - Content: Formatted markdown with Overview, Prerequisites, Steps
4. Return the Notion URL to the user
```
