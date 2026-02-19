import firebase_admin
from firebase_admin import credentials, db
import os
import json
from sensor.models import SensorReading

firebase_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

if not firebase_admin._apps:
    cred_dict = json.loads(firebase_json)
    cred = credentials.Certificate(cred_dict)

    firebase_admin.initialize_app(cred, {
        "databaseURL": os.getenv("FIREBASE_DB_URL")
    })

# hourly data
def fetch_history_from_firebase(start_epoch=None):
    ref = db.reference("sensorData/history")

    if start_epoch:
        raw = ref.order_by_key().start_at(str(start_epoch)).get()
    else:
        raw = ref.get()

    if not raw:
        return []
    
    readings = []

    for epoch, payload in raw.items():
        readings.append(SensorReading.from_history(epoch,payload))
    
    return readings


# Listeners
def listen_to_current(callback):

    def wrapper(event):
        if event.data:
            reading = SensorReading.from_current(event.data)
            callback(reading)

    ref = db.reference("sensorData/current")
    return ref.listen(wrapper)
