from django.utils import timezone
from sensor.models import Alert, AlertNotification
from sensor.services.whatsapp_service import send_whatsapp_message
from datetime import timedelta

REMINDER_INTERVAL = timedelta(hours=12)

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

def handle_alert(sensor, value, status, message):
    """
    Check if there's an existing active alert for this sensor.
    Update it if severity changed, or create a new alert.
    """
    # fail safe to ignore good levels
    if status not in ["ok", "bad"]:
        return

    severity = "critical" if status == "bad" else "warning"

    # Check if an active alert already exists
    existing_alert = Alert.objects.filter(sensor=sensor, is_active=True).first()

    if not existing_alert:
        # 1. if alert is already critical, mark bool as notfied and send whatsapp notification
        alert = Alert.objects.create(
            sensor=sensor,
            value=value,
            severity=severity,
            message=message,
            is_active=True,
            # notified_critical=(severity == "critical") 
        )

        if severity == "critical":
            send_and_log(alert)
            # send_whatsapp_message(alert)

        return

    #2. notified via whatsapp if severity moves from warning to critical but only for the first time.
    existing_alert.value = value
    existing_alert.message = message
    existing_alert.severity = severity
    existing_alert.save()

    if severity == "critical" and should_send_notification(existing_alert):
        send_and_log(existing_alert)


    # if severity == "critical" and not existing_alert.notified_critical:
    #     send_whatsapp_message(existing_alert)
    #     existing_alert.notified_critical = True
    

def should_send_notification(alert):
    if not alert.is_active:
        return False

    last_notification = (
        AlertNotification.objects
        .filter(alert=alert, channel="whatsapp")
        .order_by("-sent_at")
        .first()
    )

    if not last_notification:
        return True  # never sent before

    return timezone.now() - last_notification.sent_at >= REMINDER_INTERVAL

def send_and_log(alert : Alert):
    response = send_whatsapp_message(alert)

    AlertNotification.objects.create(
        alert=alert,
        channel="whatsapp",
        status="sent" if response.status_code==200 else "failed"
    )