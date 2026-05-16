from django.core.management import call_command
from django.test import TestCase

from notas.domain.models import Food, FoodAlias, FoodLocalizedName


class ApplyCoreFoodSeedCommandTests(TestCase):
    def setUp(self):
        self.oats = Food.objects.create(
            name="Oats, raw",
            canonical_name="oats raw",
            protein=16.9,
            carbs=66.3,
            fat=6.9,
            created_by=None,
            is_global=True,
            is_verified=False,
            is_active=False,
            visibility=Food.VISIBILITY_HIDDEN,
            data_quality_score=75,
        )

        self.chicken = Food.objects.create(
            name="Chicken breast, cooked",
            canonical_name="chicken breast cooked",
            protein=31,
            carbs=0,
            fat=3.6,
            created_by=None,
            is_global=True,
            is_verified=False,
            is_active=True,
            visibility=Food.VISIBILITY_EXTENDED,
            data_quality_score=75,
        )

        self.unknown_global = Food.objects.create(
            name="Unknown global food",
            canonical_name="unknown global food",
            protein=1,
            carbs=1,
            fat=1,
            created_by=None,
            is_global=True,
            is_verified=False,
            is_active=True,
            visibility=Food.VISIBILITY_EXTENDED,
            data_quality_score=60,
        )

    def test_apply_core_food_seed_command_promotes_seed_foods(self):
        call_command("apply_core_food_seed")

        self.oats.refresh_from_db()
        self.chicken.refresh_from_db()
        self.unknown_global.refresh_from_db()

        self.assertEqual(self.oats.visibility, Food.VISIBILITY_CORE)
        self.assertTrue(self.oats.is_verified)
        self.assertTrue(self.oats.is_active)

        self.assertEqual(self.chicken.visibility, Food.VISIBILITY_CORE)
        self.assertTrue(self.chicken.is_verified)
        self.assertTrue(self.chicken.is_active)

        self.assertEqual(
            self.unknown_global.visibility,
            Food.VISIBILITY_EXTENDED,
        )
        self.assertFalse(self.unknown_global.is_verified)

    def test_apply_core_food_seed_command_creates_aliases(self):
        call_command("apply_core_food_seed")

        self.assertTrue(
            FoodAlias.objects.filter(
                food=self.oats,
                normalized_name="avena",
                language="es",
                country="CL",
            ).exists()
        )

        self.assertTrue(
            FoodAlias.objects.filter(
                food=self.chicken,
                normalized_name="pollo",
                language="es",
                country="CL",
            ).exists()
        )

    def test_apply_core_food_seed_command_creates_localized_names(self):
        call_command("apply_core_food_seed")

        self.assertTrue(
            FoodLocalizedName.objects.filter(
                food=self.oats,
                normalized_name="avena",
                language="es",
                country="CL",
                is_primary=True,
            ).exists()
        )

        self.assertTrue(
            FoodLocalizedName.objects.filter(
                food=self.chicken,
                normalized_name="pechuga de pollo cocida",
                language="es",
                country="CL",
                is_primary=True,
            ).exists()
        )

    def test_apply_core_food_seed_command_is_idempotent(self):
        call_command("apply_core_food_seed")

        alias_count = FoodAlias.objects.count()
        localized_name_count = FoodLocalizedName.objects.count()

        call_command("apply_core_food_seed")

        self.assertEqual(FoodAlias.objects.count(), alias_count)
        self.assertEqual(FoodLocalizedName.objects.count(), localized_name_count)