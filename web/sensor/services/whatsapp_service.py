import requests
from django.conf import settings
from sensor.models import Alert
import os


def send_whatsapp_message(alert : Alert):
    url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    message_text = (
        f"*Hydroponic Alert*\n\n"
        f"{alert.sensor.upper()} sensor has gone beyond critical range.\n"
        f"The current value is: {alert.value}\n"
        f""
        f"Severity: {alert.severity.upper()}\n"
        f"Message: {alert.message}"
    )

    payload = {
        "messaging_product": "whatsapp",
        "to": settings.USER_PHONE_NUMBER,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    print("Status:", response.status_code)
    print("Body:", response.text)
    return response
