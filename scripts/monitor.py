import firebase_admin
from firebase_admin import credentials, db, messaging
import json
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timezone
import ntplib

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
            print(f"Alerts detected: {alerts}")
            # Try email notification
            send_email_alert(alerts, sensor_data)
            # Log to database
            log_alert(alerts, sensor_data, db_ref)
        else:
            print("All sensor readings are within normal ranges")
            
    except Exception as e:
        print(f"Error checking sensor data: {e}")

def send_email_alert(alerts, sensor_data):
    """Send email notification for alerts"""
    try:

        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        email_from = os.environ.get('EMAIL_FROM')
        email_password = os.environ.get('EMAIL_PASSWORD')
        email_to = os.environ.get('EMAIL_TO', email_from)
        
        if not email_from or not email_password:
            print("Email credentials not set. Setting up console alerts only.")
            return
        
        subject = "Hydroponic System Alert"
        body = f"Hydroponic System Alert\n\n"
        body += f"Time: {datetime.now()}\n\n"
        body += "Alerts:\n"
        for alert in alerts:
            body += f"- {alert}\n"
        body += f"\nCurrent Sensor Data:\n"
        body += f"Temperature: {sensor_data.get('temperature', 'N/A')}C\n"
        body += f"Humidity: {sensor_data.get('humidity', 'N/A')}%\n"
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = email_from
        msg['To'] = email_to
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_from, email_password)
        server.send_message(msg)
        server.quit()
        
        print("Email alert sent successfully")
        
    except Exception as e:
        print(f"Error sending email: {e}")

def get_ntp_time():
    """Get current time from NTP server"""
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org', version=3)
        ntp_time = datetime.fromtimestamp(response.tx_time, tz=timezone.utc)
        return ntp_time.isoformat()
    except Exception as e:
        print(f"Warning: Could not get NTP time: {e}")
        # Fallback to system time
        return datetime.now(timezone.utc).isoformat()

def log_alert(alerts, sensor_data, db_ref):
    """Log alert to Realtime Database for history"""
    try:
        alert_ref = db_ref.child('alerts').push()
        ntp_timestamp = get_ntp_time()

        alert_data = {
            'alerts': alerts,
            'sensor_data': sensor_data,
            'created_at': ntp_timestamp,
            'checked_at': datetime.now().isoformat()
        }
        alert_ref.set(alert_data)
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