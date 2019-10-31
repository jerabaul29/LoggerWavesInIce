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

path_IMU_data = "/home/jrlab/Desktop/Git/Svalbard_March_2019_IMU_data/look_at_data/Data" + "/"


def find_min_gt_index_in_ordered_array(array, value_test):
    for i, value in enumerate(array):
        if value > value_test:
            return(i)
    return(None)


def get_Down(dict_data, IMU_ID):
    return(dict_data[IMU_ID][:, 6])


def get_Time_Base(dict_data, IMU_ID):
    return(dict_data[IMU_ID][:, 0])


def show_log_spectrogram(dict_data, crrt_IMU, min_f=0.01, max_f=0.30, vmin=-13, vmax=-9, nperseg=10 * 60 * 10, FS=10):
    plt.figure()
    f, t, Sxx = signal.spectrogram(get_Down(dict_data, crrt_IMU), FS, nperseg=nperseg)
    t += get_Time_Base(dict_data, crrt_IMU)[0]
    ind_min = find_min_gt_index_in_ordered_array(f, min_f)
    ind_max = find_min_gt_index_in_ordered_array(f, max_f)
    plt.pcolormesh(t / 3600.0, f[ind_min:ind_max], np.log(Sxx[ind_min:ind_max, :] + 1e-16), label='log(Sxx)', vmin=vmin, vmax=vmax)
    cbar = plt.colorbar()
    cbar.set_label('log(Saa) \n', rotation=270, labelpad=15)
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time since 2018-03-22 18:00:00 [hr]')  # NOTE: this may need changes for other datasets
    plt.tight_layout()
    plt.show()


# load all the data ------------------------------------------------------------
list_IMUs_To_Use = ['1', '5', 'F1']

dict_all_loaded_data = {}

for crrt_IMU in list_IMUs_To_Use:
    crrt_filename = path_IMU_data + "CSV_Data_" + str(crrt_IMU) + ".csv"
    print("Loading {}".format(crrt_filename))
    dict_all_loaded_data[crrt_IMU] = np.genfromtxt(crrt_filename, skip_header=1)

common_time_base = get_Time_Base(dict_all_loaded_data, "5")
# ------------------------------------------------------------------------------

show_log_spectrogram(dict_all_loaded_data, "1")

show_log_spectrogram(dict_all_loaded_data, "5")

show_log_spectrogram(dict_all_loaded_data, "F1")


end = True
