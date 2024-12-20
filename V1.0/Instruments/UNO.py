import logging
import warnings
import numpy as np
from time import sleep,time
import re
import serial
from enum import Enum
import pdb
import time
logger = logging.getLogger(__name__)
class UNO():
    """
        Arduino UNO temperature controller
        Class contains methods to do primitive measurements, set heater conditions - power and closed loop parameters, as well as some applied routines.
    """
    instantiated = False
    instance = []
    sensorCount=2
    heaterCount=1
    sensorName=["NONE","A"] ### None is a sensor name used by lakeshore
    heaterName=["H1"]
    sensorMap={
        "NONE":0,
        "A":1}
    
            
            
    def __init__(self):
        try:
            self.connected=False
            ps = serial.tools.list_ports.comports()
            for item in ps:
                self.sm = serial.Serial(port=item.device,baudrate=115200,timeout=1)
                count=0
                while True: ### try atleast 5 times
                    resp = self.queryUNO('getInstrument')
                    if re.findall('temperatureController',resp) != []:
                        self.connected=True
                        break
                    elif count >5:
                        break
                        self.sm.close()
                    else:
                        count += 1
                   
            self.connected=True
            UNO.instance.append(self)
            UNO.instantiated=True

        except Exception as ex:
            logger.error('Error connecting to UNO\n' + 'got error' + str(ex))  
            self.connected=False

        
        #for i in range(UNO.heaterCount): #### put all heaters in closed loop with some sensor
        #    self.sm.set_heater_output_mode(i+1,self.sm.HeaterOutputMode.CLOSED_LOOP,self.sm.InputChannel(UNO.sensorMapToHeater[i])) ### heaters are on a closed loop, ## InputChannel starts with 0 for None
    def disconnect(self):
        self.sm.close()
        self.connected=False
        UNO.instantiated=False
        UNO.instance=[]
    def queryUNO(self,command):
        self.sm.write(bytes('<' + command + '>','utf-8'))
        time.sleep(0.4)
        return self.sm.readline().decode('utf-8')
            
    def getTemperature(self,sensor="ALL",aver=1):
        """
            Gets the current tempearture from sensors described in Chan. 
            Chan: Can be any of the defined sensor sensornels or All. In the case of all (default) all the sensors are returned as floats
        """
        trial=0
        data = np.zeros(aver)
        for i in range(aver):
            while True:
                inData = self.queryUNO('getTemperature')
                time.sleep(0.5)
                logging.info('read from serial of UNO' + inData)
                res = re.findall('Temperature = ([0-9\\.]+)',inData)
                if res:
                    data[i] = float(res[0])
                    break
                elif trial > 5:
                    logging.error('time out reading data')
                    self.sm.reset_input_buffer()
                    self.sm.reset_output_buffer()
                    break
                else:
                    trial +=1

        return [np.mean(data)]
    
    def getResistance(self,sensor="ALL"):
        """
            Gets the current tempearture from sensors described in Chan. 
            Chan: Can be any of the defined sensor sensornels or All. In the case of all (default) all the sensors are returned as floats
        """
        trial=0
        while True:
            inData = self.queryUNO('getResistance')
            time.sleep(0.5)
            logging.info('read from serial of UNO' + inData)
            res = re.findall('Resistance = ([0-9\\.]+)',inData)
            if res:
                break
            elif trial < 5:
                trial +=1
            else:
                res = ["0"]
        
        return [float(res[0])]    
    
    
    def doMeasure(self,sensor="All",param='T',aver=1):
        """
            Gets the current tempearture from sensors described in Chan. 
            Chan: Can be any of the defined sensor sensornels or All. In the case of all (default) all the sensors are returned as floats
        """
        if param == 'T':
            return self.getTemperature(sensor,aver)
        elif param =='R':
            return self.getResistance(sensor,aver)
        else:
            return self.getTemperature(sensor,aver)
            
            
    def setHeater(self,heaterIndex,sensorName,temperature,power,tolerance=0.01):
        """
        heaterIndex: Int:  1
        sensorIndex: 1
        Temp: Float:  Tempearture in Kelvin
        power: String of four possibilities ["OFF","LOW","MEDIUM","HIGH"] ## not yet implemented
        tolerance: multiplication of the set temperature
        """
        if power == "OFF":
            self.turnOffHeaters()
        else:
            temp = float(temperature)
            strtolerance = str(temp * tolerance)
            self.sm.write(bytes('<setTolerance,' + strtolerance + '>','utf-8'))
            time.sleep (0.5)
            self.sm.write(bytes('<setTemperature,' + str(temp) + '>','utf-8'))
            time.sleep (0.5)
        return
    def close(self):
        self.sm.disconnect()
    def waitForTemperature(self,target,sensor,accuracy,interval,timeout):
        """
            Method to set a temperature and wait for it to reach
        """
        tolerance = target*accuracy/100
        targetReached=False
        t=time()
        while not targetReached:
            currentValue = self.doMeasure(sensor)
            targetReached=np.allclose(currentValue,target,atol=tolerance)
            if (time() - t)>timeout:
                raise Exception ((
                                    "Time out occured when waiting for the sensor %s to reach temperature %g")%(sensor,target))


    def getErrors(self):
        
        return "not yet implemented"
    def turnOffHeaters(self):
        self.sm.write(bytes('<turnOffHeaters>','utf-8'))
    def turnOffOutputs(self):
        self.sm.write(bytes('<turnOffHeaters>','utf-8'))
    
