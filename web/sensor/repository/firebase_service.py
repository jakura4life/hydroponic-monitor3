import firebase_admin
from firebase_admin import credentials, db
import os
import json
from sensor.models import SensorReading
from pydantic import ValidationError

firebase_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

# if not firebase_admin._apps:
#     cred_dict = json.loads(firebase_json)
#     cred = credentials.Certificate(cred_dict)

#     firebase_admin.initialize_app(cred, {
#         "databaseURL": os.getenv("FIREBASE_DB_URL")
#     })

def get_firebase_app():
    if not firebase_admin._apps:
        firebase_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        db_url = os.getenv("FIREBASE_DB_URL")

        if not firebase_json or not db_url:
            raise RuntimeError("Firebase environment variables not configured")

        cred_dict = json.loads(firebase_json)
        cred = credentials.Certificate(cred_dict)

        firebase_admin.initialize_app(cred, {
            "databaseURL": db_url
        })

    return firebase_admin.get_app()

# hourly data
def fetch_history_from_firebase(start_epoch=None):
    get_firebase_app()

    ref = db.reference("sensorData/history")

    if start_epoch:
        raw = ref.order_by_key().start_at(str(start_epoch)).get()
    else:
        raw = ref.get()

    if not raw:
        return []
    
    readings = []

    for epoch, payload in raw.items():
        reading = safe_sensor_reading(SensorReading.from_history, epoch, payload)
        if reading:
            readings.append(reading)
        # try:
        #     readings.append(SensorReading.from_history(epoch,payload))
        # except Exception:
        #     continue
    
    return readings


# Listeners
def listen_to_current(callback):
    get_firebase_app()

    def wrapper(event):
        if event.data:
            # reading = SensorReading.from_current(event.data)
            reading = safe_sensor_reading(SensorReading.from_current, event.data)
            if reading:
                callback(reading)

    ref = db.reference("sensorData/current")
    return ref.listen(wrapper)



FIELD_MAP = {
    "tds": "TDS",
    "ph": "pH",
    "humidity": "humidity",
    "temperature": "temperature",
}


def safe_sensor_reading(factory_func, *args, **kwargs):
    try:
        return factory_func(*args, **kwargs)

    except ValidationError as e:
        # Extract original data (depends on your factory design)
        data = kwargs.get("payload") or args[-1]

        cleaned_data = data.copy()

        for error in e.errors():
            field = error["loc"][0]

            # map model field → payload key
            payload_key = FIELD_MAP.get(field, field)

            if payload_key in cleaned_data:
                cleaned_data[payload_key] = None

        try:
            return factory_func(*args[:-1], cleaned_data)
        except ValidationError:
            return None
    

# bad_data_cases = [
#     {"temperature": 12, "pH": 7, "TDS": -10, "humidity": 50, "epoch": 120, "datetime": "2026-03-23T20:23:39Z"},     # invalid TDS
#     {"temperature": 12, "pH": 15, "TDS": 300, "humidity": 50, "epoch": 120, "datetime": "2026-03-23T20:23:39Z"},    # invalid pH
#     {"temperature": 12, "pH": 6.5, "TDS": 300, "humidity": 150, "epoch": 120, "datetime": "2026-03-23T20:23:39Z"},  # invalid humidity
# ]

# for case in bad_data_cases:
#     reading = safe_sensor_reading(SensorReading.from_current, case)
#     print(reading)
    