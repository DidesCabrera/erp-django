# MCP Real Proposal Flow Test

## Purpose

This document records the real MCP flow for creating a reviewable NutritionProposal in My Scoope.

The tested flow is:

    MCP Inspector
      -> FastMCP protocol wrapper
      -> dispatch_tool_call
      -> MyscoopeAPIClient
      -> Django API Adapter
      -> Internal AI Tools
      -> NutritionProposal

---

## Required Services

Django must be running:

    python manage.py runserver

Expected Django base URL:

    http://127.0.0.1:8000/app

MCP Inspector must be running:

    npx @modelcontextprotocol/inspector

---

## Inspector Configuration

Transport:

    STDIO

Command:

    /Users/felipedides/Desktop/proyecto_django/venv/bin/python

Arguments:

    -m myscoope_mcp.run_protocol_server

Environment variables:

    PYTHONPATH=mcp_server
    MYSCOOPE_API_BASE_URL=http://127.0.0.1:8000/app

Do not use --check in Inspector.

---

## Step 1: read_dailyplan

Tool:

    read_dailyplan

Arguments:

    {
      "dailyplan_id": 123
    }

Expected successful shape:

    {
      "ok": true,
      "data": {
        "dailyplan": {}
      },
      "error": null
    }

---

## Step 2: compare_dailyplan_to_targets

Tool:

    compare_dailyplan_to_targets

Arguments:

    {
      "dailyplan_id": 123,
      "targets": {
        "protein": 190,
        "total_kcal": 2800
      },
      "tolerances": {
        "protein": 10,
        "total_kcal": 100
      }
    }

Expected successful shape:

    {
      "ok": true,
      "data": {
        "validation": {}
      },
      "error": null
    }

---

## Step 3: create_validated_dailyplan_proposal

Tool:

    create_validated_dailyplan_proposal

Arguments:

    {
      "dailyplan_id": 123,
      "title": "Propuesta MCP - Ajuste de proteína",
      "summary": "Propuesta creada desde MCP Inspector para acercar el plan a los objetivos definidos.",
      "targets": {
        "protein": 190,
        "total_kcal": 2800
      },
      "tolerances": {
        "protein": 10,
        "total_kcal": 100
      },
      "proposed_payload": {
        "intent": "adjust_dailyplan_to_targets",
        "suggested_changes": []
      }
    }

Expected successful shape:

    {
      "ok": true,
      "data": {
        "proposal": {}
      },
      "error": null
    }

---

## Verification in My Scoope

Open:

    http://127.0.0.1:8000/app/proposals/

Expected result:

    A proposal titled "Propuesta MCP - Ajuste de proteína" appears in the proposal list.

---

## Product Boundary

This flow creates a reviewable proposal.

It does not:

    approve the proposal;
    apply the proposal;
    modify the final DailyPlan;
    expose apply tools through MCP.

Final application remains inside My Scoope's authenticated human review flow.

---

## Possible Authentication Boundary

If the MCP call returns an authentication-related error, the MCP runtime is still correctly wired.

That means the next required stage is:

    Internal API Auth for MCP

The expected future solution is an internal token-based auth path from MCP to the Django API Adapter.
