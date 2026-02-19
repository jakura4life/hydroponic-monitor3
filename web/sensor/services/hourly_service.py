from sensor.repository.redis_cache import get_cached_hourly, cache_hourly
from sensor.pipeline.hour_main import process_hourly
import time
from sensor.repository.firebase_service import fetch_history_from_firebase

def get_hourly_data(range_label="1d", ignore_cache=False):
    if not ignore_cache:
        cached = get_cached_hourly(range_label)
        if cached:
            print("[CACHE] Returning cache")
            return cached

    start_epoch = range_to_start_epoch(range_label)

    readings = fetch_history_from_firebase(start_epoch)

    if not readings:
        return []

    data = process_hourly(readings)

    cache_hourly(data, range_label)
    print("[CACHE] Caching data")


    return data

def range_to_start_epoch(range_label):
    now = int(time.time())
    # print(range_label)
    if range_label == "12h":
        return now - 12 * 3600
    elif range_label == "1d":
        return now - 24 * 3600
    elif range_label == "3d":
        return now - 3 * 24 * 3600
    elif range_label == "7d":
        return now - 7 * 24 * 3600
    elif range_label == "all":
        return 0  # or earliest timestamp
    else:
        raise ValueError("Invalid range")