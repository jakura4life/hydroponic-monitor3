#include <DHT.h>


#define SensorPin A0

#define DHTPIN 2
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);


// Calibrations (old sensor) recalibrated on 28/1/26
float phSlope = -5.96;
float phIntercept = 28.46;

// new sensor //rubbish
// float pHSlope = -57.47;
// float pHIntercept = 204.4;

void setup() {
  Serial.begin(9600);
  // Serial.println("pH Sensor Calibration (HW-828 + E-201WL)"); // old
  dht.begin();
  // sensor_t sensor;
}

void loop() {
  int sensorValue = analogRead(SensorPin);
  float voltage = sensorValue * (5.0 / 1023.0);
  float phValue = phSlope * voltage + phIntercept;
  Serial.print("Voltage: ");
  Serial.print(voltage, 3);
  Serial.println(" V");

  float airTemp = dht.readTemperature();
  Serial.print("Temperature: ");
  Serial.print(airTemp, 3);
  Serial.println(" C");

  Serial.print("pH: ");
  Serial.print(phValue);
  Serial.println();
  delay(5000);
}