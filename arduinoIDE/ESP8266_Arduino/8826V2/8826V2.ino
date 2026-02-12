#include "secrets.h"
// secret.h contatins service account email, project id, and secret key.

#include <NTPClient.h>

#include <WiFiUdp.h>

#include <Firebase_ESP_Client.h>
#include <addons/TokenHelper.h>


// ASK4
#define WIFI_SSID "ASK4 Wireless"
#define WIFI_PASSWORD ""
#define DATABASE_URL "https://hydroponic-7fd3b-default-rtdb.europe-west1.firebasedatabase.app/"

// eduroam
#define EDU_SSID "eduroam"
#define EDU_IDENTITY ""
#define EDU_USERNAME ""
#define EDU_PASSWORD ""


WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 60000);

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

unsigned long lastDataReceived = 0;
bool newDataAvailable = false;

void setup() {
  Serial.begin(115200);
  Serial1.

  delay(1000);

  Serial.println("ESP32 with Firebase Timestamps");
  Serial.println("ESP32 Tracking (Temp, Humidity, pH, TDS)");

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
  
  delay(3000);
}

void receiveDataFromArduino() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    data.trim();
    
    if (!data.startsWith("UPLOAD:")) return;

    data = data.substring(7); // Remove "SENSOR:"

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
      Serial.println("Error: Formating gone wrong.");
    }
  }
}

void uploadToFirebase() {
  Serial.print("Uploading to Firebase...");

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

  FirebaseJson historyJson;
  historyJson.set("temperature", sensorData.temperature);
  historyJson.set("humidity", sensorData.humidity);
  historyJson.set("pH", sensorData.pH);
  historyJson.set("TDS", sensorData.tds);
  
  // Update current readings
  if (Firebase.RTDB.setJSON(&fbdo, "/sensorData/current", &json)) {
    Serial.println("Current data updated!");
    
    // Add to history with auto-generated timestamp key
    String historyPath = "/sensorData/history/" + String(epochTime);
    if (Firebase.RTDB.setJSON(&fbdo, historyPath.c_str(), &historyJson)) {
      Serial.println("Added to history!");
    } else {
      Serial.println("Notice: Current data saved, but history failed");
    }
    
  } else {
    Serial.printf("Failed: %s\n", fbdo.errorReason().c_str());
  }
}


// Converts Unix epoch to ISO 8601 string "YYYY-MM-DDTHH:MM:SSZ"
void epochToISO8601(unsigned long epoch, char *buffer, size_t bufSize) {
  // seconds in day
  unsigned long seconds = epoch % 60;
  unsigned long minutes = (epoch / 60) % 60;
  unsigned long hours   = (epoch / 3600) % 24;

  // days since epoch
  unsigned long days = epoch / 86400;

  // simple Gregorian calendar conversion
  int year = 1970;
  while (true) {
    int daysInYear = 365;
    if ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0)) daysInYear = 366;
    if (days >= daysInYear) {
      days -= daysInYear;
      year++;
    } else break;
  }

  int month = 1;
  int monthDays[12] = {31,28,31,30,31,30,31,31,30,31,30,31};
  if ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0)) monthDays[1] = 29;

  while (days >= monthDays[month-1]) {
    days -= monthDays[month-1];
    month++;
  }

  int day = days + 1;

  snprintf(buffer, bufSize, "%04d-%02d-%02dT%02lu:%02lu:%02luZ", 
           year, month, day, hours, minutes, seconds);
}


///
/// Setup Functions
///

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
