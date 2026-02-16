from sensor.processing.EMASmoother import EMASmoother
from sensor.models import SensorReading

def is_valid(reading : SensorReading):
    return (
        0 <= reading.ph <= 14
        and reading.tds >= 0
        and reading.humidity <= 100
    )

def normalize_ph(reading: SensorReading, ema : EMASmoother):
    reading.ph = ema.update(reading.ph)
    return reading