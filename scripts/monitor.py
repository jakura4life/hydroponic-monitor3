import firebase_admin
from firebase_admin import credentials, db, messaging
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
        # Initialize with Realtime Database URL
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://hydroponic-7fd3b-default-rtdb.europe-west1.firebasedatabase.app/' 
        })
    
    return db.reference()

def check_sensor_ranges(db_ref):
    """Check if sensor data is within acceptable ranges"""
    print(f"Checking sensor data at {datetime.now()}")
    
    try:
        # Get current sensor data from Realtime Database
        sensor_data = db_ref.child('sensorData').child('current').get()
        
        if not sensor_data:
            print("No sensor data found")
            return
        
        print(f"Current data: {sensor_data}")
        
        alerts = []
        
        # Check temperature
        temperature = sensor_data.get('temperature')
        if temperature is not None:
            if temperature < 12:
                alerts.append(f"Temperature too low: {temperature}C (min: 12C)")
            elif temperature > 30:
                alerts.append(f"Temperature too high: {temperature}C (max: 30C)")
        
        # Check humidity
        humidity = sensor_data.get('humidity')
        if humidity is not None:
            if humidity < 50:
                alerts.append(f"Humidity too low: {humidity}% (min: 50%)")
            elif humidity > 95:
                alerts.append(f"Humidity too high: {humidity}% (max: 95%)")
        
        # Send notifications if any alerts
        if alerts:
            send_notifications(alerts, sensor_data)
        else:
            print("All sensor readings are within normal ranges")
            
    except Exception as e:
        print(f"Error checking sensor data: {e}")

def send_notifications(alerts, sensor_data):
    """Send push notifications for alerts"""
    try:
        # Get all user tokens from Realtime Database
        tokens_ref = db.reference('userTokens')
        tokens_data = tokens_ref.get()
        
        tokens = []
        if tokens_data:
            # tokens_data could be a dict of user tokens
            for user_id, token_data in tokens_data.items():
                if isinstance(token_data, dict) and 'token' in token_data:
                    tokens.append(token_data['token'])
                elif isinstance(token_data, str):
                    # If tokens are stored as simple string values
                    tokens.append(token_data)
        
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
        
        # Log the alert to Realtime Database
        log_alert(alerts, sensor_data, len(tokens), response.success_count)
        
    except Exception as e:
        print(f"Error sending notifications: {e}")

def log_alert(alerts, sensor_data, sent_count, success_count):
    """Log alert to Realtime Database for history"""
    try:
        alert_ref = db.reference('alerts').push()
        alert_ref.set({
            'alerts': alerts,
            'sensor_data': sensor_data,
            'sent_to_count': sent_count,
            'success_count': success_count,
            'created_at': {'.sv': 'timestamp'},  # Firebase server timestamp
            'checked_at': datetime.now().isoformat()
        })
        print("Alert logged to Realtime Database")
    except Exception as e:
        print(f"Error logging alert: {e}")

def main():
    """Main monitoring function"""
    print("=== Hydroponic Monitor Started ===")
    
    try:
        db_ref = initialize_firebase()
        check_sensor_ranges(db_ref)
        
    except Exception as e:
        print(f"Monitor failed: {e}")
    
    print("=== Monitor Completed ===\n")

if __name__ == "__main__":
    main()