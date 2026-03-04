from django.apps import AppConfig
import os
import time
import threading

class SensorConfig(AppConfig):
    name = "sensor"

    def ready(self):
        # Prevent double listener in dev server
        if os.environ.get("RUN_MAIN") != "true":
            return
        
        def start_background_services():
            time.sleep(1)

            from sensor.services.listen_service import start_current_listener
            from sensor.services.health_service import system_health_monitor
            print("[BACKGROUND PROCESS] Started once")

            start_current_listener()
            system_health_monitor()

        threading.Thread(target=start_background_services, daemon=True).start()
