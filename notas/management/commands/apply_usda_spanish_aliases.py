from django.core.management.base import BaseCommand

from notas.application.services.food_imports.usda.spanish_aliases import (
    apply_usda_spanish_aliases_to_visible_global_foods,
)


class Command(BaseCommand):
    help = "Apply known Spanish aliases to visible USDA/global foods."

    def handle(self, *args, **options):
        result = apply_usda_spanish_aliases_to_visible_global_foods()

        self.stdout.write(
            self.style.SUCCESS(
                "USDA Spanish aliases applied: "
                f"matched_foods={result.matched_foods}, "
                f"created_aliases={result.created_aliases}, "
                f"skipped_aliases={result.skipped_aliases}"
            )
        )