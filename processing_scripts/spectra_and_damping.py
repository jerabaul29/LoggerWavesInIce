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
from GPS_distances import distance_1
from GPS_distances import distance_2
from uncertainties import ufloat

path_IMU_data = "/media/jrlab/SAMSUNG/DataJeanAnalysisSvalbardMarch2018_segments_13_to_18/"


def find_min_gt_index_in_ordered_array(array, value_test):
    for i, value in enumerate(array):
        if value > value_test:
            return(i)
    return(None)


def get_Down(dict_data, IMU_ID):
    return(dict_data[IMU_ID][:, 6])


def get_Time_Base(dict_data, IMU_ID):
    return(dict_data[IMU_ID][:, 0])


def func_Weber_damping(frq, nuFit):
    return (nuFit**0.5) * ((2 * np.pi * frq)**(7. / 2.)) / (2**0.5) / (9.81**2)


def compute_vertical_elevation_method_Graig(data_in, FS=10.0, IMU_detrend="constant"):
        '''integrate twice using fft and ifft, in addition filtering by Kohout'''

        np.seterr(divide='ignore')

        # calculate fft, filter, and then ifft to get heights

        # suppress divide by 0 warning
        # np.seterr(divide='ignore')

        data_det = signal.detrend(data_in, type=IMU_detrend)

        Y = np.fft.fft(data_det)

        # calculate weights before applying ifft
        freq = np.fft.fftfreq(data_det.size, d=1.0 / FS)
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


def compute_polynomial_approximation_noise(dict_all_loaded_data, list_IMUs, (time_start, time_end), (min_frq, max_frq)=(0.005, 0.5), nperseg=10 * 60 * 5, overlap_proportion=0.95, order=8, FS=10):
    common_time_base = get_Time_Base(dict_all_loaded_data, list_IMUs[0])

    ind_start = find_min_gt_index_in_ordered_array(common_time_base / 3600.0, time_start)
    ind_end = find_min_gt_index_in_ordered_array(common_time_base / 3600.0, time_end)

    overlap = int(nperseg * overlap_proportion)

    x_data_for_fit = np.array([])
    y_data_for_fit = np.array([])

    plt.figure()

    for crrt_IMU in list_IMUs:
        all_D_data = get_Down(dict_all_loaded_data, crrt_IMU)
        selected_D_data = all_D_data[ind_start: ind_end]
        f, Pxx_den = signal.welch(selected_D_data, FS, nperseg=nperseg, noverlap=overlap)
        min_ind = find_min_gt_index_in_ordered_array(f, min_frq)
        max_ind = find_min_gt_index_in_ordered_array(f, max_frq)
        plt.plot(f[min_ind: max_ind], Pxx_den[min_ind: max_ind], label=crrt_IMU)
        x_data_for_fit = np.concatenate((x_data_for_fit, f[min_ind: max_ind]), 0)
        y_data_for_fit = np.concatenate((y_data_for_fit, Pxx_den[min_ind: max_ind]), 0)

    p_fit_data = np.polyfit(x_data_for_fit, y_data_for_fit, order)
    p_noise_level = np.poly1d(p_fit_data)

    plt.plot(f[min_ind: max_ind], p_noise_level(f[min_ind: max_ind]), label="noise fit", linewidth=4)

    plt.legend()
    plt.xlabel('Frq [Hz]')
    plt.ylabel('PSD $\eta_{tt}$')
    plt.tight_layout()
    plt.show()

    return(p_noise_level)


def show_spectra(dict_all_loaded_data, IMU_list, (time_start, time_end), nperseg=10 * 60 * 7, overlap_proportion=0.95, p_noise_level=None, min_frq=0.005, max_frq=0.5, flag_Omega_4=False):
    common_time_base = get_Time_Base(dict_all_loaded_data, IMU_list[0])

    ind_start = find_min_gt_index_in_ordered_array(common_time_base / 3600.0, time_start)
    ind_end = find_min_gt_index_in_ordered_array(common_time_base / 3600.0, time_end)

    overlap = int(nperseg * overlap_proportion)

    list_Pxx = []

    plt.figure()

    for crrt_IMU in IMU_list:
        all_D_data = get_Down(dict_all_loaded_data, crrt_IMU)
        selected_D_data = all_D_data[ind_start: ind_end]
        f, Pxx_den = signal.welch(selected_D_data, FS, nperseg=nperseg, noverlap=overlap)
        min_ind = find_min_gt_index_in_ordered_array(f, min_frq)
        max_ind = find_min_gt_index_in_ordered_array(f, max_frq)
        f = f[min_ind: max_ind]
        Pxx_den = Pxx_den[min_ind: max_ind]

        if flag_Omega_4:
            omega_4 = (2 * np.pi * f)**4
            Pxx_den = Pxx_den / omega_4

        if p_noise_level is not None:
            Pxx_den = Pxx_den - p_noise_level(f)
        list_Pxx.append(Pxx_den)
        plt.plot(f, Pxx_den, label=crrt_IMU)
    plt.legend()
    plt.xlabel('Frq [Hz]')
    if flag_Omega_4:
        plt.ylabel('PSD $\eta$')
    else:
        plt.ylabel('PSD $\eta_{tt}$')
    plt.xlim([0.005, 0.3])
    plt.tight_layout()
    plt.show()

    return(f, list_Pxx)


def compute_show_damping(dict_spectral_data, (list_IMU_1, list_IMU_2), distance, (frq_min_damping, frq_max_damping), bands_to_avoid_in_fitting):
    total_frq_for_fit_damping = np.array([])
    total_alpha_for_fit_damping = np.array([])

    plt.figure()

    for crrt_IMU_1 in list_IMU_1:
        for crrt_IMU_2 in list_IMU_2:
            print("Use IMUs {} and {}".format(crrt_IMU_1, crrt_IMU_2))

            frq = dict_spectral_data["f"]
            Paa_1 = dict_spectral_data[crrt_IMU_1]
            Paa_2 = dict_spectral_data[crrt_IMU_2]

            min_ind = find_min_gt_index_in_ordered_array(frq, frq_min_damping)
            max_ind = find_min_gt_index_in_ordered_array(frq, frq_max_damping)

            frq_red = frq[min_ind: max_ind]
            Paa_1_red = Paa_1[min_ind: max_ind]
            Paa_2_red = Paa_2[min_ind: max_ind]

            amplitude_attenuation = np.sqrt(Paa_1_red / Paa_2_red)
            alpha = 1.0 / distance * np.log(amplitude_attenuation)

            mask_bands_bool = np.ones_like(alpha, dtype=np.int)

            for crrt_band in bands_to_avoid_in_fitting:
                crrt_min_freq = find_min_gt_index_in_ordered_array(frq_red, crrt_band[0])
                crrt_max_freq = find_min_gt_index_in_ordered_array(frq_red, crrt_band[1])

                mask_bands_bool[crrt_min_freq: crrt_max_freq] = 0

            mask_avoid_bands = np.where(mask_bands_bool == 1)
            mask_bands = np.where(mask_bands_bool == 0)

            frq_of_the_bands = frq_red[mask_bands]
            ones_size_of_bands = np.ones_like(frq_of_the_bands)

            frq_for_fit_damping = frq_red[mask_avoid_bands]
            alpha_for_fit_damping = alpha[mask_avoid_bands]

            total_frq_for_fit_damping = np.concatenate((total_frq_for_fit_damping, frq_for_fit_damping), axis=0)
            total_alpha_for_fit_damping = np.concatenate((total_alpha_for_fit_damping, alpha_for_fit_damping), axis=0)

            # plt.plot(frq_for_fit_damping, alpha_for_fit_damping, label="measurements", marker='*', linestyle='')
            plt.plot(frq_red, alpha, label="damping {} to {}".format(crrt_IMU_1, crrt_IMU_2), marker='*', linestyle='')

    # fit without taking into account uncertainty on spectra
    viscosity, covariance = scipy.optimize.curve_fit(func_Weber_damping, total_frq_for_fit_damping, total_alpha_for_fit_damping)
    perr = np.sqrt(np.diag(covariance))

    print " "
    print "Parameters and fit quality from machine fit"
    print "Viscosity from machine fit: " + str(viscosity[0])
    print "1 sigma confidence: " + str(perr[0])

    nsigma = 3
    weber_with_uncertainty = ufloat(viscosity[0], nsigma * perr[0])

    plt.fill_between(frq_of_the_bands, -100.0 * ones_size_of_bands, 100.0 * ones_size_of_bands, color='gray', alpha=0.2, label="avoided frequencies")
    plt.plot(frq_red, func_Weber_damping(frq_red, viscosity), label="Weber $\\nu = {:.1ue}$".format(weber_with_uncertainty), linewidth=2, color='r')
    plt.fill_between(frq_red, func_Weber_damping(frq_red, viscosity - nsigma * perr), func_Weber_damping(frq_red, viscosity + nsigma * perr), color='red', alpha=0.2, label="{} sigma".format(nsigma))
    plt.legend()
    if np.min(alpha) < 0:
        plt.ylim([np.min(alpha) * 1.2, np.max(alpha) * 1.2])
    else:
        plt.ylim([-np.min(alpha) * 1.2, np.max(alpha) * 1.2])

    plt.xlabel("F [Hz]")
    plt.ylabel("$\\alpha$ (m$^{-1}$)")

    plt.tight_layout()

    plt.show()


FS = 10

# load all the data ------------------------------------------------------------
# list_IMUs_To_Use = ["2", "3", "4", "5", "6"]
list_IMUs_To_Use = ["5", "3", "4", "2", "6"]

dict_all_loaded_data = {}

for crrt_IMU in list_IMUs_To_Use:
    crrt_filename = path_IMU_data + "CSV_DATA_" + str(crrt_IMU) + ".csv"
    print("Loading {}".format(crrt_filename))
    dict_all_loaded_data[crrt_IMU] = np.genfromtxt(crrt_filename, skip_header=1)

common_time_base = get_Time_Base(dict_all_loaded_data, "5")
# ------------------------------------------------------------------------------

# use a sensor with no signal to get the background noise level
time_start = 16.5
time_end = 19.5
time_limits = (time_start, time_end)
list_IMUs = ["2", "6"]

p_noise_level = compute_polynomial_approximation_noise(dict_all_loaded_data, list_IMUs, time_limits)

# look at the acceleration spectra ---------------------------------------------
time_start = 8.5
# time_end = 12.5
time_end = 12.5
time_limits = (time_start, time_end)

dict_Paa = {}
(dict_Paa["f"], [dict_Paa["5"], dict_Paa["3"], dict_Paa["4"], dict_Paa["2"], dict_Paa["6"]]) = show_spectra(dict_all_loaded_data, list_IMUs_To_Use, time_limits, p_noise_level=None)

(f_less_noise, list_Pxx_less_noise) = show_spectra(dict_all_loaded_data, list_IMUs_To_Use, time_limits, p_noise_level=p_noise_level)

_ = show_spectra(dict_all_loaded_data, list_IMUs_To_Use, time_limits, p_noise_level=None, flag_Omega_4=True)

_ = show_spectra(dict_all_loaded_data, list_IMUs_To_Use, time_limits, p_noise_level=None, flag_Omega_4=True, min_frq=0.05, max_frq=0.20)

# look at the damping ----------------------------------------------------------
frq_min_damping = 0.055
frq_max_damping = 0.17

frq_for_damping_computations = (frq_min_damping, frq_max_damping)

bands_to_avoid_in_fitting = ([0.07, 0.12],)

distance = distance_1

list_IMU_1 = ["5"]
list_IMU_2 = ["3", "4"]

list_IMUs = (list_IMU_1, list_IMU_2)

compute_show_damping(dict_Paa, list_IMUs, distance, frq_for_damping_computations, bands_to_avoid_in_fitting)

# other look at damping attempts -----------------------------------------------
frq_min_damping = 0.05
frq_max_damping = 0.085

frq_for_damping_computations = (frq_min_damping, frq_max_damping)

bands_to_avoid_in_fitting = ()

distance = 2 * distance_1

list_IMU_1 = ["5"]
list_IMU_2 = ["2", "6"]

list_IMUs = (list_IMU_1, list_IMU_2)

compute_show_damping(dict_Paa, list_IMUs, distance, frq_for_damping_computations, bands_to_avoid_in_fitting)

# TODO: in computing the damping: check the orientation of the IMU array vs the direction of the waves
# TODO: understand why this strange damping; possibility: unhomogeneous ice, with icebergs frozen in? or large floes frozen together?

end_file = True
