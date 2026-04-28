from django.db import migrations, models


def backfill_mealfood_order(apps, schema_editor):
    Meal = apps.get_model("notas", "Meal")
    MealFood = apps.get_model("notas", "MealFood")

    for meal in Meal.objects.all():
        meal_foods = (
            MealFood.objects
            .filter(meal=meal)
            .order_by("id")
        )

        for index, meal_food in enumerate(meal_foods, start=1):
            meal_food.order = index
            meal_food.save(update_fields=["order"])


class Migration(migrations.Migration):

    dependencies = [
        ("notas", "0012_backfill_dailyplanmeal_order"),
    ]

    operations = [
        migrations.AddField(
            model_name="mealfood",
            name="order",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(
            backfill_mealfood_order,
            migrations.RunPython.noop,
        ),
        migrations.AlterModelOptions(
            name="mealfood",
            options={"ordering": ["order", "id"]},
        ),
    ]