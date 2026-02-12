from django.core.management import BaseCommand
from data.processing import reset_clean_sensor_values

class Command(BaseCommand):
    help = "Removes all process column data"

    def handle(self, *args, **options):
        updated = reset_clean_sensor_values()
        self.stdout.write(
            self.style.SUCCESS(
                f"Removed {updated} readings"
            )
        )