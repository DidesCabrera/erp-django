from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from notas.management.commands.dry_run_usda_food_payloads import (
    dry_run_usda_food_payloads,
)
from notas.application.services.food_imports.usda.foundation_foods_reader import (
    FoundationFoodsReaderError,
    read_foundation_food_payloads_from_json,
)


class Command(BaseCommand):
    help = "Dry-run USDA Foundation Foods JSON import without writing to the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            type=str,
            help=(
                "Path to a JSON file containing USDA Foundation Foods payloads. "
                "Supports either a direct list or a FoundationFoods root object."
            ),
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

    def handle(self, *args, **options):
        path = Path(options["path"])
        source_version = options["source_version"]
        source_dataset = options["source_dataset"]

        if not path.exists():
            raise CommandError(f"File does not exist: {path}")

        if not path.is_file():
            raise CommandError(f"Path is not a file: {path}")

        try:
            payloads = read_foundation_food_payloads_from_json(path)
        except FoundationFoodsReaderError as exc:
            raise CommandError(str(exc)) from exc

        result = dry_run_usda_food_payloads(
            payloads=payloads,
            source_version=source_version,
            source_dataset=source_dataset,
        )

        self.stdout.write(
            self.style.SUCCESS("USDA dry-run completed.")
        )

        self.stdout.write(f"total={result.total_rows}")
        self.stdout.write(f"valid={result.valid_rows}")
        self.stdout.write(f"invalid={result.invalid_rows}")
        self.stdout.write(f"duplicates={result.duplicate_rows}")
        self.stdout.write(f"failed={result.failed_rows}")
        self.stdout.write(f"would_import={result.would_import_rows}")
        self.stdout.write(f"would_skip={result.skipped_rows}")
        self.stdout.write(f"visibility_extended={result.extended_rows}")
        self.stdout.write(f"visibility_hidden={result.hidden_rows}")

        if result.reason_counts:
            self.stdout.write("reasons:")

            for reason, count in sorted(result.reason_counts.items()):
                self.stdout.write(f"- {reason}: {count}")