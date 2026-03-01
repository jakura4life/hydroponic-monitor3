from sensor.repository.firebase_service import listen_to_current
from sensor.models import SensorReading
from sensor.pipeline.feedback import evaluate_feedback


LATEST_READING = {}

def handle_current_update(reading: SensorReading):
    global LATEST_READING

    # Convert Pydantic model to dict
    readings_dict = reading.model_dump()  # safer than vars() in v2

    # Evaluate feedback
    feedback = evaluate_feedback(readings_dict)

    # Merge reading and feedback
    LATEST_READING = {
        **readings_dict,
        **feedback
    }

    print("[REALTIME] new reading available")

def start_current_listener():
    return listen_to_current(handle_current_update)

def get_latest_reading():
    return LATEST_READING