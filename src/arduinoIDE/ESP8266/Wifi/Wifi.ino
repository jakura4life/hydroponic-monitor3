#include <ESP8266WiFi.h>

void setup()
{
  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect
  }
  delay(1000); // optional brief delay
  
  Serial.println();
  Serial.print("MAC Address: ");
  Serial.println(WiFi.macAddress());
  WiFi.begin("network-name", "pass-to-network");

  WiFi.begin("ASK4 Wireless (802.1x)",)
}

void loop() {}