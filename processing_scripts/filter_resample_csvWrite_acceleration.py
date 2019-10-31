from __future__ import print_function
import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
import datetime

# TODO: maybe would be cleaner to put this as functions rather than script


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


path_IMU_data = "/home/jrlab/Desktop/Data/Data_For_Aleksey_Harbor_2019/Out/3/_IMU_TNEDXYZ"
path_output = "/home/jrlab/Desktop/Data/Data_For_Aleksey_Harbor_2019/Out/3/_IMU_TNEDXYZ.csv"

# load the saved data
with open(path_IMU_data, "rb") as crrt_file:
    dict_data_loaded_IMU = pickle.load(crrt_file)

list_IMUs_for_plot = ["3"]

for crrt_IMU in list_IMUs_for_plot:
    size_data = np.size(dict_data_loaded_IMU[crrt_IMU].D)
    print("IMU {}".format(crrt_IMU))
    print("Number of points: {}".format(size_data))
    print("Corresponding duration (hr): {}".format(size_data / 10.0 / 3600))
    print("Corresponding numbe of 15 minutes files read: {}".format(size_data / 10 / 3600 * 4.0))

dict_filtered_resampled_data = {}
FS = 10
band_pass_filter = BandPass(lowcut=0.03, highcut=0.25, order=2)
str_time_min = "2019-04-02 09:30:00.000"
time_min = datetime.datetime.strptime(str_time_min, "%Y-%m-%d %H:%M:%S.%f")
time_max = datetime.datetime.strptime("2019-04-02 14:00:00.000", "%Y-%m-%d %H:%M:%S.%f")

time_base_start = 0
time_base_duration = (time_max - time_min).total_seconds() - time_base_start
time_base = np.arange(start=time_base_start, stop=time_base_duration, step=1.0 / FS)

for crrt_IMU in list_IMUs_for_plot:

    print("Look at instrument {}".format(crrt_IMU))

    acc_D_filtered = band_pass_filter.filter_data(dict_data_loaded_IMU[crrt_IMU].D)
    acc_N_filtered = band_pass_filter.filter_data(dict_data_loaded_IMU[crrt_IMU].N)
    acc_E_filtered = band_pass_filter.filter_data(dict_data_loaded_IMU[crrt_IMU].E)
    acc_X_filtered = band_pass_filter.filter_data(dict_data_loaded_IMU[crrt_IMU].X)
    acc_Y_filtered = band_pass_filter.filter_data(dict_data_loaded_IMU[crrt_IMU].Y)
    acc_Z_filtered = band_pass_filter.filter_data(dict_data_loaded_IMU[crrt_IMU].Z)
    Yaw_filtered = band_pass_filter.filter_data(dict_data_loaded_IMU[crrt_IMU].Yaw)
    Pitch_filtered = band_pass_filter.filter_data(dict_data_loaded_IMU[crrt_IMU].Pitch)
    Roll_filtered = band_pass_filter.filter_data(dict_data_loaded_IMU[crrt_IMU].Roll)

    time_sec_since_time_min = []

    for crrt_timestamp in dict_data_loaded_IMU[crrt_IMU].T:
        time_sec_since_time_min.append((crrt_timestamp - time_min).total_seconds())

    time_sec_since_time_min = np.array(time_sec_since_time_min)
    delta_time = time_sec_since_time_min[1:] - time_sec_since_time_min[0:-1]
    delta_time_anomaly = delta_time - 0.1
    missing_points = np.where(delta_time_anomaly > 0.06)
    number_missing_points = np.sum(delta_time_anomaly[missing_points])
    total_number_points = time_sec_since_time_min.size
    percentage_missing_points = number_missing_points * 100.0 / total_number_points

    print("percentage missing points: {}".format(percentage_missing_points))

    acc_D_filtered_resampled = np.interp(time_base, time_sec_since_time_min, acc_D_filtered)
    acc_N_filtered_resampled = np.interp(time_base, time_sec_since_time_min, acc_N_filtered)
    acc_E_filtered_resampled = np.interp(time_base, time_sec_since_time_min, acc_E_filtered)
    acc_X_filtered_resampled = np.interp(time_base, time_sec_since_time_min, acc_X_filtered)
    acc_Y_filtered_resampled = np.interp(time_base, time_sec_since_time_min, acc_Y_filtered)
    acc_Z_filtered_resampled = np.interp(time_base, time_sec_since_time_min, acc_Z_filtered)
    Yaw_filtered_resampled = np.interp(time_base, time_sec_since_time_min, Yaw_filtered)
    Pitch_filtered_resampled = np.interp(time_base, time_sec_since_time_min, Pitch_filtered)
    Roll_filtered_resampled = np.interp(time_base, time_sec_since_time_min, Roll_filtered)

    plt.figure()
    plt.plot(time_sec_since_time_min, acc_D_filtered, label="filtered D")
    plt.plot(time_base, acc_D_filtered_resampled, label="filtered resampled D")
    plt.plot(time_base, acc_N_filtered_resampled, label="filtered resampled N")
    plt.plot(time_base, acc_E_filtered_resampled, label="filtered resampled E")
    # plt.xlim([3600 * 10 - 120, 3600 * 10 + 120])
    ampl_acc_plot = 0.01
    # plt.ylim([-ampl_acc_plot, ampl_acc_plot])
    plt.legend()
    plt.tight_layout()
    plt.show()

    plt.figure()
    plt.plot(time_sec_since_time_min, acc_D_filtered, label="filtered D")
    plt.plot(time_base, acc_X_filtered_resampled, label="filtered resampled X")
    plt.plot(time_base, acc_Y_filtered_resampled, label="filtered resampled Y")
    plt.plot(time_base, acc_Z_filtered_resampled, label="filtered resampled Z")
    # plt.xlim([3600 * 10 - 120, 3600 * 10 + 120])
    ampl_acc_plot = 0.01
    # plt.ylim([-ampl_acc_plot, ampl_acc_plot])
    plt.legend()
    plt.tight_layout()
    plt.show()

    plt.figure()
    plt.plot(time_sec_since_time_min, acc_D_filtered, label="filtered D")
    plt.plot(time_base, Yaw_filtered_resampled, label="filtered resampled Yaw")
    plt.plot(time_base, Pitch_filtered_resampled, label="filtered resampled Pitch")
    plt.plot(time_base, Roll_filtered_resampled, label="filtered resampled Roll")
    # plt.xlim([3600 * 10 - 120, 3600 * 10 + 120])
    ampl_acc_plot = 2
    # plt.ylim([-ampl_acc_plot, ampl_acc_plot])
    plt.legend()
    plt.tight_layout()
    plt.show()

    # TODO: add quality check figure yaw pitch roll

    data_IMU_filtered_resampled = np.zeros((time_base.size, 10))
    data_IMU_filtered_resampled[:, 0] = time_base
    data_IMU_filtered_resampled[:, 1] = acc_X_filtered_resampled
    data_IMU_filtered_resampled[:, 2] = acc_Y_filtered_resampled
    data_IMU_filtered_resampled[:, 3] = acc_Z_filtered_resampled
    data_IMU_filtered_resampled[:, 4] = acc_N_filtered_resampled
    data_IMU_filtered_resampled[:, 5] = acc_E_filtered_resampled
    data_IMU_filtered_resampled[:, 6] = acc_D_filtered_resampled
    data_IMU_filtered_resampled[:, 7] = Yaw_filtered_resampled
    data_IMU_filtered_resampled[:, 8] = Pitch_filtered_resampled
    data_IMU_filtered_resampled[:, 9] = Roll_filtered_resampled
    # TODO: add yaw pitch roll

    crrt_file_save = path_output + "CSV_DATA_" + str(crrt_IMU) + ".csv"
    header = "Seconds_since_{} ACC_X ACC_Y ACC_Z ACC_N ACC_E ACC_D YAW PITCH ROLL".format(str_time_min)
    np.savetxt(crrt_file_save, data_IMU_filtered_resampled, header=header)

end = True
