# Logger waves in ice

This repository contains code, hardware details and explanations about the micro controller based loggers built and used by the UiO mechanics group for measuring waves in ice. All the material is released under the MIT license (see License.txt for more details). This license lets you do anything you want with the content of this repository, as long as you accept that it comes with no warranty. Most of the content of this repository was developped during the PhD of Jean Rabault, with substancial help from laboratory engineer Olav Gundersen and help from PostDoc Graig Sutherland.

I also wrote a blog post discussing this material that you may find useful: http://folk.uio.no/jeanra/Microelectronics/MicrocontrollerBasedLoggers.html

If you find the content of this repository helpful, please consider:

- Contributing to the development of an Open Source community around scientific instrumentation by sharing your own designs, and / or further development effort you would put in this code.

- Refering to our publications related to the development of those instruments.

The loggers we used are based on Arduino Mega boards. They would more generally be compatible after adaptation with most of the Arduino compatible micro controller boards. We chose the Arduino Mega as it features 4 physical serial ports, which was convenient for integrating our sensors.

# Comments and possible further contributions

The loggers built following the materials provided here have proven reliable for field work in the Arctic, and answer well the need we had at UiO when developping them. However, several points could be improved for making the assembly of those loggers easier, and further development of the code cleaner.

Reliable function depends on good construction of the loggers, and in particular of the electronics board used for assembling together all elements of the logger. Since we at UiO built only a small number of loggers and needed a very short development time to be ready for field work, we soldered / assembled those boards by hand in our workshop. This is convenient as it did let us repare, prototype and modify boards within a few hours when those loggers were still prototypes. However this may not be the best solution to go for if you plan on building a small series of similar loggers, without the aim of doing continuous modifications to the hardware. Now that we have obtained a satisfactory result, a nice contribution to this project would be to develop a **CAD version** of the electronics boards, so that PCBs could be ordered directly from suppliers.

The code used for those loggers is not Object Oriented, in particular each sensor needs to be taken care of in (relative) details in the main program to be uploaded on the micro controller. This makes it very easy for beginners to understand how things are working and modify (should I say, hack your way through?) the code, but more experienced coders will find it very frustrating after some time. While it is perfectly possible to further develop / hack on the code to make it fit your needs, **reshaping the code into an Object Oriented library** would be a nice contribution. 

# Folders architecture of the repository

As we progressively built experience about how to perform the measurements we needed, the loggers evolved. We try to keep it visible in the structure of this repository, so that you can replicate the state of any of the loggers we used on the field.

The **Logger_Hardware** folder contains the details about the hardware used. This includes:
- The home-made electronics board used for assembling together all elements of the loggers, which also features a power regulator, MOSFET and voltage divider.
- The battery solution used, including safety PCB.
- The GPS, GPS antenna, SD, Iridium and Iridium antenna modules used.
- Some purely technical details about which casing we used, and how we organised the placement of eveything in it.

The **InitializeEEPROM** folder contains the code for setting the EEPROM memory of the Arduino Mega ready for logging.

The **Logger_GPS_SD_VN** folder contains the code used for performing the measurements in the year 2016.

The **Logger_GPS_SD_VN_Binary_output** folder contains the code used for performing the measurements in the year 2017, for the loggers not featuring an Iridium module (prototype version).

The **Logger_GPS_SD_VN_Binary_output_Parser** folder contains the code for parsing the data generated by the loggers used with a binary output.

The **Logger_GPS_SD_VN_Binary_output_Iridium** folder contains the code used for performing the measurements in the year 2017, for the loggers featuring an Iridium  module (under development).

The **ArduinoMegaExtendedSerialBuffers** folder contains explanations about how to upload the code on the Arduino Mega using extended serial buffers. 

# How to build a similar logger

Steps:

- Initialize the EEPROM memory of the Arduino Mega using the **InitializeEEPROM** sketch.

- Upload the right logger code on the Arduino Mega, using an extended buffer core (see **ArduinoMegaExtendedSerialBuffers** for more details).

- Programm the VN100 IMU, in a way that corresponds to the code uploaded on the Arduino Mega (i.e., ASCII vs binary format, and output properties in the case of the binary format).

- Assemble the logger.

# Estimated cost per logger:

- VN100, thermally calibrated, with cable and connector: ~900$ (note that we use this IMU for waves in ice because the ice motions are very small, typically ~10cm for 10s swells; if you are interested in waves in the open ocean, you could pick a much cheaper IMU).

- GPS breakout: ~40$

- GPS active antenna + connector: ~16$

- SD card breakout: 8$

- SD card 8GB: 10$

- Arduino Mega: 45$

- Small electonics and materials for building the soldered board: 25$

- LiFe prismatic battery (2*3.2V, 40Ah) and PCM: 135$ (note that if you want to perform logging with an instrument you will not recover in milder environment, you will get much better one shot autonomy and price tag just assembling a battery pack from Alkaline batteries).

- Pelican case: 80$

- **Total**: 1259$ (359$ without IMU).

- Optional: Iridium module + active antenna: ~190£

