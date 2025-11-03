#include "secrets.h"
// secret.h contatins service account email, project id, and secret key.

#include <NTPClient.h>

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#include <Firebase_ESP_Client.h>
#include <addons/TokenHelper.h>


#define WIFI_SSID "ASK4 Wireless"
#define WIFI_PASSWORD ""
#define DATABASE_URL "https://hydroponic-7fd3b-default-rtdb.europe-west1.firebasedatabase.app/"

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 60000);

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

struct SensorData {
  float temperature;
  float humidity;
};

SensorData sensorData;
unsigned long lastDataReceived = 0;
bool newDataAvailable = false;
// int dataCount = 0;

void setup() {
  Serial.begin(115200);
  Serial.flush();

  delay(2000);

  Serial.println("ESP8266 with Firebase Timestamps");
  
  setupWiFi();

  timeClient.begin();
  timeClient.update();

  setupFirebase();
  
  Serial.println("System Ready - Waiting for Arduino data...");
}

void loop() {
  receiveDataFromArduino();
  
  if (newDataAvailable && Firebase.ready()) {
    uploadToFirebase();
    newDataAvailable = false;
  }
  
  delay(100);
}

void receiveDataFromArduino() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    data.trim();
    
    if (data.startsWith("SENSOR:")) {
      data = data.substring(7);
      int commaIndex = data.indexOf(',');
      
      if (commaIndex != -1) {
        sensorData.temperature = data.substring(0, commaIndex).toFloat();
        sensorData.humidity = data.substring(commaIndex + 1).toFloat();
        
        newDataAvailable = true;
        lastDataReceived = millis();
        
        Serial.printf("Received: %.1f°C, %.1f%%\n", 
                     sensorData.temperature, sensorData.humidity);
      }
    }
  }
}

void uploadToFirebase() {
  Serial.print("Uploading to Firebase...");

  timeClient.update();
  unsigned long epochTime = timeClient.getEpochTime();
  String formattedTime = timeClient.getFormattedTime();
  
  FirebaseJson json;
  json.set("temperature", sensorData.temperature);
  json.set("humidity", sensorData.humidity);
  json.set("timestamp", epochTime);
  json.set("timeString", formattedTime);

  
  // Update current readings
  if (Firebase.RTDB.setJSON(&fbdo, "/sensorData/current", &json)) {
    Serial.println("Current data updated!");
    
    // Add to history with auto-generated timestamp key
    String historyPath = "/sensorData/history/" + String(epochTime);
    if (Firebase.RTDB.setJSON(&fbdo, historyPath.c_str(), &json)) {
      Serial.println("Added to history!");
    } else {
      Serial.println("Notice: Current data saved, but history failed");
    }
    
  } else {
    Serial.printf("Failed: %s\n", fbdo.errorReason().c_str());
  }
}

void setupWiFi() {
  Serial.print(" Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.printf("WiFi Connected - IP: %s\n", WiFi.localIP().toString().c_str());
}

void setupFirebase() {
  config.database_url = DATABASE_URL;

  config.service_account.data.client_email = CLIENT_EMAIL;
  config.service_account.data.project_id = PROJECT_ID;
  config.service_account.data.private_key = PRIVATE_KEY;

  config.token_status_callback = tokenStatusCallback;
  Firebase.reconnectNetwork(true);
  fbdo.setBSSLBufferSize(2048, 512);

  Serial.print("Initializing Firebase...");
  Firebase.begin(&config, &auth);
  Serial.println(" Done");
}