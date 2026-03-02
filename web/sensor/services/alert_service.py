from django.utils import timezone
from sensor.models import Alert, AlertNotification
from sensor.services.whatsapp_service import send_whatsapp_message
from datetime import timedelta
from django.conf import settings

REMINDER_INTERVAL=settings.REMINDER_INTERVAL
ALERT_TOLERANCE=settings.ALERT_TOLERANCE

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

def handle_alert(sensor, value, status, message, recommendation):
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
            recommendation=recommendation,
            is_active=True,
            # critical count is defaulted to 0 upon creation
        )
        if severity == "critical":
            alert.critical_count += 1
            alert.save()
        # if severity == "critical":
        #     send_and_log(alert)
        #     # send_whatsapp_message(alert)
        return

    if severity == "critical":
        if existing_alert.critical_count<ALERT_TOLERANCE:
            existing_alert.critical_count += 1
    else:
        existing_alert.critical_count = 0
    #2. notified via whatsapp if severity moves from warning to critical but only for the first time.
    existing_alert.value = value
    existing_alert.message = message
    existing_alert.severity = severity
    existing_alert.save()

    if severity == "critical" and should_send_notification(existing_alert) and existing_alert.critical_count >= ALERT_TOLERANCE:
        send_and_log(existing_alert)
        return
    return
    

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

    print("WHATSAPP_ALERT: sending out alert.")
    response = send_whatsapp_message(alert)

    AlertNotification.objects.create(
        alert=alert,
        channel="whatsapp",
        status="sent" if response.status_code==200 else "failed"
    )