// initialize the EEPROM gestion for the loggers

#include <EEPROM.h>
// the addresses should correspond to the logger parameters
// address in which stores if the EEPROM has been used to generate file numbers before
int address_init = 0;
// address in which stores the current file numbering
int address_numberReset = 1;

void setup() {
  
  // wait to let the time to open the serial
  delay(5000);
  
  // start serial
  Serial.begin(115200);

  // read the parameters in EEPROM
  int initialized_before = EEPROM.read(address_init);
  long value_before = EEPROMReadlong(address_numberReset); 
  
  Serial.println();
  Serial.print("Content of address_init: ");
  Serial.print(initialized_before);
  
  Serial.println();
  
  Serial.print("Content of address_numberReset: ");
  Serial.print(value_before);
  
  Serial.println();
  
  EEPROM.write(address_init,0);
  EEPROMWritelong(address_numberReset,0);
  
  Serial.println();
  Serial.println("EEPROM reseted!");

}

void loop() {
  
  // nothing to do

}

// This function will write a 4 byte (32bit) long to the eeprom at
// the specified address to address + 3.
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

// This function will take and assembly 4 byte of the Eeprom memory
// in order to form a long variable. 
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
