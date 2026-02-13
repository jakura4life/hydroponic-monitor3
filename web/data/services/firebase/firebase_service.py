import firebase_admin
from firebase_admin import credentials, db
import os

if not firebase_admin._apps:
    cred = credentials.Certificate(
        os.path.join(os.path.dirname(__file__), "serviceAccount.json")
    )

    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://hydroponic-7fd3b-default-rtdb.europe-west1.firebasedatabase.app/"
    })

# Endpoints
def get_latest_reading():
    ref = db.reference("sensorData/current")
    return ref.get()

def get_arduino_history_reading():
    ref = db.reference("sensorData/history")
    return ref.get()


# hourly data
def fetch_history_from_firebase(start_epoch=None):
    ref = db.reference("sensorData/history")

    if start_epoch:
        return ref.order_by_key().start_at(str(start_epoch)).get()
    
    return ref.get()


# Listeners
def listen_to_current(callback):
    ref = db.reference("sensorData/current")
    return ref.listen(callback)


# Storing under new directory on DB
def store_clean_history(epoch, payload):
    ref = db.reference("history_clean")
    ref.child(str(epoch)).set(payload)
    print("[FIREBASE WRITE] Storing clean values.")

## comparison
def compare_last_stored(current_epoch):
    last_epoch = get_latest_clean_history_epoch_from_firebase()
    if last_epoch is None:
        return True # raise flag regardgless as no history can be found.
    delta = current_epoch - last_epoch
    if delta // 60 > 10:
        return True
    return False

### fetch latest epoch
def get_latest_clean_history_epoch_from_firebase():
    ref = db.reference("history_clean")
    data = ref.order_by_key().limit_to_last(1).get()

    if data:
        return int(list(data.keys())[0])
    return None