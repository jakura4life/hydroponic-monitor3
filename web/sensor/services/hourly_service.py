from sensor.repository.redis_cache import get_cached_hourly, cache_hourly
from sensor.pipeline.hour_main import process_hourly


def get_hourly_data(ignore_cache = False):
    if not ignore_cache:
        cached = get_cached_hourly()
    else:
        cached = None
    
    if cached:
        print("[CACHED HIT] hourly data returned")
        return cached
    
    print("[CACHE MISS] processing data")
    data = process_hourly()

    cache_hourly(data)
    
    return data