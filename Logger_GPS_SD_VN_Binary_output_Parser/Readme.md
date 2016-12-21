This is the parser for converting the binary data logged from the VN100 (using the **/Logger_GPS_SD_VN_Binary_output** code on the Arduino board) into a series of CSV files. For each file saved by the Arduino on the SD card, a series of CSV files is genetated. 

- Files with naming in the style *F00379_B* contain data (which data being indicated by the letter).
- Files with naming in the style *F00379_Bt* contain the Arduino timestamps (from the millis() function).

For interpretation of the letter indicating data type, see the header of **/Logger_GPS_SD_VN_Binary_output_Parser**.