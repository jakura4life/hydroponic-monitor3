from django.core.management.base import BaseCommand
from data.processing import process_unprocessed_readings

class Command(BaseCommand):
    help = "Normalize raw sensor readings"

    def handle(self, *args, **kwargs):
        updated = process_unprocessed_readings()
        self.stdout.write(
            self.style.SUCCESS(
                f"Processed {updated} readings"
            )
        )