import serial
from serial.tools import list_ports
import numpy as np
from scipy.fft import rfft, rfftfreq
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from itertools import count
from collections import deque
import csv

# Identify the correct port and print to console
ports = list_ports.comports()
for port in ports: print(port)

# Set constants e.g, port & baud rate
SERIAL_PORT = 'COM3'
BAUD_RATE = 9600
counter = 0

# Open serial com, and adjust to appropriate arduino port
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

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
    # Reads serial com, decodes from binary, and splits the string with commas to separate headers/data
    line = ser.readline().decode('utf-8').strip()
    values = line.split(', ')

	# Append values to empty lists
    xread.append(float(values[0]))
    yread.append(float(values[2]))
    ybuffer.append(float(values[2]))

	# Debug print statement
    print(f'Time: {values[0]}, Sensor Data: {values[1]}')

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

# Create a function to save data to a CSV file when plot is closed, in order to check trace in the future
def on_close(event):
	with open('breathing_monitor_data.csv', 'w', newline='') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(['Time', 'Sensor Data'])
		for x, s in zip(xread, yread):
			writer.writerow([x, s])

## Animate and show plot
fig.canvas.mpl_connect('close_event', on_close)
ani = FuncAnimation(fig=fig, func = update, interval=200) 
plt.show()