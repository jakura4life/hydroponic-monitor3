import os
import redis
import json
import time
from sensor.models import HourlyAggregate


# ----- Set Up -------
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

r = redis.Redis(
    host=REDIS_HOST,
    port=int(REDIS_PORT),
    db=0,
    decode_responses=True
)

for i in range(10):
    try:
        r.ping()
        print("Connected to Redis")
        break
    except redis.ConnectionError:
        print("Waiting for Redis...")
        time.sleep(2)

def _hourly_cache_key(range_label: str):
    return f"sensor:hourly:{range_label}"

def seconds_until_next_hour():
    now = int(time.time())
    return 3600 - (now % 3600)

#---- hourly ------
VALID_RANGES = {"all", "7d", "3d", "1d", "12h"}

def cache_hourly(hourly: list[HourlyAggregate], range_label: str):
    if range_label not in VALID_RANGES:
        raise ValueError(f"Invalid range: {range_label}")

    payload = [h.model_dump(mode="json") for h in hourly]

    key = _hourly_cache_key(range_label)
    expiry = seconds_until_next_hour()

    r.set(key, json.dumps(payload), ex=expiry)

    print(f"[CACHE] Hourly data cached ({range_label})")

def get_cached_hourly(range_label: str) -> list[HourlyAggregate] | None:
    if range_label not in VALID_RANGES:
        raise ValueError(f"Invalid range: {range_label}")

    key = _hourly_cache_key(range_label)

    data = r.get(key)
    if not data:
        return None

    raw_list = json.loads(data)
    return [HourlyAggregate.from_epoch(**item) for item in raw_list]