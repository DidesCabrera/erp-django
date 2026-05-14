import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from notas.application.services.commands.import_usda_food_payloads import (
    import_usda_food_payloads,
)


class Command(BaseCommand):
    help = "Import USDA FoodData Central-like foods from a controlled JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            type=str,
            help="Path to a JSON file containing a list of USDA-like food payloads.",
        )

        parser.add_argument(
            "--source-version",
            required=True,
            help="Source dataset version. Example: 2026-04.",
        )

        parser.add_argument(
            "--source-dataset",
            default="foundation_foods",
            help="Source dataset name. Example: foundation_foods.",
        )

        parser.add_argument(
            "--notes",
            default="",
            help="Optional notes stored in FoodImportBatch.",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        source_version = options["source_version"]
        source_dataset = options["source_dataset"]
        notes = options["notes"]

        if not path.exists():
            raise CommandError(f"File does not exist: {path}")

        if not path.is_file():
            raise CommandError(f"Path is not a file: {path}")

        try:
            with path.open("r", encoding="utf-8") as file:
                payloads = json.load(file)
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON file: {exc}") from exc

        if not isinstance(payloads, list):
            raise CommandError("JSON root must be a list of USDA-like food payloads.")

        result = import_usda_food_payloads(
            payloads=payloads,
            source_version=source_version,
            source_dataset=source_dataset,
            notes=notes,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "USDA import completed: "
                f"batch_id={result.batch.id}, "
                f"total={result.total_rows}, "
                f"imported={result.imported_rows}, "
                f"skipped={result.skipped_rows}, "
                f"failed={result.failed_rows}, "
                f"status={result.batch.status}"
            )
        )