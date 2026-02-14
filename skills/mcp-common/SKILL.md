---
name: "mcp-common"
description: "Internal shared helpers for ICA MCP tooling (client/proxy). Not intended to be invoked directly by users."
category: "meta"
scope: "system-management"
subcategory: "internal"
tags:
  - mcp
  - internal
  - shared
  - foundation
user-invocable: false
version: "10.2.14"
author: "Karsten Samaschke"
contact-email: "karsten@vanillacore.net"
website: "https://vanillacore.net"
---

# MCP Common (Internal)

Shared Python helpers used by ICA MCP tools:
- `mcp-client`
- `mcp-proxy`

This skill is not meant to be invoked directly. It exists to keep `mcp-client` and `mcp-proxy` consistent and avoid copy/paste drift.

