from django.contrib.auth import get_user_model
from django.test import TestCase

from notas.application.queries.food_picker_queries import get_food_picker_queryset
from notas.domain.models import Food


User = get_user_model()


class FoodPickerQueryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="felipe",
            email="felipe@test.com",
            password="12345678",
        )

        self.other_user = User.objects.create_user(
            username="other",
            email="other@test.com",
            password="12345678",
        )

        self.user_food = Food.objects.create(
            name="User Egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
            is_global=False,
            is_active=True,
            visibility=Food.VISIBILITY_EXTENDED,
        )

        self.other_user_food = Food.objects.create(
            name="Other User Food",
            protein=1,
            carbs=1,
            fat=1,
            created_by=self.other_user,
            is_global=False,
            is_active=True,
            visibility=Food.VISIBILITY_EXTENDED,
        )

        self.core_global_food = Food.objects.create(
            name="Global Oats Core",
            protein=16.9,
            carbs=66.3,
            fat=6.9,
            created_by=None,
            is_global=True,
            is_verified=True,
            is_active=True,
            visibility=Food.VISIBILITY_CORE,
        )

        self.extended_global_food = Food.objects.create(
            name="Global Chicken Extended",
            protein=31,
            carbs=0,
            fat=3.6,
            created_by=None,
            is_global=True,
            is_verified=False,
            is_active=True,
            visibility=Food.VISIBILITY_EXTENDED,
        )

        self.hidden_global_food = Food.objects.create(
            name="Hidden Banana",
            protein=1,
            carbs=23,
            fat=0.3,
            created_by=None,
            is_global=True,
            is_active=True,
            visibility=Food.VISIBILITY_HIDDEN,
        )

        self.rejected_global_food = Food.objects.create(
            name="Rejected Food",
            protein=1,
            carbs=1,
            fat=1,
            created_by=None,
            is_global=True,
            is_active=True,
            visibility=Food.VISIBILITY_REJECTED,
        )

        self.inactive_global_food = Food.objects.create(
            name="Inactive Global Food",
            protein=1,
            carbs=1,
            fat=1,
            created_by=None,
            is_global=True,
            is_active=False,
            visibility=Food.VISIBILITY_CORE,
        )

    def test_food_picker_queryset_includes_user_and_visible_global_foods(self):
        foods = list(get_food_picker_queryset(self.user))

        self.assertIn(self.user_food, foods)
        self.assertIn(self.core_global_food, foods)
        self.assertIn(self.extended_global_food, foods)

    def test_food_picker_queryset_excludes_private_foods_from_other_users(self):
        foods = list(get_food_picker_queryset(self.user))

        self.assertNotIn(self.other_user_food, foods)

    def test_food_picker_queryset_excludes_hidden_rejected_and_inactive_global_foods(self):
        foods = list(get_food_picker_queryset(self.user))

        self.assertNotIn(self.hidden_global_food, foods)
        self.assertNotIn(self.rejected_global_food, foods)
        self.assertNotIn(self.inactive_global_food, foods)

    def test_food_picker_queryset_orders_user_foods_before_global_foods(self):
        foods = list(get_food_picker_queryset(self.user))

        self.assertEqual(foods[0], self.user_food)

    def test_food_picker_queryset_orders_core_global_before_extended_global(self):
        foods = list(get_food_picker_queryset(self.user))

        core_index = foods.index(self.core_global_food)
        extended_index = foods.index(self.extended_global_food)

        self.assertLess(core_index, extended_index)