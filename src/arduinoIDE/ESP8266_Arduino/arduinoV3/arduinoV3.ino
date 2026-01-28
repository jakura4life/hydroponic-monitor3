
// ==================
// Definitions
// ==================

#include <DHT.h>

#define DHT_PIN 2
#define DHT_TYPE DHT22
DHT dht(DHT_PIN, DHT_TYPE);

#define PH_PIN A0
#define TDS_PIN A5

// values below form CQRobot TDS wiki
#define VREF 5.0
#define SCOUNT 30

// Calibrations (old sensor) recalibrated on 28/1/26
float phSlope = -5.96;
float phIntercept = 28.46;

// Timing
unsigned long lastSendTime = 0;
const unsigned long SEND_INTERVAL = 60000; // send every min but save history of every 10mins
// const unsigned long SEND_INTERVAL = 15000; // send every 15s but save history of every 10mins


// TSD buffers
int tdsBuffer[SCOUNT];
int tdsIndex = 0;
bool tdsReady = false;
// ==================
// Setup
// ==================

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(PH_PIN, INPUT);
  pinMode(TDS_PIN, INPUT);

  Serial.println("Arduino Sensor System Begin.");
  Serial.println("Tracking: Temp, Humidity, pH, TDS");
  delay(10000); //10 second delay to wait for esp8266 startup

}

// ==================
// Main Loop
// ==================


void loop() {
  sampleTds();

  if (millis() - lastSendTime >= SEND_INTERVAL) {
    if (tdsReady) {
      readSensorsAndSend();
      lastSendTime = millis();
    }
  }
}


// ==================
// Functions
// ==================

void readSensorsAndSend() {
  // DHT22
  float airTemp = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(airTemp) || isnan(humidity)) {
    Serial.println("Error: Failed to read DHT22");
    return;
  }

  // pH Sensor
  int phRaw = analogRead(PH_PIN);
  float phVoltage = phRaw * VREF / 1023.0;
  float phValue = phSlope * phVoltage + phIntercept;

  // TDS sensor
  int medianADC = getMedian(tdsBuffer, SCOUNT);
  float tdsVoltage = medianADC * VREF / 1024.0;

  // Temperature conpensation (air temp)
  float compensationCoefficient = 1.0 + 0.02 * (airTemp - 25.0);
  float compensatedVoltage = tdsVoltage / compensationCoefficient;

  // equation from CQRobot wiki
  float tdsValue = (133.42 * compensatedVoltage * compensatedVoltage * compensatedVoltage
                    - 255.86 * compensatedVoltage * compensatedVoltage
                    + 857.39 * compensatedVoltage)
                   * 0.5;


  // Send to ESP8266
  // Format: SENSOR:temp,humidity,pH,TDS
  String data = "UPLOAD:";
  data += String(airTemp, 1) + ",";
  data += String(humidity, 1) + ",";
  data += String(phValue, 2) + ",";
  data += String(tdsValue, 0);

  Serial.println(data);

  // Debug print
  Serial.print("Sent: ");
  Serial.println(data);
}


// TDS sampling
void sampleTds() {
  static unsigned long lastSampleTime = 0;
  if (millis() - lastSampleTime > 40) {
    lastSampleTime = millis();
    tdsBuffer[tdsIndex++] = analogRead(TDS_PIN);
    if (tdsIndex >= SCOUNT) {
      tdsIndex = 0;
      if (tdsReady == false) {
        tdsReady = true;
      }
    }
  }
}

// Median filter
int getMedian(int *array, int size) {
  int temp[size];
  for (int i = 0; i < size; i++) temp[i] = array[i];

  for (int i = 0; i < size - 1; i++) {
    for (int j = i + 1; j < size; j++) {
      if (temp[j] < temp[i]) {
        int swap = temp[i];
        temp[i] = temp[j];
        temp[j] = swap;
      }
    }
  }
  return temp[size / 2];
}
