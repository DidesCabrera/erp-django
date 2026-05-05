# Generated manually for safe proposal application audit event.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notas", "0016_nutritionproposal_apply_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="nutritionproposalauditevent",
            name="action",
            field=models.CharField(
                choices=[
                    ("created", "Created"),
                    (
                        "submitted_for_review",
                        "Submitted for review",
                    ),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                    ("cancelled", "Cancelled"),
                    ("applied", "Applied"),
                ],
                max_length=40,
            ),
        ),
    ]