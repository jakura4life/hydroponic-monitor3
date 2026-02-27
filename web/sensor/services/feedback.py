from sensor.models import SensorReading
from django.conf import settings
from sensor.services.alert_service import trigger_alert, resolve_alert
from sensor.models import Alert


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

    process_alerts(reading, feedback)    

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
    
def process_alerts(reading, feedback):
    sensor_map = {
        "ph": reading.get("ph"),
        "tds": reading.get("tds"),
        "temp": reading.get("airTemp"),
        # "humidity": reading.get("humidity"),
    }

    recommendations = {
        "ph": "Use pH adjusters to ",
        "tds": "Dilute with ",
        "temp": "djust heater,fan or ventalation.",
        # "humidity": "Increase ventilation or humidifier to reach 50–70%.",
    }

    for sensor, value in sensor_map.items():
        status = feedback.get(f"{sensor}_status")

        if status in ["bad", "ok"]:
            severity = "critical" if status == "bad" else "warning"
            message = (
                f"{sensor.upper()} is outside safe range"
                if status == "bad"
                else f"{sensor.upper()} slightly out of optimal range"
            )

            # Look for existing active alert
            existing_alert = Alert.objects.filter(sensor=sensor, is_active=True).first()

            if existing_alert:
                print('update alert')
                # Update if severity or value changed
                if existing_alert.severity != severity or existing_alert.value != value:
                    existing_alert.severity = severity
                    existing_alert.value = value
                    existing_alert.message = message
                    existing_alert.save()
            else:
                # No active alert, create one
                print('create alaer')
                Alert.objects.create(
                    sensor=sensor,
                    severity=severity,
                    value=value,
                    message=message,
                    is_active=True
                )

        elif status == "good":
            # Automatically resolve existing alert if sensor is back to good
            Alert.objects.filter(sensor=sensor, is_active=True).update(is_active=False)