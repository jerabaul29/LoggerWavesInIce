from process_IMU_data_structure import *

# example of data analysis -----------------------------------------------------

# path to the data; you will need to adapt this!
path_to_data = "/home/jrlab/Desktop/Data/Data_For_Aleksey_Harbor_2019/Parsed" + "/"

# load all the data; this will generate some warnings, this is normal: either empty files (before / after measurements)
# or a few dropouts (typically, 0.5 percent dropout rate, unsignificatn)
ignore_buggy_instrument = []
# ignore_buggy_instrument = ['3', '5', '4', '6']
analyse_folder_instance = AnalyseIMUFolder(path_to_data, verbose=5, ignore_instruments=ignore_buggy_instrument)

print(analyse_folder_instance.dict_all_data.keys())
analyse_folder_instance.dict_all_data["3"].keys()
analyse_folder_instance.dict_all_data["3"]["B"].keys()

# plot one data file from one IMU
# first file with data for IMU 2
analyse_folder_instance.plot_IMU_data('3', '01572')
# last file with data for IMU 2

# get data from all IMUs corresponding to a given time interval (UTC) and mark it in a label
time_min = datetime.datetime.strptime("2019-04-01 15:00:00.000", "%Y-%m-%d %H:%M:%S.%f")
time_max = datetime.datetime.strptime("2019-04-03 10:00:00.000", "%Y-%m-%d %H:%M:%S.%f")
label = 'all_data'
analyse_folder_instance.fusion_data_each_IMU_by_time(time_min, time_max, label)

# do a regression between Arduino and UTC timestamp, and get the VN100 timestamps in UTC
analyse_folder_instance.establish_regression_timestamp_utc_for_fusion_data(label)

# show all UTC IMU data for the corresponding label
analyse_folder_instance.plot_fusion_data(label)
plt.show()

# save the data marked with the label for later use
path_out = '/home/jrlab/Desktop/Data/Data_For_Aleksey_Harbor_2019/Out/3/'
analyse_folder_instance.save_IMU_TNEDXYZ_data(label, path_out)

# load the saved data
with open(path_out + "_IMU_TNEDXYZ", "rb") as crrt_file:
    dict_data_loaded = pickle.load(crrt_file)

# examples of how to read the data
print_structure_dict(dict_data_loaded)  # list all folders
dict_data_loaded['3'].T  # For each instrument, the .T field contains the UTC timestamp of the data
dict_data_loaded['3'].D  # for each instrument, the .D field contains the Downwards acceleration

# plot all downwards accelerations on a given time interval --------------------
IMU_list_to_plot = ['3']

time_utc_min = datetime.datetime.strptime("2019-04-01 15:00:00.000", "%Y-%m-%d %H:%M:%S.%f")
time_utc_max = datetime.datetime.strptime("2019-04-03 10:00:00.000", "%Y-%m-%d %H:%M:%S.%f")

individual_spacing = 0.05
ind = 0

fig = plt.figure()
ax = fig.subplots()

for crrt_IMU in IMU_list_to_plot:
    spacing = ind * individual_spacing
    ind += 1

    crrt_timestamp = dict_data_loaded[crrt_IMU].T

    D_data = dict_data_loaded[crrt_IMU].D
    (min_ind, max_ind) = limit_valid_indexes(crrt_timestamp, time_utc_min, time_utc_max)
    crrt_data = D_data - np.mean(D_data[min_ind:max_ind]) + spacing

    plt.plot(crrt_timestamp, crrt_data, label=crrt_IMU)

plt.legend(loc=3, ncol=4)
ax.set_xlim([time_utc_min, time_utc_max])
fig.autofmt_xdate()
plt.ylabel("Downwards acceleration (shifted)")
plt.xlabel("UTC time")
plt.savefig('./Figures/IMU_Kalman_waves_data.pdf')
plt.show()

# write the data into a CSV format ---------------------------------------------
IMU_list_to_plot = ['3']

time_utc_min = datetime.datetime.strptime("2019-03-26 15:00:00.000", "%Y-%m-%d %H:%M:%S.%f")
time_utc_max = datetime.datetime.strptime("2019-03-28 10:00:00.000", "%Y-%m-%d %H:%M:%S.%f")

for crrt_IMU in IMU_list_to_plot:

    crrt_timestamp = dict_data_loaded[crrt_IMU].T

    D_data = dict_data_loaded[crrt_IMU].D
    (min_ind, max_ind) = limit_valid_indexes(crrt_timestamp, time_utc_min, time_utc_max)
    crrt_data = D_data - np.mean(D_data[min_ind:max_ind])

    with open("./Data/CSV_Data_" + crrt_IMU + ".csv", 'w+') as crrt_file:
        header = "Year Month Day Hour Minute Second microsecond seconds_since_2019-03-26 15:00:00.000 Wave_vertical_acceleration"
        crrt_file.write(header)
        crrt_file.write("\n")

        for crrt_ind in range(min_ind, max_ind):
            crrt_file.write(crrt_timestamp[crrt_ind].strftime("%Y %m %d %H %M %S %f"))
            crrt_file.write(" ")
            crrt_file.write(str((crrt_timestamp[crrt_ind] - time_utc_min).total_seconds()))
            crrt_file.write(" ")
            crrt_file.write(str(crrt_data[crrt_ind]))
            crrt_file.write("\n")

# check that it looks good -----------------------------------------------------
data_from_csv = np.genfromtxt("./Data/CSV_Data_F1.csv", delimiter=" ")

plt.figure()
plt.plot(data_from_csv[:, 7] / 60.0 + 44, data_from_csv[:, 8])
plt.show()
