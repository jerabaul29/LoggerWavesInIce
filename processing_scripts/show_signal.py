import numpy as np
import pickle
from scipy import signal
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
import math
import scipy.optimize
from uncertainties import ufloat
import scipy
from scipy import signal

# %matplotlib qt


class BandPass(object):
    """A class to perform bandpass filtering using Butter filter."""

    def __init__(self, lowcut=0.05, highcut=0.25, fs=10.0, order=3):
        """lowcut, highcut and fs are in Hz."""
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        self.b, self.a = butter(order, [low, high], btype='band')

    def filter_data(self, data):
        """filter the data."""

        result = lfilter(self.b, self.a, data)

        return(result)

# plt.rc('text', usetex=True)

# path_IMU_data = "/media/jrlab/SAMSUNG/DataJeanAnalysisSvalbardMarch2018/2018-03-23_00:00:00_2018-03-23_05:00:00_IMU_TNEDXYZ"
# path_IMU_data = "/media/jrlab/SAMSUNG/DataJeanAnalysisSvalbardMarch2018_segments_14_to_18/2018-03-23_00:00:00_2018-03-23_15:00:00_IMU_TNEDXYZ"
path_IMU_data = "/home/jrlab/Desktop/Data/DataSvalbard2019/labeled_data/data_label.pkl_IMU_TNEDXYZ"

FS = 10

# load the saved data
with open(path_IMU_data, "rb") as crrt_file:
    dict_data_loaded_IMU = pickle.load(crrt_file)

list_IMUs_for_plot = ['1', '5', 'F1']

for crrt_IMU in list_IMUs_for_plot:
    size_data = np.size(dict_data_loaded_IMU[crrt_IMU].D)
    print("IMU {}".format(crrt_IMU))
    print("Number of points: {}".format(size_data))
    print("Corresponding duration (hr): {}".format(size_data / 10.0 / 3600))
    print("Corresponding numbe of 15 minutes files read: {}".format(size_data / 10 / 3600 * 4.0))

crrt_IMU = "5"
start_point = 0
duration =  5 * 60
end_point = start_point + duration * FS

plt.figure()
plt.plot(dict_data_loaded_IMU[crrt_IMU].T[start_point:end_point], dict_data_loaded_IMU[crrt_IMU].D[start_point:end_point])
plt.show()

# the same, but with filtered signal
band_pass_filter = BandPass(lowcut=0.03, highcut=0.25, order=2)
filtered_signal = band_pass_filter.filter_data(dict_data_loaded_IMU[crrt_IMU].D)


plt.figure()
# plt.plot(dict_data_loaded_IMU[crrt_IMU].T[start_point:end_point], dict_data_loaded_IMU[crrt_IMU].D[start_point:end_point] - np.mean(dict_data_loaded_IMU[crrt_IMU].D[start_point:end_point]))
plt.plot(dict_data_loaded_IMU[crrt_IMU].T[start_point:end_point], filtered_signal[start_point:end_point])
plt.show()

band_pass_filter = BandPass(order=2)
filtered_signal = band_pass_filter.filter_data(dict_data_loaded_IMU[crrt_IMU].D)


plt.figure()
# plt.plot(dict_data_loaded_IMU[crrt_IMU].T[start_point:end_point], dict_data_loaded_IMU[crrt_IMU].D[start_point:end_point] - np.mean(dict_data_loaded_IMU[crrt_IMU].D[start_point:end_point]))
plt.plot(dict_data_loaded_IMU[crrt_IMU].T[start_point:end_point], filtered_signal[start_point:end_point])
plt.show()

end = True
