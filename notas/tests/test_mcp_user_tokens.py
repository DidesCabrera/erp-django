from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from notas.application.services.mcp_user_tokens import (
    DEFAULT_MCP_USER_TOKEN_SCOPES,
    MCP_SCOPE_PROPOSALS_CREATE,
    MCP_SCOPE_READ,
    create_mcp_user_token,
    hash_mcp_user_token,
    revoke_mcp_user_token,
    validate_mcp_user_token,
)
from notas.domain.models import MCPUserToken


class MCPUserTokenServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="felipe",
            email="felipe@example.com",
            password="pass123",
        )

    def test_create_mcp_user_token_returns_raw_token_once_and_stores_hash(self):
        result = create_mcp_user_token(
            user=self.user,
            name="ChatGPT test token",
        )

        self.assertTrue(
            result.raw_token.startswith("mcp_user_"),
        )
        self.assertEqual(
            result.token.user,
            self.user,
        )
        self.assertEqual(
            result.token.name,
            "ChatGPT test token",
        )
        self.assertEqual(
            result.token.token_hash,
            hash_mcp_user_token(result.raw_token),
        )
        self.assertNotEqual(
            result.token.token_hash,
            result.raw_token,
        )
        self.assertEqual(
            result.token.scopes,
            DEFAULT_MCP_USER_TOKEN_SCOPES,
        )

    def test_validate_mcp_user_token_accepts_valid_token(self):
        created = create_mcp_user_token(
            user=self.user,
            name="ChatGPT test token",
        )

        result = validate_mcp_user_token(
            created.raw_token,
            required_scopes=[
                MCP_SCOPE_READ,
            ],
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.user,
            self.user,
        )
        self.assertEqual(
            result.token,
            created.token,
        )

        created.token.refresh_from_db()

        self.assertIsNotNone(
            created.token.last_used_at,
        )

    def test_validate_mcp_user_token_rejects_missing_token(self):
        result = validate_mcp_user_token("")

        self.assertFalse(result.ok)
        self.assertEqual(
            result.error.code,
            "mcp_user_token_missing",
        )

    def test_validate_mcp_user_token_rejects_unknown_token(self):
        result = validate_mcp_user_token("mcp_user_unknown")

        self.assertFalse(result.ok)
        self.assertEqual(
            result.error.code,
            "mcp_user_token_invalid",
        )

    def test_validate_mcp_user_token_rejects_inactive_token(self):
        created = create_mcp_user_token(
            user=self.user,
            name="ChatGPT test token",
        )
        created.token.is_active = False
        created.token.save(update_fields=["is_active"])

        result = validate_mcp_user_token(created.raw_token)

        self.assertFalse(result.ok)
        self.assertEqual(
            result.error.code,
            "mcp_user_token_inactive",
        )

    def test_validate_mcp_user_token_rejects_revoked_token(self):
        created = create_mcp_user_token(
            user=self.user,
            name="ChatGPT test token",
        )
        revoke_mcp_user_token(created.token)

        result = validate_mcp_user_token(created.raw_token)

        self.assertFalse(result.ok)
        self.assertEqual(
            result.error.code,
            "mcp_user_token_revoked",
        )

        created.token.refresh_from_db()

        self.assertIsNotNone(
            created.token.revoked_at,
        )



    def test_validate_mcp_user_token_rejects_expired_token(self):
        created = create_mcp_user_token(
            user=self.user,
            name="ChatGPT test token",
            expires_at=timezone.now() - timedelta(minutes=1),
        )

        result = validate_mcp_user_token(created.raw_token)

        self.assertFalse(result.ok)
        self.assertEqual(
            result.error.code,
            "mcp_user_token_expired",
        )

    def test_validate_mcp_user_token_rejects_inactive_user(self):
        created = create_mcp_user_token(
            user=self.user,
            name="ChatGPT test token",
        )
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        result = validate_mcp_user_token(created.raw_token)

        self.assertFalse(result.ok)
        self.assertEqual(
            result.error.code,
            "mcp_user_token_user_inactive",
        )

    def test_validate_mcp_user_token_rejects_missing_required_scope(self):
        created = create_mcp_user_token(
            user=self.user,
            name="Read-only token",
            scopes=[
                MCP_SCOPE_READ,
            ],
        )

        result = validate_mcp_user_token(
            created.raw_token,
            required_scopes=[
                MCP_SCOPE_PROPOSALS_CREATE,
            ],
        )

        self.assertFalse(result.ok)
        self.assertEqual(
            result.error.code,
            "mcp_user_token_missing_scope",
        )
        self.assertEqual(
            result.error.details,
            {
                "missing_scopes": [
                    MCP_SCOPE_PROPOSALS_CREATE,
                ],
            },
        )

    def test_revoke_mcp_user_token_marks_token_inactive_and_revoked(self):
        created = create_mcp_user_token(
            user=self.user,
            name="ChatGPT test token",
        )

        revoke_mcp_user_token(created.token)

        token = MCPUserToken.objects.get(id=created.token.id)

        self.assertFalse(
            token.is_active,
        )
        self.assertIsNotNone(
            token.revoked_at,
        )