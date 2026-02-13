from django.core.management.base import BaseCommand
from services.firebase.firebase_service import listen_to_current
from services.firebase.handler import current_stream_handler


class Command(BaseCommand):
    help = "Listen to Firebase current updates"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Listening to Firebase..."))
        listen_to_current(current_stream_handler)