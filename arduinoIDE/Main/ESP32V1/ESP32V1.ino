/*---------
Includes
----------*/
#include "secrets.h"  // Contains service account email, project id, and secret key
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <WiFiUdp.h>
#include <Firebase_ESP_Client.h>
#include <addons/TokenHelper.h>
#include <NTPClient.h>
// #include "esp_wpa2.h"   // WPA2 Enterprise 
/*
Connecting to WPA2 Enterprise requires lots of memory/storage to store certificate.
My ESP32 is able to connect to it but i am unable to compile the program with the full firebase 
functionality.
*/ 

/*---------
Definitions
----------*/
// ASK4
#define WIFI_SSID "ASK4 Wireless"
#define WIFI_PASSWORD ""

// hotspot
// #define WIFI_SSID HOTSPOT_SSID
// #define WIFI_PASSWORD HOTSPOT_PASSWORD

// Eduroam 
// #define EDU_SSID "eduroam"

#define DATABASE_URL "https://hydroponic-7fd3b-default-rtdb.europe-west1.firebasedatabase.app/"

#define ARDUINO_RX 16  // GPIO16 = RX2
#define ARDUINO_TX 17  // GPIO17 = TX2


/*---------
Variables
----------*/
// NTP Client
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 60000);

// Firebase
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

struct SensorData {
  float temperature;
  float humidity;
  float pH;
  float tds;
};

SensorData sensorData;

// timing
unsigned long lastDataReceived = 0;
unsigned long lastHistoryUpdate = 0;
// unsigned long lastCurrentUpdate = 0; // unused
bool newDataAvailable = false;

// const unsigned long CURRENT_UPDATE_INTERVAL = 7000;    // 7 seconds
// const unsigned long HISTORY_UPDATE_INTERVAL = 3600000; // 1 hour
const unsigned long HISTORY_UPDATE_INTERVAL = 720000; // 10 mins


/*---------
Main
----------*/

void setup() {
  Serial.begin(9600);
  Serial2.begin(115200, SERIAL_8N1, ARDUINO_RX, ARDUINO_TX);  // Using Serial2 for Arduino communication
  
  delay(1000);

  Serial.println("ESP32 with Firebase Timestamps");
  Serial.println("ESP32 Tracking (Temp, Humidity, pH, TDS)");

  setupWiFi();
  setupTime();
  setupFirebase();
  
  Serial.println("System Ready - Waiting for Arduino data...");
}

void loop() {
  checkWiFi();

  receiveDataFromArduino();
  
  if (newDataAvailable && Firebase.ready()) {
    unsigned long currentMillis = millis();
    
    updateCurrentData();

    if (currentMillis - lastHistoryUpdate >= HISTORY_UPDATE_INTERVAL) {
      updateHistoryData();
      lastHistoryUpdate = currentMillis;
    }

    newDataAvailable = false;
  }
  
  delay(10);
}


/*---------
Functions
----------*/
// serial scanner from arduino
void receiveDataFromArduino() {
  // Using Serial2 to communicate with Arduino
  if (Serial2.available() > 0) {
    String data = Serial2.readStringUntil('\n');
    data.trim();
    
    // Serial.print("Raw received: ");
    // Serial.println(data);
    
    if (!data.startsWith("UPLOAD:")) return;

    data = data.substring(7); // Remove "UPLOAD:"

    float values[4];
    int valueIndex = 0;

    while (data.length() > 0 && valueIndex < 4) {
      int commaIndex = data.indexOf(',');
      if (commaIndex == -1) {
        values[valueIndex++] = data.toFloat();
        break;
      } else {
        values[valueIndex++] = data.substring(0, commaIndex).toFloat();
        data = data.substring(commaIndex + 1);
      }
    }

    if (valueIndex == 4) {
      sensorData.temperature = values[0];
      sensorData.humidity = values[1];
      sensorData.pH = values[2];
      sensorData.tds = values[3];

      newDataAvailable = true;
      lastDataReceived = millis();

      Serial.printf(
        "Received → Temp: %.1f°C | Hum: %.1f%% | pH: %.2f | TDS: %.0f ppm\n",
        sensorData.temperature,
        sensorData.humidity,
        sensorData.pH,
        sensorData.tds
      );
    } else {
      Serial.printf("Error: Expected 4 values, got %d\n", valueIndex);
    }
  }
}

// update only current directory without storing it into history
void updateCurrentData() {
  Serial.print("Updating current data in Firebase...");
  
  timeClient.update();
  unsigned long epochTime = timeClient.getEpochTime();
  char isoTime[25];
  epochToISO8601(epochTime, isoTime, sizeof(isoTime));
  
  FirebaseJson json;
  json.set("temperature", sensorData.temperature);
  json.set("humidity", sensorData.humidity);
  json.set("pH", sensorData.pH);
  json.set("TDS", sensorData.tds);
  json.set("epoch", epochTime);
  json.set("datetime", isoTime);
  
  if (Firebase.RTDB.setJSON(&fbdo, "/sensorData/current", &json)) {
    Serial2.println("ESP32:Current data updated!");
  } else {
    Serial2.printf("ESP32:[ERROR] Failed to update current data: %s\n", fbdo.errorReason().c_str());
  }
}

// saves in history directory aswell.
void updateHistoryData() {
  Serial.print("Adding to history (hourly)...");
  
  timeClient.update();
  unsigned long epochTime = timeClient.getEpochTime();
  char isoTime[25];
  epochToISO8601(epochTime, isoTime, sizeof(isoTime));
  
  FirebaseJson historyJson;
  historyJson.set("temperature", sensorData.temperature);
  historyJson.set("humidity", sensorData.humidity);
  historyJson.set("pH", sensorData.pH);
  historyJson.set("TDS", sensorData.tds);
  historyJson.set("datetime", isoTime);
  
  // Add to history with auto-generated timestamp key
  String historyPath = "/sensorData/history/" + String(epochTime);
  if (Firebase.RTDB.setJSON(&fbdo, historyPath.c_str(), &historyJson)) {
    Serial2.println("ESP32:Added to history!");
  } else {
    Serial2.printf("ESP32:[ERROR] Failed to add to history: %s\n", fbdo.errorReason().c_str());
  }
}

void epochToISO8601(unsigned long epoch, char *buffer, size_t bufSize) {
  time_t rawtime = (time_t)epoch;
  struct tm *timeinfo;
  timeinfo = gmtime(&rawtime);
  
  strftime(buffer, bufSize, "%Y-%m-%dT%H:%M:%SZ", timeinfo);
}


/*---------
Set Up Functions
----------*/
void setupWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(1000);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nINFO: Connected to ASK4");
    Serial.printf("IP Address: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("Signal Strength: %d dBm\n", WiFi.RSSI());
  } else {
    Serial.println("\nFailed to connect to ASK4");
    ESP.restart();
  }
}

void setupFirebase() {
  config.database_url = DATABASE_URL;
  config.signer.test_mode = false;

  // Using service account credentials
  config.service_account.data.client_email = CLIENT_EMAIL;
  config.service_account.data.project_id = PROJECT_ID;
  config.service_account.data.private_key = PRIVATE_KEY;

  config.token_status_callback = tokenStatusCallback;
  
  // ESP32 specific settings
  fbdo.setBSSLBufferSize(4096, 1024);
  fbdo.setResponseSize(2048);

  // new settings
  // fbdo.setBSSLBufferSize(8192, 2048);
  // fbdo.setResponseSize(4096);
  
  Firebase.reconnectWiFi(true);

  Serial.print("Initializing Firebase...");
  Firebase.begin(&config, &auth);
  
  Serial.println(" Done");
}

void setupTime() {
  Serial.println("Setting up NTP time client...");
  
  timeClient.begin();
  timeClient.setUpdateInterval(60000);
  // timeClient.setTimeout(15000);  // 15 second timeout
  
  if (timeClient.forceUpdate()) {
    unsigned long epochTime = timeClient.getEpochTime();
    Serial.printf("Time initialized: %lu\n", epochTime);
  } else {
    Serial.println("Initial time sync failed, will retry...");
  }
}


void checkWiFi() {
  if (WiFi.status() != WL_CONNECTED) {
    ESP.restart();
  }
}
