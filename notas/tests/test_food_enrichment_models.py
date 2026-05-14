from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from notas.domain.models import (
    Food,
    FoodAlias,
    FoodImportBatch,
    FoodPortion,
    FoodSourceMetadata,
)


class FoodEnrichmentModelsTests(TestCase):
    def test_food_can_be_created_with_enrichment_defaults(self):
        user = User.objects.create_user(
            username="felipe",
            password="pass123",
        )

        food = Food.objects.create(
            name="Avena",
            protein=16.9,
            carbs=66.3,
            fat=6.9,
            created_by=user,
        )

        self.assertEqual(food.canonical_name, "")
        self.assertFalse(food.is_global)
        self.assertFalse(food.is_verified)
        self.assertTrue(food.is_active)
        self.assertEqual(food.food_group, "")
        self.assertEqual(food.food_subgroup, "")
        self.assertEqual(food.visibility, Food.VISIBILITY_EXTENDED)
        self.assertEqual(food.data_quality_score, 0)
        self.assertEqual(food.category, "user")

    def test_global_food_keeps_existing_category_contract(self):
        food = Food.objects.create(
            name="Plátano global",
            protein=1.1,
            carbs=23,
            fat=0.3,
            created_by=None,
            is_global=True,
        )

        self.assertEqual(food.category, "system")

    def test_food_source_metadata_can_track_manual_food(self):
        food = Food.objects.create(
            name="Pechuga de pollo",
            protein=31,
            carbs=0,
            fat=3.6,
            created_by=None,
        )

        metadata = FoodSourceMetadata.objects.create(
            food=food,
            source=FoodSourceMetadata.SOURCE_MANUAL,
            source_food_id="",
            source_dataset="manual",
            source_version="",
            license_name="",
        )

        self.assertEqual(metadata.food, food)
        self.assertEqual(metadata.source, FoodSourceMetadata.SOURCE_MANUAL)

    def test_food_portion_can_store_standard_grams(self):
        food = Food.objects.create(
            name="Huevo",
            protein=12.6,
            carbs=0.7,
            fat=9.5,
            created_by=None,
        )

        portion = FoodPortion.objects.create(
            food=food,
            label="1 huevo grande",
            grams=Decimal("50"),
            source="manual",
            is_default=True,
        )

        self.assertEqual(portion.food, food)
        self.assertEqual(portion.label, "1 huevo grande")
        self.assertEqual(portion.grams, Decimal("50"))
        self.assertTrue(portion.is_default)

    def test_food_alias_can_store_search_alias(self):
        food = Food.objects.create(
            name="Pechuga de pollo",
            protein=31,
            carbs=0,
            fat=3.6,
            created_by=None,
        )

        alias = FoodAlias.objects.create(
            food=food,
            name="Chicken breast",
            normalized_name="chicken breast",
            language="en",
            country="",
        )

        self.assertEqual(alias.food, food)
        self.assertEqual(alias.name, "Chicken breast")
        self.assertEqual(alias.normalized_name, "chicken breast")

    def test_food_import_batch_tracks_import_counts(self):
        batch = FoodImportBatch.objects.create(
            source="usda",
            source_version="test-version",
            status=FoodImportBatch.STATUS_COMPLETED,
            total_rows=100,
            imported_rows=80,
            skipped_rows=15,
            failed_rows=5,
        )

        self.assertEqual(batch.source, "usda")
        self.assertEqual(batch.total_rows, 100)
        self.assertEqual(batch.imported_rows, 80)
        self.assertEqual(batch.skipped_rows, 15)
        self.assertEqual(batch.failed_rows, 5)