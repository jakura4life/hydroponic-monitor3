import firebase_admin
from firebase_admin import credentials, firestore, messaging
import json
import os
from datetime import datetime

def initialize_firebase():
    """Initialize Firebase with credentials from environment variable"""
    cred_json = os.environ.get('FIREBASE_CREDENTIALS')
    if not cred_json:
        raise ValueError("FIREBASE_CREDENTIALS environment variable not set")
    
    cred_dict = json.loads(cred_json)
    cred = credentials.Certificate(cred_dict)
    
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

def check_sensor_ranges(db):
    """Check if sensor data is within acceptable ranges"""
    print(f"🔍 Checking sensor data at {datetime.now()}")
    
    try:
        # Get current sensor data
        doc_ref = db.collection('sensorData').document('current')
        doc = doc_ref.get()
        
        if not doc.exists:
            print("No sensor data found")
            return
        
        data = doc.to_dict()
        print(f"Current data: {data}")
        
        alerts = []
        
        # Check temperature
        temperature = data.get('temperature')
        if temperature is not None:
            if temperature < 12:
                alerts.append(f"Temperature too low: {temperature}°C (min: 12°C)")
            elif temperature > 30:
                alerts.append(f"Temperature too high: {temperature}°C (max: 30°C)")
        
        # Check humidity
        humidity = data.get('humidity')
        if humidity is not None:
            if humidity < 50:
                alerts.append(f"Humidity too low: {humidity}% (min: 50%)")
            elif humidity > 95:
                alerts.append(f"Humidity too high: {humidity}% (max: 95%)")
        
        # Send notifications if any alerts
        if alerts:
            send_notifications(alerts, data, db)
        else:
            print("All sensor readings are within normal ranges")
            
    except Exception as e:
        print(f"Error checking sensor data: {e}")

def send_notifications(alerts, sensor_data, db):
    """Send push notifications for alerts"""
    try:
        # Get all user tokens
        tokens_ref = db.collection('userTokens')
        docs = tokens_ref.stream()
        
        tokens = []
        for doc in docs:
            token_data = doc.to_dict()
            if 'token' in token_data:
                tokens.append(token_data['token'])
        
        if not tokens:
            print("No user tokens found for notifications")
            return
        
        # Create notification message
        alert_text = "\n".join(alerts)
        title = "Hydroponic Alert!"
        body = f"Sensor readings out of range:\n{alert_text}"
        
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data={
                'alert_count': str(len(alerts)),
                'timestamp': str(sensor_data.get('timestamp', '')),
                'type': 'sensor_alert'
            },
            tokens=tokens
        )
        
        # Send notification
        response = messaging.send_multicast(message)
        print(f"Sent {response.success_count}/{len(tokens)} notifications")
        
        # Log the alert
        log_alert(alerts, sensor_data, len(tokens), response.success_count, db)
        
    except Exception as e:
        print(f"Error sending notifications: {e}")

def log_alert(alerts, sensor_data, sent_count, success_count, db):
    """Log alert to Firestore for history"""
    try:
        alert_ref = db.collection('alerts').document()
        alert_ref.set({
            'alerts': alerts,
            'sensor_data': sensor_data,
            'sent_to_count': sent_count,
            'success_count': success_count,
            'created_at': firestore.SERVER_TIMESTAMP,
            'checked_at': datetime.now().isoformat()
        })
        print("📝 Alert logged to Firestore")
    except Exception as e:
        print(f"Error logging alert: {e}")

def main():
    """Main monitoring function"""
    print("=== Hydroponic Monitor Started ===")
    
    try:
        db = initialize_firebase()
        check_sensor_ranges(db)
        
    except Exception as e:
        print(f"Monitor failed: {e}")
    
    print("=== Monitor Completed ===\n")

if __name__ == "__main__":
    main()