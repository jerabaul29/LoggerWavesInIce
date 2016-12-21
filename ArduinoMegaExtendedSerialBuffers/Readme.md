*Note: there can be (and definitely have been in the past) some changes in the architecture of the Arduino project from a version to the next, so you may need to adapt a little bit the explanation presented here depending on the version of the Arduino IDE you are using. However, the main steps should be similar.*

# Arduino Mega with extended serial buffers

In order to avoid risks of buffer overflow, one should extend the serial buffers of the Arduino Mega. This can be done by modifying the core used to build the program uploaded on the board by the Arduino IDE.

Since the Arduino Mega has quite a lot of RAM, one can simply increase the size of all its buffers withoug risks of RAM exhaustion. For this, just create a copy of the Arduino core (avr/cores/arduino, and call it for example avr/cores/arduinoExtendedBuffer), in which the HardwareSerial.h header file is modified to extend the size of the buffers. Modifying the latest version of the Arduino core in this purpose (latest commit of the HardwareSerial.h file on the master branch of the Arduino project on github on 12 December 2016, commit cf0a250) should look like:

```
#if !defined(SERIAL_TX_BUFFER_SIZE)
#if ((RAMEND - RAMSTART) < 1023)
#define SERIAL_TX_BUFFER_SIZE 16
#else
// #define SERIAL_TX_BUFFER_SIZE 64
#define SERIAL_TX_BUFFER_SIZE 128
#endif
#endif
#if !defined(SERIAL_RX_BUFFER_SIZE)
#if ((RAMEND - RAMSTART) < 1023)
#define SERIAL_RX_BUFFER_SIZE 16
#else
// #define SERIAL_RX_BUFFER_SIZE 64
#define SERIAL_RX_BUFFER_SIZE 256
#endif
#endif
```

Create in addition a new board description in the avr/boards.txt file (similarly to what is described in this post for the Arduino UNO: http://folk.uio.no/jeanra/Microelectronics/CustomSizeArduinoBuffer.html):

```
##############################################################

megaExt.name=Arduino Mega or Mega 2560 extended buffer

megaExt.vid.0=0x2341
megaExt.pid.0=0x0010
megaExt.vid.1=0x2341
megaExt.pid.1=0x0042
megaExt.vid.2=0x2A03
megaExt.pid.2=0x0010
megaExt.vid.3=0x2A03
megaExt.pid.3=0x0042

megaExt.upload.tool=avrdude
megaExt.upload.maximum_data_size=8192

megaExt.bootloader.tool=avrdude
megaExt.bootloader.low_fuses=0xFF
megaExt.bootloader.unlock_bits=0x3F
megaExt.bootloader.lock_bits=0x0F

megaExt.build.f_cpu=16000000L
megaExt.build.core=arduinoExtendedBuffer
megaExt.build.variant=mega
# default board  may be overridden by the cpu menu
megaExt.build.board=AVR_MEGA2560
```

This should let you choose the 'Arduino Mega or Mega 2560 extended buffer' board in your Arduino IDE.
