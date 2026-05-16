from django.core.management.base import BaseCommand

from notas.application.services.food_imports.core_food_seed_service import (
    apply_core_food_seed_to_existing_global_foods,
)


class Command(BaseCommand):
    help = "Apply the initial core food seed catalog to existing global foods."

    def handle(self, *args, **options):
        result = apply_core_food_seed_to_existing_global_foods()

        self.stdout.write(
            self.style.SUCCESS(
                "Core food seed applied: "
                f"matched_foods={result.matched_foods}, "
                f"promoted_foods={result.promoted_foods}, "
                f"created_aliases={result.created_aliases}, "
                f"skipped_aliases={result.skipped_aliases}, "
                f"created_localized_names={result.created_localized_names}, "
                f"updated_localized_names={result.updated_localized_names}, "
                f"skipped_localized_names={result.skipped_localized_names}"
            )
        )