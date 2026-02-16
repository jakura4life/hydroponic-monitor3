from django.apps import AppConfig
import os

class SensorConfig(AppConfig):
    name = "sensor"

    def ready(self):
        # Prevent double listener in dev server
        if os.environ.get("RUN_MAIN") != "true":
            return

        from sensor.services.listen_service import start_current_listener
        start_current_listener()

        print("[LISTENER] Started once")