import numpy
from PyQt5.QtWidgets import QWidget, QSlider, QHBoxLayout,QLabel, QApplication, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
import sys
import random
import numpy as np
# import pydub
import os
from dsp import *
import pygame
import librosa
import scipy
from scipy import signal
import matplotlib.pyplot as plt
import sounddevice

# This is an example pull request
#TODO:: figure out why it plays first
#fix the result label
#TODO: play the selected frequency ot compare it with the actual

class Example(QWidget):

    def __init__(self):
        super().__init__()
        pygame.mixer.pre_init()
        pygame.mixer.init()
        pygame.init()
        pygame.mixer.music.set_volume(0.3)
        #do DSP first and then play sound
        self.initUI()
        self.createSoundChannels()


    def initUI(self):

        #box layout
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()

        #slider
        sld = QSlider(Qt.Orientation.Horizontal, self)
        sld.setRange(100, 20_000)
        sld.setPageStep(5)
        sld.valueChanged.connect(self.updateLabel)

        #button to re_randomize number
        self.rand_button = QPushButton('Modulate new Frequency', self)
        self.rand_button.clicked.connect(self.reselectFreq)
        self.rand_button.move(200,300)
        self.rand_button.resize(250, 25)

        #button to submit selected freq
        self.submit_button = QPushButton('Check', self)
        self.submit_button.clicked.connect(self.checkFreq)
        self.submit_button.move(100,300)

        #button to switch audio
        self.toggle_button = QPushButton('Toggle Audio that is playing', self)
        self.toggle_button.clicked.connect(self.switchAudio)
        self.toggle_button.adjustSize()
        self.toggle_button.move(100,330)

        #label to indicate which audio is playing
        self.is_playing_label = QLabel('Playing Original . . .', self)
        self.is_playing_label.move(100, 355) #right below switch button
        self.is_playing_label.adjustSize()
        self.is_playing_label.frameRect()

        #label
        self.label = QLabel('Value: 0', self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter |
                                Qt.AlignmentFlag.AlignVCenter)
        self.label.setMinimumWidth(100)

        #checks which audio to play
        self.original_is_playing = True

        #random frequency
        # self.rand_freq = random.randint(200, 20_000)
        x = random.uniform(40, 45)
        y = random.uniform(18_000, 20_000)

        array_random_bins = numpy.geomspace(x, y, 50)
        print(array_random_bins)

        self.rand_freq = array_random_bins[random.randint(0,len(array_random_bins) - 1)]


        #label rand
        self.rand_label = QLabel(str(self.rand_freq))
        self.rand_label.resize(100,25)
        hbox.addWidget(self.rand_label)
        hbox.addSpacing(15)

        #initialize slider number
        self.slider_number = 100

        #Results Label
        self.results = QLabel('Frequency not checked')
        self.results.setHidden(True)
        self.results.move(200,200)
        self.results.adjustSize()
        # self.results.font().setBold()

        #add widgets to the hbox
        hbox.addWidget(sld)
        hbox.addSpacing(15)
        hbox.addWidget(self.label)
        hbox.addSpacing(15)

        print(self.rand_freq)

        #setLayout
        self.setLayout(hbox)
        self.setGeometry(400, 400, 450, 450)
        self.setWindowTitle('QSlider')
        self.show()

    def switchAudio(self):
        #switch which audio is playing
        self.original_is_playing = not self.original_is_playing

        if self.original_is_playing:
            #play original audio
            pygame.mixer.Channel(0).set_volume(0.3)

            #mute filered
            pygame.mixer.Channel(1).set_volume(0)

            #indicate that original audio is playing
            self.is_playing_label.setText('Playing Original . . .')

        else:
            print("Filtered is called")
            #play filtered
            pygame.mixer.Channel(1).set_volume(0.3)

            #mute original
            pygame.mixer.Channel(0).set_volume(0)

            #indicate that filtered is playing
            self.is_playing_label.setText('Playing Filtered . . .')

    def reselectFreq(self):
        #use DSP abstraction to refilter the next sound
        self.rand_freq = random.randint(200, 20_000)
        self.rand_label.setText(str(self.rand_freq))
        self.results.setHidden(True)

    def updateLabel(self, value):
        self.slider_number = value
        self.theText = "Value: " + str(value) + " hertz"
        self.label.setText(self.theText)

    def checkFreq(self):
        self.upper_range, self.lower_range = calculateFreq_range_choice(self.rand_freq)

        print("Your frequency is {}. You need to be between {} and {}".format( self.rand_freq, self.lower_range, self.upper_range,))
        print("You chose {}.".format(self.slider_number))
        if self.lower_range < self.slider_number < self.upper_range:
            print("in range")
            self.results.setHidden(False)
            self.results.setText("You are in range! The boosted frequecy was {} and you picked {} which was in range of the Q factor!".format(self.rand_freq, self.slider_number))
            return True
        else:
            print("not in range you suck!")
            self.results.setHidden(False)
            self.results.setText(
                "You are not in range! The boosted frequecy was {} and you picked {} which was not in range of the Q factor!".format(
                    self.rand_freq, self.slider_number))
            return False
    def createSoundChannels(self):


        # play a sound on channel 0

        pygame.mixer.Channel(0).play(pygame.mixer.Sound('original.mp3'), loops=-1)
        pygame.mixer.Channel(0).set_volume(0.3)
        self.original_is_playing = True

        # you can play a longer sound on another channel and they won't conflict
        pygame.mixer.Channel(1).play(pygame.mixer.Sound("filtered.mp3"), loops=-1)
        pygame.mixer.Channel(1).set_volume(0)



def main():
    # initialize GUI
    app = QApplication(sys.argv)
    ex = Example()

    # start playing the background music
    # pygame.mixer.music.load(os.path.join(os.getcwd(), 'sound', 'main_theme.wav'))

    # pygame.mixer.music.play(loops=-1)  # loop forever

    #intialize pygame mixer

    #paramters
    fs = 44100
    length_seconds = 6
    length_samples = fs * length_seconds
    Q = 20
    # f0 = 1_700
    f0 = ex.rand_freq

    # y, sr = librosa.load(filename, offset=15.0, duration=5.0)
    #TODO:learn how to use libroas.load when mono = False

    data, sr = librosa.load("twin.mp3", duration = 40, mono = False, sr = 44100)
    # data, sr = librosa.load("white noise.mp3", duration = 4, sr=44100)
    # data, sr = librosa.load("shakey test.mp3", duration=8, sr=44100, mono=False)


    sample_freq = sr
    low_corner = 2_000.0
    high_corner = 4_000.0

    nyq = 0.5 * sample_freq

    low = low_corner / nyq
    high = high_corner / nyq

    #Nth order filter if you are doing a bandpass filter the order can not be too high
    order = 3

    #get b and a coeeficients for an IIR filter
    # b, a = scipy.signal.butter(order, [low,high], 'bandpass', analog = False)
    # Q = 30
    # b, a = signal.iirpeak(high, Q, sr)
    # filtered_data = scipy.signal.filtfilt(b, a, data, axis = 0)

    target_freq = 2_000

    f_step = sr / (len(data[0]))

    f = np.linspace(0, (len(data[0]) - 1) * f_step, len(data[0]))

    yf_l = scipy.fft.rfft(data[0])
    yf_r = scipy.fft.rfft(data[1])
    xf = scipy.fft.rfftfreq(len(data[0]), 1 / sr)

    yf_mag_l = np.abs(yf_l) / len(data[0])
    yf_mag_r = np.abs(yf_r) / len(data[0])

    f_plot = f[0:int(len(data[0])/2+1)]
    yf_mag_plot_l = 2 * yf_mag_l[0:int(len(data[0])/2+1)]
    yf_mag_plot_r = 2 * yf_mag_r[0:int(len(data[0]) / 2 + 1)]

    yf_mag_plot_l[0] = yf_mag_plot_l[0] / 2
    yf_mag_plot_r[0] = yf_mag_plot_r[0] / 2


    points_per_freq = len(xf) / (sr / 2)
    target_idx = int(points_per_freq * target_freq)


    #make it more analog by ramping up
    upper_freq, lower_freq = calculateFreq_range_filter(target_freq)
    # print(lower_freq, upper_freq)

    #all pass bell filter
    yf_l[target_idx - int(( lower_freq)): target_idx + int(( upper_freq))] = yf_l[target_idx - int((lower_freq)): target_idx + int(( upper_freq))] * 5
    yf_r[target_idx - int((lower_freq)): target_idx + int((upper_freq))] = yf_r[target_idx - int(( lower_freq)): target_idx + int((upper_freq))] * 5


    #get FFT of unfiltered and filtered FFT
    unfiltered_fft_l = scipy.fft.rfft(data[0])
    unfiltered_fft_r = scipy.fft.rfft(data[1])


    filtered_fft_l = unfiltered_fft_l
    filtered_fft_r = unfiltered_fft_r

    # filtered_data_l = scipy.fft.irfft(yf_l)
    # filtered_data_r = scipy.fft.irfft(yf_r)
    filtered_data_l = bandstop_bandpass_filter(data[0], Q, f0, fs)
    filtered_data_r = bandstop_bandpass_filter(data[1], Q, f0, fs)


    # filtered_fft = scipy.fft.fft(filtered_data)

    #x-axis to plots
    x_unfiltered_l = np.arange(0, len(data[0]))
    x_unfiltered_r = np.arange(0, len(data[1]))


    x_filtered_l = np.arange(0, len(filtered_data_l))
    x_filtered_r = np.arange(0, len(filtered_data_r))

    x_unfiltered_fft_l = np.arange(0, len(unfiltered_fft_l))
    x_unfiltered_fft_r = np.arange(0, len(unfiltered_fft_r))

    x_filtered_fft_l = np.arange(0, len(yf_l))
    x_filtered_fft_r = np.arange(0, len(yf_r))


    f_step_l = sr / (len(x_unfiltered_l))
    f_step_r = sr / (len(x_unfiltered_r))

    print(data)
    data[0] = 0.5 * data[0]
    data[1] = 0.5 * data[1]
    print(data)


    f_l = np.linspace(0, (len(data[0]) - 1) * f_step, len(data[0]))

    yf = scipy.fft.rfft(data[0])
    xf = scipy.fft.rfftfreq(len(data[0]), 1 / sr)

    yf_mag = np.abs(yf) / len(data[0])

    f_plot = f[0:int(len(data[0])/2+1)]
    yf_mag_plot = 2 * yf_mag[0:int(len(data[0])/2+1)]
    yf_mag_plot[0] = yf_mag_plot[0] / 2


    #x-axis for filtered plot
    yf_filtered = scipy.fft.rfft(filtered_data_l)
    xf = scipy.fft.rfftfreq(len(filtered_data_l), 1 / sr)

    yf_mag_filtered = np.abs(yf_filtered) / len(filtered_data_l)

    f_plot_filtered = f[0:int(len(filtered_data_l) / 2 + 1)]
    yf_mag_plot_filtered = 2 * yf_mag_filtered[0:int(len(filtered_data_l) / 2 + 1)]
    yf_mag_plot_filtered[0] = yf_mag_plot_filtered[0] / 2

    #amplitude of FFT's
    # f_unfiltered = np.linspace(0, (x_unfiltered.size - 1)*sr, x_unfiltered.size)
    # x_unfiltered_mag = np.abs(x_unfiltered_fft) / x_unfiltered.size

    figure, axis = plt.subplots(2,2)

    #formatting the plots
    figure.tight_layout(pad=2.0)

    #first plot
    axis[0,0].tick_params(axis='x', rotation = 10)
    axis[0,0].set_title("song unfiltered time domain")
    axis[0,0].plot(x_unfiltered_l, data[0])


    #second plot
    axis[1,0].tick_params(axis='x', rotation=10)
    axis[1,0].set_title("song filtered time domain")
    axis[1,0].plot(x_filtered_l, filtered_data_l)

    #unfiltered fft
    #testing logarithmic axis
    axis[0,1].set_xscale('log')

    axis[0,1].tick_params(axis='x', rotation=10)
    axis[0,1].set_title("song unfiltered FFT")
    # axis[0,1].plot(x_unfiltered_fft, unfiltered_fft)
    axis[0, 1].plot(f_plot, yf_mag_plot)
    # axis[0,1].plot
    # axis[0, 1].plot(f_unfiltered, unfiltered_fft)


    #filtered fft
    axis[1,1].set_xscale('log')

    axis[1, 1].tick_params(axis='x', rotation=10)
    axis[1, 1].set_title("song filtered FFT")
    # axis[1, 1].plot(x_filtered_fft_l, yf)
    axis[1,1].plot(f_plot_filtered, yf_mag_plot_filtered)


    #save plots as png
    plt.savefig('4_plots.png', dpi=1000)
    plt.show()

    #combine 2-d array
    filtered_data_both = []
    filtered_data_both.append(filtered_data_l)
    filtered_data_both.append(filtered_data_r)

    filtered_data_both = np.transpose(filtered_data_both)


    #convert the array to an mp3
    # scipy.io.wavfile.write("original.mp3", sr, data.astype(np.float16))



    data_transposed = np.transpose(data)
    print(data_transposed)


    scipy.io.wavfile.write("original.mp3", sr, data_transposed.astype(np.float32))
    scipy.io.wavfile.write("filtered.mp3", sr, filtered_data_both.astype(np.float32))

    sys.exit(app.exec())


if __name__ == '__main__':
    main()