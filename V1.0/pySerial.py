import serial
import re
import time
import pdb
ser = serial.Serial(
    port='COM7',
    baudrate=115200,timeout=1)
time.sleep(1)
#pdb.set_trace()
#ser.write(bytes('setTolerance,' + strtolerance + '\n','utf-8'))
#print(ser.readline())
#print(ser.readline())

print(ser.readline())
while(True):
    ser.write(bytes('<getTemperature>','utf-8'))
    time.sleep (0.1)
    inData = ser.readline()
    time.sleep (0.5)
    res = re.findall('Temperature = ([0-9\\.]+)',inData.decode("utf-8"))
    if res == []:
        pdb.set_trace()
    print(inData)
ser.close()