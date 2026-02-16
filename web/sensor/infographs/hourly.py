from collections import defaultdict
from datetime import datetime
from statistics import mean

from sensor.models import SensorReading, HourlyAggregate
from sensor.processing.normalization import normalize_ph, is_valid
from sensor.processing.EMASmoother import EMASmoother


def calculate_hourly_average(normalize_list: list):
    buckets = defaultdict(list)

    # Group readings into hourly buckets
    for reading in normalize_list:
        try:
            hour_key = datetime.fromtimestamp(reading.epoch).replace(
                minute=0,
                second=0,
                microsecond=0
            )

            buckets[hour_key].append(reading)

        except Exception as e:
            print(f"[HOURLY] Skipping reading: {e}")
            continue

    hourly_results = []

    # Compute averages
    for hour, readings in buckets.items():
        ph_values = [r.ph for r in readings if r.ph is not None]
        tds_values = [r.tds for r in readings if r.tds is not None]
        temp_values = [r.airTemp for r in readings if r.airTemp is not None]
        humidity_values = [r.humidity for r in readings if r.humidity is not None]

        hourly_results.append(
            HourlyAggregate(
                hour=hour,
                avg_ph=round(mean(ph_values),2) if ph_values else None,
                avg_tds=round(mean(tds_values),0) if tds_values else None,
                avg_temp=round(mean(temp_values),1) if temp_values else None,
                avg_humidity=round(mean(humidity_values),0) if humidity_values else None,
            )
        )

    return sorted(hourly_results, key=lambda x: x.hour)