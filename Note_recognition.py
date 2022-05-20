import pyaudio
import os
import struct
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
import time
from tkinter import TclError
from pynput.keyboard import Key, Controller

keyboard = Controller()

# use this backend to display in separate Tk window
56

# constants
CHUNK = 1024 * 2             # samples per frame
FORMAT = pyaudio.paInt16     # audio format (bytes per sample?)
CHANNELS = 1                 # single channel for microphone
RATE = 44100                 # samples per second

# create matplotlib figure and axes
fig, (ax1, ax2) = plt.subplots(2, figsize=(15, 7))

# pyaudio class instance
p = pyaudio.PyAudio()

# get list of availble inputs
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print ("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

# select input
audio_input = input("\n\nSelect input by Device id: ")

# stream object to get data from microphone
stream = p.open(
    input_device_index=int(audio_input),
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

# variable for plotting
x = np.arange(0, 2 * CHUNK, 2) # samples (waveform)
xf = np.linspace(0, RATE, CHUNK) # frequencies (spectrum)

# create a line object with random data
line, = ax1.plot(x, np.random.rand(CHUNK), '-', lw=2)

# create semilogx line for spectrum
line_fft, = ax2.semilogx(xf, np.random.rand(CHUNK), '-', lw=2)

# format waveform axes
ax1.set_title('AUDIO WAVEFORM')
ax1.set_xlabel('samples')
ax1.set_ylabel('volume')
ax1.set_ylim(0, 255)
ax1.set_xlim(0, 2 * CHUNK)
plt.setp(ax1, xticks=[0, CHUNK, 2 * CHUNK], yticks=[0, 128, 255])

# format spectrum axes
ax2.set_xlim(20, RATE / 2)

# show the plot
plt.show(block=False)

print('stream started')

# for measuring frame rate
frame_count = 0
start_time = time.time()

while True:
    # binary data
    data = stream.read(CHUNK)  
    
    # convert data to integers, make np array, then offset it by 128 (amplitude / 2 = 256 / 2)
    data_int = struct.unpack(str(2 * CHUNK) + 'B', data)
    
    # create np array and offset by 128
    data_np = np.array(data_int, dtype='b')[::2] + 128
    
    line.set_ydata(data_np) # waveform Y data
    
    # compute FFT and update line
    yf = fft(data_int) # 2 chunks
    cyf = np.abs(yf[0:CHUNK])  / (128 * CHUNK) # spectrum Y data (1 chunk)
    line_fft.set_ydata(cyf) 

    # frequency
    gv = 0
    xrel = 0
    for i in range(len(cyf)):
        if cyf[i] > gv and i != 0:
            gv = cyf[i]
            xrel = xf[i]

    freq = round(xrel / 2)
    print(freq)

    # probably should put in seperate function but too lazy now
    # keys = ['a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    
    # c = 259 # 261.626
    # d = 280 # 293.665
    # e = 323 # 329.628
    # f = 366 # 349.228
    
    # b = 237 # 246.942

    # if freq == c:
    #     print('keydetected = C')
    #     kp = 'a'
    #     keyboard.press(kp)

    #     for k in keys:
    #         if k != kp:
    #             keyboard.release(k)
    # elif freq == d:
    #     print('keydetected = D')
    #     kp = 'w'
    #     keyboard.press(kp)

    #     for k in keys:
    #         if k != kp:
    #             keyboard.release(k)
    # elif freq == e:
    #     print('keydetected = E')
    #     kp = 'd'
    #     keyboard.press(kp)

    #     for k in keys:
    #         if k != kp:
    #             keyboard.release(k)
    # elif freq == f:
    #     print('keydetected = F')
    #     kp = 's'
    #     keyboard.press(kp)

    #     for k in keys:
    #         if k != kp:
    #             keyboard.release(k)
    # elif freq == b:
    #     print('keydetected = B')
    #     for k in keys:
    #         keyboard.release(k)

    # update figure canvas
    try:
        fig.canvas.draw()
        fig.canvas.flush_events()
        frame_count += 1

    except TclError:

        # calculate average frame rate
        frame_rate = frame_count / (time.time() - start_time)

        print('stream stopped')
        print('average frame rate = {:.0f} FPS'.format(frame_rate))
        break

