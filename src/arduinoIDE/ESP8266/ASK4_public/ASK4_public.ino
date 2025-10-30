
#include "secrets.h"
#include <Firebase.h>
#include <ESP8266WiFi.h>

const char* target_ssid = WIFI_SSID;//"ASK4 Wireless";
const char* FIREBASE_URL;
const char* FIREBASE_KEY;


void scanAndConnect() {
  Serial.println("Scanning for networks...");
  
  // Scan for WiFi networks
  int numNetworks = WiFi.scanNetworks();
  
  if (numNetworks == 0) {
    Serial.println("No networks found");
    return;
  }
  
  Serial.printf("Found %d networks:\n", numNetworks);
  
  bool foundTarget = false;
  
  for (int i = 0; i < numNetworks; i++) {
    String ssid = WiFi.SSID(i);
    int rssi = WiFi.RSSI(i);
    int encryption = WiFi.encryptionType(i);
    
    Serial.printf("%d: %s ", i + 1, ssid.c_str());
    Serial.printf("(%ddBm) ", rssi);
    
    // Check if open network (no password)
    if (encryption == ENC_TYPE_NONE) {
      Serial.print("OPEN ");
    }
    
    // Check if this is our target network
    if (ssid == target_ssid) {
      foundTarget = true;
      Serial.print("<-- TARGET");
    }
    
    Serial.println();
  }
  
  if (foundTarget) {
    Serial.printf("\nConnecting to %s...\n", target_ssid);
    connectToWiFi(target_ssid);
  } else {
    Serial.printf("\nTarget network '%s' not found.\n", target_ssid);
  }
}

void connectToWiFi(const char* ssid) {
  WiFi.begin(ssid); // No password for open network
  
  Serial.print("Connecting");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ Connected successfully!");
    Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\n❌ Failed to connect");
  }
}

void checkConnection() {
    // Monitor connection
  static unsigned long lastCheck = 0;
  if (millis() - lastCheck > 10000) {
    lastCheck = millis();
    
    if (WiFi.status() == WL_CONNECTED) {
      Serial.printf("Connected - IP: %s, RSSI: %d dBm\n", 
                   WiFi.localIP().toString().c_str(), WiFi.RSSI());
    } else {
      Serial.println("Not connected. Attempting to reconnect...");
      connectToWiFi(target_ssid);
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(3000);
  
  Serial.println();
  Serial.println("=== Public WiFi Connector ===");
  
  WiFi.mode(WIFI_STA);
  
  // Scan and connect
  scanAndConnect();

  config.api_key = FIREBASE_KEY;
  config.database_url = FIREBASE_URL;

  Firebase.reconnectNetwork(true);
  fbdo.setBSSLBufferSize(4096, 1024);
  Firebase.setIdToken(&config, "<ID Token>", 3600 /* expiry time */, "<Refresh Token>");
}

void loop() {

  
  delay(1000);
}