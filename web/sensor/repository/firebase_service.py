import firebase_admin
from firebase_admin import credentials, db
import os
import json
from sensor.models import SensorReading

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
        try:
            readings.append(SensorReading.from_history(epoch,payload))
        except Exception:
            continue
    
    return readings


# Listeners
def listen_to_current(callback):
    get_firebase_app()

    def wrapper(event):
        if event.data:
            reading = SensorReading.from_current(event.data)
            callback(reading)

    ref = db.reference("sensorData/current")
    return ref.listen(wrapper)
