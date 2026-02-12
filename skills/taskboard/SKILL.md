---
name: taskboard
description: Manage tasks in the IT Operations Taskboard (Notion). Use when the user asks to create, update, query, or list tasks in the Notion task tracker. Triggers on requests like "create a task in Notion", "add a task to the board", "update task status", "assign task to", "list Notion tasks", "what tasks are open", "manage taskboard", "task tracker".
---

# IT Operations Taskboard (Notion)

Manage tasks in the **Tasks Tracker** database in Notion. Use `ToolSearch` with query `"notion"` to load the required Notion MCP tools before proceeding.

## Database Reference

- **Data Source ID**: `2bc57acb-d749-8062-b7a7-000be1c688ee`
- **Database URL**: https://www.notion.so/2bc57acbd74980819b1cf04601aa762e
- **Teamspace**: IT Operations (`29c57acb-d749-81f0-b2d2-004280b09680`)

## Schema

| Property | Type | Values |
|----------|------|--------|
| `Task name` | title (required) | Task title |
| `Status` | status | `Not started`, `In progress`, `Done` |
| `Priority` | select | `High`, `Medium`, `Low` (no "Highest" — use `High` as maximum) |
| `Assignee` | person | JSON array string of user IDs |
| `Due date` | date | Expanded format: `date:Due date:start`, `date:Due date:end`, `date:Due date:is_datetime` (0 or 1) |
| `Task type` | multi_select | JSON array: `🐞 Bug`, `💬 Feature request`, `💅 Polish`, `Upgrade` |
| `Effort level` | select | `Small`, `Medium`, `Large` |
| `Description` | text | Detailed task description |
| `Summary` | text | Brief summary |
| `Azure DevOps Task` | url | Link to related Azure DevOps work item |

## Known Team Members

| Name | Notion User ID |
|------|----------------|
| Boeswetter, Daniel | `28cd872b-594c-81b9-bc61-00021801a189` |

For other users, query `mcp__notion__notion-get-users` with `{"query": "<name>"}`.

## Create Tasks

Use `mcp__notion__notion-create-pages`. Create up to 100 tasks per call.

```json
{
  "parent": {"data_source_id": "2bc57acb-d749-8062-b7a7-000be1c688ee"},
  "pages": [{
    "properties": {
      "Task name": "Title",
      "Status": "Not started",
      "Priority": "High",
      "Assignee": "[\"<user-id>\"]",
      "date:Due date:start": "2026-02-11",
      "date:Due date:is_datetime": 0,
      "Description": "What needs to be done."
    }
  }]
}
```

## Find Tasks

Search within database:
```json
mcp__notion__notion-search({
  "query": "keywords",
  "data_source_url": "collection://2bc57acb-d749-8062-b7a7-000be1c688ee"
})
```

Query "All Tasks" view:
```json
mcp__notion__notion-query-database-view({
  "view_url": "view://2bc57acb-d749-80f6-9cb0-000c124b1be1"
})
```

## Update Tasks

Use `mcp__notion__notion-update-page` with the task's page ID:
```json
mcp__notion__notion-update-page({
  "page_id": "<task-page-id>",
  "properties": {"Status": "In progress", "Priority": "High"}
})
```

## Important

1. Assignee and Task type values must be **JSON array strings**: `"[\"id\"]"` not `["id"]`
2. Do not include the title in page content — set it via `Task name` property
3. Default Status to `Not started` for new tasks
4. Look up unknown user IDs dynamically via `mcp__notion__notion-get-users`
