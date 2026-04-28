from django.db import migrations


def backfill_dailyplanmeal_order(apps, schema_editor):
    DailyPlan = apps.get_model("notas", "DailyPlan")
    DailyPlanMeal = apps.get_model("notas", "DailyPlanMeal")

    for dailyplan in DailyPlan.objects.all():
        dpms = (
            DailyPlanMeal.objects
            .filter(dailyplan=dailyplan)
            .order_by("hour", "order", "id")
        )

        for index, dpm in enumerate(dpms, start=1):
            dpm.order = index
            dpm.save(update_fields=["order"])


class Migration(migrations.Migration):

    dependencies = [
        ("notas", "0011_meal_foods_aggregation_cached"),
    ]

    operations = [
        migrations.RunPython(backfill_dailyplanmeal_order, migrations.RunPython.noop),
        migrations.AlterModelOptions(
            name="dailyplanmeal",
            options={"ordering": ["order", "id"]},
        ),
    ]