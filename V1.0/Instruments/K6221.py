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
import numpy as np
logger = logging.getLogger(__name__)
class K6221():
    instantiated = False
    instance = []
    def __init__(self,K6221Address='GPIB::12::INSTR'):
        self.connected = self.connect()
        K6221.instantiated=True
        K6221.instance.append(self)
        self.sm.write_termination='\n'
        self.sm.read_termination='\n'
        self.sm.chunk_size=102400
        self.sm.write(':SYST:PRES')
        time.sleep(1)
        self.sm.write('*RST') ### reset 6221
        self.sm.write('FORM:ELEM READ') ## send out only the reading
        self.sm.write(':SYST:COMM:SER:BAUD 19200') ### set baud
        self.sm.write(':SYST:COMM:SER:TERM LF') ### set termiantion to line feed
        self.sm.write(':SYST:COMM:SER:SEND "*RST"') ### reset 2182
        time.sleep(1)
        self.sm.write(':SYST:COMM:SER:SEND "*CLS"') ### reset 2182
        time.sleep(0.2)
        self.sm.write(':SYST:COMM:SER:SEND ":INIT:CONT OFF;:ABORT"') ### init off
        time.sleep(0.2)
        self.sm.write(':SYST:COMM:SER:SEND ":SYST:BEEP:STAT OFF"') ### init off
        time.sleep(0.2)
        self.sm.write('SYST:COMM:SER:SEND "FORM:ELEM READ"') ## send out only the reading
        time.sleep(0.2)
        self.sm.write('SYST:COMM:SER:SEND "STAT:PRES"') ## send out only the reading
        time.sleep(0.2)
        self.sm.write('SYST:COMM:SER:SEND "STAT:QUE:CLE"') ## send out only the reading
        time.sleep(0.2)

    def disconnect(self):
        K6221.instantiated=False
        k6221.instance=[]
        self.sm.close()
    def connect(self):
        try:
            rm = visa.ResourceManager('@py')
            self.sm=rm.open_resource(K6221Address) ## setting a delay between write and query
            self.sm.write_termination='\n'
            self.sm.read_termination='\n'
            self.sm.chunk_size=102400
            logging.debug('Connected to 6221 at ' + K6221Address)
            return True
        except Exception:
            logging.error('Unable to connect to 6221 at ' + K6221Address)
            return False


 ############## configure source smu#####
    def setSourceMode(self,chan,param,slim,comp):
        self.sm.write(':SOUR:SWE:ABOR')
        if slim.lower() == 'auto': ## set range
            self.sm.write('SOUR:CURR:RANG:AUTO ON')
        else:
            self.sm.write('SOUR:CURR:RANG '+slim)
        if comp.lower() == 'auto': ## set range
            self.sm.write('SOUR:CURR:COMP '+str(100)) ## set compliance of voltage to maximum
        else:
            self.sm.write('SOUR:CURR:COMP '+comp) ## set compliance 
        self.sm.write(':OUTP ON') ## set compliance 

    def setSenseMode(self,chan,param,mlim,nplc,aver): ## put only generic sensing modes
        ### since, 2182 is connected via serial port, the command must be routed.
        ####configure measure SMU
        self.sm.write(':SYST:CLE') ## clear the interface
        self.sm.write(':SYST:COMM:SER:SEND "SENS:CHAN 1"') ##set channel 1 for measurements
        time.sleep(0.2)
        self.sm.write(':SYST:COMM:SER:SEND "SENS:FUNC \'VOLT:DC\'"') ##set channel 1 for measurements
        time.sleep(0.2)
        self.sm.write(':SYST:COMM:SER:SEND "SENS:VOLT:NPLC ' + str(nplc) + '"') ##set channel 1 for measurements
        time.sleep(0.2)
        self.sm.write(':SYST:COMM:SER:SEND ":TRAC:CLE"') ## clean the trace
        time.sleep(0.2)
        if mlim.lower() == 'auto':
            self.sm.write('SYST:COMM:SER:SEND "SENS:VOLT:RANG:AUTO ON"') ## set auto range
        else:
            self.sm.write('SYST:COMM:SER:SEND "SENS:VOLT:RANG '+ mlim + '"') ## set voltage range
        time.sleep(0.2)
        self.sm.write(':SYST:COMM:SER:SEND ":SAMP:COUN ' + str(aver) +'"') ## anytime read that many data

    def dodIdV(self,dIdVData):
        sourceStart=float(dIdVData["sStart"])
        sourceStop = float(dIdVData["sEnd"])
        points = int(dIdVData["sPoints"])
        senseSMU = dIdVData["sense"]
        aver = int(dIdVData["aver"])
        amp = dIdVData["damp"]
        delay = dIdVData["ddel"]
        nplc = float(dIdVData["nplc"])
        sourceLimit = dIdVData["slimit"]
        measureLimit= dIdVData["mlimit"]
        sourceStep = (sourceStop - sourceStart)/points
        self.sm.write(':SOUR:SWE:ABOR') ### abort any sweep
        self.setSourceMode('1','I',sourceLimit,measureLimit)
        self.setSenseMode('1','V',measureLimit,nplc,aver)
        #k.smua.measure.autorangei            = k.smua.AUTORANGE_ON
        time.sleep(0.5)
        print(self.sm.query('SOUR:DCON:NVPR?'))
        time.sleep(0.5)
        if int(self.sm.query('SOUR:DCON:NVPR?')) == 1:
            self.sm.write(':SOUR:DCON:STAR '+str(sourceStart))
            self.sm.write(':SOUR:DCON:STOP '+str(sourceStop))
            self.sm.write(':SOUR:DCON:STEP '+str(sourceStep))
            self.sm.write(':SOUR:DCON:DELT '+amp)
            self.sm.write(':SOUR:DCON:DEL '+delay)
            self.sm.write(':TRAC:POIN '+ str(points))
            self.sm.write('SOUR:DCON:CAB OFF')
            self.sm.write('SOUR:DCON:ARM')
            time.sleep(1)
            self.sm.write('INIT:IMM') ### started the measurement
            time.sleep(points*float(delay)+ 10)
            self.sm.write('SOUR:SWE:ABOR')
            time.sleep(5)
            values=self.getTraceData('1','I',points)
            print(values)
        else:
            values = np.zeros(points)
        currValues=np.linspace(sourceStart,sourceStop,points)
        measuredValues=resultBook()
        measuredValues.dIdV = values
        measuredValues.I = currValues
        measuredValues.points = len(currValues)
        return measuredValues

    def doMeasure(self,smu,param,aver):
        mData = []
        self.sm.write('\x03') ### clear the RS232
        self.sm.write(':SYST:COMM:SER:SEND "\x03"') ### clear the RS232
        self.sm.write(':SYST:COMM:SER:SEND ":READ?"') ## do one read into trace buffers 
        waitingForData=True
        timeSlept=0
        while waitingForData:
            if len(mData) >= aver:
                logging.info('got all Data')
                waitingForData=False
            elif timeSlept > 30:
                logging.warning('timed out')
                waitingForData=False
            else: 
                try:
                    time.sleep(0.2)
                    resp = self.sm.query(':SYST:COMM:SER:ENT?')
                    mData=np.append(mData,np.asarray(re.findall('[+-][0-9\.]+E[+-][0-9]+',resp),dtype=float))
                    logging.info('Adding data' + resp)
                except Exception as err:
                    logging.warning('Unable to add the data' + resp)
                timeSlept +=0.5
                time.sleep(0.3)
        return np.mean(mData)

    def doSource(self,smu,param,value): ## no use for other values. It can only output current
        self.sm.write(':CURR ' + str(value))
        return 
    def writeK2182(self,comm):
        return(self.sm.write(':SYST:COMM:SER:SEND "' + comm + '"'))
    def queryK2182(self,comm):
        self.sm.write(':SYST:COMM:SER:SEND "' + comm + '"')
        time.sleep(0.2)
        return(self.sm.query(':SYST:COMM:SER:ENT?'))
    ################ get data from 2812A ##############
    def get2182TraceData(self,smu,param,tPoints):
        self.sm.write('\x03') ### clear the RS232
        self.sm.write(':SYST:COMM:SER:SEND "\x03"') ### clear the RS232
        mData = []
        time.sleep(5)
        self.sm.write(':SYST:COMM:SER:SEND ":TRAC:DATA?"')
        time.sleep(1)
        waitingForData=True
        timeSlept=0
        while waitingForData:
            if len(mData) >= tPoints:
                logging.info('got all Data')
                waitingForData=False
            elif timeSlept > 10:
                logging.warning('timed out')
                waitingForData=False
            else: 
                try:
                    time.sleep(1)
                    resp = self.sm.query(':SYST:COMM:SER:ENT?')
                    logging.info('Read from instrument: ' + resp)
                    mData=np.append(mData,np.asarray(re.findall('[+-][0-9\.]+E[+-][0-9]+',resp),dtype=float))
                    logging.info('Adding data' + resp)
                except ValueError:
                    logging.warning('Unable to add the data' + resp)
                timeSlept +=1.5
                time.sleep(0.5)
        return mData

    ################ get data from 6221 ##############
    def getTraceData(self,smu,param,tPoints):
        mData = []
        waitingForData=True
        timeSlept=0
        while waitingForData:
            if len(mData) >= tPoints:
                logging.info('got all Data')
                waitingForData=False
            elif timeSlept > 30:
                logging.warning('timed out. Leaving with either empty or partial data of length ' + str(len(mData)))
                waitingForData=False
            else:
                try:
                    resp = self.sm.query(':TRAC:DATA?')
                    mData=np.append(mData,np.asarray(re.findall('[+-][0-9\.]+E[+-][0-9]+',resp),dtype=float))
                    logging.info('Adding data' + resp)
                except Exception as e:
                    logging.warning('Unable to add the data. Got this  ' + resp)
                timeSlept +=0.5
                time.sleep(0.5)
        return mData
    def ivt(self,ivtData): # smu1 is source and smu2 is sense
        sValue=float(ivtData["sValue"])
        tPoints = int(ivtData["tPoints"])
        tInt = float(ivtData["tInt"])
        aver = int(ivtData["aver"])
        nplc = float(ivtData["nplc"])
        slim = ivtData["slimit"]
        mlim = ivtData["mlimit"]
        ######################## Set source settings ###################
        self.sm.write(':SOUR:SWE:ABOR') ### abort any sweep
        self.setSourceMode('1','I',slim,mlim)
        self.setSenseMode('1','V',mlim,nplc,aver)
        self.doSource('1','I',sValue)
        #### General measurement settings
        self.sm.write(':TRAC:CLE') ### reset 2182
        self.sm.write(':SYST:COMM:SER:SEND ":SENS:VOLT:LPAS OFF"') ### reset 2182
        time.sleep(0.1)
        self.sm.write(':SYST:COMM:SER:SEND ":SENS:VOLT:DFIL OFF"') ### reset 2182
        time.sleep(0.1)
        self.sm.write(':SYST:COMM:SER:SEND ":TRAC:CLE"') ### reset 2182
        time.sleep(0.1)
        self.sm.write(':SYST:COMM:SER:SEND ":TRAC:FEED SENS"') ### reset 2182
        time.sleep(0.1)
        self.sm.write(':SYST:COMM:SER:SEND ":TRAC:POIN ' + str(tPoints) +'"') ### reset 2182
        time.sleep(0.1)
        self.sm.write(':SYST:COMM:SER:SEND ":TRIG:SOUR TIM"') ### set timer
        time.sleep(0.1)
        self.sm.write(':SYST:COMM:SER:SEND ":TRIG:TIM ' + str(tInt) +'"') ### set timer
        time.sleep(0.1)
        self.sm.write(':SYST:COMM:SER:SEND ":TRIG:COUN ' + str(tPoints) +'"') ### reset 2182
        time.sleep(0.1)
        self.sm.write(':SYST:COMM:SER:SEND ":TRAC:FEED:CONT NEXT"') ### reset 2182
        time.sleep(1)
        self.sm.write(':SYST:COMM:SER:SEND ":INIT"') ### init measurements
        time.sleep(tPoints*(float(tInt) + 0.2) + 5)
        time.sleep(1)
        #self.sm.write(':SYST:COMM:SER:SEND ":TRAC:DATA?"')
        #time.sleep(5)
        #values=np.array(self.sm.query_ascii_values(':SYST:COMM:SER:ENT?'))
        values=self.get2182TraceData('1','I',tPoints)
        print(values)
        RB = resultBook()
        RB.I = np.ones(tPoints)*sValue
        RB.V = values
        RB.T=np.linspace(0,tPoints*tInt,tPoints)
        RB.points = len(values)
        return RB


    def IVSweep(self,dcivData): # smu1 is source and smu2 is sense
        start=float(dcivData["sStart"])
        stop = float(dcivData["sEnd"])
        points = int(dcivData["sPoints"])
        loop = dcivData["Loop"]
        LoopBiDir = dcivData["LoopBiDir"]
        aver = int(dcivData["aver"])
        nplc = float(dcivData["nplc"])
        sourceLimit = dcivData["slimit"]
        measureLimit= dcivData["mlimit"]
        stepPeriod=dcivData["sDel"]
        pWidth=dcivData["pWidth"]
        pPeriod=dcivData["pPeriod"]
        pulse=dcivData["Pulse"]
        ######################## Set source settings ###################
        self.sm.write(':SOUR:SWE:ABOR') ### abort any sweep
        self.setSourceMode('1','I',sourceLimit,measureLimit)
        self.setSenseMode('1','V',measureLimit,nplc,aver)
        #### General measurement settings
        if loop: 
            if LoopBiDir:
                sweepList = np.concatenate([np.linspace(0,stop,points),np.linspace(stop,0,points),np.linspace(0,-stop,points),np.linspace(-stop,0,points)])
            else:
                sweepList = np.concatenate([np.linspace(start,stop,points),np.linspace(stop,start,points)])
        else:
            sweepList = np.linspace(start,stop,points)
        tPoints = len(sweepList)
        logging.info('sweep list' + str(sweepList))
        currStep = (stop-start)/points
        self.sm.write(':SOUR:SWE:SPAC LIST') ## going for linear always. if too many points, its failing 
        self.sm.write(':SOUR:SWE:RANG AUTO') # auto limit
        self.sm.write(':SOUR:SWE:CAB OFF') # remove compliance off
 ################ setting sweep points
        print(self.sm.query('SOUR:LIST:CURR?'))
        self.sm.write('SOUR:SWE:COUN 1') ## just one sweep
        if measureLimit.lower() == 'auto':
            self.sm.write('SOUR:CURR:COMP 100') ## just one sweep
        else:
            self.sm.write('SOUR:CURR:COMP ' +str(measureLimit)) ## just one sweep
        self.sm.write(':TRAC:CLE') ## clear trace of 6221
        self.sm.write(':SYST:COMM:SER:SEND ":SENS:VOLT:LPAS OFF"') ### reset 2182
        time.sleep(0.1)
        self.sm.write(':SYST:COMM:SER:SEND ":SENS:VOLT:DFIL OFF"') ### reset 2182
        time.sleep(0.1)
        self.sm.write(':SYST:COMM:SER:SEND ":TRAC:CLE"') ### reset 2182
        time.sleep(1)
        self.sm.write(':TRAC:CLE') 
        self.sm.write(':TRAC:FEED SENS') ### reset 2182
        self.sm.write(':TRAC:FEED:CONT NEXT') ### reset 2182
        self.sm.write(':TRAC:POIN ' + str(tPoints)) 
        if pulse:
            self.sm.write('SOUR:LIST:CURR ' + str(start)) ## clears the list and adds 0
            self.sm.write('SOUR:LIST:DEL ' + str(pPeriod)) ## clears the list and adds 0
            for i in range(1,tPoints):
                self.sm.write('SOUR:LIST:CURR:APP ' + str(sweepList[i]))
                self.sm.write('SOUR:LIST:DEL:APP ' + str(pPeriod))
            self.sm.write(':SOUR:SWE:RANG BEST') # limit set to the highest sweep value
           
            self.sm.write(':SOUR:PDEL:WIDT ' + str(pWidth)) 
            self.sm.write(':SOUR:PDEL:SDEL 100E-6') ## I think again this is only for fixed output
            self.sm.write(':SOUR:PDEL:LOW 0') 
            self.sm.write(':SOUR:PDEL:SWE ON') 
            self.sm.write(':SOUR:PDEL:LME 2') 
            self.sm.write(':SOUR:PDEL:ARM')
            time.sleep(1)
            self.sm.write(':INIT:IMM')
            time.sleep(tPoints*(float(pPeriod) + float(pWidth) + 0.1) + 5) ### waiting for just the exact time was not being enough
            self.sm.write('SOUR:SWE:ABOR')
            values=self.getTraceData('1','I',tPoints)
        else: ### normal sweeping
            self.sm.write('SOUR:LIST:CURR ' + str(start)) ## clears the list and adds 0
            self.sm.write('SOUR:LIST:DEL ' + str(stepPeriod)) ## clears the list and adds 0
            for i in range(1,tPoints):
                self.sm.write('SOUR:LIST:CURR:APP ' + str(sweepList[i]))
                self.sm.write('SOUR:LIST:DEL:APP ' + str(stepPeriod))
            self.sm.write(':SOUR:SWE:RANG BEST') # limit set to the highest sweep value
            self.sm.write(':TRIG:SOUR TLINK')
            self.sm.write(':TRIG:DIR SOUR')
            self.sm.write(':TRIG:OLIN 2')
            self.sm.write(':TRIG:ILIN 1')
            self.sm.write(':TRIG:OUTP DEL')
            self.sm.write(':TRAC:CLE') ### reset 2182
            self.sm.write(':SYST:COMM:SER:SEND ":SENS:VOLT:LPAS OFF"') ### reset 2182
            time.sleep(0.1)
            self.sm.write(':SYST:COMM:SER:SEND ":SENS:VOLT:DFIL OFF"') ### reset 2182
            time.sleep(0.1)
            self.sm.write(':SYST:COMM:SER:SEND ":TRAC:CLE"') ### reset 2182
            time.sleep(0.1)
            self.sm.write(':SYST:COMM:SER:SEND ":TRAC:FEED SENS"') ### reset 2182
            time.sleep(0.1)
            self.sm.write(':SYST:COMM:SER:SEND ":TRAC:POIN ' + str(tPoints) +'"') ### reset 2182
            time.sleep(0.1)
            self.sm.write(':SYST:COMM:SER:SEND ":TRIG:SOUR EXT"') ### reset 2182
            time.sleep(0.1)
            self.sm.write(':SYST:COMM:SER:SEND ":TRIG:COUN ' + str(tPoints) +'"') ### reset 2182
            time.sleep(0.1)
            self.sm.write(':SYST:COMM:SER:SEND ":TRAC:FEED:CONT NEXT"') ### reset 2182
            time.sleep(0.1)
            self.sm.write(':SOUR:SWE:ARM')
            time.sleep(1)
            self.sm.write(':SYST:COMM:SER:SEND ":INIT"') ### start 2182
            self.sm.write(':INIT:IMM') ## start 6221
            time.sleep(tPoints*(float(stepPeriod) + 0.1) + 30)
            self.sm.write('SOUR:SWE:ABOR')
            self.turnOffOutputs()
            time.sleep(1)
            #self.sm.write(':SYST:COMM:SER:SEND ":TRAC:DATA?"')
            #time.sleep(5)
            #values=np.array(self.sm.query_ascii_values(':SYST:COMM:SER:ENT?'))
            values=self.get2182TraceData('1','I',tPoints)
        print(values)
        logging.info('got these values\n' + str(values))
        measuredValues=resultBook()
        measuredValues.points = len(values)
        measuredValues.I = sweepList
        measuredValues.V = values

        return measuredValues

    def getErrors(self):
        err = self.sm.query(":syst:err?")
        logging.info(err)
        #self.sm.close()
        return err
    def preset(self):
        self.sm.write(':SYST:COMM:SER:SEND ":SYST:PRES"') ### reset 2182
        self.sm.write(':SYST:PRES') ### reset 6221
    def turnOffOutputs(self):
        self.sm.write(':OUTP OFF')


