import json

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class AIToolsAPIInternalAuthCSRFFreeTests(TestCase):
    def setUp(self):
        self.client_with_csrf = Client(enforce_csrf_checks=True)

        self.user = User.objects.create_user(
            username="felipe",
            email="felipe@example.com",
            password="pass123",
        )

    def test_internal_auth_bearer_request_does_not_require_csrf_token(self):
        with self._env(
            token="dev-token",
            username="felipe",
        ):
            response = self.client_with_csrf.post(
                reverse("ai_tools_list_user_proposals"),
                data=json.dumps({}),
                content_type="application/json",
                HTTP_AUTHORIZATION="Bearer dev-token",
            )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertTrue(data["ok"])
        self.assertIn("proposals", data["data"])
        self.assertIsNone(data["error"])

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

        return False
        