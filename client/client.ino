
// Network Connection 
#include <SPI.h>
#include <WiFiNINA.h>
#include <WiFiUdp.h>

// HTTP and JSON
#include <ArduinoJson.h>
#include <ArduinoHttpClient.h>

// Time management
#include <RTCZero.h>

RTCZero rtc;

#include "arduino_secrets.h"

#define BATCH_SIZE 50
#define SAMPLE_DELAY 200

/////// Enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;                           // your network key Index number (needed only for WEP)

String device_id = DEVICE_ID;           // Device ID for auth with psql
String device_api_key = DEVICE_API_KEY; // Device KEY for auth with psql


int status = WL_IDLE_STATUS;

WiFiClient wifi;
HttpClient client = HttpClient(wifi, SERV_HOST, SERV_PORT);

void setup() {
  Serial.begin(115200);

  // attempt to connect to WiFi network:
  while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:
    delay(10000);
  }
  
  // you're connected now, so print out the status:
  printWiFiStatus();

  unsigned long epoch;
  int numberOfTries = 0, maxTries = 6;
  do {
    epoch = WiFi.getTime();
    numberOfTries++;
  }
  while ((epoch == 0) && (numberOfTries < maxTries));

  if (numberOfTries > maxTries) {
    Serial.print("NTP unreachable!!");
    while (1);
  }
  else {
    Serial.print("Epoch received: ");
    Serial.println(epoch);
    rtc.setEpoch(epoch);

    Serial.println();
  }
}


void loop() {
  // Get one data batch
  const int capacity = JSON_OBJECT_SIZE(8*BATCH_SIZE+1);
  StaticJsonDocument<capacity> doc;
  JsonArray arr = doc.to<JsonArray>();

  for (int i=0; i<BATCH_SIZE; i++) {
    JsonObject obj = doc.createNestedObject();
    obj["e"] = WiFi.getTime();
    obj["m"] = millis();
    obj["x"] = analogRead(A0);
    obj["y"] = analogRead(A1);
    obj["z"] = analogRead(A3);  // sewing mistake
    obj["t"] = analogRead(A2);  // sewing mistake
    obj["g"] = analogRead(A4);
    obj["h"] = analogRead(A5);
    delay(SAMPLE_DELAY);
  }  

  // serializeJson(doc, Serial);
  sendBatch(&arr);
}


void sendBatch(JsonArray *jsonData){
  Serial.println("making POST request");
  
  String postArgs = "?device_id=" + device_id;
  client.beginRequest();
  client.post("/api/upload"+postArgs);
  client.sendHeader(HTTP_HEADER_CONTENT_TYPE, "application/json");
  client.sendHeader(HTTP_HEADER_CONTENT_LENGTH, measureJson(*jsonData));
  client.sendHeader("X-API-Key", device_api_key);
  client.endRequest();

  String data = "";
  serializeJson(*jsonData, data);
  client.write((const byte*)data.c_str(), data.length());

  // read the status code and body of the response
  int statusCode = client.responseStatusCode();
  String response = client.responseBody();

  Serial.print("POST Status code: ");
  Serial.println(statusCode);
  Serial.print("POST Response: ");
  Serial.println(response);
}


void printWiFiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}
