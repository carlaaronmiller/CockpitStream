from pymavlink import mavutil
import serial
import time

#Config serial connections and cockpit.
#ROV is 192.168.2.3, Jetski is 192.168.2.2 (ZT = 192.168.195.60)
boot_time = time.time()
ROVCp = mavutil.mavlink_connection('udpout:192.168.2.3:14570',source_system=1,source_component=1)
jetskiCp = mavutil.mavlink_connection('udpout:192.168.195.60:14570',source_system=1,source_component=1)
ser0 = serial.Serial('/dev/ttyUSB0',9600)
ser1 = serial.Serial('/dev/ttyUSB1',9600)

#Pass the argument of the serial line which you want to read.
#TODO: CREATE DATAFRAME FOR DIFFERENT SENSOR TYPES, FLUORO / RHO / CT.
#RHODAMINE: 123.1234 , 12345  #PPBvalue,rawValue.
#FLUORO : 00.0000
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

def getRhoNum(serNum):
	#Get a line from the sensor.
	sensorLine = getSensorLine(serNum)
	#Parse it for the the specific values in said line.
	#AML Rhodamine implementation:
	#PPBvalue,rawValue.
	splitLine = sensorLine.split(',')
	sensorNums = [None] * 2
	sensorNums[0] = int(float(splitLine[0])*1e5) #PPBValue.
	sensorNums[1] = int(float(splitLine[1])) #RawValue.
	return sensorNums[0]


def getFluoroNum(serNum):
	#Get a line from the sensor.
	sensorLine = getSensorLine(serNum)
	sensorNum = int(float(sensorLine)*1e5)
	return sensorNum


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


#Ping the connection to set up the connection.
ROVCp.mav.ping_send(int((time.time()-boot_time)*1e6),0,0,0)
time.sleep(1)
#Wait for acknowledgement.
msg=ROVCp.recv_match()


def sendCockpitValue(dest,name,sensorValue):
	dest.mav.named_value_float_send(int((time.time() - boot_time)*1e3),name.encode(),sensorValue)


while True:
	#Send both with different names.
	RhoPPB = getRhoNum(ser1)
	CTVals = getCTNums(ser0)
	print("Rho: ",RhoPPB)
	print("CT: ",CTVals)
	sendCockpitValue(ROVCp,"RhoPPB",RhoPPB)
	sendCockpitValue(ROVCp,"Cond",CTVals[0])
	sendCockpitValue(ROVCp,"Temp",CTVals[1])
	print("Sleeping.")
	time.sleep(1)
