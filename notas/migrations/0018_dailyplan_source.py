# Generated manually for AI/MCP DailyPlan provenance.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notas", "0017_nutritionproposalauditevent_applied_action"),
    ]

    operations = [
        migrations.AddField(
            model_name="dailyplan",
            name="source",
            field=models.CharField(
                choices=[
                    ("manual", "Manual"),
                    ("ai", "AI"),
                    ("system", "System"),
                    ("mcp", "MCP"),
                ],
                default="manual",
                max_length=20,
            ),
        ),
    ]