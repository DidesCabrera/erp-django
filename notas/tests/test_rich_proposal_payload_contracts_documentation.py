from pathlib import Path

from django.test import SimpleTestCase


class RichProposalPayloadContractsDocumentationTests(SimpleTestCase):
    def test_documentation_exists(self):
        path = Path("docs/architecture/rich_proposal_payload_contracts.md")

        self.assertTrue(path.exists())

    def test_documentation_mentions_supported_intents(self):
        content = Path(
            "docs/architecture/rich_proposal_payload_contracts.md"
        ).read_text()

        self.assertIn("create_meal", content)
        self.assertIn("create_dailyplan", content)

    def test_documentation_mentions_core_modules(self):
        content = Path(
            "docs/architecture/rich_proposal_payload_contracts.md"
        ).read_text()

        self.assertIn("notas/application/dto/proposal_payloads.py", content)
        self.assertIn(
            "notas/application/validation/proposal_payload_validators.py",
            content,
        )
        self.assertIn(
            "notas/application/queries/proposal_simulation_queries.py",
            content,
        )

    def test_documentation_mentions_product_boundary(self):
        content = Path(
            "docs/architecture/rich_proposal_payload_contracts.md"
        ).read_text()

        self.assertIn("does not", content)
        self.assertIn("create Meal records", content)
        self.assertIn("modify existing DailyPlans", content)
        self.assertIn("apply proposals", content)

    def test_documentation_mentions_next_stage(self):
        content = Path(
            "docs/architecture/rich_proposal_payload_contracts.md"
        ).read_text()

        self.assertIn("Etapa 2", content)
        self.assertIn("Crear propuesta de comida desde MCP", content)