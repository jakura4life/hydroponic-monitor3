from sensor.processing.normalization import normalize_ph
from sensor.processing.EMASmoother import EMASmoother
from sensor.models import HourlyAggregate
from collections import defaultdict
from statistics import mean
from django.conf import settings

USE_EMA = settings.USE_EMA

# should only process not fetch
def process_hourly(readings):
    normalize_list = []
    ema = EMASmoother()

    for reading in readings:
        if USE_EMA:
            smooth_reading = normalize_ph(reading, ema)
        normalize_list.append(smooth_reading)

    hourly_data = calculate_hourly_average(normalize_list)

    return hourly_data

# helper function
def calculate_hourly_average(normalize_list: list):

    buckets = defaultdict(list)

    # Group readings into hourly buckets
    for reading in normalize_list:
        try:
            # bucket key as epoch int for the start of the hour
            hour_epoch = reading.epoch - (reading.epoch % 3600)
            buckets[hour_epoch].append(reading)
        except Exception as e:
            print(f"[HOURLY] Skipping reading: {e}")
            continue

    hourly_results = []

    # Compute averages
    try:
        for hour_epoch, readings in buckets.items():
            ph_values = [r.ph for r in readings if r.ph is not None]
            tds_values = [r.tds for r in readings if r.tds is not None]
            temp_values = [r.temperature for r in readings if r.temperature is not None]
            humidity_values = [r.humidity for r in readings if r.humidity is not None]

            hourly_results.append(
                HourlyAggregate.from_epoch(
                    hour=hour_epoch,
                    avg_ph=round(mean(ph_values),2) if ph_values else None,
                    avg_tds=round(mean(tds_values),0) if tds_values else None,
                    avg_temp=round(mean(temp_values),1) if temp_values else None,
                    avg_humidity=round(mean(humidity_values),0) if humidity_values else None,
                )
            )
    except Exception as e:
        print(f"[HOURLY] Error in computing averages: {e}")

    # Sort by hour ascending
    return sorted(hourly_results, key=lambda x: x.hour)