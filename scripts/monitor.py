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
            'databaseURL': 'https://hydroponic-7fd3b-default-rtdb.europe-west1.firebasedatabase.app/'
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
                'temperature_alert': False,
                'humidity_alert': False,
                'ph_alert': False,
                'tds_alert': False,
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
            'temperature_alert': False,
            'humidity_alert': False,
            'ph_alert': False,
            'tds_alert': False,
        }

def update_alert_state(db_ref, alert_type, is_active):
    """Update a specific alert state in Firebase"""
    try:
        db_ref.child('alerts').child('active').child(alert_type).set(is_active)
        db_ref.child('alerts').child('active').child('lastUpdated').set({
        'server_timestamp': { '.sv': 'timestamp' },  # Firebase server time
        'formatted': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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

def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    if seconds is None:
        return "Unknown"
    
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"

def get_alerted_sensor_data(sensor_data, alert_type):
    """Extract only the relevant sensor data for the specific alert"""
    alerted_val = None  # Initialize with default value
    
    if alert_type == 'temperature_alert' and 'temperature' in sensor_data:
        alerted_val = sensor_data['temperature']
    elif alert_type == 'humidity_alert' and 'humidity' in sensor_data:
        alerted_val = sensor_data['humidity']
    elif alert_type == 'ph_alert' and 'ph' in sensor_data:
        alerted_val = sensor_data['ph']
    elif alert_type == 'tds_alert' and 'tds' in sensor_data:
        alerted_val = sensor_data['tds']
    
    return alerted_val

def log_alert_event(db_ref, event_type, alert_types, sensor_data):
    """Log alert activation and resolution events with duration tracking"""
    try:
        ntp_timestamp = get_ntp_time()
        
        if event_type == 'activated':
            # Log activation and store start time
            for alert_type in alert_types:
                # Get only the relevant sensor data for this alert
                alerted_val = get_alerted_sensor_data(sensor_data, alert_type)
                
                event_ref = db_ref.child('alerts').child('activated').push()
                event_data = {
                    'alert_type': alert_type,
                    'sensor_val': alerted_val,  # Only store alerted variable
                    'start_times' : ntp_timestamp,
                }
                event_ref.set(event_data)
                
                # Store start time for duration calculation later
                # db_ref.child('alerts').child('start_times').child(alert_type).set(ntp_timestamp)
            
            print(f"Alert activation logged: {alert_types}")
            
        elif event_type == 'resolved':
            # Calculate duration for each resolved alert
            for alert_type in alert_types:
                # Get only the relevant sensor data for this alert
                alerted_val = get_alerted_sensor_data(sensor_data, alert_type)
                
                # Get the start time from the activated alert entry
                activated_alerts = db_ref.child('alerts').child('activated').get() or {}
                start_time = None
                alert_key_to_delete = None
                
                # Find the matching activated alert and get its timestamp
                for alert_key, alert_data in activated_alerts.items():
                    if alert_data.get('alert_type') == alert_type:
                        start_time = alert_data.get('start_times')
                        alert_key_to_delete = alert_key
                        break
                
                if start_time:
                    # Calculate duration
                    try:
                        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(ntp_timestamp.replace('Z', '+00:00'))
                        duration_seconds = int((end_dt - start_dt).total_seconds())
                        
                        # Format duration for readability
                        duration_str = format_duration(duration_seconds)
                    except Exception as e:
                        print(f"Error calculating duration: {e}")
                        duration_seconds = None
                        duration_str = "Unknown"
                    
                    # Log resolution with duration
                    event_ref = db_ref.child('alerts').child('resolved').push()
                    
                    # Create event data for resolved alert
                    event_data = {
                        'alert_type': alert_type,
                        'sensor_val': alerted_val,  # Only store alerted variable
                        'activated_at': start_time,
                        'resolved_at': ntp_timestamp,
                        'duration_seconds': duration_seconds,
                        'duration_readable': duration_str,
                    }

                    event_ref.set(event_data)
                    
                    print(f"Alert resolution logged: {alert_type} (duration: {duration_str})")
                else:
                    # No start time found, log without duration
                    event_ref = db_ref.child('alerts').child('resolved').push()
                    event_data = {
                        'alert_type': alert_type,
                        'sensor_val': alerted_val,  # Only store alerted variable
                        'resolved_at': ntp_timestamp,
                        'duration_seconds': None,
                        'duration_readable': 'Unknown',
                    }
                    event_ref.set(event_data)
                    print(f"Alert resolution logged (no start time): {alert_type}")
                
                if alert_key_to_delete:
                    db_ref.child('alerts').child('activated').child(alert_key_to_delete).delete()
                    print(f"✅ Deleted resolved alert from activated: {alert_key_to_delete}")
                else:
                    # Fallback: try to delete by alert_type
                    delete_from_activated(alert_type, db_ref)
            
    except Exception as e:
        print(f"Error logging alert event: {e}")

def delete_from_activated(alert_type, db_ref):
    """Find and delete the matching alert from activated directory"""
    try:
        activated_ref = db_ref.child('alerts').child('activated')
        activated_alerts = activated_ref.get()
        
        if activated_alerts:
            for alert_key, alert_data in activated_alerts.items():
                # Check if alert_type matches
                if alert_data.get('alert_type') == alert_type:
                    # For more precise matching, you can also check sensor data
                    # But since we're deleting by alert_type, this should be sufficient
                    
                    # Delete the matching alert
                    activated_ref.child(alert_key).delete()
                    print(f"✅ Deleted resolved alert from activated: {alert_key}")
                    return True
        
        print(f"⚠️  No matching alert found in activated directory for: {alert_type}")
        return False
        
    except Exception as e:
        print(f"❌ Error deleting from activated: {e}")
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
            alert_type = 'temperature_alert'
            if temperature < 12 or temperature > 28:
                if not active_alerts.get(alert_type, False):
                    # This is a NEW alert
                    if temperature < 12:
                        alerts.append(f"Temperature too low: {temperature}C (min: 12C)")
                    else:
                        alerts.append(f"Temperature too high: {temperature}C (max: 28C)")
                    new_alert_types.append(alert_type)
                    # Log activation
                    log_alert_event(db_ref, 'activated', [alert_type], sensor_data)
                # Update state to active
                update_alert_state(db_ref, alert_type, True)
            else:
                # Temperature is normal, check if we need to resolve an alert
                if active_alerts.get(alert_type, False):
                    resolved_alert_types.append(alert_type)
                    update_alert_state(db_ref, alert_type, False)
        
        # Check humidity
        humidity = sensor_data.get('humidity')
        if humidity is not None:
            alert_type = 'humidity_alert'
            if humidity < 50 or humidity > 80:
                if not active_alerts.get(alert_type, False):
                    # This is a NEW alert
                    if humidity < 50:
                        alerts.append(f"Humidity too low: {humidity}% (min: 50%)")
                    else:
                        alerts.append(f"Humidity too high: {humidity}% (max: 80%)")
                    new_alert_types.append(alert_type)
                    # Log activation
                    log_alert_event(db_ref, 'activated', [alert_type], sensor_data)
                # Update state to active
                update_alert_state(db_ref, alert_type, True)
            else:
                # Humidity is normal, check if we need to resolve an alert
                if active_alerts.get(alert_type, False):
                    resolved_alert_types.append(alert_type)
                    update_alert_state(db_ref, alert_type, False)
        
        # Log resolution events if any
        if resolved_alert_types:
            log_alert_event(db_ref, 'resolved', resolved_alert_types, sensor_data)
            print(f"Resolved alerts: {resolved_alert_types}")
        
        # Send notifications only for NEW alerts
        if alerts and new_alert_types:
            print(f"NEW alerts detected: {alerts}")
            send_email_alert(alerts, sensor_data, new_alert_types)
        elif any(active_alerts.values()):
            # There are ongoing alerts but no new ones
            ongoing_alerts = []
            for alert_type, is_active in active_alerts.items():
                if is_active:
                    if alert_type == 'temperature_alert':
                        ongoing_alerts.append(f"Temperature out of range: {temperature}C")
                    elif alert_type == 'humidity_alert':
                        ongoing_alerts.append(f"Humidity out of range: {humidity}%")
            
            print(f"Ongoing alerts (no new notification): {ongoing_alerts}")
        else:
            print("All sensor readings are within normal ranges")
            
    except Exception as e:
        print(f"Error checking sensor data: {e}")

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