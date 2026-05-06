# Internal API Auth for MCP

## Purpose

This stage adds an internal authentication path that allows the My Scoope MCP Server to call the Django AI Tools API Adapter as a configured user.

The goal is to unblock this flow:

    MCP Inspector / External AI
      -> FastMCP Server
      -> MyscoopeAPIClient
      -> Django API Adapter
      -> Internal AI Tools
      -> NutritionProposal

The MCP server must be able to authenticate without relying on a browser session.

---

## Problem

The Django API Adapter currently works with Django session authentication.

That works for normal web users, but an MCP server is not a browser session.

When the MCP server calls the API Adapter, Django may reject the request or return a login redirect.

This means the MCP runtime is wired correctly, but authentication from MCP to Django is missing.

---

## MVP Auth Strategy

For the local/private MVP, My Scoope will support an internal Bearer token.

Environment variables:

    MYSCOOPE_INTERNAL_API_TOKEN
    MYSCOOPE_INTERNAL_API_USERNAME

Example:

    MYSCOOPE_INTERNAL_API_TOKEN=dev-mcp-token
    MYSCOOPE_INTERNAL_API_USERNAME=felipe

The MCP server sends:

    Authorization: Bearer dev-mcp-token

The Django API Adapter validates the token and resolves:

    request.user = User(username="felipe")

---

## Why Username Instead of user_id

The MCP auth boundary must not accept user_id from the request payload.

Invalid pattern:

    {
      "user_id": 1,
      "dailyplan_id": 123
    }

Correct pattern:

    Authorization: Bearer <configured-token>

The server configuration determines the authenticated user.

This prevents an external client from impersonating another user by changing JSON payload data.

---

## Session Auth Still Works

This internal auth path must not break normal Django session auth.

Allowed paths:

    Browser session user
      -> request.user is already authenticated

    MCP Bearer token
      -> request.user is resolved from internal configuration

If neither is valid, the API Adapter rejects the request.

---

## Boundary Rules

The internal MCP auth layer must not:

- accept user_id as authority;
- accept username from payload;
- expose apply tools;
- bypass Internal AI Tools permissions;
- bypass API Adapter contracts;
- mutate data directly;
- authenticate arbitrary users dynamically;
- create users automatically.

The internal MCP auth layer may:

- read Authorization Bearer header;
- compare it with MYSCOOPE_INTERNAL_API_TOKEN;
- resolve a configured user from MYSCOOPE_INTERNAL_API_USERNAME;
- attach that user to the request before the AI tool view executes.

---

## Expected Request Flow

    MCP Server
      -> Authorization: Bearer <token>
      -> ai_tool_api_view decorator
      -> resolve internal API user
      -> request.user
      -> parse JSON
      -> endpoint function
      -> Internal AI Tool
      -> AIToolResult.as_dict()

---

## Error Cases

The implementation should handle:

    missing token
    invalid token
    missing configured username
    configured user does not exist
    inactive user
    anonymous user
    malformed Authorization header

Errors should preserve the API Adapter contract:

    {
      "ok": false,
      "data": {},
      "error": {
        "code": "...",
        "message": "...",
        "details": {}
      }
    }

---

## Expected Error Codes

Suggested stable error codes:

    internal_api_auth_missing
    internal_api_auth_invalid
    internal_api_auth_user_not_configured
    internal_api_auth_user_not_found
    internal_api_auth_user_inactive

---

## Security Note

This MVP is intended for local/private development.

Before public production exposure, My Scoope should evolve this into a stronger auth model:

- per-user MCP tokens;
- revocable tokens;
- scoped permissions;
- token expiration;
- audit metadata;
- OAuth or signed service credentials.

---

## Current Product Rule

The product rule remains unchanged:

    MCP can read.
    MCP can validate.
    MCP can create proposals.
    Human reviews.
    My Scoope applies approved changes safely.
    Everything is audited.

MCP must not apply final changes directly.
