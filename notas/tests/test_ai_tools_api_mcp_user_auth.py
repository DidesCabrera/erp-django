import json

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from notas.application.services.mcp_user_tokens import (
    MCP_SCOPE_PROPOSALS_CREATE,
    MCP_SCOPE_READ,
    create_mcp_user_token,
)


class AIToolsAPIMCPUserAuthTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username="felipe",
            email="felipe@example.com",
            password="pass123",
        )

    def test_read_endpoint_accepts_mcp_user_token_with_read_scope(self):
        created = create_mcp_user_token(
            user=self.user,
            name="Read token",
            scopes=[
                MCP_SCOPE_READ,
            ],
        )

        response = self.client.post(
            reverse("ai_tools_list_user_proposals"),
            data=json.dumps({}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {created.raw_token}",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertTrue(data["ok"])
        self.assertIn(
            "proposals",
            data["data"],
        )
        self.assertIsNone(
            data["error"],
        )

    def test_create_endpoint_rejects_mcp_user_token_without_create_scope(self):
        created = create_mcp_user_token(
            user=self.user,
            name="Read-only token",
            scopes=[
                MCP_SCOPE_READ,
            ],
        )

        response = self.client.post(
            reverse("ai_tools_create_validated_dailyplan_build_proposal"),
            data=json.dumps({}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {created.raw_token}",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        data = response.json()

        self.assertFalse(data["ok"])
        self.assertEqual(
            data["error"]["code"],
            "mcp_user_token_missing_scope",
        )

    def test_create_endpoint_accepts_mcp_user_token_with_create_scope(self):
        created = create_mcp_user_token(
            user=self.user,
            name="Create token",
            scopes=[
                MCP_SCOPE_PROPOSALS_CREATE,
            ],
        )

        response = self.client.post(
            reverse("ai_tools_create_validated_dailyplan_build_proposal"),
            data=json.dumps({}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {created.raw_token}",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        data = response.json()

        self.assertFalse(data["ok"])
        self.assertEqual(
            data["error"]["code"],
            "missing_required_field:dailyplan_id",
        )