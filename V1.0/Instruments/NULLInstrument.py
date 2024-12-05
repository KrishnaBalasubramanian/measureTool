import logging
import warnings
import numpy as np
from time import sleep,time
class NULLInstrument():
    """
        This is a template for all isntruments. It is Null
    """
    instantiated = False
    instances=[]
    def __init__(self):
        self.sm=None
        NULLInstrument.instantiated=True
        NULLInstrument.instances.append(self)
        self.connected=True
        
    def turnOffOutputs(self):
        return True
    def disconnect(self):
        NULLInstrument.instantiated=False
        self.connected=False
    def doMeasure(self):
        """
            Gets the current tempearture from sensors described in Chan. 
            Chan: Can be any of the defined sensor sensornels or All. In the case of all (default) all the sensors are returned as floats
        """
        return 0
    
    def close(self):
        logger.info("Did nothing")
    
    def turnOffOutputs(self):
        return True
    def getErrors(self):
        return "not yet implemented"
    
