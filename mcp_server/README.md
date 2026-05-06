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

## Manual Harness

The MCP server includes a small manual harness for local development.

Example:

```bash
PYTHONPATH=mcp_server python -m myscoope_mcp.manual_harness read_dailyplan \
  --arguments '{"dailyplan_id": 123}'

## Real MCP Protocol Wrapper

The next stage connects the existing dispatcher to the official Python MCP SDK.

The real MCP wrapper must remain thin:

```text
FastMCP tool
  → dispatch_tool_call
  → MyscoopeAPIClient
  → Django API Adapter