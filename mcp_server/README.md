# My Scoope MCP Server MVP

This folder contains the future MCP Server MVP for My Scoope.

The MCP server is intentionally separate from the Django app.

## Architecture

```text
MCP Client / External AI
  → MCP Server
  → Django API Adapter
  → Internal AI Tools Layer
  → Read / Validation / Proposal Layers
  → Domain