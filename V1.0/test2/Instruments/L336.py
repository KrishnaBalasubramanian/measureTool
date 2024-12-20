import logging
import warnings
import numpy as np
from time import sleep,time
from lakeshore import Model336
from enum import Enum
import pdb
logger = logging.getLogger(__name__)
class L336():
    """
        Lakeshore 336 temperature controller
        Class contains methods to do primitive measurements, set heater conditions - power and closed loop parameters, as well as some applied routines.
    """
    instantiated = False
    instance = []
    sensorCount=9
    heaterCount=4
    sensorName=["NONE","A","B","C","D","D1","D2","D3","D4"] ### None is a sensor name used by lakeshore
    heaterName=["H1","H2","H3","H4"]
    sensorMapToHeater = [1,2,3,4] ### This should have sensorName index for each heater for closed loop functioning.
    sensorMap={
        "NONE":0,
        "A":1,
        "B":2,
        "C":3,
        "D":4,
        "D1":5,
        "D2":6,
        "D3":7,
        "D4":8}
    def __init__(self):
        self.sm = Model336()
        L336.instance.append(self)
        L336.instantiated=True
        #for i in range(L336.heaterCount): #### put all heaters in closed loop with some sensor
        #    self.sm.set_heater_output_mode(i+1,self.sm.HeaterOutputMode.CLOSED_LOOP,self.sm.InputChannel(L336.sensorMapToHeater[i])) ### heaters are on a closed loop, ## InputChannel starts with 0 for None
    def disconnect(self):
        self.sm.disconnect_usb()
        L336.instantiated=False
        L336.instance=[]
    def doMeasure(self,sensor="All"):
        """
            Gets the current tempearture from sensors described in Chan. 
            Chan: Can be any of the defined sensor sensornels or All. In the case of all (default) all the sensors are returned as floats
        """
        measureData=self.sm.get_all_kelvin_reading() ### This gives only valid sensors data. So, no data for "None" as the sensor. 
        if sensor == "A":
            tempData = float(measureData[1])
        elif sensor =="B":
            tempData = float(measureData[2])
        elif sensor =="C":
            tempData = float(measureData[3])
        elif sensor =="D":
            tempData = float(measureData[4])
        elif sensor =="D1":
            tempData = float(measureData[5])
        elif sensor =="D2":
            tempData = float(measureData[6])
        elif sensor =="D3":
            tempData = float(measureData[7])
        elif sensor =="D3":
            tempData = float(measureData[8])
        else:
            tempData = np.array(measureData)
        return tempData
    def setHeater(self,heaterIndex,sensorName,temperature,power):
        """
        heaterIndex: Int:  from 1-4 for heaters 1 - 4 in Model336
        sensorIndex: Int from 1-8
        Temp: Float:  Tempearture in Kelvin
        power: String of four possibilities ["OFF","LOW","MEDIUM","HIGH"]
        """
        self.sm.set_heater_output_mode(heaterIndex,self.sm.HeaterOutputMode.CLOSED_LOOP,self.sm.InputChannel(L336.sensorMap[sensorName])) ### heaters are on a closed loop, ## InputChannel starts with 0 for None
        self.sm.set_control_setpoint(heaterIndex,temperature) ### set the temperature set point
        self.sm.set_heater_range(heaterIndex,self.sm.HeaterRange[power]) ### sets the heater to the required thing
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
        self.sm.all_heaters_off()
    
