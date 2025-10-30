#include <ESP8266WiFi.h>
#include <Firebase_ESP_Client.h>
#include <addons/TokenHelper.h>

#define WIFI_SSID "ASK4 Wireless"
#define WIFI_PASSWORD ""
#define DATABASE_URL "https://hydroponic-7fd3b-default-rtdb.europe-west1.firebasedatabase.app/"

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

unsigned long dataMillis = 0;
int count = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("🚀 Starting Firebase ESP8266...");
  
  // Connect to WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("📡 Connecting to WiFi");
  unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    if (millis() - startTime > 30000) {
      Serial.println("\n❌ WiFi connection failed!");
      return;
    }
  }
  Serial.println();
  Serial.print("✅ Connected with IP: ");
  Serial.println(WiFi.localIP());

  // Configure Firebase with hardcoded service account
  config.database_url = DATABASE_URL;
  
  // Replace these with your actual service account values
  config.service_account.data.client_email = "firebase-adminsdk-fbsvc@hydroponic-7fd3b.iam.gserviceaccount.com";
  config.service_account.data.project_id = "hydroponic-7fd3b";
  config.service_account.data.private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDRwTw4a4oNZxf9\nRJHlQV5inoY9lzjsgy84i2KvYNOGBea7oefAdTzM+HgGiiOy72Yb12IYQ9TUCt0c\n/Fo4UwVj1fLkC4Cd9MXpjgEHPdtglYQghEr8sYUfETT/v70c73C4hngCHQjum11w\ngPj+DZ2knPseHCPH6ZMs3hvOWAnbFi8tWi/dMdkWOwN/D4u+S1nVP72IuYFs0S2n\nAc2TR2VEaFpXGHOChU52vzM4gL7mqNuuIswzVQlGUjpo7ZjCnmeOPD/+RfLGIFu3\nhXVg+Q9m5PFVs8+1LJXl/EmykuijLgIERvlpeyQce/WQ8XoLcldvl/AaCCp4T4Mv\nIQJVMDg1AgMBAAECggEAByH4+YUvUbMwsGWGyDg6bK7t1dsrgyAXOLxwARKRQX84\nCvzfi96guuqfGup9z3L5yAFsE0hT4i2yulkwJeFYL1PXmYl07fTPJG5LsCfvwBTN\nhFU4qeeien2OuGdYLQtNDA/8iuaFsXwkh7PHDnfpkARg5gj4btmimNW+YHxYwh5V\npXW84qqrF/wNHaJvRSY5D++jX3k4HWQS+1OUQxfj7Gjxe1F/87yQv9HlMLQiW9Tf\n9Cc+PRaki0UOEKGuwFSKSNk9g42EnOqqZAGO2yLQWn6AQkbXAI8LtWoe/wSC07tN\nGunR5m7Cer8h+vVVN0PlniBCYf//qcGexhVb/vhTAQKBgQDyFC64K4aMNn5PudWn\njY/ADcFSJlRUeQdR8+nw1ucF1VTIh/7dN2o2UlbHlgTxQMSbMGEvUr7tKLIqciPk\nCE/DFVgw6GDw20AkgB4VWM4LVR1t3Foi2WYK37+XlEuAfCVlcdGp2nZzu+f95M+Z\ns4W3ZYCk/sNOciJpcUwPcMLLAQKBgQDd0TAF0d18/MhqyWdQkj13jG1Q5z4jUbZY\nQCD+cLdd27PTyqQoXPxFrFAHPrz3ZeaS8kU/miLXLKIezJx/m6G/hxClDfIVcYo1\neUACYUnenWI5viCtOW2o1BO8PV6yF5GYWFePuTcR8MHVGtd8n75/qYloRe2zjPRc\nPPW06QExNQKBgQDdz6RnWGp2e1ANmUetuUZoQbJLpZdLt4H/k7Fd3mvcqnZ/MC1V\nYXtOvu+I/WsV67S6RgAmrnkHMWze+6rrPLppFFu0pJh+2UbSqxnlkXNqatkGWwu0\nNuMLP618JINx/U7+vuXP7r7umNSfjVKzkQ0K2FSh2lX2wRnK5+c7lqTGAQKBgBJb\nrc3NgLdHdI7h/Fr+v3eVd7aqbMofiSfkptZoHcT22fs9Wji8+WQKztTKrHkNRfgD\ndRe+egO0/fXumUU2bDydwRLoBJEhxH6IenO3+ZUjEW4V/j5X8mt2oeuCaMP0j2g8\nZ4LNoXEqq+AnSI5X6jxGm8i1gObLU64OnYdLgX3BAoGBAIcwYWYpY3lg3CnowinU\n5DArbYpLyKf5Cf2v3P+esmMPRFeQ4oe2qevquEmMLbyoIxyzyis/EQxLvX2w9oms\nuzf9ZCTtSfPLCChRAYrnQKZ1+oz/25Zbces7brGK5UqqWRg21iGv2BT968VXFbXH\n10Ex+PB6sp+dhDxkwSmUO6Cf\n-----END PRIVATE KEY-----\n";
  
  config.token_status_callback = tokenStatusCallback;
  Firebase.reconnectNetwork(true);
  fbdo.setBSSLBufferSize(2048, 512);

  Serial.println("🔑 Initializing Firebase...");
  Firebase.begin(&config, &auth);
}

void loop() {
  if (Firebase.ready()) {
    if (millis() - dataMillis > 10000) {
      dataMillis = millis();
      
      String path = "/test/int";
      Serial.printf("📤 Setting %s to %d... ", path.c_str(), count);
      
      if (Firebase.RTDB.setInt(&fbdo, path, count)) {
        Serial.println("✅ Success");
        count++;
      } else {
        Serial.printf("❌ Failed: %s\n", fbdo.errorReason().c_str());
      }
    }
  } else {
    Serial.println("❌ Firebase not ready");
    if (config.signer.tokens.status == token_status_error) {
      Serial.printf("   Token error: %s\n", config.signer.tokens.error.message.c_str());
    }
  }
  delay(2000);
}