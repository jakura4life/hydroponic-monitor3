import time
import threading
from django.utils import timezone
from django.conf import settings
from sensor.models import SystemHealthEvent, SystemStatus
from sensor.services.whatsapp_service import send_system_whatsapp, format_elapsed

SYSTEM_TOLERANCE=settings.SYSTEM_TOLERANCE
CHECK_INTERVAL=settings.CHECK_INTERVAL
SYSTEM_REMINDER_INTERVAL=settings.SYSTEM_REMINDER_INTERVAL #6h

# global variable
IS_SYSTEM_OFFLINE=False

def system_health_monitor():
    thread = threading.Thread(target=monitor_loop, daemon=True)
    time.sleep(3)
    thread.start()

def monitor_loop():
    print("[SYSTEM HEALTH] Monitor started")

    while True:
        global IS_SYSTEM_OFFLINE
        print("[SYSTEM HEALTH] Checking latest global reading...")

        # try:
        latest = SystemStatus.objects.first()

        if latest:
            last_epoch = latest.last_epoch
            now_epoch = int(timezone.now().timestamp())
            second_since = now_epoch - last_epoch
            print(f"[HEALTH SERVICE] time since last reading {second_since} seconds.")
            if second_since > SYSTEM_TOLERANCE:
                IS_SYSTEM_OFFLINE = True
                trigger_offline(latest)
            else:
                IS_SYSTEM_OFFLINE = False
                resolve_offline()

        # except Exception as e:
        #     print("[SYSTEM HEALTH ERROR]", e)

        time.sleep(CHECK_INTERVAL)

def trigger_offline(latest : SystemStatus):
    existing = SystemHealthEvent.objects.filter(
        status="offline",
        is_active=True
    ).first()

    now = timezone.now()
    if not existing:
        event = SystemHealthEvent.objects.create(
            status="offline",
            is_active=True,
            created_at = latest.last_received_at,
            last_notified_at=None
        )

        response=send_system_whatsapp(event, notification_type="initial")
        if response and response.status_code == 200:
            event.last_notified_at = now
            event.save()
        return
    
    if existing.last_notified_at:
        time_since_last_notif = now - existing.last_notified_at
        print (time_since_last_notif)

        if time_since_last_notif >= SYSTEM_REMINDER_INTERVAL:
            existing.elapsed = (now - existing.created_at).total_seconds()
            # existing.save()

            response=send_system_whatsapp(existing, notification_type="reminder")
            existing.last_notified_at = now if response.status_code==200 else None
            existing.save()
            return

    print("[SYSTEM HEALTH] time delta for reminder not met")
    
def resolve_offline():
    existing = SystemHealthEvent.objects.filter(
        status="offline",
        is_active=True
    ).first()

    if not existing:
        return
    
    

    now = timezone.now()
    existing.status = "resolved"
    existing.is_active = False
    existing.resolved_at = now
    existing.elapsed = (timezone.now() - existing.created_at).total_seconds()
    response=send_system_whatsapp(existing, notification_type="resolved")
    existing.last_notified_at = now if response.status_code==200 else None

    existing.save()




def isSystemOffline():
    return IS_SYSTEM_OFFLINE


def get_system_health():
    active_event = SystemHealthEvent.objects.filter(
        status='offline',
        is_active=True
    ).first()

    latest_event = SystemHealthEvent.objects.order_by("-created_at").first()

    payload = {
        "is_offline": bool(active_event),
        "active_event": None,
        "latest_event": None,
    }

    if active_event:
        payload["active_event"] = {
            "started_at": active_event.created_at,
            "elapsed": format_elapsed(int(active_event.elapsed)),
        }

    if latest_event:
        payload["latest_event"] = {
            "status": latest_event.status,
            "started_at": latest_event.created_at.strftime("%d %b %Y, %H:%M") if latest_event.created_at else None,
            "resolved_at": latest_event.resolved_at.strftime("%d %b %Y, %H:%M") if latest_event.resolved_at else None,
            "elapsed": format_elapsed(int(latest_event.elapsed)),
        }

    return payload

