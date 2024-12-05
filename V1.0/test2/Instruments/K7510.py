#
# This file is part of the measureTool
#
# Copyright (c) 2013-2024  Krishna Balasubramanian
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import logging
import time
import pdb
import pyvisa as visa
import os
import numpy as np
logger = logging.getLogger(__name__)
class K7510():
    instantiated = False
    instance = []
    def __init__(self):
        self.connected = self.connect()
        K7510.instance.append(self)
        K7510.instantiated=True
        time.sleep(1)
        self.sm.write('*RST') ### reset 6221
 
    def connect(self,K7510Address = 'USB0::0x05E6::0x7510::04599177::INSTR'):
        try:
            rm = visa.ResourceManager()
            self.sm = rm.open_resource(K7510Address) ## setting a delay between write and query
            self.sm.write_termination='\n'
            self.sm.read_termination='\n'
            self.sm.chunk_size=102400
            logging.debug('Connected to DMM at ' + K7510Address)
            return True
        except Exception:
            pdb.set_trace()
            logging.error('Unable to connect to DMM at ' + K7510Address)
            return False
    
    def disconnect(self):
        K7510.instantiated=False
        K7510.instance=[]
        self.sm.close()

    def setSenseMode(self,chan,param,mlim,nplc,aver):
        """
            Set the sensing modes the tool
            chan: If there are multiple channels. they are named A,B,C
            param: "DC" for DC volt meter, "RES" for 2 wire resistance
            mlim: "auto" for auto range or a float value for defined range
            nplc: this is scaling factor * 20 ms obtained from 50 Hz
            aver: Number of measurements done per reading 
        
        """
        if param == "DC":
            fun = 'VOLT:DC'
        elif param =="2-wire":
            fun = 'RES'
        elif param =="4-wire":
            fun = "FRES"
        else:
            print("Wrong mode selected")
            logging.error("Wrong mode selected")
        self.sm.write(':SENS:FUNC "'+fun + '"')
        if mlim == "auto":
            self.sm.write(':SENS:' + fun + ':RANG:AUTO ON')
        else:
            self.sm.write(':SENS:' + fun + ':RANG '+ str(mlim)) 
        self.sm.write(':SENS:' + fun + ':NPLC ' + str(nplc)) #### set the filter cycles
        self.sm.write(':SENS:COUN ' + str(aver)) ### make these many measurements
        self.measureCount = aver

    def doMeasure(self,chan='A'):
        self.sm.write(':TRAC:CLEAR')
        self.sm.query(':READ?')
        readData = self.sm.query(':TRAC:DATA? 1,' + str(self.measureCount))
        return(np.fromstring(readData,dtype=float,sep=','))
    def getTraceData(self):
        return self.sm.query(':TRAC:DATA? 1,' + str(self.measureCount))
    
    def getErrors(self):
        err = self.sm.query(":syst:err?")
        logging.info(err)
        #self.sm.close()
        return err
