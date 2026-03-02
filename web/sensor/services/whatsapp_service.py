import requests
from django.conf import settings
from sensor.models import Alert
import os


def send_whatsapp_message(alert : Alert, notification_type="initial"):
    url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    recommendation_details = ""
    if alert.recommendation and isinstance(alert.recommendation, dict):
        recommendation_details = alert.recommendation.get("details", "")
    
    if notification_type=="initial":
        header = "New Hydroponic Alert"
    else:
        header = "Ongoing Hydroponic Alert Reminder"

    update_format=alert.updated_at.strftime("%I:%M %p")

    message_text = (
        f"*{header}*\n"
        f"*{alert.sensor.upper()} sensor* is reading a value beyond optimum boundary. Please tend to this matter ASAP.\n\n"
        f"The current value is: *{alert.value}*\n"
        f"Severity: *{alert.severity.upper()}*\n"
        # f"Message: {alert.message}\n\n"
        f"*Recommendation:*\n"
        f"{recommendation_details}\n\n\n" 
        f"_Alert created at: {alert.created_at.strftime('%d %b, %I:%M %p')}_\n"
        f"_Data last updated at: ({update_format})_\n"

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
