
# Script for logging and displaying magnetometer serial data 
# Libraries required:
#  - pySerial 
# - matplotlib
#   - numPy 
#   - python-dateutil
# Written for the Honeywell HMR2300 magnetometer 
# Author: Zac DeMeo

import serial
import atexit
import time
import binascii
import numpy as np

### Begin script settings ###

# Serial communication settings
serialPort = 'COM5'
baud = 9600
par = serial.PARITY_NONE
sbits = serial.STOPBITS_ONE
bsize = serial.EIGHTBITS

# Terminal settings
displayOutput = True

# Data logging settings
logOutput = True

# Real time graph settings
graphOutput = False # Experimental
windowSize = 60 # Samples/window

### End script settings ###

### Functions ###
def onExit(s, f):
 try:
  s.write(chr(27)) # Send escape character; stop polling HMR2300 sensors
  s.close()
  if logOutput:
   f.close()
 except:
  print("Something went wrong...")

# Assumes HMR2300 ID is 00  
def setupMagnetometer(s):
 s.write('*00WE\r') # Activate "Write Enable"
 time.sleep(0.05)
 s.write('*00B\r') # Set to binary output (this allows for faster sampling rates)
 time.sleep(0.05)
 s.write('*00WE\r') # Activate "Write Enable"
 time.sleep(0.05)
 s.write('*00R=100\r') # Set device to 100 samples/s
 time.sleep(0.05)
 s.write('*00C\r') # Set HMR2300 to output data continuously
 time.sleep(0.05)
 
# Setup CSV logging 
def setupLogOutput(): 
 # Get system time and create CSV filename string
 t = time.localtime(time.time())
 filename = time.strftime('%d%b%y_%H;%M;%S', t) + '.csv'
 
 # Initialize CSV object and writer object
 f = open(filename, 'wb')
 
 return f
 
# Setup Writer object for writing CSV files 
def setupWriter(f):
 writer = csv.writer(f, dialect='excel')
 writer.writerow(('Sample', 'X (nT)', 'Y (nT)', 'Z (nT)')) # First row in CSV output
 
 return writer
 
# Initialize output plot variables
def setupGraphOutput():
 import matplotlib.pyplot as plt
 
 x = []
 y = []
 z = []
 tx = []
 
 fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, sharey=False) 
 plt.xlim(0, windowSize)
 ax1.set_ylabel('X (nT)')
 ax2.set_ylabel('Y (nT)')
 ax3.set_ylabel('Z (nT)')
 ax3.set_xlabel('Sample #')
 plt.ion() # Interactive mode on
 plt.show() # Show plot


 
### Main loop ###
if (displayOutput == False and logOutput == False and graphOutput == False):
 print("What exactly are you trying to accomplish?")
 exit()

# Initialize pySerial library 
s = serial.Serial(port=serialPort, baudrate=baud, parity=par, stopbits=sbits, bytesize=bsize)
setupMagnetometer(s)

if logOutput:
 import time
 import csv
 
 f = setupLogOutput() 
 writer = setupWriter(f)
else:
 f = None
 
if graphOutput:
 setupGraphOutput() 

# Register onExit() method to be called upon script termination
atexit.register(onExit, s, f) 
 
# Counter to keep track of how many samples have been collected
i = 0

# Now, start data acquisition
while True:
 line = ''
 #s.write('*00P\r') # Poll HMR2300 once
  
 while True:
  # Read byte from serial buffer
  char = s.read()
 
  # When a carriage return is read from buffer, convert line from binary to hex
  if char == '\r':
   line = binascii.hexlify(line)
   break
  else:
   line += char 
  
 # Break serial data into respective x-, y-, and z-components 
 hexLine = [line[:4], line[4:8], line[8:12]] # (X, Y, Z)
 
 # Convert each hex component to decimal. Python doesn't seem to preserve the sign of each hex value. Work around this.
 try:
  decLine = [int(hexLine[0], 16), int(hexLine[1], 16), int(hexLine[2], 16)] # (X, Y, Z)
 except:
  continue
 
 # Restore the sign of each measurement
 for j in range(0, 3):
  if decLine[j] >= 35536:
   decLine[j] -= 65536
   
 #print 'X: ' + str(decLine[0]) + ' Y: ' + str(decLine[1]) + ' Z: ' + str(decLine[2]) 
 
 # Update graph as serial data is processed
 if graphOutput:
  if n == windowSize * i:
   x = []
   y = []
   z = []
   tx = []
   
   i += 1
   plt.xlim(n, windowSize * i)
  
  tx.append(n)
  x.append(fParsedLine[0])
  y.append(fParsedLine[1])
  z.append(fParsedLine[2])
  ax1.plot(tx, x, 'b-')
  ax2.plot(tx, y, 'g-')
  ax3.plot(tx, z, 'r-')
  plt.draw()
  plt.pause(0.001)
 
 # Now, wait before polling HMR2300 again
 #time.sleep(.001) 

 # The first reading is usually incorrect. Throw the first sample out
 if i == 0:
  i += 1
  continue

 # Convert HMR2300 raw output to nT and round
 x = np.around(decLine[0] * 6.667, 1)
 y = np.around(decLine[1] * 6.667, 1)
 z = np.around(decLine[2] * 6.667, 1)

 # Print output to console
 if displayOutput:
  print('X: ' + str(x) + ' Y: ' + str(y) + ' Z: ' + str(z))

 # Write line to CSV file
 if logOutput:
  writer.writerow((i, x, y, z))
  
 i += 1
