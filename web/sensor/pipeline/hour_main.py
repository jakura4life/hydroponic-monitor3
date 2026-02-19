from sensor.processing.normalization import normalize_ph, is_valid
from sensor.processing.EMASmoother import EMASmoother
from sensor.infographs.hourly import calculate_hourly_average


# should only process not fetch
def process_hourly(readings):
    ema = EMASmoother()
    normalize_list = []

    for reading in readings:
        if is_valid(reading):
            reading = normalize_ph(reading, ema)
            normalize_list.append(reading)

    hourly_data = calculate_hourly_average(normalize_list)

    return hourly_data
