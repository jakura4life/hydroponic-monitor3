from django.core.management.base import BaseCommand
from data.ingestion import ingest_history_reading

class Command(BaseCommand):
    help = "Fetch sensor data from Firebase and store raw readings"

    def handle(self, *args, **kwargs):
        created, skipped = ingest_history_reading()
        self.stdout.write(
            self.style.SUCCESS(
                f"Ingest complete: {created} created, {skipped} skipped"
            )
        )