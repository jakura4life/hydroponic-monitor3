from sensor.repository.firebase_service import listen_to_current
from sensor.models import SensorReading, SystemStatus
from sensor.pipeline.feedback import evaluate_feedback
import time

LATEST_READING = {}
STREAM = None
# RUN_ONCE = False

def handle_current_update(reading: SensorReading):
    global LATEST_READING, RUN_ONCE
    # if RUN_ONCE:
    #     return

    # Convert Pydantic model to dict
    readings_dict = reading.model_dump()  # safer than vars() in v2

    # print(readings_dict)
    SystemStatus.objects.update_or_create(
        id=1,
        defaults={"last_epoch": readings_dict["epoch"]}
    )

    # Evaluate feedback
    feedback = evaluate_feedback(readings_dict)
    # print (readings_dict)

    # Merge reading and feedback
    LATEST_READING = {
        **readings_dict,
        **feedback
    }

    print("[REALTIME] new reading available")


def start_current_listener():
    # pass
    STREAM = listen_to_current(handle_current_update)
    return STREAM

def get_latest_reading():
    return LATEST_READING

def test_system_health():
    from sensor.repository.firebase_service import safe_sensor_reading
    from sensor.models import SensorReading
    case = {"temperature": 12, "pH": 7, "TDS": -10, "humidity": 50, "epoch": 1769880335, "datetime": "2026-01-31T17:25:35Z"}

    reading = safe_sensor_reading(SensorReading.from_current,case)

    handle_current_update(reading)

# test_system_health()