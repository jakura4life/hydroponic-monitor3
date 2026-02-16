from sensor.repository.firebase_service import listen_to_current
import time

def handle_current_update(reading):
    global LATEST_READING
    LATEST_READING = reading
    print("[REALTIME]", reading)

def start_current_listener():
    return listen_to_current(handle_current_update)

def get_latest_reading():
    return LATEST_READING