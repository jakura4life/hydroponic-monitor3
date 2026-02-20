from sensor.repository.firebase_service import listen_to_current
from sensor.services.feedback import evaluate_feedback
import time

LATEST_READING = {}

def handle_current_update(reading):
    global LATEST_READING

    readings_dict = vars(reading)

    feedback = evaluate_feedback(readings_dict)
    LATEST_READING = {
        **readings_dict,
        **feedback
    }

    # print("[REALTIME]", LATEST_READING)
    print("[REALTIME] new reading avilable")


def start_current_listener():
    return listen_to_current(handle_current_update)

def get_latest_reading():
    return LATEST_READING