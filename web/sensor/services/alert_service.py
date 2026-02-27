from django.utils import timezone
from ..models import Alert


def trigger_alert(sensor, value, severity, message):
    existing = Alert.objects.filter(sensor=sensor, is_active=True).first()
    if existing:
        return

    Alert.objects.create(
        sensor=sensor,
        value=value,
        severity=severity,
        message=message,
    )


def resolve_alert(sensor):
    active_alert = Alert.objects.filter(sensor=sensor, is_active=True).first()
    if active_alert:
        active_alert.is_active = False
        active_alert.resolved_at = timezone.now()
        active_alert.save()

from sensor.models import Alert

def handle_alert(sensor, value, status, message):
    """
    Check if there's an existing active alert for this sensor.
    Update it if severity changed, or create a new alert.
    """

    if status not in ["ok", "bad"]:
        return

    severity = status

    # Check if an active alert already exists
    existing_alert = Alert.objects.filter(sensor=sensor, is_active=True).first()

    if existing_alert:
        # Update if severity or value changed
        if existing_alert.severity != severity or existing_alert.value != value:
            existing_alert.severity = severity
            existing_alert.value = value
            existing_alert.message = message
            existing_alert.save()
    else:
        # No active alert, create one
        Alert.objects.create(
            sensor=sensor,
            value=value,
            severity=severity,
            message=message,
            is_active=True
        )