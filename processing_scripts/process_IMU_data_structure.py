import numpy as np
import matplotlib.pyplot as plt
import pynmea2
import datetime
import os
import fnmatch
from printind.printind_function import printi
import itertools
import time
import pickle
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

printi("Put the Python intepreter in UTC...")
os.environ['TZ'] = 'UTC'
time.tzset()
printi("Done!")

LIST_COLORS = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']


def limit_valid_indexes(all_timestamps, min_time, max_time):
    """find the min and max indexes for each all_timestamps[in_between] is between
    min_time and max_time"""

    min_ind = 0

    for crrt_ind in range(len(all_timestamps)):
        if all_timestamps[crrt_ind] > min_time:
            min_ind = crrt_ind
            break

    max_ind = 0
    nbr_ind = len(all_timestamps)

    for crrt_ind in range(len(all_timestamps)):
        if all_timestamps[nbr_ind - crrt_ind - 1] < max_time:
            max_ind = nbr_ind - crrt_ind - 1
            break

    return(min_ind, max_ind)


def generate_list_IMU_IDs(path_root_IMU_data):
    """Generate the list of IMU IDs present in the path_root_IMU_data folder"""

    return os.listdir(path_root_IMU_data)


def generate_IMU_data(path_root_IMU_data, IMU_ID, dict_all_data, verbose=1):
    """Generate all IMU data for one IMU ID and save it into dict_all_data"""

    if verbose > 0:
        printi("generate IMU data for IMU ID: " + IMU_ID)

    total_path = path_root_IMU_data + IMU_ID + '/'
    list_all_files = os.listdir(total_path)

    if 'B' in dict_all_data[IMU_ID]:
        pass
    else:
        dict_all_data[IMU_ID]['B'] = {}
        dict_all_data[IMU_ID]['Bt'] = {}

    for crrt_file in list_all_files:

        # IMU data
        if fnmatch.fnmatch(crrt_file, 'F?????_B'):
            if verbose > 2:
                printi("read IMU data from " + crrt_file)
            file_number = crrt_file[1: 6]
            # note: sometimes the parser adds a blank line; therefore, use invalid_raise to make sure not crashing the genfromtxt function
            # this will generate automatic error messages, that can be ignored
            dict_all_data[IMU_ID]['B'][file_number] = np.genfromtxt(total_path + crrt_file, delimiter=',', invalid_raise=False)

        # Arduino timestamps
        if fnmatch.fnmatch(crrt_file, 'F?????_Bt'):
            if verbose > 2:
                printi("read IMU timestamps from " + crrt_file)
            file_number = crrt_file[1: 6]
            dict_all_data[IMU_ID]['Bt'][file_number] = np.genfromtxt(total_path + crrt_file, delimiter=',', invalid_raise=False)


def generate_GPS_data(path_root_IMU_data, IMU_ID, dict_all_data, verbose=1):
    """Generate all GPS data for one IMU ID and save it in dict_all_data"""

    total_path = path_root_IMU_data + IMU_ID + '/'
    list_all_files = os.listdir(total_path)

    if verbose > 0:
        printi("generate GPS data for IMU ID: " + IMU_ID)

    if 'G' in dict_all_data[IMU_ID]:
        pass
    else:
        dict_all_data[IMU_ID]['G'] = {}
        dict_all_data[IMU_ID]['Gt'] = {}
        dict_all_data[IMU_ID]['G']['GPGGA'] = {}
        dict_all_data[IMU_ID]['G']['GPRMC'] = {}
        dict_all_data[IMU_ID]['G']['msg_GPGGA'] = {}
        dict_all_data[IMU_ID]['G']['msg_GPRMC'] = {}
        dict_all_data[IMU_ID]['Gt']['GPGGA'] = {}
        dict_all_data[IMU_ID]['Gt']['GPRMC'] = {}

    for crrt_file in list_all_files:

        # GPS data
        if fnmatch.fnmatch(crrt_file, 'F?????_G'):
            if verbose > 2:
                printi("read GPS data from " + crrt_file)
            file_number = crrt_file[1: 6]

            crrt_file_name = total_path + crrt_file

            # use the GPRMC and GPGGA
            list_GPGGA_lines = []
            list_GPGGA_line_index = []
            list_GPGGA_messages = []

            list_GPRMC_lines = []
            list_GPRMC_line_index = []
            list_GPRMC_messages = []

            with open(total_path + crrt_file, "r") as crrt_file:
                for crrt_line_ind, crrt_line in enumerate(crrt_file):
                    if crrt_line[0: 5] == 'GPGGA':
                        list_GPGGA_lines.append(crrt_line)
                        list_GPGGA_line_index.append(crrt_line_ind)
                        crrt_msg = pynmea2.parse(crrt_line)
                        list_GPGGA_messages.append(crrt_msg)

                    if crrt_line[0: 5] == 'GPRMC':
                        try:
                            list_GPRMC_lines.append(crrt_line)
                            list_GPRMC_line_index.append(crrt_line_ind)
                            crrt_msg = pynmea2.parse(crrt_line)
                            list_GPRMC_messages.append(crrt_msg)
                        except:
                            print("corrupted checksum; use last point")
                            list_GPRMC_lines.append(crrt_line)
                            list_GPRMC_line_index.append(crrt_line_ind)
                            list_GPRMC_messages.append(crrt_msg)

            dict_all_data[IMU_ID]['G']['msg_GPGGA'][file_number] = list_GPGGA_messages
            dict_all_data[IMU_ID]['G']['msg_GPRMC'][file_number] = list_GPRMC_messages

            all_GPGGA_lines = ''.join(list_GPGGA_lines)
            all_GPRMC_lines = ''.join(list_GPRMC_lines)

            with open(crrt_file_name + '_GPGGA', "w") as crrt_file:
                crrt_file.write(all_GPGGA_lines)

            with open(crrt_file_name + '_GPRMC', "w") as crrt_file:
                crrt_file.write(all_GPRMC_lines)

            dict_all_data[IMU_ID]['G']['GPGGA'][file_number] = np.genfromtxt(crrt_file_name + '_GPGGA', delimiter=',', invalid_raise=False)
            dict_all_data[IMU_ID]['G']['GPRMC'][file_number] = np.genfromtxt(crrt_file_name + '_GPRMC', delimiter=',', invalid_raise=False)

            # read the _Gt, and keep only the right line numbers
            all_GPS_timestamps = np.genfromtxt(total_path + 'F' + file_number + '_Gt', invalid_raise=False)
            dict_all_data[IMU_ID]['Gt']['GPGGA'][file_number] = all_GPS_timestamps[list_GPGGA_line_index]
            dict_all_data[IMU_ID]['Gt']['GPRMC'][file_number] = all_GPS_timestamps[list_GPRMC_line_index]


def print_structure_dict(dict_in, prefix=''):
    """Recursively print the structure of a dictionary, showing all keys.
    """
    for crrt_key in dict_in.keys():
        print(prefix + "-- " + crrt_key)

        if isinstance(dict_in[crrt_key], dict):
            print_structure_dict(dict_in[crrt_key], prefix + "    ")


def datetime_as_unix_time(t):
    """datetime to unix time (seconds since 1st january 1970).
    """
    return(t - datetime.datetime(1970, 1, 1)).total_seconds()


def unix_time_as_datetime(t):
    """unix time (seconds since 1st january 1970) to datetime.
    """
    return(datetime.datetime.utcfromtimestamp(t))


class IMU_TNEDXYZ(object):
    """A simple container class: IMU data, with field T (timestamps), N (North
    acceleration), E (East acceleration), D (Down acceleration), X (Acc X in
    IMU reference frame), Y (Acc Y), Z (Acc Z)."""

    def __init__(self, IMU_T, IMU_N, IMU_E, IMU_D, IMU_X, IMU_Y, IMU_Z, IMU_Yaw, IMU_Pitch, IMU_Roll):
        self.T = IMU_T
        self.N = IMU_N
        self.E = IMU_E
        self.D = IMU_D
        self.X = IMU_X
        self.Y = IMU_Y
        self.Z = IMU_Z
        self.Yaw = IMU_Yaw
        self.Pitch = IMU_Pitch
        self.Roll = IMU_Roll


class AnalyseIMUFolder(object):
    """A class to analyse all IMU data contained in an IMU data folder.

    The structure of the IMU folder should be the following:

    - IMU_data (at location path_to_root)
    |
    |--- IMU_ID_2
    |       |
    |       |--- F000458_B
    |       |--- F000458_G
    |       |--- etc...
    |
    |--- IMU_ID_2
    |       |
    |       |--- etc...
    |
    |--- etc...
    """

    def __init__(self, path_to_root=None, verbose=1, ignore_instruments=None):
        """Initialize. In addition if path_to_root is given and not none,
        read all data in the corresponding directory structure. Should have the organisation
        described in the class docstring.
        """
        path_to_root = path_to_root
        self.verbose = verbose
        self.ignore_instruments = ignore_instruments

        self.dict_all_data = {}
        self.dict_information_label_fusion = {}

        self.list_IMU_IDs = None
        self.list_valid_IMU_IDs = None

        if path_to_root is not None:

            self.list_valid_IMU_IDs = []

            if verbose > 1:
                printi("generate list_IMU_IDs")

            self.list_IMU_IDs = generate_list_IMU_IDs(path_to_root)

            if verbose > 2:
                printi("list_IMU_IDs: " + str(self.list_IMU_IDs))

            if verbose > 1:
                printi("generate all data")

            for crrt_IMU in self.list_IMU_IDs:

                analyse_IMU = True

                if self.ignore_instruments is not None:
                    if crrt_IMU in self.ignore_instruments:
                        printi("Ignore IMU ID {}".format(crrt_IMU))
                        analyse_IMU = False

                if analyse_IMU:
                    printi("Parse IMU ID {}".format(crrt_IMU))

                    self.list_valid_IMU_IDs.append(crrt_IMU)

                    self.dict_all_data[crrt_IMU] = {}
                    generate_IMU_data(path_to_root, crrt_IMU, self.dict_all_data, verbose=self.verbose)
                    generate_GPS_data(path_to_root, crrt_IMU, self.dict_all_data, verbose=self.verbose)

    def load_additional_data(self, path_to_root):
        """load more data; for example, when data is separated into different
        splitted folders to limit size of each of them. Should contain the same
        IMUs as the inital command"""

        if self.list_valid_IMU_IDs is None:
            self.list_valid_IMU_IDs = []

            if self.verbose > 1:
                printi("generate list_IMU_IDs")

            self.list_IMU_IDs = generate_list_IMU_IDs(path_to_root)

            if self.verbose > 2:
                printi("list_IMU_IDs: " + str(self.list_IMU_IDs))

            for crrt_IMU in self.list_IMU_IDs:

                if self.ignore_instruments is not None:
                    if crrt_IMU in self.ignore_instruments:
                        pass
                    else:
                        self.list_valid_IMU_IDs.append(crrt_IMU)

        if self.verbose > 1:
            printi("generate all data")

        for crrt_IMU in self.list_IMU_IDs:

            if self.ignore_instruments is not None:
                if crrt_IMU in self.ignore_instruments:
                    break

            if self.list_IMU_IDs is None:
                self.dict_all_data[crrt_IMU] = {}

            generate_IMU_data(path_to_root, crrt_IMU, self.dict_all_data, verbose=self.verbose)
            generate_GPS_data(path_to_root, crrt_IMU, self.dict_all_data, verbose=self.verbose)

    def print_exhaustive_overview_data(self):
        """Show all data and keys in the dictionary containing read and processed
        data.
        """
        print_structure_dict(self.dict_all_data)

    def plot_IMU_data(self, IMU_ID, file_number, show=True):
        """Plot IMU data for the IMU_ID and file_number"""

        # look at the acceleration, NED
        data_IMU = self.dict_all_data[IMU_ID]['B'][file_number]
        data_IMU_N = data_IMU[1:, 26]
        data_IMU_E = data_IMU[1:, 27]
        data_IMU_D = data_IMU[1:, 28]
        data_IMU_Dm = data_IMU_D - np.mean(data_IMU_D)
        data_IMU_Ax = data_IMU[:, 3]
        data_IMU_Ay = data_IMU[:, 4]
        data_IMU_Az = data_IMU[:, 5]
        data_IMU_Azm = data_IMU_Az - np.mean(data_IMU_Az)
        timestamps_IMU = self.dict_all_data[IMU_ID]['Bt'][file_number] / 1000.

        # grab the first GPS data as messages
        GPS_GPRMC_messages = self.dict_all_data[IMU_ID]['G']['msg_GPRMC'][file_number]
        GPS_GPRMC_first_message = GPS_GPRMC_messages[0]
        GPS_GPRMC_last_message = GPS_GPRMC_messages[-1]

        string_GPRMC_first = datetime.datetime.combine(GPS_GPRMC_first_message.datestamp, GPS_GPRMC_first_message.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        string_GPRMC_last = datetime.datetime.combine(GPS_GPRMC_last_message.datestamp, GPS_GPRMC_last_message.timestamp).strftime("%Y-%m-%d %H:%M:%S")

        min_nbr_index = min(timestamps_IMU.size, data_IMU_N.size)

        plt.figure()
        plt.plot(timestamps_IMU[:min_nbr_index], data_IMU_N[:min_nbr_index], label='North')
        plt.plot(timestamps_IMU[:min_nbr_index], data_IMU_E[:min_nbr_index], label='East')
        plt.plot(timestamps_IMU[:min_nbr_index], data_IMU_Dm[:min_nbr_index], label='Down - mean')
        plt.plot(timestamps_IMU[:min_nbr_index], data_IMU_Ax[:min_nbr_index], label='Ax')
        plt.plot(timestamps_IMU[:min_nbr_index], data_IMU_Ay[:min_nbr_index], label='Ay')
        plt.plot(timestamps_IMU[:min_nbr_index], data_IMU_Azm[:min_nbr_index], label='Az - mean')
        plt.xlabel('Arduino timestamp (s)')
        plt.ylabel('Acceleration (m / $s^2$)')
        plt.title('Start: ' + string_GPRMC_first + ' Stop: ' + string_GPRMC_last)
        plt.legend()

        if show:
            plt.show()

    def fusion_data_each_IMU_by_time(self, time_min, time_max, label):
        """Fusion all data for each IMU. Only data between time_min and time_max
        is kept. Label is used to index different fusion data (so that can do
        several fusion data on one dataset, and keep track of them)

        time_min and time_max should be Python datetime. Can be specified as:
        datetime.datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S.%f")"""

        for IMU_ID in self.dict_all_data.keys():

            # list of all available file keys
            list_file_keys = self.dict_all_data[IMU_ID]['B'].keys()

            if self.verbose > 2:
                printi("keys found: " + str(list_file_keys))

            # order the keys
            sorted_keys = sorted(list_file_keys)

            if self.verbose > 2:
                printi("keys sorted: " + str(sorted_keys))

            # lists for holding the data to append
            list_to_concatenate_B = []
            list_to_concatenate_Bt = []
            list_GPRMC_msg = []
            list_GPRMC_timestamps = []

            # go through all file keys
            for crrt_file_key in sorted_keys:

                # check if there is any time data
                if len(self.dict_all_data[IMU_ID]['G']['msg_GPRMC'][crrt_file_key]) < 2:
                    printi("Not enough data in file: " + crrt_file_key + " of IMU: " + IMU_ID + " ignoring entry")

                # check if time is OK
                else:
                    GPS_GPRMC_messages = self.dict_all_data[IMU_ID]['G']['msg_GPRMC'][crrt_file_key]
                    GPS_GPRMC_first_message = GPS_GPRMC_messages[0]
                    GPS_GPRMC_last_message = GPS_GPRMC_messages[-1]

                    try:
                        time_GPRMC_first = datetime.datetime.combine(GPS_GPRMC_first_message.datestamp, GPS_GPRMC_first_message.timestamp)
                        time_GPRMC_last = datetime.datetime.combine(GPS_GPRMC_last_message.datestamp, GPS_GPRMC_last_message.timestamp)
                    except:
                        time_GPRMC_first = None
                        time_GPRMC_last = None

                    if time_GPRMC_first is not None:
                        if (time_GPRMC_first < time_min) or (time_GPRMC_last > time_max):
                        # if (time_GPRMC_last < time_min) or (time_GPRMC_first > time_max):
                            printi("Time in file: " + crrt_file_key + " of IMU: " + IMU_ID + " is outside of bounds!")
                            printi("time_GPRMC_first: " + time_GPRMC_first.strftime("%Y-%m-%d %H:%M:%S"))
                            printi("time_GPRMC_last: " + time_GPRMC_last.strftime("%Y-%m-%d %H:%M:%S"))
                            printi("Ignoring entry")

                        # there is data and time is ok: append
                        else:
                            if self.verbose > 1:
                                printi("Information for fusion IMU_ID " + IMU_ID + " crrt_file_key " + crrt_file_key + " -----")
                                printi("shape self.dict_all_data[IMU_ID]['B'][crrt_file_key][1:, :]: " + str(self.dict_all_data[IMU_ID]['B'][crrt_file_key][1:, :].shape))
                                printi("shape self.dict_all_data[IMU_ID]['Bt'][crrt_file_key]): " + str(len(self.dict_all_data[IMU_ID]['Bt'][crrt_file_key])))
                                printi("shape self.dict_all_data[IMU_ID]['G']['msg_GPRMC'][crrt_file_key]: " + str(len(self.dict_all_data[IMU_ID]['G']['msg_GPRMC'][crrt_file_key])))
                                printi("shape self.dict_all_data[IMU_ID]['Gt']['GPRMC'][crrt_file_key]: " + str(len(self.dict_all_data[IMU_ID]['Gt']['GPRMC'][crrt_file_key])))
                                printi("End information -------------------------")

                            min_nbr_index = min(self.dict_all_data[IMU_ID]['B'][crrt_file_key][1:, :].shape[0], len(self.dict_all_data[IMU_ID]['Bt'][crrt_file_key]))

                            list_to_concatenate_B.append(self.dict_all_data[IMU_ID]['B'][crrt_file_key][1:min_nbr_index + 1, :])
                            list_to_concatenate_Bt.append(self.dict_all_data[IMU_ID]['Bt'][crrt_file_key][0: min_nbr_index])
                            list_GPRMC_msg.append(self.dict_all_data[IMU_ID]['G']['msg_GPRMC'][crrt_file_key])
                            list_GPRMC_timestamps.append(self.dict_all_data[IMU_ID]['Gt']['GPRMC'][crrt_file_key])
                    else:
                        print("--------------- WARNING !!!!! failed time_GPRMC_first! -----------------------------------")
                        print("warning is for IMU {} file number {}".format(IMU_ID, crrt_file_key))

            # do the fusion of all data for this IMU
            self.dict_all_data[IMU_ID]['B_fusion' + label] = np.concatenate(list_to_concatenate_B)
            self.dict_all_data[IMU_ID]['Bt_fusion' + label] = np.concatenate(list_to_concatenate_Bt)
            list_all_GPRMC_msg = list(itertools.chain.from_iterable(list_GPRMC_msg))
            self.dict_all_data[IMU_ID]['GPRMC_msg_fusion' + label] = list_all_GPRMC_msg
            self.dict_all_data[IMU_ID]['Gt_GPRMC_fusion' + label] = np.concatenate(list_GPRMC_timestamps)
            self.dict_information_label_fusion[label] = (time_min, time_max)

    def establish_regression_timestamp_utc_for_fusion_data(self, label):
        """Do a regression of time for the fusion data corresponding to label.
        Use the regression to compute UTC time for IMU Arduino timestamps."""

        for IMU_ID in self.dict_all_data.keys():

            GPS_arduino_timestamps = self.dict_all_data[IMU_ID]['Gt_GPRMC_fusion' + label]

            list_unix_timestamps = []
            for crrt_GPRMC_msg in self.dict_all_data[IMU_ID]['GPRMC_msg_fusion' + label]:
                try:
                    crrt_value = datetime_as_unix_time(datetime.datetime.combine(crrt_GPRMC_msg.datestamp, crrt_GPRMC_msg.timestamp))
                except:
                    print("faulty datetime addition")
                
                list_unix_timestamps.append(crrt_value)
                

            unix_timestamps = np.array(list_unix_timestamps)

            # do the linear regression between GPS unix timestamps and arduino timestamps
            size_min = min(GPS_arduino_timestamps.shape[0], unix_timestamps.shape[0])
            polynomial_timestamp_fit = np.polyfit(GPS_arduino_timestamps[:size_min], unix_timestamps[:size_min], 1)
            polynomial_interpolator = np.poly1d(polynomial_timestamp_fit)

            # obtain the unix timestamps for IMU data
            IMU_data_arduino_timestamp = self.dict_all_data[IMU_ID]['Bt_fusion' + label]

            # obtain the datetime timestamps for IMU data
            list_datetime_timestamps = []
            list_unix_timestamps = []
            for crrt_arduino_timestamp in IMU_data_arduino_timestamp:
                crrt_unix_time = polynomial_interpolator(crrt_arduino_timestamp)
                list_unix_timestamps.append(crrt_unix_time)
                IMU_data_arduino_datetime_timestamp = unix_time_as_datetime(crrt_unix_time)
                list_datetime_timestamps.append(IMU_data_arduino_datetime_timestamp)

            self.dict_all_data[IMU_ID]['Bt_fusion_unix_timestamp' + label] = list_unix_timestamps
            self.dict_all_data[IMU_ID]['Bt_fusion_datetime_timestamp' + label] = list_datetime_timestamps

    def plot_fusion_data(self, label, show=True, take_away_mean=False):
        """Show all fusion data.
        """

        for IMU_ID in self.dict_all_data.keys():

            data_IMU = self.dict_all_data[IMU_ID]['B_fusion' + label]
            data_IMU_N = data_IMU[:, 26]
            data_IMU_E = data_IMU[:, 27]
            data_IMU_D = data_IMU[:, 28]

            data_IMU_Ax = data_IMU[:, 3]
            data_IMU_Ay = data_IMU[:, 4]
            data_IMU_Az = data_IMU[:, 5]

            timestamps_IMU = self.dict_all_data[IMU_ID]['Bt_fusion_datetime_timestamp' + label]

            plt.figure()

            # NED
            plt.plot(timestamps_IMU, data_IMU_N, label='N')
            plt.plot(timestamps_IMU, data_IMU_E, label='E')
            if take_away_mean:
                plt.plot(timestamps_IMU, data_IMU_D - np.mean(data_IMU_D), label='D - mean(D)')
            else:
                plt.plot(timestamps_IMU, data_IMU_D, label='D')

            # XYZ
            plt.plot(timestamps_IMU, data_IMU_Ax, label='Ax')
            plt.plot(timestamps_IMU, data_IMU_Ay, label='Ay')
            if take_away_mean:
                plt.plot(timestamps_IMU, data_IMU_Az - np.mean(data_IMU_Az), label='Az - mean(Az)')
            else:
                plt.plot(timestamps_IMU, data_IMU_Az, label='Az')

            plt.xlabel('time (UTC)')
            plt.ylabel('m/$s^2$')
            plt.title('IMU ' + IMU_ID)
            plt.legend(bbox_to_anchor=(1.05, 0), loc='lower center', borderaxespad=0.)

    def return_IMU_data_timestamp(self, IMU_ID, label):
        """Return fusion data corresponding to IMU_ID. The data returned is a
        IMU_TNED object.
        """

        data_IMU = self.dict_all_data[IMU_ID]['B_fusion' + label]
        data_IMU_N = data_IMU[:, 26]
        data_IMU_E = data_IMU[:, 27]
        data_IMU_D = data_IMU[:, 28]
        data_IMU_X = data_IMU[:, 3]
        data_IMU_Y = data_IMU[:, 4]
        data_IMU_Z = data_IMU[:, 5]
        data_IMU_Yaw = data_IMU[:, 11]
        data_IMU_Pitch = data_IMU[:, 12]
        data_IMU_Roll = data_IMU[:, 13]

        timestamps_IMU = self.dict_all_data[IMU_ID]['Bt_fusion_datetime_timestamp' + label]

        IMU_TNEDXYZ_instance = IMU_TNEDXYZ(timestamps_IMU, data_IMU_N, data_IMU_E, data_IMU_D, data_IMU_X, data_IMU_Y, data_IMU_Z, data_IMU_Yaw, data_IMU_Pitch, data_IMU_Roll)

        return IMU_TNEDXYZ_instance

    def save_IMU_TNEDXYZ_data(self, label, path_out):
        """Save all fused data corresponding to label into path_out.
        The saved data is a dict. Fields are ['time_information'] = (time_min, time_max)
        and ['IMU_ID'] = IMU_TNED object.

        To load: pickle.load(open(path_out, "rb"))
        """

        dict_to_save = {}
        dict_to_save['time_information'] = self.dict_information_label_fusion[label]

        for IMU_ID in self.dict_all_data.keys():
            dict_to_save[IMU_ID] = self.return_IMU_data_timestamp(IMU_ID, label)

        pickle.dump(dict_to_save, open(path_out + "_IMU_TNEDXYZ", "wb"))

    def save_GPS_data(self, label, path_out):
        """Save the GPRMC data corresponding to all instruments. Fields are
        ['IMU_ID'] and ['time_information']
        """

        dict_to_save = {}
        dict_to_save['time_information'] = self.dict_information_label_fusion[label]

        for IMU_ID in self.dict_all_data.keys():
            dict_to_save[IMU_ID] = self.dict_all_data[IMU_ID]["GPRMC_msg_fusion" + label]

        pickle.dump(dict_to_save, open(path_out + "_GPRMC", "wb"))

    def show_instruments_loaded_time(self, verbose=None):
        if verbose is None:
            verbose = self.verbose

        fig = plt.figure()
        ax = fig.add_subplot(111)

        for instrument_nbr, crrt_instrument in enumerate(self.list_valid_IMU_IDs):
            (GPRMC_first, GPRMC_last) = self.min_max_time_instrument(crrt_instrument)

            start = mdates.date2num(GPRMC_first)
            end = mdates.date2num(GPRMC_last)
            width = end - start

            if verbose > 5:
                print(start)
                print(end)
                print(width)

            # Plot rectangle
            rect = Rectangle((start, instrument_nbr), width, 1, color=LIST_COLORS[instrument_nbr], label=crrt_instrument, alpha=0.8)
            # rect = Rectangle((start, instrument_nbr), width, 1, color="blue", label=crrt_instrument)
            ax.add_patch(rect)

            plt.plot([GPRMC_first, GPRMC_last], [instrument_nbr + 0.5, instrument_nbr + 0.5], color=LIST_COLORS[instrument_nbr])

        plt.legend()
        ax.set_yticklabels([])
        plt.gcf().autofmt_xdate()
        plt.title("currently loaded instrument times")
        plt.show()

    def min_max_time_instrument(self, crrt_instrument):
        list_sorted_keys = sorted(self.dict_all_data[crrt_instrument]["B"].keys())
        first_key = list_sorted_keys[0]
        last_key = list_sorted_keys[-1]

        GPS_GPRMC_messages = self.dict_all_data[crrt_instrument]['G']['msg_GPRMC'][first_key]
        GPS_GPRMC_first_message = GPS_GPRMC_messages[0]
        GPRMC_first = datetime.datetime.combine(GPS_GPRMC_first_message.datestamp, GPS_GPRMC_first_message.timestamp)

        GPS_GPRMC_messages = self.dict_all_data[crrt_instrument]['G']['msg_GPRMC'][last_key]
        GPS_GPRMC_last_message = GPS_GPRMC_messages[-1]
        GPRMC_last = datetime.datetime.combine(GPS_GPRMC_last_message.datestamp, GPS_GPRMC_last_message.timestamp)

        return(GPRMC_first, GPRMC_last)

    def maximum_common_loaded_time(self, verbose=0):
        """give the maximum time range for which all sensors have some data available."""

        min_time = datetime.datetime.strptime("1970-01-01 00:00:01.000", "%Y-%m-%d %H:%M:%S.%f")
        max_time = datetime.datetime.strptime("2170-01-01 00:00:01.000", "%Y-%m-%d %H:%M:%S.%f")

        for crrt_instrument in self.list_valid_IMU_IDs:
            (GPRMC_first, GPRMC_last) = self.min_max_time_instrument(crrt_instrument)

            if GPRMC_first > min_time:
                min_time = GPRMC_first

            if GPRMC_last < max_time:
                max_time = GPRMC_last

        if verbose > 0:
            print("min time common to all: {}".format(min_time))
            print("max time common to all: {}".format(max_time))

        return(min_time, max_time)
