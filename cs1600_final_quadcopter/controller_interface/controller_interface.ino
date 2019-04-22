#include <Adafruit_CC3000.h>
#include <SPI.h>
#include "utility/debug.h"
#include "utility/socket.h"

// Network code adapted from the ChatServer example sketch in the Adafruit CC3000 library
// Input processing code adapted from the SerialEvent Arduino example

// These are the interrupt and control pins
#define ADAFRUIT_CC3000_IRQ 3
// These can be any two pins
#define ADAFRUIT_CC3000_VBAT 5
#define ADAFRUIT_CC3000_CS 10

// Use hardware SPI for the remaining pins
// On an UNO, SCK = 13, MISO = 12, and MOSI = 11
Adafruit_CC3000 cc3000 = Adafruit_CC3000(ADAFRUIT_CC3000_CS, ADAFRUIT_CC3000_IRQ, ADAFRUIT_CC3000_VBAT, SPI_CLOCK_DIVIDER);

#define WLAN_SSID "quadcontrol"
#define WLAN_PASS "password"
// Security can be WLAN_SEC_UNSEC, WLAN_SEC_WEP, WLAN_SEC_WPA or WLAN_SEC_WPA2
#define WLAN_SECURITY WLAN_SEC_WPA2

// TCP port to listen for connections
#define LISTEN_PORT 5555

Adafruit_CC3000_Server commandServer(LISTEN_PORT);

// Default midrange values for pitch, roll, yaw, and throttle
int PITCH_EVEN = 123;
int ROLL_EVEN = 123;
int YAW_EVEN = 123;
int THROT_EVEN = 123;

// Used for processing input
bool readComplete = false;
String valueString = "";

// Control values
int throt = 0;
int pitch = PITCH_EVEN;
int roll = ROLL_EVEN;
int yaw = YAW_EVEN;

void setup() {
  analogWrite(PITCH, pitch);
  analogWrite(ROLL, roll);
  analogWrite(YAW, yaw);
  analogWrite(THROT, throt);
  Serial.begin(115200);
  valueString.reserve(200);
  Serial.println(F("Let's fly a quad!\n")); 
  Serial.print("Free RAM: "); Serial.println(getFreeRam(), DEC);
  
  // Init the server
  Serial.println(F("\nInitializing..."));
  if (!cc3000.begin())
  {
    Serial.println(F("Couldn't begin()! Check your wiring?"));
    while(1);
  }
  
  Serial.print(F("\nAttempting to connect to ")); Serial.println(WLAN_SSID);
  if (!cc3000.connectToAP(WLAN_SSID, WLAN_PASS, WLAN_SECURITY)) {
    Serial.println(F("Failed!"));
    while(1);
  }
   
  Serial.println(F("Connected!"));
  
  Serial.println(F("Request DHCP"));
  while (!cc3000.checkDHCP())
  {
    delay(100);
  }  

  // Display the IP address DNS, Gateway 
  while (!displayConnectionDetails()) {
    delay(1000);
  }
  
  // Can be removed to save memory
  Serial.println(F("\r\nNOTE: This sketch may cause problems with other sketches"));
  Serial.println(F("since the .disconnect() function is never called, so the"));
  Serial.println(F("AP may refuse connection requests from the CC3000 until a"));
  Serial.println(F("timeout period passes.  This is normal behaviour since"));
  Serial.println(F("there isn't an obvious moment to disconnect with a server.\r\n"));

  // Start listening
  commandServer.begin();
  
  Serial.println(F("Listening for connections..."));
}

void loop() {
  // Tasks
  updateFlightValues();
  processString();
  handleNetworkInput();
}

// Outputs the control values
void updateFlightValues() {
  analogWrite(PITCH, pitch);
  analogWrite(ROLL, roll);
  analogWrite(YAW, yaw);
  analogWrite(THROT, throt);
}

// Reads input strings from the client controller
void handleNetworkInput() {
  // Get a client which is connected.
  Adafruit_CC3000_ClientRef client = commandServer.available();
  if (client) {
    // Check if there is data available to read.
    if (client.available() > 0) {
      // Read a byte and write it to all clients.
      uint8_t ch = client.read();
      Serial.println("Read");
      // If the incoming character is a newline set a flag
      if (ch == '\n') {
        readComplete = true;
      } else {
        // Add it to the inputString:
        valueString += (char)(ch);
      }
    }
  } 
}

// Updates the control values
void processString() {
  if (readComplete) {
     if (valueString.equals("unlock")) {
       Serial.println("unlocking");
       throt = 0;
       yaw = 255;
     } else if (valueString.startsWith("t")) {
       valueString = valueString.substring(1);
       unsigned long newValue = valueString.toInt();
       throt = newValue;
     } else if (valueString.startsWith("p")) {
       valueString = valueString.substring(1);
       unsigned long newValue = valueString.toInt();
       pitch = newValue;
     } else if (valueString.startsWith("r")) {
       valueString = valueString.substring(1);
       unsigned long newValue = valueString.toInt();
       roll = newValue;
     } else if (valueString.startsWith("y")) {
       valueString = valueString.substring(1);
       unsigned long newValue = valueString.toInt();
       yaw = newValue;
     }
     readComplete = false;
     valueString = "";
  }
}

// Get console input
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      readComplete = true;
    } else {
      valueString += inChar;
    }
  }
}

// Method from example for displaying connection information
bool displayConnectionDetails(void)
{
  uint32_t ipAddress, netmask, gateway, dhcpserv, dnsserv;
  
  if(!cc3000.getIPAddress(&ipAddress, &netmask, &gateway, &dhcpserv, &dnsserv))
  {
    Serial.println(F("Unable to retrieve the IP Address!\r\n"));
    return false;
  }
  else
  {
    Serial.print(F("\nIP Addr: ")); cc3000.printIPdotsRev(ipAddress);
    Serial.print(F("\nNetmask: ")); cc3000.printIPdotsRev(netmask);
    Serial.print(F("\nGateway: ")); cc3000.printIPdotsRev(gateway);
    Serial.print(F("\nDHCPsrv: ")); cc3000.printIPdotsRev(dhcpserv);
    Serial.print(F("\nDNSserv: ")); cc3000.printIPdotsRev(dnsserv);
    Serial.println();
    return true;
  }
}
