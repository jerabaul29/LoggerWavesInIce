from __future__ import print_function
import numpy as np
from scipy import signal
from process_IMU_data_structure import AnalyseIMUFolder
from process_IMU_data_structure import limit_valid_indexes
import matplotlib.pyplot as plt
import datetime

# path to the data; you will need to adapt this!
path_to_data = "/home/jrlab/Desktop/Data/DataPolarsysell2018/parsed_27042018/"


# def segment(number):
#     return(path_to_data + str(number) + "/")


# load all the data; this will generate some warnings, this is normal: either empty files (before / after measurements)
# or a few dropouts (typically, 0.5 percent dropout rate, unsignificatn)
# ignore_buggy_instrument = ["F2", 'Nansen']
ignore_buggy_instrument = ["1", "5"]
# ignore_buggy_instrument = ['5', '4', '6', "F2", "Nansen"]
analyse_folder_instance = AnalyseIMUFolder(path_to_data, verbose=5, ignore_instruments=ignore_buggy_instrument)


# # load some additional data
# # analyse_folder_instance.load_additional_data(path_to_root=segment(12))
# analyse_folder_instance.load_additional_data(path_to_root=segment(14))
# analyse_folder_instance.show_instruments_loaded_time(verbose=0)
# analyse_folder_instance.load_additional_data(path_to_root=segment(13))
# analyse_folder_instance.show_instruments_loaded_time(verbose=0)
# # analyse_folder_instance.load_additional_data(path_to_root=segment(12))
# # analyse_folder_instance.show_instruments_loaded_time(verbose=0)
# # already loaded: analyse_folder_instance.load_additional_data(path_to_root=segment(15))
# analyse_folder_instance.load_additional_data(path_to_root=segment(16))
# analyse_folder_instance.show_instruments_loaded_time(verbose=0)
# analyse_folder_instance.load_additional_data(path_to_root=segment(17))
# analyse_folder_instance.show_instruments_loaded_time(verbose=0)
# analyse_folder_instance.load_additional_data(path_to_root=segment(18))
# analyse_folder_instance.show_instruments_loaded_time(verbose=0)

# analyse_folder_instance.load_additional_data(path_to_root=path_to_data)

# show the time loaded
analyse_folder_instance.show_instruments_loaded_time(verbose=0)
_ = analyse_folder_instance.maximum_common_loaded_time(verbose=1)

time_min = datetime.datetime.strptime("2018-04-26 18:00:00.000", "%Y-%m-%d %H:%M:%S.%f")
time_max = datetime.datetime.strptime("2018-04-27 08:00:00.000", "%Y-%m-%d %H:%M:%S.%f")
label = 'crrt_segment'
analyse_folder_instance.fusion_data_each_IMU_by_time(time_min, time_max, label)


# do a regression between Arduino and UTC timestamp, and get the VN100 timestamps in UTC
analyse_folder_instance.establish_regression_timestamp_utc_for_fusion_data(label)

# show all UTC IMU data for the corresponding label
# analyse_folder_instance.plot_fusion_data(label)
# plt.show()

# save the acceleration data and the GPRMC data
path_out = "/home/jrlab/Desktop/Data/DataPolarsysell2018/parsed_27042018"
analyse_folder_instance.save_IMU_TNEDXYZ_data(label=label, path_out=path_out + "/" + str(time_min).replace(" ", "_") + "_" + str(time_max).replace(" ", "_"))
analyse_folder_instance.save_GPS_data(label=label, path_out=path_out + "/" + str(time_min).replace(" ", "_") + "_" + str(time_max).replace(" ", "_"))
