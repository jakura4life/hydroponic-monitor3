from collections import defaultdict
from .process import normalize_ph

def calculate_hourly_average(history_data):
    hourly_data = defaultdict(list)

    for epoch_str, values in history_data.items():
        try:
            epoch = int(epoch_str)
            hour_bucket = epoch - (epoch % 3600)

            ph = normalize_ph(float(values["pH"]))

            if ph is None:
                continue

            hourly_data[hour_bucket].append(ph)

        except (KeyError, ValueError, TypeError):
            continue

    # Compute average
    hourly_avg = {}

    for hour, ph_values in hourly_data.items():
        if ph_values:
            avg_ph = sum(ph_values) / len(ph_values)
            hourly_avg[hour] = round(avg_ph, 3)

    return hourly_avg