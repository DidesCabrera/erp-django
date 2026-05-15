from django.core.management.base import BaseCommand

from notas.application.services.food_imports.core_catalog_curation import (
    promote_initial_core_foods,
)


class Command(BaseCommand):
    help = "Promote known global foods to the initial core catalog."

    def handle(self, *args, **options):
        result = promote_initial_core_foods()

        self.stdout.write(
            self.style.SUCCESS(
                "Initial core foods promoted: "
                f"matched_foods={result.matched_foods}, "
                f"promoted_foods={result.promoted_foods}"
            )
        )