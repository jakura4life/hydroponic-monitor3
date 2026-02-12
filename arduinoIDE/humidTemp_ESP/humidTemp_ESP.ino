#include <DHT.h>
#include <DHT_U.h>




// define
#define DHT_PIN 2
#define DHT_TYPE DHT22
DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(9600);


  dht.begin();
  delay(2000);
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {


    Serial.println("Error:DHT_READ_FAILED");

    delay(15000);
    return;
  }

  String data = "TEMP: " + String(temperature, 1) + ", HUM: " + String(humidity, 1);

  Serial.println(data);


  unsigned long startTime = millis();
  while (millis() - startTime < 5000) {
    if (Serial.available()) {
      String response = Serial.readStringUntil('\n');
      Serial.println("ESP Response: "+ response);
      break;
    }
  }

  delay(30000);
}
