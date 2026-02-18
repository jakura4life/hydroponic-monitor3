from sensor.processing.normalization import normalize_ph, is_valid
from sensor.processing.EMASmoother import EMASmoother
from sensor.models import SensorReading
from sensor.infographs.hourly import calculate_hourly_average
from sensor.repository.redis_cache import cache_hourly
from sensor.repository.firebase_service import fetch_history_from_firebase

def process_hourly(startepoch=None):
    ema = EMASmoother()

    readings = fetch_history_from_firebase(startepoch)
    normalize_list = []

    for reading in readings:
        if is_valid(reading):
            reading = normalize_ph(reading, ema)
            normalize_list.append(reading)

    hourly_data = calculate_hourly_average(normalize_list)

    return hourly_data
