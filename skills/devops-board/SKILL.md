---
name: devops-board
description: Manage work items on the Azure DevOps board for IT Operations / SRE. Use when the user asks to create, update, query, or list work items in Azure DevOps. Triggers on requests like "create a DevOps task", "create work item", "add to Azure DevOps board", "update DevOps item", "list DevOps tasks", "what's on the DevOps board", "assign DevOps work item".
---

# Azure DevOps Board (DevOps - SRE)

Manage work items on the **DevOps** board in Azure DevOps. Use `ToolSearch` with query `"+azureDevOps work item"` to load the required Azure DevOps MCP tools before proceeding.

## Board Reference

- **Organization**: `value-ag`
- **Project**: `Software`
- **Work Item Type**: `DevOps`
- **Area Path**: `Software\DevOps - SRE`
- **Iteration Path**: `Software`

## Work Item Fields

| Field | Parameter | Values |
|-------|-----------|--------|
| Title | `title` (required) | Work item title |
| Type | `workItemType` (required) | Always `DevOps` for this board |
| Assigned To | `assignedTo` | Email address |
| Priority | `priority` | `1` (highest) to `4` (lowest) |
| State | `state` | `New`, `In Planning`, `Approved`, `Committed`, `In Progress`, `Done`, `Closed` |
| Area Path | `areaPath` | `Software\DevOps - SRE` |
| Due Date | `additionalFields` | `{"Microsoft.VSTS.Scheduling.DueDate": "YYYY-MM-DD"}` |
| Description | `description` | HTML format |

## Known Team Members

| Name | Azure DevOps Email |
|------|-------------------|
| Boesswetter, Daniel | `daniel.boesswetter@extern.hypoport.de` |
| Samaschke, Karsten | `karsten.samaschke@extern.hypoport.de` |

## Create Work Items

Use `mcp__azureDevOps__create_work_item`:

```json
{
  "workItemType": "DevOps",
  "title": "Task title",
  "assignedTo": "daniel.boesswetter@extern.hypoport.de",
  "areaPath": "Software\\DevOps - SRE",
  "priority": 1,
  "description": "<p>Description in HTML.</p>",
  "additionalFields": {
    "Microsoft.VSTS.Scheduling.DueDate": "2026-02-11"
  }
}
```

Create multiple work items by making parallel `create_work_item` calls.

## Find Work Items

Use WIQL queries via `mcp__azureDevOps__list_work_items`:

```json
{
  "wiql": "SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo] FROM workitems WHERE [System.WorkItemType] = 'DevOps' AND [System.AreaPath] = 'Software\\DevOps - SRE' AND [System.State] <> 'Closed' ORDER BY [System.Id] DESC",
  "top": 20
}
```

Search by text via `mcp__azureDevOps__search_work_items`:

```json
{
  "searchText": "keywords",
  "projectId": "Software",
  "organizationId": "value-ag"
}
```

## Update Work Items

Use `mcp__azureDevOps__update_work_item`:

```json
{
  "workItemId": 57408,
  "state": "In Progress",
  "assignedTo": "daniel.boesswetter@extern.hypoport.de"
}
```

## Important

1. Always set `areaPath` to `Software\DevOps - SRE` and `workItemType` to `DevOps`
2. Priority is numeric: `1` = highest, `4` = lowest
3. Description must be **HTML format** (wrap in `<p>` tags)
4. Due dates go in `additionalFields` as `Microsoft.VSTS.Scheduling.DueDate`
5. Note the spelling: Daniel's Azure DevOps email uses **boesswetter** (double s), while his Notion name uses **boeswetter** (single s)
