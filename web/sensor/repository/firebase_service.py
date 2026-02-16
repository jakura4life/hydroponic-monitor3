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



# # Storing under new directory on DB
# def store_clean_history(epoch, payload):
#     ref = db.reference("history_clean")
#     ref.child(str(epoch)).set(payload)
#     print("[FIREBASE WRITE] Storing clean values.")

# ## comparison
# def compare_last_stored(current_epoch):
#     last_epoch = get_latest_clean_history_epoch_from_firebase()
#     if last_epoch is None:
#         return True # raise flag regardgless as no history can be found.
#     delta = current_epoch - last_epoch
#     if delta // 60 > 10:
#         return True
#     return False

# ### fetch latest epoch
# def get_latest_clean_history_epoch_from_firebase():
#     ref = db.reference("history_clean")
#     data = ref.order_by_key().limit_to_last(1).get()

#     if data:
#         return int(list(data.keys())[0])
#     return None