This is a modified version of the code used in 2016, that implements one solution that can be used to perform logging of binary data from the VN100. This could be adapted to log other binary outputs. 

---------------------------------------------------------------
This logger uses:
- the VN100 with binary output
- the GPS with usual serial output
---------------------------------------------------------------

---------------------------------------------------------------
The configuration of the VN100 is:

Baud rate      : 57600
Async          : NoOutput
Binary output 1: 
    Async mode    : Serial Port 1
    Rate dividor  : 80
    Common group  : None
    IMU group     : UncompensatedMag
                    UncompensatedAccel
                    UncompensatedGyro
                    Temp
                    Press
    Attitude group: Yaw Pitch Roll
                    DCM
                    MagNed
                    AccelNed
    IMU filtering : 80
 
 This corresponds to the binary header (in HEX):
 fa 14 3e 00 3a 00
 
 The length of the message is (in byte): 123
 
 Note that the post can have in addition an
 end of line marker (in HEX):
 0a 0d
 ---------------------------------------------------------------
 
 ---------------------------------------------------------------
 To examine the content of the SD card on Linux computer,
 use for example xxd:
 
 tail -x FileName | head -y | xxd
 ---------------------------------------------------------------
