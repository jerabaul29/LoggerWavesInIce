/*
Code for logger working with a VN100 IMU outputing IMU data in ASCII

PORTS CONFIGURATION:
Use debugging on Serial
Use GPS on       Serial1
Use VN100 on     Serial2
Use SD card on   SPI

FEATURES
Logging of GPS
Logging of IMU
Saving on SD card
Use of a watchdog
Segmentation in several data files on the SD card
Battery voltage is available through voltage divider on pin A7 (assembing board feature)
Sensors can be shut off by MOSFET, on pin D2 (assembling board feature)

NOTE:
when the file is closed by losing power
rather than closing it nicely, data can be lost.
I.e. risk to loose the last data set. This is not a problem when 15 minutes 
files are used

NOTE ON VN100 OUTPUT:
This will work with the VN100 output:
57600 bauds
parameters so that header is:
fa 14 3e 00 3a 00

NOTE:
Keys for indicating the nature of the line / dataframe to come when logging on the SD card:
- S,: message about the Start of the file: booting, or new file timer
- M,: timestamp in Arduino internal clock reference frame
- R,: raw data about battery level
- C,: converted data about battery level
- B,: binary data
- $G: start of GPS data. When parsing, this is turned into a _G and _Gt file. Problematic lines (ie lines for which parsing
do not work) are stored in a _P (and timestamps in a _Pt) file.
*/

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// include the libraries
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#include <SPI.h>
#include <SD.h>
#include <Adafruit_GPS.h>
// note: we do not use software serial
// but it seems to be necessary for initializing
// Adafruit_GPS library
#include <SoftwareSerial.h>
#include <avr/wdt.h>
#include <EEPROM.h>

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// print to serial
// if we want to print to serial for debugging
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// if we want to print to serial
// print to serial for debugging; 0 is no debugging output on Serial, 1 is
// debugging output on Serial
#define SERIAL_PRINT 0

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// MOSFET for switching on / off power to the VN and GPS
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#define PIN_MOSFET 2

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// Voltage divider for measuring remaining battery
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#define PIN_VOLTAGE A7
// voltage divider factor
#define DIVIDER_FACTOR 0.6666
// threshold value for shutting off the logger on low battery
// disable: use the battery until the end: 0.0
// safe use: use the battery up to some point: 5.5V
#define THRESHOLD_VALUE 0.0
//
int sensorVoltageValue = 0;
float batteryVoltage   = 0.;
String stringMessageVoltage;

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// SD card
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// slave select on Arduino Mega
// this is for the SPI driven SD card
const int chipSelect = 53;
// name of the file on which writting in the SD card library type
File dataFile;

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// GPS def
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// config GPS chip and instance creation
#define SERIAL_GPS Serial1
Adafruit_GPS GPS(&SERIAL_GPS);
// GPS string
String dataStringGPS = "";

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// IMU def
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#define SERIAL_IMU Serial2
// the header is:
// fa 14 3e 00 3a 00
// bytes:
// 0  1  2  3  4  5
#define byte0 0xfa
#define byte1 0x14
#define byte2 0x3e
#define byte3 0x00
#define byte4 0x3a
#define byte5 0x00
// the state of the variable checking if received a full header is:
// 255 (nothing received), 0 (byte0 received), 1 (byte0 and byte1 received consecutively),
// 2 (byte0 and byte1 and byte2 received consecutively), etc
byte state_header = 255;
// we define the buffer of bytes to write to the SD card; it is over twice as long as the
// binary message we expect to avoid problems with one message lost
#define lengthBufferIMU 275
byte binaryIMUBuffer[lengthBufferIMU] = {0};
byte position_buffer = 0;
// IMU string
String dataStringIMU = "";
String dataStringTimeStamp = "";
// length of a binary data frame
#define lengthIMUBinarDataFrame 124

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// filename gestion
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// filename, will be modified based on EEPROM data for saving on several files
char currentFileName[] = "F00000";
int nbrOfZeros = 5; // number of zeros after the letter in the name convention
// time in milliseconds after which write to a new file
//                      900 s is 900 000 milliseconds is 15 minutes
#define time_WNF 900000
//#define time_WNF 10000
// timer for writting new file
unsigned long timer_WNF = 1;

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// EEPROM gestion
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// address in which stores if the EEPROM has been used to generate file numbers before
int address_init = 0;
// address in which stores the current file numbering
int address_numberReset = 1;


// setup --------------------------------------------------------------------------------------
void setup() {

  // let the time to open the serial if needed %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  delay(5000);

  // enable watchdog, if 8 seconds hang %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  wdt_enable(WDTO_8S);
  wdt_reset();

  // init for blinking %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  pinMode(13, OUTPUT);
  digitalWrite(13,LOW);

  // init MOSFET pin %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  pinMode(PIN_MOSFET, OUTPUT);
  // by default, put on sensors
  // this is needed to go through setup
  digitalWrite(PIN_MOSFET, HIGH);

  // EEPROM check %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  int EEPROM_ready = EEPROM.read(address_init);

  if (not(EEPROM_ready==1)){
    // initialize
    EEPROM.write(address_init,1);
    EEPROMWritelong(address_numberReset,0);
  }

  wdt_reset();

  // open serial %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

  #if SERIAL_PRINT
  // Open serial communications and wait for port to open:
  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect.
  }
  Serial.println();
  Serial.println();
  Serial.println("Booting");
  // check if everyhting is normal with Mega speed
  int time1 = millis();
  Serial.println();
  Serial.print("Time1: ");
  Serial.print(time1);
  time1 = millis();
  Serial.println();
  Serial.print("Time2: ");
  Serial.print(time1);
  Serial.println();
  #endif

  wdt_reset();

  // setup SD card %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

  // see if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) {
    #if SERIAL_PRINT
    Serial.println("Card failed, or not present");
    #endif
    // blink to indicate failure
    blinkLED();
  }
  #if SERIAL_PRINT
  Serial.println("card initialized.");
  #endif

  wdt_reset();

  // setup GPS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  delay(250);

  // 9600 NMEA is the default baud rate for Adafruit MTK GPS's- some use 4800
  GPS.begin(9600);

  // uncomment this line to turn on RMC (recommended minimum) and GGA (fix data) including altitude
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  // uncomment this line to turn on only the "minimum recommended" data
  // GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCONLY);

  // Set the update rate
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);   // 1 Hz update rate
  GPS.sendCommand(PMTK_API_SET_FIX_CTL_1HZ);
  // For the parsing code to work nicely and have time to sort thru the data, and
  // print it out we don't suggest using anything higher than 1 Hz

  // Request updates on antenna status, comment out to keep quiet
  // GPS.sendCommand(PGCMD_ANTENNA);

  delay(1000);

  // Ask for firmware version
  // SERIAL_GPS.println(PMTK_Q_RELEASE);

  #if SERIAL_PRINT
  Serial.println("GPS initialized");
  #endif

  wdt_reset();

  // setup IMU %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

  // here, use the VN100

  // on port Serial2 of the Mega (see define statement)
  SERIAL_IMU.begin(57600);
  initIMUBuffer();

  #if SERIAL_PRINT
  Serial.println(F("Init VN100 on Serial 2"));
  #endif

  wdt_reset();

  // end of the setup %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

  #if SERIAL_PRINT
  Serial.println();
  Serial.println("----- End setup -----");
  Serial.println();
  #endif

  // update the name of the file to write on %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

  // update the EEPROM
  // name of the current file on which writting on the SD card, print that
  // booted from beginning, print battery state
  UpdateCurrentFile();
  dataFile.println("S,Booting from beginning!\n");
  CheckVoltage();

  // flush all buffers to avoid too much garbage %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  delay(1000);

  while (SERIAL_GPS.available()>0){
    GPS.read();
  }

  while (SERIAL_IMU.available()>0){
    SERIAL_IMU.read();
  }

  // ready to start the logging %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  wdt_reset();

}

void loop() {

  // add a small delay to avoid conflicts when reading several
  // ports at possibly high frequency
  delayMicroseconds(10);

  wdt_reset();

  // GPS stuff %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

  // check at each loop if new information from the GPS
  while (SERIAL_GPS.available()>0){

    char c_GPS = GPS.read();

    if (c_GPS=='\n'){

      // reached the end of a string: time to log

      // add millis informations
      dataStringGPS += "\nM,";
      dataStringGPS += String(millis());

      // SD post
      postSD(dataStringGPS);

      // re initialize the logging string
      dataStringGPS = "";

    }
    else{
      dataStringGPS += c_GPS;
    }

  }

  // IMU stuff %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

  // check at each loop if new information from the IMU
  while (SERIAL_IMU.available()>0){

    byte byte_IMU = SERIAL_IMU.read();
    binaryIMUBuffer[position_buffer] = byte_IMU;
    position_buffer = (position_buffer + 1) % lengthBufferIMU;

    if (checkHeaderIMU(byte_IMU)){
      #if SERIAL_PRINT
      Serial.println();
      Serial.println("Reached a new IMU header end");
      #endif

      postSD_binary(binaryIMUBuffer, lengthIMUBinarDataFrame);

      initIMUBuffer();
    }

  }

}

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// check if received a full IMU header
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
bool checkHeaderIMU(byte byte_IMU){

  if (state_header == 255){
    if (byte_IMU == byte0){
      state_header = 0;
      #if SERIAL_PRINT
      Serial.println();
      Serial.print("Received byte0 ");
      Serial.print(byte_IMU, HEX);
      #endif
    }

    else{
      #if SERIAL_PRINT
      Serial.print(byte_IMU, HEX);
      Serial.print(" ");
      #endif

      return false;

    }
  }

  else if (state_header == 0){
    if (byte_IMU == byte1){
      state_header = 1;
      #if SERIAL_PRINT
      Serial.println();
      Serial.print("Received byte1 ");
      Serial.print(byte_IMU, HEX);
      #endif
    }
    else{
      state_header = 255;
      #if SERIAL_PRINT
      Serial.println();
      Serial.print("Received wrong byte!");
      #endif
    }
  }

  else if (state_header == 1){
    if (byte_IMU == byte2){
      state_header = 2;
      #if SERIAL_PRINT
      Serial.println();
      Serial.print("Received byte2 ");
      Serial.print(byte_IMU, HEX);
      #endif
    }
    else{
      state_header = 255;
      #if SERIAL_PRINT
      Serial.println();
      Serial.print("Received wrong byte!");
      #endif
    }
  }

  else if (state_header == 2){
    if (byte_IMU == byte3){
      state_header = 3;
      #if SERIAL_PRINT
      Serial.println();
      Serial.print("Received byte3 ");
      Serial.print(byte_IMU, HEX);
      #endif
    }
    else{
      state_header = 255;
      #if SERIAL_PRINT
      Serial.println();
      Serial.print("Received wrong byte!");
      #endif
    }
  }

  else if (state_header == 3){
    if (byte_IMU == byte4){
      state_header = 4;
      #if SERIAL_PRINT
      Serial.println();
      Serial.print("Received byte4 ");
      Serial.print(byte_IMU, HEX);
      #endif
    }
    else{
      state_header = 255;
      #if SERIAL_PRINT
      Serial.println();
      Serial.print("Received wrong byte!");
      #endif
    }
  }

  else if (state_header == 4){
    if (byte_IMU == byte5){

      state_header = 255;

      #if SERIAL_PRINT
      Serial.println();
      Serial.print("Received byte5 ");
      Serial.print(byte_IMU, HEX);
      Serial.println();
      #endif

      return true;

    }
    else{
      state_header = 255;
      #if SERIAL_PRINT
      Serial.println();
      Serial.print("Received wrong byte!");
      #endif
    }
  }

  return false;

}

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// initialize the IMU binary buffer to make it ready to a new string to log
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
void initIMUBuffer(){
  binaryIMUBuffer[0] = byte0;
  binaryIMUBuffer[1] = byte1;
  binaryIMUBuffer[2] = byte2;
  binaryIMUBuffer[3] = byte3;
  binaryIMUBuffer[4] = byte4;
  binaryIMUBuffer[5] = byte5;
  position_buffer = 6;

  #if SERIAL_PRINT
  Serial.println("Initialized binary buffer IMU");
  #endif
}

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// LED 13 blink
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// make led 13 on the board blink continuously to report fault
void blinkLED(){
  while (1){
    digitalWrite(13, HIGH);   // turn the LED on
    delay(100);              // wait for a second
    digitalWrite(13, LOW);    // turn the LED
    delay(100);              // wait for a second
  }
}

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// log a string on the SD card
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
void postSD(String dataStringPost){

  // note: delays are here to avoid conflicts on using the SD card
  // when using it at high frequency

  #if SERIAL_PRINT
  unsigned long startLog = millis();
  Serial.println();
  Serial.println("Start post...");
  Serial.print("Time log beginning: ");
  Serial.println(startLog);
  #endif

  // decide if time to write to a new file
  if (millis() - timer_WNF > time_WNF){
    // reset timer
    timer_WNF = millis();
    #if SERIAL_PRINT
    Serial.println("Update file name because timer");
    #endif
    UpdateCurrentFile();
    dataFile.println("S,New file created (timer)\n");
    CheckVoltage();
  }

  // if the file is available, write to it:
  if (dataFile) {
    dataStringPost += '\n';
    dataFile.println(dataStringPost);

    delay(5);

    #if SERIAL_PRINT
    Serial.println("post success, content:");
    Serial.print(dataStringPost);
    #endif
  }
  // if the file isn't open, pop up an error:
  // and reboot
  else {
    #if SERIAL_PRINT
    Serial.println("post failure");
    #endif
    while(1){
      // do nothing watchdog fires
    }
  }

  #if SERIAL_PRINT
  unsigned long endLog = millis();
  Serial.print("Time log end: ");
  Serial.println(endLog);
  Serial.print("Time log delay: ");
  Serial.println(endLog-startLog);
  #endif

}

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// log binary buffer on the SD card
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
void postSD_binary(byte* dataBufferPost, byte numberOfBytesPost){

  // note: delay are here to avoid conflicts on using the SD card
  // when using it at high frequency

  // take away the buffer at the end
  //numberOfBytesPost -= 6;

  String stringTimePostBinary = "\nM,";
  stringTimePostBinary += String(millis());
  stringTimePostBinary += "\n";

  #if SERIAL_PRINT
  unsigned long startLog = millis();
  Serial.println();
  Serial.println("Start post binary...");
  Serial.print("Time log binary beginning: ");
  Serial.println(startLog);
  Serial.print("Position binary buffer: ");
  Serial.println(numberOfBytesPost);
  #endif

  // decide if time to write to a new file
  if (millis() - timer_WNF > time_WNF){
    // reset timer
    timer_WNF = millis();
    #if SERIAL_PRINT
    Serial.println("Update file name because timer");
    #endif
    UpdateCurrentFile();
    dataFile.println("S,New file created (timer)\n");
    CheckVoltage();
  }

  // if the file is available, write to it:
  if (dataFile) {
    dataFile.println("B,\n");
    dataFile.write(dataBufferPost, numberOfBytesPost);
    dataFile.println(stringTimePostBinary);
    delay(5);
    #if SERIAL_PRINT
    Serial.println("post binary success, content:");
    for (int ind_buffer=0; ind_buffer<numberOfBytesPost; ind_buffer++){
      Serial.print(dataBufferPost[ind_buffer], HEX);
      Serial.print(" ");
    }
    #endif
  }
  // if the file isn't open, pop up an error:
  // and reboot
  else {
    #if SERIAL_PRINT
    Serial.println("post binary failure");
    #endif
    while(1){
      // do nothing watchdog fires
    }
  }

  #if SERIAL_PRINT
  unsigned long endLog = millis();
  Serial.println();
  Serial.print("Time log binary end: ");
  Serial.println(endLog);
  Serial.print("Time log binary delay: ");
  Serial.println(endLog-startLog);
  Serial.println();
  #endif
}

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// reads from EEPROM the name of the next file on which to write and updates the EEPROM
// open the new current file
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
void UpdateCurrentFile(){

  // note: could be problem at initialization in the setup loop, no file opened yet
  // but the library is handling the exception right
  // close current file
  delay(5);
  dataFile.close();
  delay(5);

  // read the current file number in EEPROM
  long value_before_fileIndex = EEPROMReadlong(address_numberReset);

  // update it by increasing by 1. This is the new file number to write on
  long new_value_fileIndex = value_before_fileIndex + 1;
  EEPROMWritelong(address_numberReset,new_value_fileIndex);

  // generate the string to put as the file numbering
  String str_index = String(new_value_fileIndex);
  int str_length = str_index.length();

  // put the characters of the name at the right place
  for (int ind_rank = 0; ind_rank < str_length; ind_rank++){
    int i_rank = nbrOfZeros + ind_rank - str_length + 1;
    currentFileName[i_rank] = str_index[ind_rank];
  }

  #if SERIAL_PRINT
  Serial.print("str_rank: ");
  Serial.println(str_index);
  Serial.print("File name: ");
  Serial.println(currentFileName);
  #endif

  delay(5);
  // open the file. only one file can be open at a time,
  dataFile = SD.open(currentFileName, FILE_WRITE);
  delay(5);
}

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// measure the voltage of the battery
// log it
// it the voltage is too low, take action
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
void CheckVoltage(){

  sensorVoltageValue = analogRead(PIN_VOLTAGE);
  // first value may be garbage; discard
  sensorVoltageValue = analogRead(PIN_VOLTAGE);
  // version without calibration, may be dangerous...
  batteryVoltage = 5.0/1024*float(sensorVoltageValue)/DIVIDER_FACTOR;

  #if SERIAL_PRINT
  Serial.println();
  Serial.print("Digital in voltage: ");
  Serial.print(sensorVoltageValue);
  Serial.println();
  Serial.print("Battery voltage (no calib.): ");
  Serial.print(batteryVoltage);
  Serial.println();
  #endif

  stringMessageVoltage = "";
  stringMessageVoltage += "R,";
  stringMessageVoltage += String(sensorVoltageValue);
  stringMessageVoltage += "\nC,";
  stringMessageVoltage += String(batteryVoltage);
  stringMessageVoltage += "\nM,";
  stringMessageVoltage += String(millis());

  // (maybe) log the battery level?
  postSD(stringMessageVoltage);

  if (batteryVoltage < THRESHOLD_VALUE){

    postSD("Err,SHUT LOW VOLTAGE!!");

    // close the file
    dataFile.close();
    // battery is low!
    // shut off the sensors
    digitalWrite(PIN_MOSFET, LOW);

    // print something on serial if possible
    #if SERIAL_PRINT
    Serial.println();
    Serial.print("SHUTTING OFF, LOW VOLTAGE!!");
    Serial.println();
    #endif

    // NOTE: could add some code here to go for example to a 15 minutes sleep

  }
  else {
    // everything is fine. Put up if was not before
    digitalWrite(PIN_MOSFET, HIGH);
  }
}

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// Write a 4 byte (32bit) long to the eeprom splitted on 4 bytes
// at the specified address up to address + 3
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
void EEPROMWritelong(int address, long value)
{
  //Decomposition from a long to 4 bytes by using bitshift.
  //One = Most significant -> Four = Least significant byte
  byte four = (value & 0xFF);
  byte three = ((value >> 8) & 0xFF);
  byte two = ((value >> 16) & 0xFF);
  byte one = ((value >> 24) & 0xFF);

  //Write the 4 bytes into the eeprom memory.
  EEPROM.write(address, four);
  EEPROM.write(address + 1, three);
  EEPROM.write(address + 2, two);
  EEPROM.write(address + 3, one);
}

// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// read 4 bytes of memory from the EEPROM (address up to address + 4)
// assemble the 4 bytes to form a long variable
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
long EEPROMReadlong(long address)
{
  //Read the 4 bytes from the eeprom memory.
  long four = EEPROM.read(address);
  long three = EEPROM.read(address + 1);
  long two = EEPROM.read(address + 2);
  long one = EEPROM.read(address + 3);

  //Return the recomposed long by using bitshift.
  return ((four << 0) & 0xFF) + ((three << 8) & 0xFFFF) + ((two << 16) & 0xFFFFFF) + ((one << 24) & 0xFFFFFFFF);
}
