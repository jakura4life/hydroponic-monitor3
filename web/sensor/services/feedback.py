from sensor.models import SensorReading
from django.conf import settings

# def evaluate_feedback(reading):
#     feedback = {}

#     ph = reading.get("ph")
#     tds = reading.get("tds")
#     temp = reading.get("airTemp")
#     humidity = reading.get("humidity")

#     # pH rules (hydroponics typical)
#     if ph is not None:
#         if 5.5 <= ph <= 6.5:
#             feedback["ph_status"] = "good"
#         elif 5.0 <= ph <= 7.0:
#             feedback["ph_status"] = "ok"
#         else:
#             feedback["ph_status"] = "bad"

#     # TDS rules
#     if tds is not None:
#         if 500 <= tds <= 900:
#             feedback["tds_status"] = "good"
#         elif 300 <= tds <= 1200:
#             feedback["tds_status"] = "ok"
#         else:
#             feedback["tds_status"] = "bad"

#     # Temperature rules
#     if temp is not None:
#         if 18 <= temp <= 24:
#             feedback["temp_status"] = "good"
#         elif 15 <= temp <= 30:
#             feedback["temp_status"] = "ok"
#         else:
#             feedback["temp_status"] = "bad"

#     # Humidity rules
#     if humidity is not None:
#         if 50 <= humidity <= 70:
#             feedback["humidity_status"] = "good"
#         elif 40 <= humidity <= 80:
#             feedback["humidity_status"] = "ok"
#         else:
#             feedback["humidity_status"] = "bad"

#     return feedback

def evaluate_feedback(reading):
    feedback = {}
    ranges = settings.EVAL_RANGES

    feedback["ph_status"] = evaluate_status(
        reading.get("ph"),
        ranges["ph"]
    )

    feedback["tds_status"] = evaluate_status(
        reading.get("tds"),
        ranges["tds"]
    )

    feedback["temp_status"] = evaluate_status(
        reading.get("airTemp"),
        ranges["temp"]
    )

    feedback["humidity_status"] = evaluate_status(
        reading.get("humidity"),
        ranges["humidity"]
    )

    return feedback

def evaluate_status(value, ranges):
    if value is None:
        return "unknown"

    good_min, good_max = ranges["good"]
    ok_min, ok_max = ranges["ok"]

    if good_min <= value <= good_max:
        return "good"
    elif ok_min <= value <= ok_max:
        return "ok"
    else:
        return "bad"