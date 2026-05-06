import json
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notas.domain.models import (
    DailyPlan,
    DailyPlanMeal,
    Food,
    Meal,
    MealFood,
    NutritionProposal,
    WeightLog,
)


def json_post(
    client,
    url_name: str,
    payload: dict | None = None,
    token: str | None = None,
):
    headers = {}

    if token is not None:
        headers["HTTP_AUTHORIZATION"] = f"Bearer {token}"

    return client.post(
        reverse(url_name),
        data=json.dumps(payload or {}),
        content_type="application/json",
        **headers,
    )


class AIToolsAPIInternalAuthContractTests(TestCase):
    def setUp(self):
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

        WeightLog.objects.create(
            user=self.user,
            date=date.today(),
            weight_kg=100,
        )

        self.food = Food.objects.create(
            name="Base Food",
            protein=10,
            carbs=20,
            fat=0,
            created_by=self.user,
        )

        self.meal = Meal.objects.create(
            name="Base Meal",
            created_by=self.user,
            is_public=False,
            is_draft=False,
        )

        self.mealfood = MealFood.objects.create(
            meal=self.meal,
            food=self.food,
            quantity=100,
            order=1,
        )

        self.dailyplan = DailyPlan.objects.create(
            name="Training Day",
            created_by=self.user,
            is_public=False,
            is_draft=False,
        )

        DailyPlanMeal.objects.create(
            dailyplan=self.dailyplan,
            meal=self.meal,
            order=1,
        )

        self.other_dailyplan = DailyPlan.objects.create(
            name="Other Private Plan",
            created_by=self.other_user,
            is_public=False,
            is_draft=False,
        )

        self.proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            source=NutritionProposal.SOURCE_AI,
            title="Existing proposal",
            targets={
                "protein": 190,
            },
            proposed_payload={
                "intent": "adjust_dailyplan_to_targets",
                "suggested_changes": [],
            },
        )

        self.other_proposal = NutritionProposal.objects.create(
            dailyplan=self.other_dailyplan,
            created_by=self.other_user,
            source=NutritionProposal.SOURCE_AI,
            title="Other private proposal",
            targets={
                "protein": 190,
            },
            proposed_payload={
                "intent": "adjust_dailyplan_to_targets",
                "suggested_changes": [],
            },
        )

    def assert_success_response(self, response):
        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(
            set(data.keys()),
            {
                "ok",
                "data",
                "error",
            },
        )
        self.assertTrue(data["ok"])
        self.assertIsInstance(data["data"], dict)
        self.assertIsNone(data["error"])

        json.dumps(data)

        return data

    def assert_error_response(
        self,
        response,
        code: str,
        status_code: int = 200,
    ):
        self.assertEqual(response.status_code, status_code)

        data = response.json()

        self.assertEqual(
            set(data.keys()),
            {
                "ok",
                "data",
                "error",
            },
        )
        self.assertFalse(data["ok"])
        self.assertEqual(data["data"], {})
        self.assertIsInstance(data["error"], dict)
        self.assertEqual(data["error"]["code"], code)

        json.dumps(data)

        return data

    def test_internal_auth_can_read_dailyplan(self):
        with self._env(
            token="dev-token",
            username="felipe",
        ):
            response = json_post(
                self.client,
                "ai_tools_read_dailyplan",
                {
                    "dailyplan_id": self.dailyplan.id,
                },
                token="dev-token",
            )

        data = self.assert_success_response(response)

        self.assertEqual(
            data["data"]["dailyplan"]["id"],
            self.dailyplan.id,
        )

    def test_internal_auth_can_read_proposal(self):
        with self._env(
            token="dev-token",
            username="felipe",
        ):
            response = json_post(
                self.client,
                "ai_tools_read_proposal",
                {
                    "proposal_id": self.proposal.id,
                },
                token="dev-token",
            )

        data = self.assert_success_response(response)

        self.assertEqual(
            data["data"]["proposal"]["id"],
            self.proposal.id,
        )

    def test_internal_auth_can_compare_dailyplan_to_targets(self):
        with self._env(
            token="dev-token",
            username="felipe",
        ):
            response = json_post(
                self.client,
                "ai_tools_compare_dailyplan_to_targets",
                {
                    "dailyplan_id": self.dailyplan.id,
                    "targets": {
                        "protein": 30,
                        "total_kcal": 200,
                    },
                    "tolerances": {
                        "protein": 5,
                        "total_kcal": 10,
                    },
                },
                token="dev-token",
            )

        data = self.assert_success_response(response)

        self.assertIn(
            "validation",
            data["data"],
        )

    def test_internal_auth_can_create_validated_proposal(self):
        with self._env(
            token="dev-token",
            username="felipe",
        ):
            response = json_post(
                self.client,
                "ai_tools_create_validated_dailyplan_proposal",
                {
                    "dailyplan_id": self.dailyplan.id,
                    "title": "MCP proposal",
                    "summary": "Created through internal API auth.",
                    "targets": {
                        "protein": 30,
                        "total_kcal": 200,
                    },
                    "tolerances": {
                        "protein": 5,
                        "total_kcal": 10,
                    },
                    "proposed_payload": {
                        "intent": "adjust_dailyplan_to_targets",
                        "suggested_changes": [
                            {
                                "type": "update_meal_food_quantity",
                                "mealfood_id": self.mealfood.id,
                                "from_quantity": 100,
                                "to_quantity": 150,
                            }
                        ],
                    },
                },
                token="dev-token",
            )

        data = self.assert_success_response(response)

        proposal_data = data["data"]["proposal"]

        self.assertEqual(
            proposal_data["title"],
            "MCP proposal",
        )
        self.assertEqual(
            proposal_data["dailyplan_id"],
            self.dailyplan.id,
        )

        proposal = NutritionProposal.objects.get(
            id=proposal_data["id"],
        )

        self.assertEqual(
            proposal.created_by,
            self.user,
        )
        self.assertEqual(
            proposal.dailyplan,
            self.dailyplan,
        )

        self.mealfood.refresh_from_db()

        self.assertEqual(
            self.mealfood.quantity,
            100,
        )

    def test_internal_auth_blocks_private_dailyplan_from_other_user(self):
        with self._env(
            token="dev-token",
            username="felipe",
        ):
            response = json_post(
                self.client,
                "ai_tools_read_dailyplan",
                {
                    "dailyplan_id": self.other_dailyplan.id,
                },
                token="dev-token",
            )

        self.assert_error_response(
            response,
            "not_found",
        )

    def test_internal_auth_blocks_private_proposal_from_other_user(self):
        with self._env(
            token="dev-token",
            username="felipe",
        ):
            response = json_post(
                self.client,
                "ai_tools_read_proposal",
                {
                    "proposal_id": self.other_proposal.id,
                },
                token="dev-token",
            )

        self.assert_error_response(
            response,
            "not_found",
        )

    def test_internal_auth_does_not_allow_user_id_impersonation_for_proposal_creation(self):
        with self._env(
            token="dev-token",
            username="felipe",
        ):
            response = json_post(
                self.client,
                "ai_tools_create_validated_dailyplan_proposal",
                {
                    "user_id": self.other_user.id,
                    "dailyplan_id": self.other_dailyplan.id,
                    "title": "Should not be created",
                    "targets": {
                        "protein": 30,
                    },
                },
                token="dev-token",
            )

        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(data["ok"])
        self.assertIn(
            data["error"]["code"],
            {
                "not_found",
                "dailyplan_not_available_for_proposal",
            },
        )

        self.assertFalse(
            NutritionProposal.objects.filter(
                title="Should not be created",
                dailyplan=self.other_dailyplan,
                created_by=self.user,
            ).exists()
        )

    def test_internal_auth_preserves_invalid_json_contract(self):
        with self._env(
            token="dev-token",
            username="felipe",
        ):
            response = self.client.post(
                reverse("ai_tools_list_user_proposals"),
                data="{invalid json",
                content_type="application/json",
                HTTP_AUTHORIZATION="Bearer dev-token",
            )

        self.assert_error_response(
            response,
            "invalid_json",
            status_code=400,
        )

    def test_internal_auth_preserves_non_object_json_contract(self):
        with self._env(
            token="dev-token",
            username="felipe",
        ):
            response = self.client.post(
                reverse("ai_tools_list_user_proposals"),
                data=json.dumps(["not", "object"]),
                content_type="application/json",
                HTTP_AUTHORIZATION="Bearer dev-token",
            )

        self.assert_error_response(
            response,
            "json_body_must_be_object",
            status_code=400,
        )

    def test_internal_auth_preserves_method_not_allowed_contract(self):
        with self._env(
            token="dev-token",
            username="felipe",
        ):
            response = self.client.get(
                reverse("ai_tools_list_user_proposals"),
                HTTP_AUTHORIZATION="Bearer dev-token",
            )

        self.assert_error_response(
            response,
            "method_not_allowed",
            status_code=405,
        )

    def test_missing_auth_still_redirects_like_session_login(self):
        response = json_post(
            self.client,
            "ai_tools_list_user_proposals",
            {},
        )

        self.assertEqual(
            response.status_code,
            302,
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

        return False