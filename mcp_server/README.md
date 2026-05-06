# My Scoope MCP Server

This folder contains the MCP Server and Real MCP Protocol Wrapper for My Scoope.

The MCP server is intentionally separate from the Django app.

## Architecture

```text
MCP Client / External AI
  → FastMCP Protocol Wrapper
  → dispatch_tool_call
  → MCP tool handlers
  → MyscoopeAPIClient
  → Django API Adapter
  → Internal AI Tools Layer
  → Read / Validation / Proposal Layers
  → Domain