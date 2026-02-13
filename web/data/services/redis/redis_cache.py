
import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)



def cache_latest(epoch, data):
    r.set("sensor:latest_clean", json.dumps({
        "epoch": epoch,
        **data
    }))
    print("[CACH] Cache recent clean values using redis")

def get_data():
    data = r.get("sensor:latest_clean")
    if data:
        return data
    return None


def is_duplicate(epoch):
    last = r.get("sensor:last_epoch")
    if last is None:
        return False
    return (int(epoch) == int(last))


def set_last_epoch(epoch):
    r.set("sensor:last_epoch", epoch)


def cache_hourly_ph(data):
    r.set("sensor:hourly_ph", json.dumps(data))

def get_cached_hourly_ph():
    data = r.get("sensor:hourly_ph")
    if data:
        return json.loads(data)
    return None

def cache_hourly_ph(data):
    r.setex("sensor:hourly_ph", 300, json.dumps(data))