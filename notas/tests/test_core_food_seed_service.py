from django.contrib.auth import get_user_model
from django.test import TestCase

from notas.application.services.food_imports.core_food_seed_service import (
    apply_core_food_seed_to_existing_global_foods,
)
from notas.domain.models import Food, FoodAlias, FoodLocalizedName


User = get_user_model()


class CoreFoodSeedServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="felipe",
            email="felipe@test.com",
            password="12345678",
        )

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

        self.user_food_with_same_canonical_name = Food.objects.create(
            name="Oats user copy",
            canonical_name="oats raw",
            protein=16.9,
            carbs=66.3,
            fat=6.9,
            created_by=self.user,
            is_global=False,
            is_verified=False,
            is_active=True,
            visibility=Food.VISIBILITY_EXTENDED,
            data_quality_score=75,
        )

    def test_apply_core_food_seed_promotes_known_global_foods(self):
        result = apply_core_food_seed_to_existing_global_foods()

        self.assertEqual(result.matched_foods, 2)
        self.assertEqual(result.promoted_foods, 2)

        self.oats.refresh_from_db()
        self.chicken.refresh_from_db()

        self.assertEqual(self.oats.visibility, Food.VISIBILITY_CORE)
        self.assertTrue(self.oats.is_verified)
        self.assertTrue(self.oats.is_active)

        self.assertEqual(self.chicken.visibility, Food.VISIBILITY_CORE)
        self.assertTrue(self.chicken.is_verified)
        self.assertTrue(self.chicken.is_active)

    def test_apply_core_food_seed_does_not_modify_unknown_global_foods(self):
        apply_core_food_seed_to_existing_global_foods()

        self.unknown_global.refresh_from_db()

        self.assertEqual(
            self.unknown_global.visibility,
            Food.VISIBILITY_EXTENDED,
        )
        self.assertFalse(self.unknown_global.is_verified)
        self.assertTrue(self.unknown_global.is_active)

    def test_apply_core_food_seed_does_not_modify_user_foods(self):
        apply_core_food_seed_to_existing_global_foods()

        self.user_food_with_same_canonical_name.refresh_from_db()

        self.assertFalse(self.user_food_with_same_canonical_name.is_global)
        self.assertFalse(self.user_food_with_same_canonical_name.is_verified)
        self.assertEqual(
            self.user_food_with_same_canonical_name.visibility,
            Food.VISIBILITY_EXTENDED,
        )

    def test_apply_core_food_seed_creates_aliases(self):
        result = apply_core_food_seed_to_existing_global_foods()

        self.assertGreater(result.created_aliases, 0)

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

    def test_apply_core_food_seed_creates_localized_names(self):
        result = apply_core_food_seed_to_existing_global_foods()

        self.assertEqual(result.created_localized_names, 2)

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

    def test_apply_core_food_seed_is_idempotent(self):
        first_result = apply_core_food_seed_to_existing_global_foods()
        second_result = apply_core_food_seed_to_existing_global_foods()

        self.assertEqual(first_result.matched_foods, 2)
        self.assertEqual(second_result.matched_foods, 2)

        self.assertGreater(first_result.created_aliases, 0)
        self.assertEqual(second_result.created_aliases, 0)
        self.assertGreater(second_result.skipped_aliases, 0)

        self.assertEqual(first_result.created_localized_names, 2)
        self.assertEqual(second_result.created_localized_names, 0)
        self.assertGreater(second_result.skipped_localized_names, 0)