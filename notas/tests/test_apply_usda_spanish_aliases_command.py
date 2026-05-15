from django.core.management import call_command
from django.test import TestCase

from notas.domain.models import Food, FoodAlias


class ApplyUSDASpanishAliasesCommandTests(TestCase):
    def test_command_applies_usda_spanish_aliases(self):
        Food.objects.create(
            name="Oats, raw",
            canonical_name="oats raw",
            protein=16.9,
            carbs=66.3,
            fat=6.9,
            created_by=None,
            is_global=True,
            is_active=True,
            visibility=Food.VISIBILITY_CORE,
        )

        call_command("apply_usda_spanish_aliases")

        self.assertTrue(
            FoodAlias.objects.filter(
                normalized_name="avena",
                language="es",
                country="CL",
            ).exists()
        )