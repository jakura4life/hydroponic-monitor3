# sensor/services/feedback.py
from sensor.models import Alert
from django.conf import settings
from sensor.services.alert_service import trigger_alert, resolve_alert, handle_alert

"""
dashboard top bar alerts are derieved from the alerts table.
"""

def evaluate_feedback(reading_dict):
    """
    Evaluate a reading and return feedback with statuses and recommendations.
    Also handles alert creation/updating.
    reading dict:
    'epoch': 1772283912, 'datetime': datetime.datetime(2026, 2, 28, 13, 5, 12, tzinfo=TzInfo(0)), 'ph': 6.38, 'tds': 73.0, 'airTemp': 18.9, 'humidity': 51.4}
    
    feedback:
    {'ph_status': 'good', 'ph_recommendation': '', 'tds_status': 'bad', 'tds_recommendation': 'Add more hydroponic solution.', 'temp_status': 'good', 'temp_recommendation': '', 'humidity_status': 'good', 'humidity_recommendation': ''}
    """
    feedback = {}
    ranges = settings.EVAL_RANGES

    # Evaluate each sensor
    for sensor in ["ph", "tds", "airTemp", "humidity"]:
        value = reading_dict.get(sensor)
        sensor_ranges = ranges[sensor]
        
        status = evaluate_status(value, sensor_ranges)
        feedback[f"{sensor}_status"] = status

        recommendation = generate_recommendation(sensor, value, status)
        feedback[f"{sensor}_recommendation"] = recommendation


    # Process alerts for sensors
    process_alerts(reading_dict, feedback)
    return feedback


def evaluate_status(value, ranges):
    """Return 'good', 'ok', or 'bad' based on sensor value and ranges."""
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


def generate_recommendation(sensor, value, status):
    """
    Generate a textual recommendation based on sensor value & status.
    """
    if status == "good" or value is None:
        return ""

    if sensor == "ph":
        if value < settings.EVAL_RANGES["ph"]["good"][0]:
            return {
                "short": "Increase pH level",
                "details": (
                    "pH level affects the plant's ability in absoring nutrients from the water.\n"
                    "If too low, plants cannot absorb essential minerals.\n\n"
                    "You can:\n"
                    "- Add pH increaser solution\n"
                    "- Use baking soda or crushed eggshells"
                )
            }
        else:
            return {
                "short": "Decrease pH level",
                "details": (
                    "pH level affects the plant's ability in absoring nutrients from the water.\n"
                    "High pH levels (7.5>) cause nutrient lockout where plants are unable to absorb any nutirents from their roots.\n\n"
                    "You can:\n"
                    "- Add pH reducer solution\n"
                    "- Use white vinegar or lemon juice"
                )
            }
    elif sensor == "tds":
        if value < settings.EVAL_RANGES["tds"]["good"][0]:
            return {
                "short": "Increase nutrient concentration",
                "details": (
                    "TDS sensor measures the concentration of solutes in the water\n"
                    "Low TDS means insufficient dissolved nutrients in the water.\n\n"
                    "Add more hydroponic nutrient solution to the water."
                )
            }
        else:
            return {
                "short": "Dilute nutrient solution",
                "details": (
                    "TDS sensor measures the concentration of solutes in the water\n"
                    "High TDS may cause nutrient burn, causing disclouration on leafs as well as brown and slimy roots\n\n"
                    "Add clean water to reduce concentration of the solution."
                )
            }
    elif sensor == "temp":
        if value < settings.EVAL_RANGES["temp"]["good"][0]:
            return {
                "short": "Increase temperature",
                "details": (
                    "Hydroponics usally works best at 18 to 25 celcius.\n"
                    "Temperature outside this range cause solution reading (particularly TDS/EC) to be inaccurate.\n\n"
                    "you can:\n"
                    "-  Turn on heaters to help warm up the environmental temperature"

                )
            }
        else:
            return {
                "short": "Decrease enviroment temperature",
                "details": (
                    "Hydroponics usally works best at 18 to 25 celcius.\n"
                    "Temperature outside this range cause solution reading (particularly TDS/EC) to be inaccurate.\n\n"
                    "you can:"
                    "-  Improve cooling via a fan"
                    "-  Improve ventalation (such as opening a window)"
                )
            }
    elif sensor == "humidity":
        if value < settings.EVAL_RANGES["humidity"]["good"][0]:
            return {
                "short": "Increase humidity",
                "details": (
                    "Humidity indicates the amount of moisture present in the air\n"
                    "High humidity can lead to the growth of mold and fungi\n\n"
                    "you can:"
                    "-  Increase humidity via reducing ventilation (closing windows) if you think the indooor humidity is higher than outside.\n"
                    "-  Turn on humidifier."
                )
            }
        else:
            return {
                "short": "Decrease humidity",
                "details": (
                    "Humidity indicates the amount of moisture present in the air\n"
                    "Low humidity cause dehydration and brown cripsy leafs.\n\n"
                    "You can:"
                    "-  Decrease humidity via improving ventilation (openning windows), letting moisture escape outdoor.\n"
                    "-  Turn on humidifier."
                )
            }
    return ""

def process_alerts(reading_dict, feedback):
    """
    dashboard top bar alerts
    """
    sensor_map = {
        "ph": reading_dict.get("ph"),
        "tds": reading_dict.get("tds"),
        "temp": reading_dict.get("airTemp"),
        "humidity": reading_dict.get("humidity"),
    }

    for sensor, value in sensor_map.items():
        status = feedback.get(f"{sensor}_status")
        if status in ["bad", "ok"]:
            message = (
                f"{sensor.upper()} is outside safe range"
                if status == "bad"
                else f"{sensor.upper()} slightly out of optimal range"
            )
            handle_alert(sensor, value, status, message)

        elif status == "good":
            resolve_alert(sensor)
