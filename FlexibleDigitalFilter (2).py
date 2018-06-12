# Flexible Digital Filter(Low-pass filter)
# 
# Developer: Ibrahim Sarpani 
#
# May 2018
#
# Final Year Project

from pyqtgraph.Qt import QtGui, QtCore
import time
import pyqtgraph as pg
import sys
import numpy as np
from math import pi,e
import scipy.fftpack
# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

import matplotlib.pyplot as plt



# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

           
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="Flexible Digital Filter")
#win.resize(1200,600)  		<---Resize pygtgraph window
win.setWindowTitle('Flexible Digital Filter')
    
pg.setConfigOptions(antialias=False)		# Enable antialiasing for prettier plots but reduce performance(True/False)

#pw = pg.plot()

p1 = win.addPlot(title="Input Signal")
p2 = win.addPlot(title="Filtered Signal")

win.nextRow() 		#Put the graphs on the next row on the window

p3 = win.addPlot(title="Input Spectrum")
p4 = win.addPlot(title="Output Spectrum")

h=0.1 	 #Time range 0-h sec
k=0.0001 	#sampling time in second

mid = 0    #Initialize middle point
                                                        
def update():	#Coding for Plotting Signal and Spectrum using Pyqtgraph (Pyqtgraph is the fastest program to visualize data for python!!!)
	
	             #clear=Clear the graph #pen=graph color y=yellow #symbolBrush=(R ,G ,B) #symbolPen-->drawing symbol outline such as circles    
				 #everytime updating the graph(True/False)
	p1.plot(x, z, clear=True,pen='y', symbolBrush=(255,255,0),symbolSize=3, symbolPen=None)		#Plot an array of input signal
	p2.plot(x, y, clear=True,pen='c',symbolBrush=(0,255,255),symbolSize=3, symbolPen=None) 		#Plot an array of output/filtered signal
	p1.setLabel('left', "Amplitude", units='V')
	p1.setLabel('bottom', "Time", units='s')
	p2.setLabel('left', "Amplitude", units='V')
	p2.setLabel('bottom', "Time", units='s')
	
	p1.showGrid(x=True, y=True)		#Enable Grid for Graph(True/False)
	p2.showGrid(x=False, y=True)
	
	
	p3.plot(xf, 2.0/d*np.abs(zf[:d//2]), clear=True)  #Plotting function for alternative FFT
	p4.plot(xf, 2.0/d*np.abs(yf[:d//2]), clear=True)
	#p3.plot(frq, abs(zf), clear=True)		#Plotting input spectrum
	#p4.plot(frq, abs(yf), clear=True)		#Plotting output spectrum
	p3.setLabel('left', "Amplitude", units='')
	p3.setLabel('bottom', "Frequency", units='Hz')
	p4.setLabel('left', "Amplitude", units='')
	p4.setLabel('bottom', "Frequency", units='Hz')
	p3.showGrid(x=True, y=True)
	p4.showGrid(x=True, y=True)
	
	
	QtGui.QApplication.processEvents()

def updateAxisRange():	#Coding for setting X and Y axis range value of Pyqtgraph

	p1.setYRange(-1.2, 1.2, padding=None,update=True)
	p1.setXRange(0, 0.01, padding=None,update=True)
	
	p2.setYRange(-1.2, 1.2, padding=None,update=True)
	p2.setXRange(0, 0.01, padding=None,update=True)
	
	p3.setYRange(0, 0.8, padding=None,update=True)
	p3.setXRange(0, 500, padding=None,update=True)
	
	p4.setYRange(0, 0.8, padding=None,update=True)
	p4.setXRange(0, 500, padding=None,update=True)

while True:
	
	values = mcp.read_adc(0) 	#Getting value from mcp3008 channel 0 (0-1024)
	volts = (values* 3.3) / float(1023) 	#Converting mcp3008 value ex.1024 to voltage ex.3.3V
	voltage= round(volts,3)		#Round up voltage value to 3 decimal place
	z = [voltage-mid] 			#Initialize value y in volts
	x = [0]      #Initialize value x = time in second

	t = 0		 #Initialize time = 0s
	maxx = 0
	minn = 1
	
	
	time.sleep(k)	#Delay time for next sample
	
	while t<=h: 	#Determine time range
		values = mcp.read_adc(0)
		volts = (values* 3.3) / float(1023)
		voltage= round(volts,3)
		z.append(voltage-mid)		#Updating values of Y in an array---> input signal
		t = t+k			#Update time	
		x.append(t)		#Updating values of x = time in an array---> input signal
		
		if voltage>maxx: 	#<--- This function to find the middle point where it rise and fall from the input signal
			maxx=voltage	#
		if voltage<minn:	#
			minn=voltage	#
		
		
		time.sleep(k)	#Delay time for next sample
	
	mid = (maxx+minn)/2		#The value of the middle point
	
	### fc = 200Hz !!!!!
	### Sample time = 0.001s !!!
	
	fc = 200             #<----Alternative low-pass filter equation from wikipedia
	RC = 1/(2*pi*fc)
	dt = k
	a = dt/(RC+dt)
	
	
	
	y = [0]		#Initialize output signal = 0
	
	n = 0		#Initialize output arry list number 1
	p = 0
	
	
	 
	a0 = 0.01249	#Coefficient values from Matlab
	
	b0 = 0.9875
	
	
	while p<=h:
		p = p + k
		n = n + 1		#Updating output number
		#y.append(a0*y[n]+b0*z[n])	#Low-pass filter equation
		y.append(a*z[n]+(1-a)*y[n-1])
		
		
	d = len(x)	#Count the sample number/size
	
	
	zf = scipy.fftpack.fft(z)                #<------ Alternative FFT(fast fourier transform) coding
	yf = scipy.fftpack.fft(y)				  #<------
	xf = np.linspace(0.0, 1.0/(2.0*0.0002), d/2)  #<------
	
	#m = np.arange(d)
	#J = d/(1/k)
	
	#frq = m/J
	
	#frq = frq[range(d/2)]
	
	#zf = np.fft.fft(z)/d	#Find spectrum of input signal using FFT
	#yf = np.fft.fft(y)/d	#Find spectrum of output signal using FFT
	
	#zf = zf[range(d/2)]
	#yf = yf[range(d/2)]
	
	
	update()	#Updating Signal and Spectrum Graphs
	
	
	updateAxisRange()	#Setting X and Y axis range values
	
#Please credit my program...
	

							
		
	
		
    
    

	

    


	
	
	

	  

	

	


