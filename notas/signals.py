from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from notas.models import Profile, Plan, MealFood
from notas.services.meal_nutrition import compute_meal_nutrition
from notas.services.foods_aggregation import build_meal_foods_projection



@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if not created:
        return

    # Plan default: primer plan Member
    default_plan = Plan.objects.filter(role="member").first()

    Profile.objects.create(
        user=instance,
        role="member",
        plan=default_plan,
        is_verified=False,
    )


@receiver(post_save, sender=MealFood)
@receiver(post_delete, sender=MealFood)
def recompute_meal_cache(sender, instance, **kwargs):
    meal = instance.meal

    data = compute_meal_nutrition(meal)

    meal.protein_cached = data["protein"]
    meal.carbs_cached = data["carbs"]
    meal.fat_cached = data["fat"]

    meal.kcal_protein_cached = data["kcal_protein"]
    meal.kcal_carbs_cached = data["kcal_carbs"]
    meal.kcal_fat_cached = data["kcal_fat"]
    meal.total_kcal_cached = data["total_kcal"]

    meal.alloc_protein_cached = data["alloc"]["protein"]
    meal.alloc_carbs_cached = data["alloc"]["carbs"]
    meal.alloc_fat_cached = data["alloc"]["fat"]

    meal.foods_aggregation_cached = build_meal_foods_projection(meal)

    meal.save(update_fields=[
        "protein_cached", "carbs_cached", "fat_cached",
        "kcal_protein_cached", "kcal_carbs_cached", "kcal_fat_cached",
        "total_kcal_cached",
        "alloc_protein_cached", "alloc_carbs_cached", "alloc_fat_cached",
    ])

