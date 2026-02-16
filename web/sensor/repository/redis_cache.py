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



#---- hourly ------
def cache_hourly(hourly: list[HourlyAggregate]):
    payload = [h.model_dump(mode="json") for h in hourly]

    r.set("sensor:hourly", json.dumps(payload), ex=3600)

    print("[CACHE] Hourly data cached")

def get_cached_hourly() -> list[HourlyAggregate] | None:
    data = r.get("sensor:hourly")
    # print("[CACHE RAW]", data)

    if not data:
        return None

    raw_list = json.loads(data) 

    return [HourlyAggregate(**item) for item in raw_list]