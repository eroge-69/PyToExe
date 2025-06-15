Python 3.14.0a3 (tags/v3.14.0a3:401bfc6, Dec 17 2024, 10:58:10) [MSC v.1942 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> import time
... import matplotlib.pyplot as plt
... from drawnow import *
... import serial
... val = [ ]
... cnt = 0
... #create the serial port object
... port = serial.Serial('COM4', 115200, timeout=0.5)
... plt.ion()
... #create the figure function
... def makeFig():
...     plt.ylim(-1023,1023)
...     plt.title('Osciloscope')
...     plt.grid(True)
...     plt.ylabel('data')
...     plt.plot(val, 'ro-', label='Channel 0')
...     plt.legend(loc='lower right')
... while (True):
...     port.write(b's') #handshake with Arduino
...     if (port.inWaiting()):# if the arduino replies
...         value = port.readline()# read the reply
...         print(value)#print so we can monitor it
...         number = int(value) #convert received data to integer 
...         print('Channel 0: {0}'.format(number))
...         # Sleep for half a second.
...         time.sleep(0.01)
...         val.append(int(number))
...         drawnow(makeFig)#update plot to reflect new data input
...         plt.pause(.000001)
...         cnt = cnt+1
...     if(cnt>50):
