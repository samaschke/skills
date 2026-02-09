---
name: hww-proposal
description: Use this skill when the user asks to create an HWW proposal, a "how we work" proposal, or any decision proposal using the IDM (Integrative Decision Making) process. Triggers on requests like "create an HWW proposal", "new proposal for how we work", "HWW proposal", "create a process proposal", "IDM proposal".
---

# HWW Proposal Creator

This skill creates proposals in the **Team > How we work > Processes** Engineering Docs database in Notion, using the Integrative Decision Making (IDM) process template.

**IMPORTANT**: This is the **Team-level** Engineering Docs database, NOT the IT Operations Engineering Docs.

## Prerequisites

### Required MCP Server
- **Notion MCP Server** must be configured and running

### Required Tools
| Tool | Purpose |
|------|---------|
| `mcp__notion__notion-search` | Search for existing proposals |
| `mcp__notion__notion-fetch` | Fetch page details |
| `mcp__notion__notion-create-pages` | Create new proposal pages |
| `mcp__notion__notion-get-users` | Look up the user's Notion ID for Author property |

### Before Using This Skill

1. **Check tool availability**: Use `ToolSearch` with query `"notion create"` to verify `mcp__notion__notion-create-pages` is available
2. **If tools are missing**: Inform the user: "The Notion MCP server is not configured. Please add it to your Claude Code MCP settings."
3. **Setup instructions**: The Notion MCP server requires a Notion API key. See: https://developers.notion.com/docs/getting-started

### Availability Check
```
Before proceeding, verify the Notion MCP tools are available:
1. Call ToolSearch with query "notion create"
2. If mcp__notion__notion-create-pages is NOT found:
   - Inform user: "The Notion MCP server is not configured. Please add it to your Claude Code MCP settings."
   - Do NOT attempt to create the proposal
3. If found: Proceed with the skill
```

## Database Information

- **Database URL**: https://www.notion.so/28b57acbd74980af86ddc361d1885ab1
- **Data Source ID**: `28b57acb-d749-802c-a0bd-000bcc27b64a`

**WARNING**: Do NOT confuse with the IT Operations Engineering Docs database (`2a257acb-d749-8025-a4b2-000b3bf734d4`). This skill uses the Team-level database.

## Available Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `Doc name` | title | Yes | Proposal title |
| `Author` | person | Yes | User ID string (looked up dynamically via `notion-get-users`) |
| `Status` | status | Yes | Always `Proposal` for new proposals |
| `Category` | multi_select | Yes | One or more categories (see below) |
| `Summary` | text | Yes | Brief one-liner describing the proposal |
| `Reviewer` | person | No | Optional reviewer |
| `Reviewers` | person | No | Optional additional reviewers |

### Property Format Rules

**CRITICAL** — these formats were validated through trial and error:
- `Author`: Plain user ID string, e.g. `"23ed872b-594c-813d-967b-00029b5a5134"` — NOT an array, NOT a mention tag
- `Category`: Plain string, e.g. `"Process"` or `"Architecture"` — NOT a JSON array
- `Status`: Plain string `"Proposal"`
- `Doc name`: Plain string
- `Summary`: Plain string

### Available Categories

- `Tech Spec`
- `PRD`
- `Guide`
- `Best Practices`
- `Architecture`
- `Process`
- `Incident / Failure Root Cause Analysis`

### Status Lifecycle

`Draft` → `Data gathering` → `Proposal` → `Decided/Published` / `Outdated`

New proposals always start at `Proposal` status.

## Workflow

### Step 1: Gather Information from the User

Ask the user for:
1. **Proposal title** — what is the proposal about?
2. **Category** — one of the available categories (most proposals use `Process` or `Architecture`)
3. **Summary** — a one-line summary for the database view
4. **Proposal content** — the actual proposal details: context, problem, options considered, recommended approach, consequences, etc.

If the user provides a natural language description, structure it into the proposal content format.

### Step 2: Look Up the User's Notion ID

Call `mcp__notion__notion-get-users` to find the current user:

```json
{
  "query": "<user's name or partial name>"
}
```

Extract the `id` field from the matching result. This is used as the `Author` property value.

### Step 3: Create the Proposal Page

Use `mcp__notion__notion-create-pages` with the IDM template + proposal content:

```json
{
  "parent": {
    "data_source_id": "28b57acb-d749-802c-a0bd-000bcc27b64a"
  },
  "pages": [{
    "properties": {
      "Doc name": "<Proposal Title>",
      "Author": "<user-notion-id>",
      "Status": "Proposal",
      "Category": "<category>",
      "Summary": "<one-line summary>"
    },
    "content": "<IDM template + proposal content (see below)>"
  }]
}
```

### Step 4: Return the Notion URL

After creation, return the Notion URL from the response to the user.

## IDM Template (Verbatim)

Every proposal page MUST include this IDM template as the first section of the content. The `Proposal` toggle section contains the user's actual proposal content. The `Decision` toggle is always created empty.

**Copy this template exactly** — the indentation (tabs), toggle symbols (`▶`), `<empty-block/>` tags, and formatting are all required for Notion to render the page correctly:

```
# **\>\> Proposal Stage, please review the proposal \<\<**
Process
▶### **1. Present the Proposal**
	One person (the proposer) states:
	- The problem to solve
	- The proposed technical solution
	- Purpose & intent
	- Constraints & assumptions
	- Scope of the decision
	The Facilitator ensures the proposal is **clear, concise, and ideally testable**.
	<empty-block/>
▶### **2. Clarifying Questions Round**
	Team members may ask *only clarifying questions* — not reactions, opinions, or arguments.
	✔️ Good question:
	- "Does the proposed caching layer apply only to read operations?"
	✖️ Bad question (not allowed yet):
	- "Are you sure this is efficient enough?" → This is a reaction.
	<br>The goal is that **everyone **<span underline="true">**understands**</span>** the proposal.**
	---
	<empty-block/>
	<empty-block/>
▶### **3. Reaction Round**
	Round robin: each person shares a brief, personal reaction.
	✔️ They may express concerns, excitement, alternatives, intuitions.
	✖️ They may NOT debate or discuss reactions.
	(This step is essential for lowering **emotional charge** and making **hidden information visible)**
	---
	<empty-block/>
	<empty-block/>
	<empty-block/>
▶### **4. Proposal Amendments (Optional)**
	The proposer may adjust the proposal after hearing reactions.
	But nobody else may alter it.
	---
	<empty-block/>
	<empty-block/>
▶### **5. Objection Round**
	The Facilitator asks:
	> "Do you see any reason this proposal is **not safe enough to try or might cause harm** to the team or system?"
	Participants may raise **objections** that must meet the validity criteria:
	### ✔️ Valid Technical Objections (Examples)
	- "This will violate a key performance constraint (X)."
	- "We know this approach breaks compatibility with module Y."
	- "We lack essential infrastructure to run this."
	- "This prevents another role from fulfilling a core responsibility."
	### ✖️ Invalid Objections (Examples)
	- "I prefer another design."
	- "This doesn't feel elegant."
	- "This isn't how I would do it."
	- "We haven't analyzed every detail yet."
	- "What if it doesn't scale in five years?"
	The Facilitator filters objections using a strict **validity test** (detailed below).
	▶### Validity test
		The facilitator asks:
		- **Is this objection based on existing constraints or responsibilities?**
		- **Does this proposal truly cause harm or is it just uncertainty?**
		- **Is the harm concrete and evidence-based?**
		- **Is the risk unacceptable — or merely possible?**
		If the objection fails the test → **invalid → discarded**.
		<empty-block/>
		Many tech objections are invalid because they are:
		- about preference
		- based on fear of the unknown
		- "what-if" speculation
		- requests for more analysis (which stalls progress)
		<empty-block/>
	---
	<empty-block/>
	<empty-block/>
	<empty-block/>
▶### **6. Integration Round**
	If objections exist, the group integrates them by modifying the proposal in a way that:
	✔️ Addresses the objection
	✔️ Preserves the proposal's core intent
	✔️ Moves the decision forward
	<empty-block/>
	The Facilitator encourages integrative thinking:
	- What is the *real risk* behind the objection?
	- Can we add a constraint, guardrail, or monitoring?
	- Can we narrow the scope?
	- Can we timebox or create a prototype first?
	- What's the smallest version of the proposal that is safe to try?
	<empty-block/>
	Most objections are resolved here.
	---
	<empty-block/>
	<empty-block/>
	<empty-block/>
	<empty-block/>
	<empty-block/>
	▶### **What Happens When an Objection Cannot Be Integrated?**
		This is the most important part.
		Not possible to integrate means:
		- The objection reflects a **real risk**
		- The proposal **cannot be modified to eliminate the risk**
		- And the group is **stuck**
		There are several options to go from here:
		<empty-block/>
		▶ ▶️ **Option 1: Split the Decision**
			Break the proposal into **smaller, safer pieces.**
			**Example:**
			- Instead of "switch our whole backend to event-sourcing,"
			decide only on "implement event-sourcing for 1 service to evaluate feasibility."
			This resolves many "unintegrable" objections.
		▶ ▶️ Option 2: Adjust Scope or Add Constraints
			The proposal becomes:
			- narrower
			- timeboxed
			- limited to a prototype
			- reversible
			This turns risk into experimentation.
		▶ ▶️ Option 3: Add Safeguards / Monitoring
			Example:
			- Error rate threshold
			- Performance threshold
			- Rollback plan
			- Feature flag
			- Canary release
			The objection often evaporates if there's a rollback path.
		▶ ▶️ Option 4: Defer Parts, Decide the Rest (similar to Option 2)
			Some decisions can move forward even if a subcomponent is postponed.
			**Example**:
			You can choose the overall architecture pattern but postpone the database technology selection.
		▶ ▶️ Option 5: Change the Proposal Completely
			If valid objections show the proposal is fundamentally flawed, the Facilitator may:
			- Stop the process
			- Ask the Proposer to draft a new proposal
			- Or invite others to propose alternatives
			This avoids forcing a bad decision.
		▶ ▶️ Option 6: Use the "Least Harmful Safe-to-Try Option"
			This is key: Our decisions should **never require full agreement**.
			If multiple valid objections exist but one option is still **safer to try than the others**,
			that option becomes the decision.
			This keeps the team moving.
---
<empty-block/>
<empty-block/>
<empty-block/>
▶## Proposal
	<PROPOSAL_CONTENT_HERE>
<empty-block/>
▶## Decision
	<empty-block/>
<empty-block/>
```

### How to Use the Template

1. Copy the entire template above
2. Replace `<PROPOSAL_CONTENT_HERE>` with the user's actual proposal content (formatted as Notion-flavored markdown with tab indentation since it's inside a toggle)
3. The `Decision` toggle stays empty — it will be filled in after the IDM process is complete

## Content Formatting Notes

The content uses **Notion-flavored Markdown** with these special elements:
- **Tab indentation** (`\t`) — content inside toggles must be indented with tabs
- **Toggle symbols** — `▶` at the start of a line creates a collapsible toggle
- **Empty blocks** — `<empty-block/>` creates visual spacing
- **Underline spans** — `<span underline="true">text</span>`
- **Escaped angle brackets** — `\>\>` and `\<\<` in headings
- **Horizontal rules** — `---` for visual separation within toggles

## Example

```
User: "Create an HWW proposal for adopting trunk-based development"

1. Look up user → notion-get-users with query matching the user's name
2. Get user ID from response (e.g. "23ed872b-594c-813d-967b-00029b5a5134")
3. Create page:
   - Doc name: "Adopt Trunk-Based Development"
   - Author: "<user-id>"
   - Status: "Proposal"
   - Category: "Process"
   - Summary: "Transition from feature branches to trunk-based development with short-lived branches and feature flags."
   - Content: IDM template with proposal content in the Proposal toggle
4. Return Notion URL to user
```

## Important Notes

1. **Always use the correct data source ID**: `28b57acb-d749-802c-a0bd-000bcc27b64a` (Team Engineering Docs)
2. **Do NOT use** the IT Operations database (`2a257acb-d749-8025-a4b2-000b3bf734d4`)
3. **Property values are plain strings** — not arrays, not JSON, not mention tags
4. **Always look up the user's Notion ID** — do not hardcode it
5. **Always include the full IDM template** — it is the standard for all HWW proposals
6. **The Proposal toggle must contain the actual proposal content** — indented with tabs
7. **The Decision toggle is always empty** on creation
8. **Don't include the title in the content** — it's set via the `Doc name` property
