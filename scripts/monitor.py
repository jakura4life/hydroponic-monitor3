import firebase_admin
from firebase_admin import credentials, db
import json
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timezone
import ntplib

def initialize_firebase():
    """Initialize Firebase with credentials"""
    cred_json = os.environ.get('FIREBASE_CREDENTIALS')
    if not cred_json:
        raise ValueError("FIREBASE_CREDENTIALS environment variable not set")
    
    cred_dict = json.loads(cred_json)
    cred = credentials.Certificate(cred_dict)
    
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://hydroponic-7fd3b-default-rtdb.firebaseio.com/'
        })
    
    return db.reference()

def get_ntp_time():
    """Get current time from NTP server"""
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org', version=3)
        ntp_time = datetime.fromtimestamp(response.tx_time, tz=timezone.utc)
        return ntp_time.isoformat()
    except Exception as e:
        print(f"Warning: Could not get NTP time: {e}")
        return datetime.now(timezone.utc).isoformat()

def get_active_alerts(db_ref):
    """Read current active alert states from Firebase"""
    try:
        alerts_ref = db_ref.child('alerts').child('active')
        active_alerts = alerts_ref.get()
        
        # Default structure if it doesn't exist
        if not active_alerts:
            active_alerts = {
                'temperature_high': False,
                'temperature_low': False,
                'humidity_high': False,
                'humidity_low': False
            }
            # Initialize the structure
            alerts_ref.set(active_alerts)
            print("Initialized active alerts structure in Firebase")
        
        print(f"Current active alerts: {active_alerts}")
        return active_alerts
        
    except Exception as e:
        print(f"Error reading active alerts: {e}")
        # Return default structure on error
        return {
            'temperature_high': False,
            'temperature_low': False,
            'humidity_high': False,
            'humidity_low': False
        }

def update_alert_state(db_ref, alert_type, is_active):
    """Update a specific alert state in Firebase"""
    try:
        db_ref.child('alerts').child('active').child(alert_type).set(is_active)
        db_ref.child('alerts').child('lastUpdated').set({
            '.sv': 'timestamp'
        })
        print(f"Updated {alert_type} to {is_active}")
    except Exception as e:
        print(f"Error updating alert state: {e}")

def send_email_alert(alerts, sensor_data, alert_types):
    """Send email notification for new alerts"""
    try:
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        email_from = os.environ.get('EMAIL_FROM')
        email_password = os.environ.get('EMAIL_PASSWORD')
        email_to = os.environ.get('EMAIL_TO', email_from)
        
        if not email_from or not email_password:
            print("Email credentials not set. Please set EMAIL_FROM and EMAIL_PASSWORD environment variables.")
            return False
        
        print(f"Attempting to send email alert from {email_from} to {email_to}")
        
        subject = "🚨 NEW Hydroponic System Alert"
        
        text_content = f"Hydroponic System Alert\n\n"
        text_content += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        text_content += "NEW Alerts Detected:\n"
        for alert in alerts:
            text_content += f"- {alert}\n"
        text_content += f"\nCurrent Sensor Data:\n"
        text_content += f"Temperature: {sensor_data.get('temperature', 'N/A')}C\n"
        text_content += f"Humidity: {sensor_data.get('humidity', 'N/A')}%\n"
        text_content += f"Timestamp: {sensor_data.get('timestamp', 'N/A')}\n"
        text_content += "\nThis is a NEW alert from your Hydroponic Monitoring System."
        
        msg = MIMEText(text_content, 'plain')
        msg['Subject'] = subject
        msg['From'] = email_from
        msg['To'] = email_to
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_from, email_password)
        server.sendmail(email_from, email_to, msg.as_string())
        server.quit()
        
        print("Email alert sent successfully for new alerts")
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

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
        
        # Get current active alert states
        active_alerts = get_active_alerts(db_ref)
        
        alerts = []
        new_alert_types = []
        resolved_alert_types = []
        
        # Check temperature
        temperature = sensor_data.get('temperature')
        if temperature is not None:
            if temperature < 12:
                alert_type = 'temperature_low'
                if not active_alerts.get(alert_type, False):
                    # This is a NEW alert
                    alerts.append(f"Temperature too low: {temperature}C (min: 12C)")
                    new_alert_types.append(alert_type)
                # Update state to active
                update_alert_state(db_ref, alert_type, True)
            elif temperature > 30:
                alert_type = 'temperature_high'
                if not active_alerts.get(alert_type, False):
                    # This is a NEW alert
                    alerts.append(f"Temperature too high: {temperature}C (max: 30C)")
                    new_alert_types.append(alert_type)
                # Update state to active
                update_alert_state(db_ref, alert_type, True)
            else:
                # Temperature is normal, check if we need to resolve an alert
                for temp_alert in ['temperature_low', 'temperature_high']:
                    if active_alerts.get(temp_alert, False):
                        resolved_alert_types.append(temp_alert)
                        update_alert_state(db_ref, temp_alert, False)
        
        # Check humidity
        humidity = sensor_data.get('humidity')
        if humidity is not None:
            if humidity < 50:
                alert_type = 'humidity_low'
                if not active_alerts.get(alert_type, False):
                    # This is a NEW alert
                    alerts.append(f"Humidity too low: {humidity}% (min: 50%)")
                    new_alert_types.append(alert_type)
                # Update state to active
                update_alert_state(db_ref, alert_type, True)
            elif humidity > 95:
                alert_type = 'humidity_high'
                if not active_alerts.get(alert_type, False):
                    # This is a NEW alert
                    alerts.append(f"Humidity too high: {humidity}% (max: 95%)")
                    new_alert_types.append(alert_type)
                # Update state to active
                update_alert_state(db_ref, alert_type, True)
            else:
                # Humidity is normal, check if we need to resolve an alert
                for humid_alert in ['humidity_low', 'humidity_high']:
                    if active_alerts.get(humid_alert, False):
                        resolved_alert_types.append(humid_alert)
                        update_alert_state(db_ref, humid_alert, False)
        
        # Send notifications only for NEW alerts
        if alerts and new_alert_types:
            print(f"NEW alerts detected: {alerts}")
            send_email_alert(alerts, sensor_data, new_alert_types)
            log_alert(alerts, sensor_data, db_ref, alert_types=new_alert_types, is_new=True)
        elif any(active_alerts.values()):
            # There are ongoing alerts but no new ones
            ongoing_alerts = []
            for alert_type, is_active in active_alerts.items():
                if is_active:
                    if alert_type == 'temperature_low':
                        ongoing_alerts.append(f"Temperature too low: {temperature}C")
                    elif alert_type == 'temperature_high':
                        ongoing_alerts.append(f"Temperature too high: {temperature}C")
                    elif alert_type == 'humidity_low':
                        ongoing_alerts.append(f"Humidity too low: {humidity}%")
                    elif alert_type == 'humidity_high':
                        ongoing_alerts.append(f"Humidity too high: {humidity}%")
            
            print(f"Ongoing alerts (no new notification): {ongoing_alerts}")
            log_alert(ongoing_alerts, sensor_data, db_ref, alert_types=list(active_alerts.keys()), is_new=False)
        else:
            print("All sensor readings are within normal ranges")
        
        # Log resolved alerts
        if resolved_alert_types:
            print(f"Resolved alerts: {resolved_alert_types}")
            log_resolved_alert(resolved_alert_types, sensor_data, db_ref)
            
    except Exception as e:
        print(f"Error checking sensor data: {e}")

def log_alert(alerts, sensor_data, db_ref, alert_types, is_new=True):
    """Log alert to Realtime Database for history"""
    try:
        alert_ref = db_ref.child('alerts').child('history').push()
        ntp_timestamp = get_ntp_time()
        
        alert_data = {
            'alerts': alerts,
            'alert_types': alert_types,
            'sensor_data': sensor_data,
            'created_at': ntp_timestamp,
            'checked_at': datetime.now().isoformat(),
            'timestamp_source': 'ntp',
            'is_new_alert': is_new,
            'alert_status': 'new' if is_new else 'ongoing'
        }
        alert_ref.set(alert_data)
        print(f"Alert logged to history (new: {is_new})")
    except Exception as e:
        print(f"Error logging alert: {e}")

def log_resolved_alert(resolved_types, sensor_data, db_ref):
    """Log resolved alerts to database"""
    try:
        resolved_ref = db_ref.child('alerts').child('resolved').push()
        resolved_data = {
            'resolved_alert_types': resolved_types,
            'sensor_data': sensor_data,
            'resolved_at': {'.sv': 'timestamp'},
            'checked_at': datetime.now().isoformat()
        }
        resolved_ref.set(resolved_data)
        print("Resolved alerts logged to database")
    except Exception as e:
        print(f"Error logging resolved alerts: {e}")

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