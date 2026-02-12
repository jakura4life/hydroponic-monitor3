// Arduino Code - Reads temperature & humidity and sends to ESP8266

// Define your sensor pins
const int DHT_PIN = 2; // DHT22 data pin

// Include DHT library
#include <DHT.h>
#define DHT_TYPE DHT22
DHT dht(DHT_PIN, DHT_TYPE);

unsigned long lastSendTime = 0;
const unsigned long SEND_INTERVAL = 360000; // Send every 10 seconds

void setup() {
  Serial.begin(115200); // Communication with ESP8266
  
  // Initialize sensor
  dht.begin();
  
  Serial.println("Arduino Sensor System Ready - Temp & Humidity Only");

  delay(7000);
  Serial.println("Sending first data for testing.");
  readSensorsAndSend();
}

void loop() {
  if (millis() - lastSendTime >= SEND_INTERVAL) {
    readSensorsAndSend();
    lastSendTime = millis();
  }
  
  // delay(100);
}

void readSensorsAndSend() {
  // Read DHT22 temperature and humidity
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  // Check if sensor readings are valid
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Error: Failed to read DHT sensor!");
    return;
  }
  
  // Send data to ESP8266
  String data = "SENSOR:";
  data += String(temperature, 1) + ",";
  data += String(humidity, 1);
  
  Serial.println(data);
  
  // Print to serial monitor for debugging
  Serial.print("Sent: ");
  Serial.println(data);
}