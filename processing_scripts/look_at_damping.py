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

# plt.rc('text', usetex=True)

path_IMU_data = "/home/jrlab/Desktop/Data/DataPolarsysell2018/parsed_27042018/2018-04-26_18:00:00_2018-04-27_08:00:00_IMU_TNEDXYZ"
FS = 10

g = 9.81


def funcFitDecay(frq, nuFit):
    return (nuFit**0.5) * ((2 * np.pi * frq)**(7. / 2.)) / (2**0.5) / (g**2)


# TODO: to look at damping, cannot use the PSD of the elevation because of added noise due to double integration;
#       instead, compute damping directly on the PSD / FFT of the acceleration. Check formular for that.
# TODO: - resample time
# TODO: discuss with Graig; should we transmit PSD / FFT of elevation or acceleration? Maybe acceleration is better

# load the saved data
with open(path_IMU_data, "rb") as crrt_file:
    dict_data_loaded_IMU = pickle.load(crrt_file)


def noise(frequency, scaling=0.17):
    return((scaling * 9.81e-3)**2 * ((2 * np.pi * frequency)**(-4)))


list_IMUs_for_plot = ["2", "3", "4"]

for crrt_IMU in list_IMUs_for_plot:
    size_data = np.size(dict_data_loaded_IMU[crrt_IMU].D)
    print("IMU {}".format(crrt_IMU))
    print("Number of points: {}".format(size_data))
    print("Corresponding duration (hr): {}".format(size_data / 10.0 / 3600))
    print("Corresponding numbe of 15 minutes files read: {}".format(size_data / 10 / 3600 * 4.0))

# look at the acceleration spectra ---------------------------------------------
nperseg = 10 * 60 * 5
# nperseg = 10 * 60 * 10
overlap_proportion = 0.95
overlap = int(nperseg * overlap_proportion)

plt.figure()

for crrt_IMU in list_IMUs_for_plot:
    f, Pxx_den = signal.welch(dict_data_loaded_IMU[crrt_IMU].D, FS, nperseg=nperseg, noverlap=overlap)
    plt.semilogy(f, Pxx_den, label=crrt_IMU)
plt.legend()
plt.xlabel('Frq [Hz]')
plt.ylabel('PSD $\eta_{tt}$')
plt.xlim([0.005, 0.3])
plt.title("files between 2018-03-23_00:00:00 to 2018-03-23_05:00:00")
plt.tight_layout()
plt.show()

npts_analysis = 10 * 60 * 60
segment_number = 2

plt.figure()

for crrt_IMU in list_IMUs_for_plot:
    f, Pxx_den = signal.welch(dict_data_loaded_IMU[crrt_IMU].D[npts_analysis * segment_number: npts_analysis * (segment_number + 1)], FS, nperseg=nperseg, noverlap=overlap)
    plt.semilogy(f, Pxx_den, label=crrt_IMU)
plt.legend()
plt.xlabel('Frq [Hz]')
plt.ylabel('PSD $\eta_{tt}$')
plt.xlim([0.005, 0.3])
plt.title("files between 2018-03-23_00:00:00 to 2018-03-23_05:00:00")
plt.tight_layout()
plt.show()

# look at the elevation spectra ------------------------------------------------
# inspired by Graig processing
# parameters for the band pass filtering

global_fs = FS
global_lowcut = 0.05
global_highcut = 0.25

# parameters for the part of the acceleration signal to use
# avoid beginning and end of signal, fixed length in FFTs and Welch so
# that no need to transmit the frequence points by Iridium
# lets use 1024 s ~ 17 minutes
IMU_nfft = nperseg
IMU_noverlap = overlap
IMU_detrend = "constant"


class BandPass(object):
    """A class to perform bandpass filtering using Butter filter."""

    def __init__(self, lowcut=global_lowcut, highcut=global_highcut, fs=global_fs, order=2):
        """lowcut, highcut and fs are in Hz."""
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        self.b, self.a = butter(order, [low, high], btype='band')

    def filter_data(self, data):
        """filter the data."""

        result = lfilter(self.b, self.a, data)

        return(result)


def compute_vertical_elevation_method_Graig(data_in):
        '''integrate twice using fft and ifft, in addition filtering by Kohout'''

        np.seterr(divide='ignore')

        # calculate fft, filter, and then ifft to get heights

        # suppress divide by 0 warning
        # np.seterr(divide='ignore')

        data_det = signal.detrend(data_in, type=IMU_detrend)

        Y = np.fft.fft(data_det)

        # calculate weights before applying ifft
        freq = np.fft.fftfreq(data_det.size, d=1.0 / global_fs)
        weights = -1.0 / ((2 * np.pi * freq)**2)
        # need to do some filtering for low frequency (from Kohout)
        f1 = 0.03
        f2 = 0.04
        Yf = np.zeros_like(Y)
        ind = np.argwhere(np.logical_and(freq >= f1, freq <= f2))
        Yf[ind] = Y[ind] * 0.5 * (1 - np.cos(np.pi * (freq[ind] - f1) / (f2 - f1))) * weights[ind]
        Yf[freq > f2] = Y[freq > f2] * weights[freq > f2]

        # apply ifft to get height
        elev = -np.real(np.fft.ifft(2 * Yf))

        return(elev)


def find_first_index_where_greater_than(np_array, value):
    for index, crrt_value in (enumerate, np_array):
        if crrt_value > value:
            return index


# plot with the noise ----------------------------------------------------------
plt.figure()

for crrt_IMU in list_IMUs_for_plot:
    # print("PSD for IMU {}".format(crrt_IMU))

    # print("compute elevation")
    nbr_points = np.size(dict_data_loaded_IMU[crrt_IMU].D)
    closest_power_of_2 = math.log(nbr_points) / math.log(2.0)
    integer_closest_power_of_2 = int(math.floor(closest_power_of_2))
    crrt_elev = compute_vertical_elevation_method_Graig(dict_data_loaded_IMU[crrt_IMU].D[:2**integer_closest_power_of_2])

    # print("compute Welch")
    f, crrt_Pxx = signal.welch(crrt_elev, FS, nperseg=nperseg, noverlap=overlap)
    # f, crrt_Pxx = signal.csd(crrt_elev, crrt_elev, fs=FS, nperseg=nperseg, noverlap=overlap, return_onesided=True)

    # print("plot")
    plt.semilogy(f, crrt_Pxx, label=crrt_IMU)

plt.semilogy(f, noise(f), color='k', linestyle='--', linewidth=2, label='noise')
plt.xlabel('Frq [Hz]')
plt.ylabel('PSD $\eta$')
min_frq_plot = global_lowcut * 0.8
max_frq_plot = global_highcut
plt.xlim([min_frq_plot, max_frq_plot])
plt.ylim([1e-7, 5e-3])
plt.legend()
plt.tight_layout()
plt.show()

# plot with the noise ----------------------------------------------------------
plt.figure()

for crrt_IMU in list_IMUs_for_plot:
    # print("PSD for IMU {}".format(crrt_IMU))

    # print("compute elevation")
    nbr_points = np.size(dict_data_loaded_IMU[crrt_IMU].D)
    closest_power_of_2 = math.log(nbr_points) / math.log(2.0)
    integer_closest_power_of_2 = int(math.floor(closest_power_of_2))
    crrt_elev = compute_vertical_elevation_method_Graig(dict_data_loaded_IMU[crrt_IMU].D[:2**integer_closest_power_of_2])

    # print("compute Welch")
    f, crrt_Pxx = signal.welch(crrt_elev, FS, nperseg=nperseg, noverlap=overlap)
    # f, crrt_Pxx = signal.csd(crrt_elev, crrt_elev, fs=FS, nperseg=nperseg, noverlap=overlap, return_onesided=True)

    # print("plot")
    plt.plot(f, crrt_Pxx, label=crrt_IMU)

plt.plot(f, noise(f), color='k', linestyle='--', linewidth=2, label='noise')
plt.xlabel('Frq [Hz]')
plt.ylabel('PSD $\eta$')
min_frq_plot = global_lowcut * 0.8
max_frq_plot = global_highcut
plt.xlim([min_frq_plot, max_frq_plot])
plt.ylim([1e-7, 2e-3])
plt.legend()
plt.tight_layout()
plt.show()

# plot without the noise -------------------------------------------------------
plt.figure()

for crrt_IMU in list_IMUs_for_plot:
    print("PSD for IMU {}".format(crrt_IMU))

    print("compute elevation")
    nbr_points = np.size(dict_data_loaded_IMU[crrt_IMU].D)
    closest_power_of_2 = math.log(nbr_points) / math.log(2.0)
    integer_closest_power_of_2 = int(math.floor(closest_power_of_2))
    crrt_elev = compute_vertical_elevation_method_Graig(dict_data_loaded_IMU[crrt_IMU].D[:2**integer_closest_power_of_2])

    print("compute Welch")
    f, crrt_Pxx = signal.welch(crrt_elev, FS, nperseg=nperseg, noverlap=overlap)
    # f, crrt_Pxx = signal.csd(crrt_elev, crrt_elev, fs=FS, nperseg=nperseg, noverlap=overlap, return_onesided=True)
    crrt_Pxx = crrt_Pxx - noise(f, scaling=0.18)

    print("plot")
    plt.semilogy(f, crrt_Pxx, label=crrt_IMU)

plt.xlabel('Frq [Hz]')
plt.ylabel('PSD[$\eta$] - PSD[noise]')
min_frq_plot = global_lowcut * 0.8
max_frq_plot = global_highcut
plt.xlim([min_frq_plot, max_frq_plot])
plt.ylim([1e-7, 5e-3])
plt.legend()
plt.tight_layout()
plt.show()

# plot without the noise -------------------------------------------------------
plt.figure()

for crrt_IMU in list_IMUs_for_plot:
    print("PSD for IMU {}".format(crrt_IMU))

    print("compute elevation")
    nbr_points = np.size(dict_data_loaded_IMU[crrt_IMU].D)
    closest_power_of_2 = math.log(nbr_points) / math.log(2.0)
    integer_closest_power_of_2 = int(math.floor(closest_power_of_2))
    crrt_elev = compute_vertical_elevation_method_Graig(dict_data_loaded_IMU[crrt_IMU].D[:2**integer_closest_power_of_2])

    print("compute Welch")
    f, crrt_Pxx = signal.welch(crrt_elev, FS, nperseg=nperseg, noverlap=overlap)
    # f, crrt_Pxx = signal.csd(crrt_elev, crrt_elev, fs=FS, nperseg=nperseg, noverlap=overlap, return_onesided=True)
    crrt_Pxx = crrt_Pxx - noise(f, scaling=0.18)

    print("plot")
    plt.plot(f, crrt_Pxx, label=crrt_IMU)

plt.xlabel('Frq [Hz]')
plt.ylabel('PSD[$\eta$] - PSD[noise]')
min_frq_plot = global_lowcut * 0.8
max_frq_plot = global_highcut
plt.xlim([min_frq_plot, max_frq_plot])
plt.ylim([1e-7, 1.5e-3])
plt.legend()
plt.tight_layout()
plt.show()

# look at damping --------------------------------------------------------------

# nperseg = 10 * 60 * 5
# nperseg = 10 * 60 * 10
nperseg = 10 * 60 * 20
overlap_proportion = 0.95
overlap = int(nperseg * overlap_proportion)


def damping_Weber(frequency, nu=0.0095):
    return((nu**0.5) * ((2 * np.pi * frequency)**3.5) / np.sqrt(2.0) / 9.81**2)


# generate the Welch spectra data and look at damping from it
dict_welch_spectra = {}
first_signal_length = None

for crrt_IMU in list_IMUs_for_plot:

    nbr_points = np.size(dict_data_loaded_IMU[crrt_IMU].D)
    closest_power_of_2 = math.log(nbr_points) / math.log(2.0)
    integer_closest_power_of_2 = int(math.floor(closest_power_of_2))
    crrt_elev = compute_vertical_elevation_method_Graig(dict_data_loaded_IMU[crrt_IMU].D[:2**integer_closest_power_of_2])

    if first_signal_length is None:
        first_signal_length = np.size(crrt_elev)

    assert (np.size(crrt_elev) == first_signal_length)

    f, crrt_Pxx = signal.welch(crrt_elev, FS, nperseg=nperseg, noverlap=overlap)
    # f, crrt_Pxx = signal.csd(crrt_elev, crrt_elev, fs=FS, nperseg=nperseg, noverlap=overlap, return_onesided=True)

    dict_welch_spectra[crrt_IMU] = (f, crrt_Pxx)


def compute_damping(IMU_out, IMU_in, distance_m=1500, plot=True, index_limits=None, smoothing=False):

    attenuation_PSD = dict_welch_spectra[IMU_out][1] / dict_welch_spectra[IMU_in][1]
    attenuation_coefficient = np.sqrt(attenuation_PSD)
    damping_coefficient = np.log(attenuation_coefficient) / distance_m
    frequency = dict_welch_spectra[IMU_out][0]
    assert(np.size(dict_welch_spectra[IMU_out][0]) == np.size(dict_welch_spectra[IMU_in][0]))

    if smoothing:
        damping_coefficient = signal.savgol_filter(damping_coefficient, window_length=7, polyorder=2)

    if index_limits is not None:
        (ind_min, ind_max) = index_limits
        if plot:
            plt.plot(frequency[ind_min: ind_max], damping_coefficient[ind_min: ind_max], label="damping {} to {}".format(IMU_out, IMU_in))

        return(frequency[ind_min: ind_max], damping_coefficient[ind_min: ind_max])

    else:
        if plot:
            plt.plot(frequency, damping_coefficient, label="damping {} to {}".format(IMU_out, IMU_in))

        return(frequency, damping_coefficient)


def find_min_gt_index_in_ordered_array(array, value_test):
    for i, value in enumerate(array):
        if value > value_test:
            return(i)

    return(None)


f, _ = compute_damping("4", "6", distance_m=1500, plot=False)
f_min = 0.05
f_max = 0.1
ind_min = find_min_gt_index_in_ordered_array(f, f_min)
ind_max = find_min_gt_index_in_ordered_array(f, f_max)

plt.figure()

for crrt_IMU in list_IMUs_for_plot:
    f, Pxx_den = dict_welch_spectra[crrt_IMU]
    plt.plot(f[ind_min: ind_max], Pxx_den[ind_min: ind_max], label=crrt_IMU)
red_f = f[ind_min: ind_max]
plt.plot(red_f, noise(red_f), color='k', linestyle='--', linewidth=2, label='noise')
plt.legend()
plt.xlabel('Frq [Hz]')
plt.ylabel('PSD $\eta$')
plt.title("files between 2018-03-23_00:00:00 to 2018-03-23_05:00:00")
plt.tight_layout()
plt.show()

# figure without smooting ------------------------------------------------------
f, damping = compute_damping("5", "3", distance_m=distance_1, index_limits=(ind_min, ind_max), smoothing=False, plot=False)
f_min = 0.065
f_max = 0.09
ind_min = find_min_gt_index_in_ordered_array(f, f_min)
ind_max = find_min_gt_index_in_ordered_array(f, f_max)

list_all_damping = []
frequency_for_fit = []
damping_for_fit = []

plt.figure()

distance_1 = 1500
distance_2 = 2 * distance_1

# plot the dampings
f, damping = compute_damping("5", "3", distance_m=distance_1, index_limits=(ind_min, ind_max))
list_all_damping.append(damping)
frequency_for_fit = np.append(frequency_for_fit, f)
damping_for_fit = np.append(damping_for_fit, damping)
f, damping = compute_damping("5", "4", distance_m=distance_1, index_limits=(ind_min, ind_max))
list_all_damping.append(damping)
frequency_for_fit = np.append(frequency_for_fit, f)
damping_for_fit = np.append(damping_for_fit, damping)
f, damping = compute_damping("5", "2", distance_m=distance_2, index_limits=(ind_min, ind_max))
list_all_damping.append(damping)
frequency_for_fit = np.append(frequency_for_fit, f)
damping_for_fit = np.append(damping_for_fit, damping)
f, damping = compute_damping("5", "6", distance_m=distance_2, index_limits=(ind_min, ind_max))
list_all_damping.append(damping)
frequency_for_fit = np.append(frequency_for_fit, f)
damping_for_fit = np.append(damping_for_fit, damping)
f, damping = compute_damping("3", "2", distance_m=distance_1, index_limits=(ind_min, ind_max))
list_all_damping.append(damping)
frequency_for_fit = np.append(frequency_for_fit, f)
damping_for_fit = np.append(damping_for_fit, damping)
f, damping = compute_damping("3", "6", distance_m=distance_1, index_limits=(ind_min, ind_max))
list_all_damping.append(damping)
frequency_for_fit = np.append(frequency_for_fit, f)
damping_for_fit = np.append(damping_for_fit, damping)
f, damping = compute_damping("4", "2", distance_m=distance_1, index_limits=(ind_min, ind_max))
list_all_damping.append(damping)
frequency_for_fit = np.append(frequency_for_fit, f)
damping_for_fit = np.append(damping_for_fit, damping)
f, damping = compute_damping("4", "6", distance_m=distance_1, index_limits=(ind_min, ind_max))
list_all_damping.append(damping)
frequency_for_fit = np.append(frequency_for_fit, f)
damping_for_fit = np.append(damping_for_fit, damping)

array_damping = np.array(list_all_damping)
axis_damping = 0
mean_damping = np.mean(array_damping, axis=axis_damping)
std_damping = np.std(array_damping, axis=axis_damping)

# fit without taking into account uncertainty on spectra
viscosity, covariance = scipy.optimize.curve_fit(funcFitDecay, frequency_for_fit, damping_for_fit)
perr = np.sqrt(np.diag(covariance))

print " "
print "Parameters and fit quality from machine fit"
print "Viscosity from machine fit: " + str(viscosity)
print "1 sigma confidence: " + str(perr)

nu_weber = viscosity
# nu_weber = 0.015
number_std = 2
number_std_W = 6
plt.plot(f, mean_damping, color='b', linewidth=2, label="mean damping")
plt.fill_between(f, mean_damping - number_std * std_damping, mean_damping + number_std * std_damping, facecolor='red', alpha=0.2, label='mean damping uncertainty')
plt.plot(f, damping_Weber(f, nu=nu_weber), label="Weber $\\nu = {}$".format(nu_weber), color='k', linewidth=2)
plt.fill_between(f, damping_Weber(f, nu=nu_weber - number_std_W * perr), damping_Weber(f, nu=nu_weber + number_std_W * perr), color='black', alpha=0.2, label="Weber fit uncertainty")
plt.legend(ncol=3)
plt.xlabel("f [Hz]")
plt.ylabel("$\\alpha$ [$m^{-1}$]")
plt.xlim([f_min, f_max])
plt.ylim([-0.0002, 0.0008])
# plt.ylim([-0.0002, 0.0006])
plt.show()

#  -----------------------------------------------------------------------------
# rationale: too little signal to trust the innermost sensors at higher frequencies
# compute the damping based only on sensors outmost and in the middle. Look at the
# whole range where signal for the middle sensor; It is decided that there is signal
# for the middle sensor until middle sensor signal meets inner sensor signal

f, damping = compute_damping("5", "3", distance_m=distance_1, smoothing=False, plot=False)
f_min = 0.065
f_max = 0.16
ind_min = find_min_gt_index_in_ordered_array(f, f_min)
ind_max = find_min_gt_index_in_ordered_array(f, f_max)

list_all_damping = []
frequency_for_fit = []
damping_for_fit = []

plt.figure()

distance_1 = 1500
distance_2 = 2 * distance_1

# plot the dampings
f, damping = compute_damping("5", "3", distance_m=distance_1, index_limits=(ind_min, ind_max), smoothing=False)
list_all_damping.append(damping)
frequency_for_fit = np.append(frequency_for_fit, f)
damping_for_fit = np.append(damping_for_fit, damping)
f, damping = compute_damping("5", "4", distance_m=distance_1, index_limits=(ind_min, ind_max), smoothing=False)
list_all_damping.append(damping)
frequency_for_fit = np.append(frequency_for_fit, f)
damping_for_fit = np.append(damping_for_fit, damping)

array_damping = np.array(list_all_damping)
axis_damping = 0
mean_damping = np.mean(array_damping, axis=axis_damping)
std_damping = np.std(array_damping, axis=axis_damping)

# fit without taking into account uncertainty on spectra
viscosity, covariance = scipy.optimize.curve_fit(funcFitDecay, frequency_for_fit, damping_for_fit)
perr = np.sqrt(np.diag(covariance))

print " "
print "Parameters and fit quality from machine fit"
print "Viscosity from machine fit: " + str(viscosity)
print "1 sigma confidence: " + str(perr)

nu_weber = viscosity
# nu_weber = 0.015
number_std = 2
number_std_W = 6
# plt.plot(f, mean_damping, color='b', linewidth=2, label="mean damping")
# plt.fill_between(f, mean_damping - number_std * std_damping, mean_damping + number_std * std_damping, facecolor='red', alpha=0.2, label='mean damping uncertainty')
plt.plot(f, damping_Weber(f, nu=nu_weber), label="Weber $\\nu = {}$".format(nu_weber), color='k', linewidth=2)
plt.fill_between(f, damping_Weber(f, nu=nu_weber - number_std_W * perr), damping_Weber(f, nu=nu_weber + number_std_W * perr), color='black', alpha=0.2, label="Weber fit uncertainty")
plt.legend(ncol=2)
plt.xlabel("f [Hz]")
plt.ylabel("$\\alpha$ [$m^{-1}$]")
plt.xlim([f_min, f_max])
plt.ylim([-0.0002, 0.0008])
# plt.ylim([-0.0002, 0.0006])
plt.show()

# ------------------------------------------------------------------------------
# the previous figure is interesting, but it looks like some anomaly regarding
# damping around the peak frequency; what if this anomaly is suppressed?

distance_1 = 1500
distance_2 = 2 * distance_1

smooting = False

f, damping = compute_damping("5", "3", distance_m=distance_1, smoothing=smooting, plot=False)
f_min = 0.065
f_max = 0.079
f_min_total = f_min
f_min_interm = f_max
ind_min = find_min_gt_index_in_ordered_array(f, f_min)
ind_max = find_min_gt_index_in_ordered_array(f, f_max)

list_all_damping = []
frequency_for_fit = []
damping_for_fit = []

plt.figure()

f, damping = compute_damping("5", "3", distance_m=distance_1, index_limits=(ind_min, ind_max), smoothing=smooting)
list_all_damping.append(damping)
frequency_for_fit = np.append(frequency_for_fit, f)
damping_for_fit = np.append(damping_for_fit, damping)
f, damping = compute_damping("5", "4", distance_m=distance_1, index_limits=(ind_min, ind_max), smoothing=smooting)
list_all_damping.append(damping)
frequency_for_fit = np.append(frequency_for_fit, f)
damping_for_fit = np.append(damping_for_fit, damping)

f, damping = compute_damping("5", "3", distance_m=distance_1, smoothing=smooting, plot=False)
f_min = 0.105
f_max = 0.155
f_max_interm = f_min
f_max_total = f_max
ind_min = find_min_gt_index_in_ordered_array(f, f_min)
ind_max = find_min_gt_index_in_ordered_array(f, f_max)

f, damping = compute_damping("5", "3", distance_m=distance_1, index_limits=(ind_min, ind_max), smoothing=smooting)
list_all_damping.append(damping)
frequency_for_fit = np.append(frequency_for_fit, f)
damping_for_fit = np.append(damping_for_fit, damping)
f, damping = compute_damping("5", "4", distance_m=distance_1, index_limits=(ind_min, ind_max), smoothing=smooting)
list_all_damping.append(damping)
frequency_for_fit = np.append(frequency_for_fit, f)
damping_for_fit = np.append(damping_for_fit, damping)

array_damping = np.array(list_all_damping)
axis_damping = 0
# mean_damping = np.mean(array_damping, axis=axis_damping)
# std_damping = np.std(array_damping, axis=axis_damping)

# fit without taking into account uncertainty on spectra
viscosity, covariance = scipy.optimize.curve_fit(funcFitDecay, frequency_for_fit, damping_for_fit)
perr = np.sqrt(np.diag(covariance))

print " "
print "Parameters and fit quality from machine fit"
print "Viscosity from machine fit: " + str(viscosity)
print "1 sigma confidence: " + str(perr)

nu_weber = viscosity
# nu_weber = 0.015
number_std_W = 3
# plt.plot(f, mean_damping, color='b', linewidth=2, label="mean damping")
# plt.fill_between(f, mean_damping - number_std * std_damping, mean_damping + number_std * std_damping, facecolor='red', alpha=0.2, label='mean damping uncertainty')
f, damping = compute_damping("5", "3", distance_m=distance_1, smoothing=False, plot=False)
weber_with_uncertainty = ufloat(nu_weber, number_std_W * perr)
# plt.plot(f, damping_Weber(f, nu=nu_weber), label="Weber $\\nu = {:.2E} \pm {:.2E}$".format(nu_weber[0], number_std_W * perr[0]), color='k', linewidth=2)
plt.plot(f, damping_Weber(f, nu=nu_weber), label="Weber $\\nu = {:.1ue}$".format(weber_with_uncertainty), color='k', linewidth=2)
plt.fill_between(f, damping_Weber(f, nu=nu_weber - number_std_W * perr), damping_Weber(f, nu=nu_weber + number_std_W * perr), color='black', alpha=0.2, label="Weber fit uncertainty")


plt.legend(ncol=2)
plt.xlabel("f [Hz]")
plt.ylabel("$\\alpha$ [$m^{-1}$]")
plt.xlim([f_min_total, f_max_total])
plt.ylim([-0.0002, 0.0008])
# plt.ylim([-0.0002, 0.0006])
plt.show()

# summarizing figure -----------------------------------------------------------
f, damping = compute_damping("5", "3", distance_m=distance_1, smoothing=False, plot=False)
f_min = f_min_total
f_max = f_max_total
ind_min = find_min_gt_index_in_ordered_array(f, f_min)
ind_max = find_min_gt_index_in_ordered_array(f, f_max)

y_min = -0.0002
y_max = 0.001

plt.figure()

distance_1 = 1500

# plot the dampings
_ = compute_damping("5", "3", distance_m=distance_1, index_limits=(ind_min, ind_max), smoothing=False)
list_all_damping.append(damping)
frequency_for_fit = np.append(frequency_for_fit, f)
damping_for_fit = np.append(damping_for_fit, damping)
_ = compute_damping("5", "4", distance_m=distance_1, index_limits=(ind_min, ind_max), smoothing=False)
list_all_damping.append(damping)
frequency_for_fit = np.append(frequency_for_fit, f)
damping_for_fit = np.append(damping_for_fit, damping)

plt.plot(f, damping_Weber(f, nu=weber_with_uncertainty.nominal_value), label="Weber $\\nu = {:.1ue}$ m$^2$/s".format(weber_with_uncertainty), color='k', linewidth=2)
plt.fill_between(f, damping_Weber(f, nu=weber_with_uncertainty.nominal_value - weber_with_uncertainty.std_dev), damping_Weber(f, nu=weber_with_uncertainty.nominal_value + weber_with_uncertainty.std_dev), color='black', alpha=0.2, label="Weber fit uncertainty")

plt.fill_between([f_min_interm, f_max_interm], [y_min, y_min], [y_max, y_max], color='red', alpha=0.2, label="anomalous damping")

plt.legend(ncol=1, loc="upper right")
plt.xlabel("f [Hz]")
plt.ylabel("$\\alpha$ [$m^{-1}$]")
plt.xlim([f_min, f_max])
plt.ylim([y_min, y_max])
plt.tight_layout()
# plt.ylim([-0.0002, 0.0006])
plt.show()

# ------------------------------------------------------------------------------
# TODO
# - is it ok to do like this, or is there too little signal?
# - look at PSD eta_tt in both log and non log scale to see where signal
# - see if results the same when taking away the noise level
# - check orientation of the sensors (ie direction middle to outer) vs direction
# of the waves.

end = True
