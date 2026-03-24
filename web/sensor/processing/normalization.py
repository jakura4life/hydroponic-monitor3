from sensor.processing.EMASmoother import EMASmoother
from sensor.models import SensorReading


def normalize_ph(reading: SensorReading, ema : EMASmoother):
    if reading.ph:
        new_reading = reading.model_copy()
        new_reading.ph = ema.update(reading.ph)
        return new_reading
    return reading