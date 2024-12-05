import logging
import warnings
import numpy as np
from time import sleep,time
class testTC():
    """
        Tempeature controller emulator
        Class contains methods to do primitive measurements, set heater conditions - power and closed loop parameters, as well as some applied routines.
    """
    instantiated = False
    instances=[]
    sensorCount=9
    heaterCount=4
    sensorName=["None","A","B","C","D","D1","D2","D3","D4"] ### None is a sensor name used by lakeshore
    heaterName=["H1","H2","H3","H4"]
    sensorMapToHeater = [1,2,3,4] ### This should have sensorName index for each heater for closed loop functioning.
    def __init__(self):
        self.sm=None
        testTC.instantiated=True
        testTC.instances.append(self)
        
    def disconnect(self):
        testTC.instantiated=False
    def doMeasure(self,sensor="All"):
        """
            Gets the current tempearture from sensors described in Chan. 
            Chan: Can be any of the defined sensor sensornels or All. In the case of all (default) all the sensors are returned as floats
        """
        measureData=np.random.rand(testTC.sensorCount-1) 
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
    def setHeater(self,heaterIndex,Temp,power):
        """
        heaterIndex: Int:  from 1-4 for heaters 1 - 4 in Model336
        Temp: Float:  Tempearture in Kelvin
        power: String of four possibilities ["OFF","LOW","MEDIUM","HIGH"]
        """
        self.Temp = Temp
        self.heaterRange=power
        return
    def close(self):
        logger.info("Did nothing")
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
    
