from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notas", "0018_dailyplan_source"),
    ]

    operations = [
        migrations.AddField(
            model_name="food",
            name="is_global",
            field=models.BooleanField(
                default=False,
                help_text="If true, this food is available to every user as part of the global catalog.",
            ),
        ),
    ]