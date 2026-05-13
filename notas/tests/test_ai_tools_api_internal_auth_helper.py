from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase, override_settings

from notas.application.services.mcp_user_tokens import (
    MCP_SCOPE_PROPOSALS_CREATE,
    MCP_SCOPE_READ,
    create_mcp_user_token,
)
from notas.interface.api.auth import (
    extract_bearer_token,
    get_authorization_header,
    resolve_internal_api_user,
)


class InternalAPIAuthHelperTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            username="felipe",
            email="felipe@example.com",
            password="pass123",
        )

        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="pass123",
        )

    def build_request(self, authorization: str | None = None):
        headers = {}

        if authorization is not None:
            headers["HTTP_AUTHORIZATION"] = authorization

        return self.factory.post(
            "/app/ai-tools/list-user-proposals/",
            data={},
            content_type="application/json",
            **headers,
        )

    def test_get_authorization_header_returns_empty_string_when_missing(self):
        request = self.build_request()

        self.assertEqual(
            get_authorization_header(request),
            "",
        )

    def test_get_authorization_header_reads_http_authorization(self):
        request = self.build_request(
            "Bearer dev-token",
        )

        self.assertEqual(
            get_authorization_header(request),
            "Bearer dev-token",
        )

    def test_extract_bearer_token_returns_empty_string_when_missing(self):
        request = self.build_request()

        self.assertEqual(
            extract_bearer_token(request),
            "",
        )

    def test_extract_bearer_token_returns_empty_string_for_non_bearer_header(self):
        request = self.build_request(
            "Token dev-token",
        )

        self.assertEqual(
            extract_bearer_token(request),
            "",
        )

    def test_extract_bearer_token_returns_trimmed_token(self):
        request = self.build_request(
            "Bearer   dev-token   ",
        )

        self.assertEqual(
            extract_bearer_token(request),
            "dev-token",
        )

    def test_resolve_internal_api_user_rejects_missing_token(self):
        request = self.build_request()

        result = resolve_internal_api_user(request)

        self.assertFalse(result.ok)
        self.assertIsNone(result.user)
        self.assertEqual(
            result.error.code,
            "internal_api_auth_missing",
        )

    @override_settings()
    def test_resolve_internal_api_user_rejects_missing_configured_token(self):
        request = self.build_request(
            "Bearer dev-token",
        )

        with self.settings():
            import os

            original_token = os.environ.pop(
                "MYSCOOPE_INTERNAL_API_TOKEN",
                None,
            )
            original_username = os.environ.get(
                "MYSCOOPE_INTERNAL_API_USERNAME",
            )

            try:
                os.environ["MYSCOOPE_INTERNAL_API_USERNAME"] = "felipe"

                result = resolve_internal_api_user(request)

                self.assertFalse(result.ok)
                self.assertEqual(
                    result.error.code,
                    "internal_api_auth_not_configured",
                )
            finally:
                if original_token is not None:
                    os.environ["MYSCOOPE_INTERNAL_API_TOKEN"] = original_token
                else:
                    os.environ.pop("MYSCOOPE_INTERNAL_API_TOKEN", None)

                if original_username is not None:
                    os.environ["MYSCOOPE_INTERNAL_API_USERNAME"] = original_username
                else:
                    os.environ.pop("MYSCOOPE_INTERNAL_API_USERNAME", None)

    def test_resolve_internal_api_user_rejects_invalid_token(self):
        request = self.build_request(
            "Bearer wrong-token",
        )

        with self._env(
            token="dev-token",
            username="felipe",
        ):
            result = resolve_internal_api_user(request)

        self.assertFalse(result.ok)
        self.assertEqual(
            result.error.code,
            "internal_api_auth_invalid",
        )

    def test_resolve_internal_api_user_rejects_missing_username_config(self):
        request = self.build_request(
            "Bearer dev-token",
        )

        with self._env(
            token="dev-token",
            username=None,
        ):
            result = resolve_internal_api_user(request)

        self.assertFalse(result.ok)
        self.assertEqual(
            result.error.code,
            "internal_api_auth_user_not_configured",
        )

    def test_resolve_internal_api_user_rejects_unknown_username(self):
        request = self.build_request(
            "Bearer dev-token",
        )

        with self._env(
            token="dev-token",
            username="unknown",
        ):
            result = resolve_internal_api_user(request)

        self.assertFalse(result.ok)
        self.assertEqual(
            result.error.code,
            "internal_api_auth_user_not_found",
        )
        self.assertEqual(
            result.error.details,
            {
                "username": "unknown",
            },
        )

    def test_resolve_internal_api_user_rejects_inactive_user(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        request = self.build_request(
            "Bearer dev-token",
        )

        with self._env(
            token="dev-token",
            username="felipe",
        ):
            result = resolve_internal_api_user(request)

        self.assertFalse(result.ok)
        self.assertEqual(
            result.error.code,
            "internal_api_auth_user_inactive",
        )

    def test_resolve_internal_api_user_returns_configured_user(self):
        request = self.build_request(
            "Bearer dev-token",
        )

        with self._env(
            token="dev-token",
            username="felipe",
        ):
            result = resolve_internal_api_user(request)

        self.assertTrue(result.ok)
        self.assertEqual(
            result.user,
            self.user,
        )
        self.assertEqual(
            result.auth_source,
            "internal_api",
        )
        self.assertIsNone(result.error)

    def test_resolve_internal_api_user_returns_mcp_user_token_owner(self):
        created = create_mcp_user_token(
            user=self.other_user,
            name="ChatGPT token",
            scopes=[
                MCP_SCOPE_READ,
            ],
        )
        request = self.build_request(
            f"Bearer {created.raw_token}",
        )

        with self._env(
            token=None,
            username=None,
        ):
            result = resolve_internal_api_user(
                request,
                required_scopes=[
                    MCP_SCOPE_READ,
                ],
            )

        self.assertTrue(result.ok)
        self.assertEqual(
            result.user,
            self.other_user,
        )
        self.assertEqual(
            result.auth_source,
            "mcp_user_token",
        )

    def test_resolve_internal_api_user_rejects_mcp_user_token_without_scope(self):
        created = create_mcp_user_token(
            user=self.other_user,
            name="Read-only token",
            scopes=[
                MCP_SCOPE_READ,
            ],
        )
        request = self.build_request(
            f"Bearer {created.raw_token}",
        )

        result = resolve_internal_api_user(
            request,
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
            result.error.status_code,
            403,
        )
        self.assertEqual(
            result.auth_source,
            "mcp_user_token",
        )

    def _env(self, token: str | None, username: str | None):
        return TemporaryEnv(
            {
                "MYSCOOPE_INTERNAL_API_TOKEN": token,
                "MYSCOOPE_INTERNAL_API_USERNAME": username,
            }
        )


class TemporaryEnv:
    def __init__(self, values):
        self.values = values
        self.previous = {}

    def __enter__(self):
        import os

        for key, value in self.values.items():
            self.previous[key] = os.environ.get(key)

            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

        return self

    def __exit__(self, exc_type, exc, traceback):
        import os

        for key, previous_value in self.previous.items():
            if previous_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = previous_value