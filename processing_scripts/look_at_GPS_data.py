import numpy as np
import pickle
from scipy import signal
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from geopy.distance import vincenty

path_GPS_data = "/media/jrlab/SAMSUNG/DataJeanAnalysisSvalbardMarch2018/2018-03-23_00:00:00_2018-03-23_05:00:00_GPRMC"

"""
The conclusion is: the GPS position data is not very good. Same effect as observed in 2017. Seems that a lot of noise on the position recorded.
"""

# load the saved data
with open(path_GPS_data, "rb") as crrt_file:
    dict_data_loaded_GPS = pickle.load(crrt_file)

refPosition = (78.223823, 16.530437)
refPositionLat = refPosition[0]
refPositionLon = refPosition[1]

list_IMUs = dict_data_loaded_GPS.keys()[1:]

# with coordinates -------------------------------------------------------------
plt.figure()

for crrt_IMU in list_IMUs:
    list_gps_lat = []
    list_gps_lon = []

    GPRMC_data = dict_data_loaded_GPS[crrt_IMU]

    for crrt_GPS_point in GPRMC_data:
        list_gps_lat.append(crrt_GPS_point.lat)
        list_gps_lon.append(crrt_GPS_point.lon)

    plt.plot(list_gps_lon[0:20], list_gps_lat[0:20], '-o', label=crrt_IMU)

plt.xlabel('Longitude (E)')
plt.ylabel('Latitude (N)')
plt.legend()
plt.show()

plt.figure()

for crrt_IMU in list_IMUs:
    list_gps_lat = []
    list_gps_lon = []

    GPRMC_data = dict_data_loaded_GPS[crrt_IMU]

    for crrt_GPS_point in GPRMC_data:
        list_gps_lat.append(crrt_GPS_point.lat)
        list_gps_lon.append(crrt_GPS_point.lon)

    plt.plot(list_gps_lon, '-o', label=crrt_IMU)

plt.legend()
plt.show()

plt.figure()

for crrt_IMU in list_IMUs:
    list_gps_lat = []
    list_gps_lon = []

    GPRMC_data = dict_data_loaded_GPS[crrt_IMU]

    for crrt_GPS_point in GPRMC_data:
        list_gps_lat.append(crrt_GPS_point.lat)
        list_gps_lon.append(crrt_GPS_point.lon)

    plt.plot(list_gps_lat, '-o', label=crrt_IMU)

plt.legend()
plt.show()

# with vincenty ----------------------------------------------------------------
plt.figure()

for crrt_IMU in list_IMUs:
    list_gps_lat = []
    list_gps_lon = []

    GPRMC_data = dict_data_loaded_GPS[crrt_IMU]

    for crrt_GPS_point in GPRMC_data:
        list_gps_lat.append(crrt_GPS_point.lat)
        list_gps_lon.append(crrt_GPS_point.lon)

    plt.plot(list_gps_lon[0:20], list_gps_lat[0:20], '-o', label=crrt_IMU)

plt.xlabel('Longitude (E)')
plt.ylabel('Latitude (N)')
plt.legend()
plt.show()
