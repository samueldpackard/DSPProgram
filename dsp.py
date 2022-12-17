import scipy
import numpy as np



def calculateFreq_range_choice(freq):
    exp = np.log10(freq)

    upper_range = exp + 0.176
    lower_range = exp - 0.176

    return 10**(upper_range), 10**(lower_range)


def calculateFreq_range_filter(freq):
    exp = np.log10(freq)

    upper_range = exp + 0.022
    lower_range = exp - 0.022

    return 10**(upper_range), 10**(lower_range)

def second_order_bell_filter(f01, BW, fs):

    w0 = 2 * np.pi * f01 / fs
    Q = f01 / BW

    cos = np.cos(w0)
    alpha = np.sin(w0) / (2 * Q)
    A = 3.16

    b = [1 + (alpha * A), -2 * cos, 1 - (alpha * A)]
    a = [1 + (alpha / A), -2 * cos, 1 - (alpha / A)]

    return b, a


def bandstop_bandpass_filter(input_signal, Q, f0, fs, bell=False):

    # For storing the allpass output
    allpass_filtered = np.zeros_like(input_signal)

    # Initialize filter's buffers
    x1 = 0
    x2 = 0
    y1 = 0
    y2 = 0

    # Process the input signal with the allpass
    for i in range(input_signal.shape[0]):
        # Calculate the bandwidth from Q and center frequency
        BW = f0 / Q

        # Get the coefficients
        b, a = second_order_bell_filter(f0, BW, fs)

        x = input_signal[i]

        # Actual allpass filtering:
        # difference equation of the second-order allpass
        y = b[0] * x + b[1] * x1 + b[2] * x2 - a[1] * y1 - a[2] * y2
        # y = (b[0] / a[0]) * x + (b[1] / a[0]) * x1 + (b[2] / a[0]) * x2 - (a[1] / a[0]) * y1 - (a[2] / a[0]) * y2
        # Update the filter's buffers
        y2 = y1
        y1 = y
        x2 = x1
        x1 = x

        # Assign the resulting sample to the output array
        allpass_filtered[i] = y

    output = 0.5 * allpass_filtered
    # output = allpass_filtered

    return output