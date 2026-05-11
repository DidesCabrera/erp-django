from pathlib import Path

from django.test import SimpleTestCase


class SafeApplyFlowDocumentationTests(SimpleTestCase):
    def test_documentation_exists(self):
        path = Path(
            "docs/architecture/safe_apply_flow_for_approved_proposals.md"
        )

        self.assertTrue(path.exists())

    def test_documentation_mentions_supported_intents(self):
        content = Path(
            "docs/architecture/safe_apply_flow_for_approved_proposals.md"
        ).read_text()

        self.assertIn("create_meal", content)
        self.assertIn("create_dailyplan", content)

    def test_documentation_mentions_apply_contract_layer(self):
        content = Path(
            "docs/architecture/safe_apply_flow_for_approved_proposals.md"
        ).read_text()

        self.assertIn("notas/application/dto/proposal_apply.py", content)
        self.assertIn("build_create_meal_apply_plan", content)
        self.assertIn("build_create_dailyplan_apply_plan", content)

    def test_documentation_mentions_apply_commands(self):
        content = Path(
            "docs/architecture/safe_apply_flow_for_approved_proposals.md"
        ).read_text()

        self.assertIn("apply_approved_create_meal_proposal", content)
        self.assertIn("apply_approved_create_dailyplan_proposal", content)

    def test_documentation_mentions_create_meal_boundary(self):
        content = Path(
            "docs/architecture/safe_apply_flow_for_approved_proposals.md"
        ).read_text()

        self.assertIn("does not", content)
        self.assertIn("attach the Meal to any DailyPlan", content)
        self.assertIn("modify the context DailyPlan", content)

    def test_documentation_mentions_create_dailyplan_snapshots(self):
        content = Path(
            "docs/architecture/safe_apply_flow_for_approved_proposals.md"
        ).read_text()

        self.assertIn("snapshot Meals", content)
        self.assertIn("DailyPlanMeal", content)
        self.assertIn("not reusable Meals", content)

    def test_documentation_mentions_mcp_boundary(self):
        content = Path(
            "docs/architecture/safe_apply_flow_for_approved_proposals.md"
        ).read_text()

        self.assertIn("Apply tools are not exposed to MCP", content)
        self.assertIn("MCP cannot", content)
        self.assertIn("apply", content)

    def test_documentation_mentions_next_stage(self):
        content = Path(
            "docs/architecture/safe_apply_flow_for_approved_proposals.md"
        ).read_text()

        self.assertIn("Etapa 6", content)
        self.assertIn("Apply UI Integration", content)