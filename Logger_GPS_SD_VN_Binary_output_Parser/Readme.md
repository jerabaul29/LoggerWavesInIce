This is the parser for converting the binary data logged from the VN100 (using the **/Logger_GPS_SD_VN_Binary_output** code on the Arduino board) into a series of CSV files. For each file saved by the Arduino on the SD card, a series of CSV files is genetated. 

- Files with naming in the style *F00379_B* contain data (which data being indicated by the letter).
- Files with naming in the style *F00379_Bt* contain the Arduino timestamps (from the millis() function).

For interpretation of the letter indicating data type, see the header of **/Logger_GPS_SD_VN_Binary_output_Parser**.

It seems that this code has problems with windows. Use either plain Linux (Ubuntu works fine), or Linux subsystem on Windows. The code is Python 2.7. If you have some issues, see through the issue for help:

https://github.com/jerabaul29/LoggerWavesInIce/issues/2

# Note about Python2

This code is Python2 as it is quite old, but Python2 has been depreciated in Ubuntu 20.04. To use, use a virtual environment. For example on my machine running Ubuntu 20.04 (you will need to update paths for them to work on your own machine):

```
~/Desktop/Git/LoggerWavesInIce/Logger_GPS_SD_VN_Binary_output_Parser [master|✔]> sudo apt install virtualenv
[verbose output...]
~/Desktop/Git/LoggerWavesInIce/Logger_GPS_SD_VN_Binary_output_Parser [master|✔]> mkdir -p /home/jrmet/Desktop/VEnvs/p2
~/Desktop/Git/LoggerWavesInIce/Logger_GPS_SD_VN_Binary_output_Parser [master|✔]> virtualenv -p /usr/bin/python2.7 /home/jrmet/Desktop/VEnvs/p2/
created virtual environment CPython2.7.18.candidate.1-64 in 436ms
  creator CPython2Posix(dest=/home/jrmet/Desktop/VEnvs/p2, clear=False, global=False)
  seeder FromAppData(download=False, distro=latest, pip=latest, progress=latest, idna=latest, CacheControl=latest, distlib=latest, wheel=latest, colorama=latest, six=latest, webencodings=latest, pep517=latest, pytoml=latest, contextlib2=latest, setuptools=latest, pyparsing=latest, retrying=latest, pkg_resources=latest, html5lib=latest, msgpack=latest, certifi=latest, requests=latest, chardet=latest, lockfile=latest, ipaddr=latest, urllib3=latest, appdirs=latest, packaging=latest, via=copy, app_data_dir=/home/jrmet/.local/share/virtualenv/seed-app-data/v1.0.1.debian)
  activators BashActivator,CShellActivator,FishActivator,PowerShellActivator,PythonActivator
~/Desktop/Git/LoggerWavesInIce/Logger_GPS_SD_VN_Binary_output_Parser [master|✔]> source /home/jrmet/Desktop/VEnvs/p2/bin/activate
(p2) ~/Desktop/Git/LoggerWavesInIce/Logger_GPS_SD_VN_Binary_output_Parser [master|✔]> pip install crcmod
DEPRECATION: Python 2.7 reached the end of its life on January 1st, 2020. Please upgrade your Python as Python 2.7 is no longer maintained. A future version of pip will drop support for Python 2.7. More details about Python 2 support in pip, can be found at https://pip.pypa.io/en/latest/development/release-process/#python-2-support
Collecting crcmod
  Downloading crcmod-1.7.tar.gz (89 kB)
     |████████████████████████████████| 89 kB 2.1 MB/s 
Building wheels for collected packages: crcmod
  Building wheel for crcmod (setup.py) ... done
  Created wheel for crcmod: filename=crcmod-1.7-py2-none-any.whl size=18498 sha256=69720a61f0b00030522c701e8fc3df859acb6a3f7434cbfd527b16c03f2228de
  Stored in directory: /home/jrmet/.cache/pip/wheels/06/c2/19/2d00b8cea7d9ac6e19d286b0c41cf7a9eb39f64bd21ed43194
Successfully built crcmod
Installing collected packages: crcmod
Successfully installed crcmod-1.7
(p2) ~/Desktop/Git/LoggerWavesInIce/Logger_GPS_SD_VN_Binary_output_Parser [master|✔]> pip install numpy
DEPRECATION: Python 2.7 reached the end of its life on January 1st, 2020. Please upgrade your Python as Python 2.7 is no longer maintained. A future version of pip will drop support for Python 2.7. More details about Python 2 support in pip, can be found at https://pip.pypa.io/en/latest/development/release-process/#python-2-support
Collecting numpy
  Downloading numpy-1.16.6-cp27-cp27mu-manylinux1_x86_64.whl (17.0 MB)
     |████████████████████████████████| 17.0 MB 2.6 MB/s 
Installing collected packages: numpy
Successfully installed numpy-1.16.6
(p2) ~/Desktop/Git/LoggerWavesInIce/Logger_GPS_SD_VN_Binary_output_Parser [master|✔]> python test_process_folder.py 
Processing file: F00294
Processing file: F00379
```
