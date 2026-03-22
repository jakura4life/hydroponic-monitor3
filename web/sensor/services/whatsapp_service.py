import requests
from django.conf import settings
from sensor.models import Alert, SystemHealthEvent
import os

URL = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_ID}/messages"

HEADERS = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

RECEIVER = settings.USER_PHONE_NUMBER

def send_whatsapp_message(alert : Alert, notification_type="initial"):
    recommendation_details = ""
    if alert.recommendation and isinstance(alert.recommendation, dict):
        recommendation_details = alert.recommendation.get("details", "")
    
    if notification_type=="initial":
        header = "New Hydroponic Alert"
    else:
        header = "Ongoing Hydroponic Alert Reminder"

    update_format=alert.updated_at.strftime("%H:%M")

    message_text = (
        f"*{header}*\n"
        f"*{alert.sensor.upper()} sensor* is reading a value beyond optimum boundary. Please tend to this matter ASAP.\n\n"
        f"The current value is: *{alert.value}*\n"
        f"Severity: *{alert.severity.upper()}*\n"
        # f"Message: {alert.message}\n\n"
        f"*Recommendation:*\n"
        f"{recommendation_details}\n\n\n" 
        f"_Alert created at: {alert.created_at.strftime("%d %b %Y, %H:%M")}_\n"
        f"_Data last updated at: {update_format}_\n"

    )

    payload = {
        "messaging_product": "whatsapp",
        "to": RECEIVER,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    response = requests.post(URL, json=payload, headers=HEADERS)
    print("[WHATSAPP SERIVCE]", response.status_code)
    return response


def send_system_whatsapp(sys_evnt :SystemHealthEvent, notification_type='initial'):
    created_time = sys_evnt.created_at.strftime("%d %b %Y, %H:%M")
    elapsed = format_elapsed(int(sys_evnt.elapsed))
    if notification_type == "initial":
        header = "*Arduino Offline*"
        message_text = (
            f"{header}\n\n"
            f"Arduino is not sending data to Firebase database.\n\n"
            f"_Detected at: {created_time}_"
        )
    elif notification_type == "resolved":
        resolve_time = sys_evnt.resolved_at.strftime("%d %b %Y, %H:%M")
        header = "*System Restored*"
        message_text = (
            f"{header}\n\n"
            f"Arduino is back online.\n"
            f"Duration: {elapsed}\n\n"

            f"_Resolve at: {resolve_time}_\n"
            f"_Detected at: {created_time}_"
        )
    else:
        header = "*System Reminder*"
        message_text = (
            f"{header}\n\n"
            f"Arduino is still offline.\n"
            f"Duration: {elapsed}\n\n"

            f"_Detected at: {created_time}_"
        )

    payload = {
        "messaging_product": "whatsapp",
        "to": RECEIVER,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    response = requests.post(URL, json=payload, headers=HEADERS)
    print("[WHATSAPP SERIVCE]", response.status_code)
    return response



## util
def format_elapsed(seconds: int) -> str:
    if not seconds or seconds < 0:
        return "0m"

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)

    parts = []

    if days > 0:
        parts.append(f"{days}day")

    if hours > 0 or days > 0:
        parts.append(f"{hours}hour")

    parts.append(f"{minutes}min")

    return " ".join(parts)