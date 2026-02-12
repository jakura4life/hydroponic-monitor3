import firebase_admin
from firebase_admin import credentials, db
import os
# from data.normalization import normalize_latest_readings, normalize_history_readings

if not firebase_admin._apps:
    cred = credentials.Certificate(
        os.path.join(os.path.dirname(__file__), "../../serviceAccount.json")
    )

    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://hydroponic-7fd3b-default-rtdb.europe-west1.firebasedatabase.app/"
    })


def get_latest_reading():
    ref = db.reference("sensorData/current")
    return ref.get()

def get_history_reading():
    ref = db.reference("sensorData/history")
    return ref.get()

def listen_to_current(callback):
    ref = db.reference("sensorData/current")
    return ref.listen(callback)

def listen_to_history(callback):
    """
    Opens a persistent Firebase socket.
    callback(message) will be called on every change.
    """
    ref = db.reference("sensorData/history")
    return ref.listen(callback)


def current_stream_handler(message):
    """
    Handles updates to sensorData/current
    """
    event = message.event_type
    data = message.data

    if event != "put" or data is None:
        return

    try:
        epoch = int(data["epoch"])
    except (KeyError, TypeError):
        return

    print(f"[CURRENT] epoch={epoch} data={data}")


def history_stream_handler(message):
    """
    Handles new historical sensor readings
    """
    event = message.event_type
    path = message.path
    data = message.data

    if event != "put" or data is None:
        return

    # Ignore initial full dump
    if path == "/":
        return

    try:
        epoch = int(path.lstrip("/"))
    except ValueError:
        return

    print(f"[HISTORY] epoch={epoch} data={data}")

