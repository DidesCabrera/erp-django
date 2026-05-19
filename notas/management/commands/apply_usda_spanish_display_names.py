from django.core.management.base import BaseCommand

from notas.application.services.food_imports.usda.spanish_display_names import (
    apply_usda_spanish_display_names_to_visible_global_foods,
)


class Command(BaseCommand):
    help = "Apply generated Spanish display names to visible USDA/global foods."

    def handle(self, *args, **options):
        result = apply_usda_spanish_display_names_to_visible_global_foods()

        self.stdout.write(
            self.style.SUCCESS(
                "USDA Spanish display names applied: "
                f"matched_foods={result.matched_foods}, "
                f"created_localized_names={result.created_localized_names}, "
                f"updated_localized_names={result.updated_localized_names}, "
                f"skipped_localized_names={result.skipped_localized_names}"
            )
        )
        