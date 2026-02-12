from django.core.management.base import BaseCommand
from services.firebase_service import (
    listen_to_current,
    listen_to_history,
)
from services.firebase_service import (
    current_stream_handler,
    history_stream_handler,
)


class Command(BaseCommand):
    help = "Listen to Firebase realtime updates (current + history)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Listening to Firebase streams..."))

        listen_to_current(current_stream_handler)
        listen_to_history(history_stream_handler)

        # Keep process alive
        import time
        while True:
            time.sleep(60)