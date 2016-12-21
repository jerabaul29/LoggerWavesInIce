/*
This is a simple script for testing the IdidiumSBD library with the RockBlock7
- RockBlock7        to    Arduino Mega
- Rockblock7 OnOff  to    Mega 53
- Rockblock7 GND    to    Mega GND
- Rockblock7 5vIn   to    Mega 5V
- Rockblock7 TXD    to    Mega TX1
- Rockblock7 RXD    to    Mega RX1
This means that the D in RXD and TXD means 'Device', i.e. RX of the device (Mega)
instead of RX of the host (Rockblock7)

NOTE: Test on open air
NOTE: implement a version that lets the logging continue while blocking to transmit GPS
*/

#include "IridiumSBD.h"

#define SERIAL_PRINT 1

// Iridium module %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#define PIN_ONOFF 53
#define SERIAL_IRIDIUM Serial1
IridiumSBD isbd(SERIAL_IRIDIUM, PIN_ONOFF);   // RockBLOCK SLEEP pin on 10
int signalQuality = 255;

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
void setup() {
  delay(5000);

  // Start the serial port for debugging
  #if SERIAL_PRINT
  Serial.begin(115200);
  Serial.println("-- Starting Serial");
  #endif

  // Iridium setup %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  #if SERIAL_PRINT
  Serial.println("-- Starting Iridium SBD object");
  #endif
  SERIAL_IRIDIUM.begin(19200);

  #if SERIAL_PRINT
  Serial.println("-- Attaching Serial to Iridium SBD");
  isbd.attachConsole(Serial);
  isbd.attachDiags(Serial);
  #endif

  #if SERIAL_PRINT
  Serial.println("-- Set power profile");
  #endif
  isbd.setPowerProfile(1); // set to low power configuration

  #if SERIAL_PRINT
  Serial.println("-- Call begin method");
  #endif
  isbd.begin();            // Wake up and prepare to communicate

  #if SERIAL_PRINT
  Serial.println("-- Query signal quality");
  #endif
  isbd.getSignalQuality(signalQuality);

  // test of sleep and wake up %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  #if SERIAL_PRINT
  Serial.println("-- Iridium to sleep and wait 5 secs");
  #endif
  isbd.sleep();

  delay(5000);

  #if SERIAL_PRINT
  Serial.println("-- Call begin method");
  #endif
  isbd.begin();


}

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
void loop() {

  #if SERIAL_PRINT
  if (Serial.available() > 0){
    char command = Serial.read();

    if (command == 'Q'){
      #if SERIAL_PRINT
      Serial.println("-- Query signal qualit");
      #endif
      isbd.getSignalQuality(signalQuality);
    }

    else if (command == 'S'){
      #if SERIAL_PRINT
      Serial.println("-- Send a text string");
      #endif
      isbd.sendSBDText("Hello!");
    }

    else if (command == 'B'){
      #if SERIAL_PRINT
      Serial.println("-- Send a binary data chunk");
      #endif
      uint8_t s[6] = {0xfa, 0x14, 0x3e, 0x00, 0x3a, 0x00};
      isbd.sendSBDBinary(s, 6);
    }

  }
  #endif

}
