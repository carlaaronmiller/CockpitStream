Implementation for a basic script to stream data from an AML XChange sensor into raspberry pi via serial port and present data via BlueRobotics Cockpit.

Hardware requirements:
- Serial to USB Converter to stream data from sensor along USB port. I used the following converter: "Dtech USB To TTL Serial Adapter"
- AML Xchange Sensor Port Connector: "Lemo	FAG-1B 304 CLA 736-FAG1B304CLA	4 pin Fixed Plug, Non Latching"

Wiring: 
![image](https://github.com/user-attachments/assets/2f27405c-7ae7-4bac-9b8e-b9605b715210)
- Connect RX/TX lines from sensor and USB adapter.
- Need to give 8-30 VDC power, and make three way ground connection between USB, sensor, and power supply.

Python package requirments (recommend using pip to install):
- Python 3
- Pymavlink
- serial
- time

BlueOS Configuration:
1. Navigate to MAVLINK ENDPOINTS in the BlueOS sidebar, then create a UDP Server with the following parameters:
         Type:UDP Server, IP:192.168.2.2 (default), Port: 14570
2. Using the terminal command line, navigate to where you have installed the script and start it running using the command "python AMLRho.py"
3. Install the BlueRobotics Cockpit Extension from the Extension Browser.
4. In Cockpit, edit the interface and add a miniwidget. In values, search the name of the value which you are streaming (i.e RhodaminePPB).

   
