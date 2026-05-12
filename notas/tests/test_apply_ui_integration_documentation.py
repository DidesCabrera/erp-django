from pathlib import Path

from django.test import SimpleTestCase


class ApplyUIIntegrationDocumentationTests(SimpleTestCase):
    def test_documentation_exists(self):
        path = Path("docs/architecture/apply_ui_integration.md")

        self.assertTrue(path.exists())

    def test_documentation_mentions_stage(self):
        content = Path(
            "docs/architecture/apply_ui_integration.md"
        ).read_text()

        self.assertIn("Etapa 6", content)
        self.assertIn("Apply UI Integration", content)

    def test_documentation_mentions_apply_route(self):
        content = Path(
            "docs/architecture/apply_ui_integration.md"
        ).read_text()

        self.assertIn("POST /app/proposals/<proposal_id>/apply/", content)
        self.assertIn("proposal_apply", content)

    def test_documentation_mentions_supported_intents(self):
        content = Path(
            "docs/architecture/apply_ui_integration.md"
        ).read_text()

        self.assertIn("create_meal", content)
        self.assertIn("create_dailyplan", content)

    def test_documentation_mentions_apply_commands(self):
        content = Path(
            "docs/architecture/apply_ui_integration.md"
        ).read_text()

        self.assertIn("apply_approved_create_meal_proposal", content)
        self.assertIn("apply_approved_create_dailyplan_proposal", content)

    def test_documentation_mentions_ui_partials(self):
        content = Path(
            "docs/architecture/apply_ui_integration.md"
        ).read_text()

        self.assertIn("review_apply_action.html", content)
        self.assertIn("review_applied_result.html", content)
        self.assertIn("review_actions.html", content)

    def test_documentation_mentions_double_apply_protection(self):
        content = Path(
            "docs/architecture/apply_ui_integration.md"
        ).read_text()

        self.assertIn("Double Apply Protection", content)
        self.assertIn("no duplicate Meal is created", content)
        self.assertIn("no duplicate DailyPlan is created", content)

    def test_documentation_mentions_mcp_boundary(self):
        content = Path(
            "docs/architecture/apply_ui_integration.md"
        ).read_text()

        self.assertIn("MCP cannot", content)
        self.assertIn("apply", content)

    def test_documentation_mentions_next_stage(self):
        content = Path(
            "docs/architecture/apply_ui_integration.md"
        ).read_text()

        self.assertIn("Etapa 7", content)
        self.assertIn("Proposal UX Polish and Audit Visibility", content)