from django.core.management import call_command
from django.test import TestCase

from notas.domain.models import Food, FoodAlias, FoodLocalizedName


class ApplyCoreFoodSeedCommandTests(TestCase):
    def setUp(self):
        self.oats = self._create_global_food(
            name="Oats, raw",
            canonical_name="oats raw",
            protein=16.9,
            carbs=66.3,
            fat=6.9,
            is_active=False,
            visibility=Food.VISIBILITY_HIDDEN,
        )

        self.chicken = self._create_global_food(
            name="Chicken breast, cooked",
            canonical_name="chicken breast cooked",
            protein=31,
            carbs=0,
            fat=3.6,
        )

        self.egg = self._create_global_food(
            name="Eggs, Grade A, Large, egg whole",
            canonical_name="eggs grade a large egg whole",
            protein=12.4,
            carbs=0.96,
            fat=9.96,
        )

        self.white_rice = self._create_global_food(
            name="Rice, white, long grain, unenriched, raw",
            canonical_name="rice white long grain unenriched raw",
            protein=7.13,
            carbs=80,
            fat=0.66,
        )

        self.brown_rice = self._create_global_food(
            name="Rice, brown, long grain, unenriched, raw",
            canonical_name="rice brown long grain unenriched raw",
            protein=7.5,
            carbs=76.2,
            fat=2.68,
        )

        self.almonds = self._create_global_food(
            name="Nuts, almonds, whole, raw",
            canonical_name="nuts almonds whole raw",
            protein=21.2,
            carbs=21.6,
            fat=49.9,
        )

        self.kale = self._create_global_food(
            name="Kale, raw",
            canonical_name="kale raw",
            protein=2.92,
            carbs=4.42,
            fat=1.49,
        )

        self.hummus = self._create_global_food(
            name="Hummus, commercial",
            canonical_name="hummus commercial",
            protein=7.35,
            carbs=14.9,
            fat=17.1,
        )

        self.unknown_global = self._create_global_food(
            name="Unknown global food",
            canonical_name="unknown global food",
            protein=1,
            carbs=1,
            fat=1,
            data_quality_score=60,
        )

    def test_apply_core_food_seed_command_promotes_seed_foods(self):
        call_command("apply_core_food_seed")

        for food in self._seed_foods():
            food.refresh_from_db()
            self.assertEqual(food.visibility, Food.VISIBILITY_CORE)
            self.assertTrue(food.is_verified)
            self.assertTrue(food.is_active)

        self.unknown_global.refresh_from_db()

        self.assertEqual(
            self.unknown_global.visibility,
            Food.VISIBILITY_EXTENDED,
        )
        self.assertFalse(self.unknown_global.is_verified)

    def test_apply_core_food_seed_command_creates_aliases(self):
        call_command("apply_core_food_seed")

        expected_aliases = [
            (self.oats, "avena"),
            (self.chicken, "pollo"),
            (self.egg, "huevo"),
            (self.white_rice, "arroz blanco"),
            (self.brown_rice, "arroz integral"),
            (self.almonds, "almendras"),
            (self.kale, "col rizada"),
            (self.hummus, "humus"),
        ]

        for food, normalized_name in expected_aliases:
            self.assertTrue(
                FoodAlias.objects.filter(
                    food=food,
                    normalized_name=normalized_name,
                    language="es",
                    country="CL",
                ).exists(),
                msg=f"Missing alias {normalized_name!r} for {food.canonical_name!r}",
            )

    def test_apply_core_food_seed_command_creates_localized_names(self):
        call_command("apply_core_food_seed")

        expected_localized_names = [
            (self.oats, "avena"),
            (self.chicken, "pechuga de pollo cocida"),
            (self.egg, "huevo entero"),
            (self.white_rice, "arroz blanco crudo"),
            (self.brown_rice, "arroz integral crudo"),
            (self.almonds, "almendras crudas"),
            (self.kale, "kale crudo"),
            (self.hummus, "hummus"),
        ]

        for food, normalized_name in expected_localized_names:
            self.assertTrue(
                FoodLocalizedName.objects.filter(
                    food=food,
                    normalized_name=normalized_name,
                    language="es",
                    country="CL",
                    is_primary=True,
                ).exists(),
                msg=(
                    f"Missing localized name {normalized_name!r} "
                    f"for {food.canonical_name!r}"
                ),
            )

    def test_apply_core_food_seed_command_is_idempotent(self):
        call_command("apply_core_food_seed")

        alias_count = FoodAlias.objects.count()
        localized_name_count = FoodLocalizedName.objects.count()

        call_command("apply_core_food_seed")

        self.assertEqual(FoodAlias.objects.count(), alias_count)
        self.assertEqual(FoodLocalizedName.objects.count(), localized_name_count)

    def _seed_foods(self):
        return [
            self.oats,
            self.chicken,
            self.egg,
            self.white_rice,
            self.brown_rice,
            self.almonds,
            self.kale,
            self.hummus,
        ]

    def _create_global_food(
        self,
        *,
        name,
        canonical_name,
        protein,
        carbs,
        fat,
        is_active=True,
        visibility=Food.VISIBILITY_EXTENDED,
        data_quality_score=75,
    ):
        return Food.objects.create(
            name=name,
            canonical_name=canonical_name,
            protein=protein,
            carbs=carbs,
            fat=fat,
            created_by=None,
            is_global=True,
            is_verified=False,
            is_active=is_active,
            visibility=visibility,
            data_quality_score=data_quality_score,
        )