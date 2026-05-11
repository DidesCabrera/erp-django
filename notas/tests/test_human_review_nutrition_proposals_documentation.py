from pathlib import Path

from django.test import SimpleTestCase


class HumanReviewNutritionProposalsDocumentationTests(SimpleTestCase):
    def test_documentation_exists(self):
        path = Path("docs/architecture/human_review_nutrition_proposals.md")

        self.assertTrue(path.exists())

    def test_documentation_mentions_supported_intents(self):
        content = Path(
            "docs/architecture/human_review_nutrition_proposals.md"
        ).read_text()

        self.assertIn("create_meal", content)
        self.assertIn("create_dailyplan", content)

    def test_documentation_mentions_review_viewmodel(self):
        content = Path(
            "docs/architecture/human_review_nutrition_proposals.md"
        ).read_text()

        self.assertIn(
            "notas/presentation/proposals/proposal_review_viewmodels.py",
            content,
        )
        self.assertIn("build_proposal_review_vm", content)
        self.assertIn("vm.content.proposal_review", content)

    def test_documentation_mentions_templates(self):
        content = Path(
            "docs/architecture/human_review_nutrition_proposals.md"
        ).read_text()

        self.assertIn(
            "notas/templates/notas/proposals/partials/review_create_meal.html",
            content,
        )
        self.assertIn(
            "notas/templates/notas/proposals/partials/review_create_dailyplan.html",
            content,
        )
        self.assertIn(
            "notas/templates/notas/proposals/partials/review_actions.html",
            content,
        )

    def test_documentation_mentions_safe_boundary(self):
        content = Path(
            "docs/architecture/human_review_nutrition_proposals.md"
        ).read_text()

        self.assertIn("does not apply nutrition changes", content)
        self.assertIn("does not create a final `Meal`", content)
        self.assertIn("does not create a final `DailyPlan`", content)

    def test_documentation_mentions_review_actions(self):
        content = Path(
            "docs/architecture/human_review_nutrition_proposals.md"
        ).read_text()

        self.assertIn("Aprobar propuesta", content)
        self.assertIn("Rechazar propuesta", content)
        self.assertIn("Cancelar propuesta", content)

    def test_documentation_mentions_next_stage(self):
        content = Path(
            "docs/architecture/human_review_nutrition_proposals.md"
        ).read_text()

        self.assertIn("Etapa 5", content)
        self.assertIn("Safe Apply Flow for Approved Proposals", content)