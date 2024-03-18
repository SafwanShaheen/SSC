import numpy as np
from scipy.fft import rfft, rfftfreq
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from itertools import count
import pandas as pd
from collections import deque
from pathlib import Path

## Parse mock data
df = pd.read_csv('Real Time/data.csv') ## Set mock data file path

## Initialise empty lists and set constants
xread, yread = [], []
sampleRate = 10000                  ## Sample Frequency
counter = count(0,1)                ## Counter used to append next data point from CSV to lists

## Create ring buffer and number of data points for FFT
stop = 200
ybuffer = deque([], maxlen=stop)

## Create and initialise plot 
fig,[ax1, ax2] = plt.subplots(2)
fig.tight_layout(pad=5.0)
ax1.plot(xread, yread)

## Append new data point to empty lists, and calculate and return FFT
def read_and_process_data(idx):
    ## Append data points to empty lists
    xread.append(df.iloc[idx, 0])
    yread.append(df.iloc[idx, 2])
    ybuffer.append(df.iloc[idx, 2])                ## Append to ring buffer; removes oldest data point when new data point added
    
    ## Return 'null' data until ring buffer is full and FFT is ready to perform 
    default = 0
    displayMessage = 'Calibrating'

    ## Perform FFT and calculate power
    if len(ybuffer) >= stop:                       ## Perform FFT once ring buffer is full
        yfft = rfft(ybuffer)
        Amplitude = np.abs(yfft)
        Power = Amplitude**2
        xf = rfftfreq(stop, d=0.1 / sampleRate)

        ## Find position of peak power in list, and then find peak frequency
        peakPower = Power.argmax(axis=0)
        peakFreq = xf[peakPower]
        return Power, xf, peakFreq
    else:
        return default, default, displayMessage     ##Otherwise, return 'null' data

## Update graph
def update(i):
    idx = next(counter) ## Used to append next data point to list
    Power, xf, peakFreq = read_and_process_data(idx)
    ## Plot breathing monitor trace
    ax1.cla()
    ax1.plot(xread,yread)
    ax1.title.set_text('Breathing Monitor')
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Sensor Value (arb)')
    ## Plot frequency domain
    ax2.cla()
    ax2.plot(xf, Power)
    ax2.title.set_text('Frequency Domain')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Power (arb)')
    ## Display peak frequency
    ax2.text(0.7, 0.9, 'Peak Frequency (Hz):' + str(peakFreq), horizontalalignment='center', verticalalignment='center', transform=ax2.transAxes)

## Animate and show plot
ani = FuncAnimation(fig=fig, func = update, interval=200) 
plt.show()