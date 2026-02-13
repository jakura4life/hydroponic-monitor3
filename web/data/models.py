from django.http import JsonResponse
from .services.firebase.firebase_service import fetch_history_from_firebase
from .services.redis.redis_cache import get_cached_hourly_ph, cache_hourly_ph
from .data_process.hourly import calculate_hourly_average

def hourly_ph_model():

    cached = get_cached_hourly_ph()
    if cached:
        return cached

    history = fetch_history_from_firebase()
    hourly_avg = calculate_hourly_average(history)

    cache_hourly_ph(hourly_avg)

    return cached