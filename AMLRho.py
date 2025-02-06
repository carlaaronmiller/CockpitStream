#The following script accepts data from a variety of AML XChange sensors and forwards the data to the BlueRobotics Cockpit control application.

from pymavlink import mavutil
import serial
import time

#General setup:
#Config serial connections and cockpit.
#ROV is 192.168.2.3, Jetski is 192.168.2.2 (ZT = 192.168.195.60)
boot_time = time.time()
ROVCp = mavutil.mavlink_connection('udpout:192.168.2.3:14570',source_system=1,source_component=1)
jetskiCp = mavutil.mavlink_connection('udpout:192.168.195.60:14570',source_system=1,source_component=1)

#These ports are hard coded in, will have to find a better way to either auto select or let user config port from terminal.
ser0 = serial.Serial('/dev/ttyUSB0',9600)
ser1 = serial.Serial('/dev/ttyUSB1',9600)

#Function to pull a line from the sensor attached from the argument serial number.
def getSensorLine(serNum):
	#Initalize an empty buffer and an empty string.
	line = []
	fullLine = ""
	#Wait for the end of the next line to start reading a line.
	while serNum.read().decode("utf-8",errors='ignore')!='\n':
		pass
	#Read bytes in one at a time, the join and return the full line.
	while True:
		b = (serNum.read()).decode("utf-8",errors='ignore')
		line.append(b)
		if b =='\n':
			fullLine = ''.join(line)
			print("Full line is: ",fullLine)
			line = []
			serNum.reset_input_buffer()
			serNum.reset_output_buffer()
			return fullLine

#Parsing script for AML rhodamine fluorometer.
def getRhoNum(serNum):
	#Get a line from the sensor.
	sensorLine = getSensorLine(serNum)
	#Parse it for the the specific values in said line.
	#AML Rhodamine implementation (i.e. MUX data format = rhodamine ppb, raw voltage)
	splitLine = sensorLine.split(',')
	sensorNums = [None] * 2
	sensorNums[0] = int(float(splitLine[0])*1e5) #PPBValue.
	sensorNums[1] = int(float(splitLine[1])) #RawValue.
	return sensorNums[0]

#Parsing script for AML Conductivity / Temperature sensor.
def getCTNums(serNum):
	#Get a line from the sensor.
	sensorLine = getSensorLine(serNum)
	#Parse it for the the specific values in said line.
	#AML Rhodamine implementation:
	#PPBvalue,rawValue.
	splitLine = sensorLine.split()
	sensorNums = [None] * 2
	sensorNums[0] = int(float(splitLine[0])*1e5) #Conductivity Value.
	sensorNums[1] = int(float(splitLine[1])) #Temperature Value.
	return sensorNums


#IMPROTANT: Need to ping the host first for the autopilot to accept the connection.
#Conversion of time unit for timestamping.
microSecToSec = 1e6
ROVCp.mav.ping_send(int((time.time()-boot_time)*microSecToSec),0,0,0)
time.sleep(1)
#Wait for acknowledgement.
msg = ROVCp.recv_match()

#Sends a message of type "name" to the specific host with the sensor value. 
def sendCockpitValue(dest,name,sensorValue):
	dest.mav.named_value_float_send(int((time.time() - boot_time)*microSecToSec),name.encode(),sensorValue)

#Main function.
while True:
	#Rhodamine sensor on serial 0, CT sensor on serial 1.
	CTVals = getCTNums(ser0)
	RhoPPB = getRhoNum(ser1)
	
	#Print values to the terminal.
	print("Rho: ",RhoPPB)
	print("CT: ",CTVals)
	
	#Send the values to cockpit. Need two separate calls to send the conductivity and temperature values from the CT sensor.
	sendCockpitValue(ROVCp,"RhoPPB",RhoPPB)
	sendCockpitValue(ROVCp,"Cond",CTVals[0])
	sendCockpitValue(ROVCp,"Temp",CTVals[1])

	time.sleep(1)
