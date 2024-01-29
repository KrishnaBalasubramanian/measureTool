###################################################################
# Tool that can be used to run various electornic device measurements using Keithley and Keysight equipments####
# (c) Krishna Balasubramanian ###
###################### Version 7 ###############################


import tkinter as tk
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import threading
import queue
import time
import pdb
import re
import logging
import pyvisa as visa
from keithley2600 import Keithley2600
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

#######################################################################
############### Global Constants ######################################
####### Not modified through GUI ##############################
filterCount =1 ### measurement filter count
autoComp = '1E-3' ### auto range compliance
matplotlib.use('TkAgg')
rCount = 0

class K2636B():
    def __init__(self):
        K2636BAddress='GPIB::26::INSTR'
        self.inst = Keithley2600(K2636BAddress)


 ############## configure source smu#####
    def setSourceMode(self,channel,param,lim,comp):
        if channel == 'a':
            self.sSMU = self.inst.smua
        else:
            self.sSMU = self.inst.smub

        if param == 'V':
            self.sSMU.source.func = self.sSMU.OUTPUT_DCVOLTS
            self.sSMU.source.limitv =float(lim) 
            self.sSMU.source.limiti =float(comp) 
            self.sSMU.source.rangev =float(lim) 
        elif param == 'I':
            self.sSMU.source.func = self.sSMU.OUTPUT_DCAMPS
            self.sSMU.source.limiti =float(lim) 
            self.sSMU.source.limitv =float(comp) 
            self.sSMU.source.rangei =float(lim)
        self.sSMU.source.output=self.sSMU.OUTPUT_ON

    def setSenseMode(self,channel,param,lim,nplc,aver):
        if channel == 'a':
            self.mSMU = k.smua
        else:
            self.mSMU = k.smub
        ####configure measure SMU
        self.mSMU.measure.nplc = nplc
        self.mSMU.measure.filter.count = filterCount #### setting for now to 1. Not sure, if we should be playing with this! 
        self.mSMU.measure.filter.type = self.mSMU.FILTER_MOVING_AVG
        self.mSMU.measure.filter.enable = self.mSMU.FILTER_ON
        if param == 'V':
            if lim.lower() == 'auto':
                self.mSMU.measure.autorangev=self.mSMU.AUTORANGE_ON
            else:
                self.mSMU.measure.rangev = lim
        elif param == 'I':
            if lim.lower() == 'auto':
                self.mSMU.measure.autorangei=self.mSMU.AUTORANGE_ON
            else:
                self.mSMU.measure.rangei = float(lim)
       
    def doMeasure(self,smu,param,aver):
        temp = np.zeros(aver)
        for j in range(aver):
            if param == 'V':
                temp[j] = self.mSMU.measure.v()
            else:
                temp[j] = self.mSMU.measure.i()
        measure = np.mean(temp)
        print(measure)
        return measure
    def doSource(self,smu,param,value):
        if param == 'V':
            self.sSMU.source.levelv = value
        else:
            self.sSMU.source.leveli = value
        return 

    def PulsedSweep(self,smu1,smu2,param1,start, stop, points,loop, pPeriod, pWidth,measureLimit,nplc): # smu1 is source and smu2 is sense
        ######################## Set source settings ###################
        self.setSourceMode(smu1,param1,str(stop),str(measureLimit))
        #### General measurement settings
        if loop: 
            sweepList = np.concatenate([np.linspace(start,stop,points),np.linspace(stop,start,points)])
            tPoints = 2*points
        else:
            tPoints = points
            sweepList = np.linspace(start,stop,points)
        ################ setting sweep points
        if param1 == 'V':
            sParam = 'I'
            self.sSMU.trigger.source.listv(sweepList)
        else:
            sParam = 'V'
            self.sSMU.trigger.source.listi(sweepList)
        self.setSenseMode(smu2,sParam,measureLimit,nplc,1)
        ### Disabling Auto-Ranging and Auto-Zero ensures accurate and consistent timing
        ### prepare source buffers
        self.sSMU.nvbuffer1.clear()
        self.sSMU.nvbuffer1.collectimestamps=1
        self.sSMU.nvbuffer1.collectsourcevalues=1
        
        ### Prepare the Reading Buffers
        self.mSMU.nvbuffer1.clear()
        self.mSMU.nvbuffer1.collecttimestamps= 1
        self.mSMU.nvbuffer2.clear()
        self.mSMU.nvbuffer2.collecttimestamps= 1
        #### end of settings
        ### Configure the Trigger Model
        ###============================
        ### Pressing the TRIG button on the front panel will trigger the sweep to start
        k.display.trigger.clear()
        ### Timer 1 controls the pulse period. It is set to be stimulated when the channel is armed! when initiate command is issued. 
        k.trigger.timer[1].count    = tPoints -1
        k.trigger.timer[1].delay= pPeriod
        k.trigger.timer[1].passthrough    = True # required to send out a event immediate after this is triggered!
        k.trigger.timer[1].stimulus        = self.sSMU.trigger.ARMED_EVENT_ID 


        ### Timer 2 controls the measure delay
        k.trigger.timer[2].count            = 1
        ### Set the measure delay long enough so that measurements start after the pulse
        ### has settled, but short enough that it fits within the width of the pulse.
        #k.trigger.timer[2].delay            = pWidth - (1/localnode.linefreq)*nplc - 60e-6
        k.trigger.timer[2].delay            = pWidth -nplc/50 - 60e-6
        k.trigger.timer[2].passthrough    = False
        k.trigger.timer[2].stimulus        = k.trigger.timer[1].EVENT_ID

        ### Timer 3 controls the pulse width
        k.trigger.timer[3].count            = 1
        k.trigger.timer[3].delay            = pWidth
        k.trigger.timer[3].passthrough    = False
        k.trigger.timer[3].stimulus        = k.trigger.timer[1].EVENT_ID

        ### sweep source  configurations
        self.sSMU.trigger.source.action        = self.sSMU.ENABLE
        self.mSMU.trigger.measure.action        = self.mSMU.ENABLE
        self.sSMU.trigger.endpulse.action    = self.sSMU.SOURCE_IDLE
        self.sSMU.trigger.endsweep.action    = self.sSMU.SOURCE_IDLE
        self.sSMU.trigger.count                = points
        self.sSMU.trigger.arm.stimulus        = 0
        self.mSMU.trigger.count                = points
        self.mSMU.trigger.arm.stimulus        = 0
        self.sSMU.trigger.source.stimulus    = k.trigger.timer[1].EVENT_ID
        self.mSMU.trigger.measure.stimulus    = k.trigger.timer[2].EVENT_ID
        self.sSMU.trigger.endpulse.stimulus    = k.trigger.timer[3].EVENT_ID
        

        ###==============================
        ### End Trigger Model Configuration

        self.sSMU.source.output                = self.sSMU.OUTPUT_ON
        ### Start the trigger model execution
        self.sSMU.trigger.initiate()
        self.mSMU.trigger.initiate()
        time.sleep(points*pPeriod + 3)
        return [k.read_buffer(self.mSMU.nvbuffer1)] ### nvbuffer 1 is read value


    def turnOffOutputs(self):
        self.sSMU.source.output=0


class K6221():
    def __init__(self):
        self.K6221Address='GPIB::12::INSTR'
        self.connected = self.connect()
        self.sm.write_termination='\n'
        self.sm.read_termination='\n'
        self.sm.chunk_size=102400
        self.sm.write(':SYST:PRES')
        time.sleep(1)
        self.sm.write('FORM:ELEM READ') ## send out only the reading
        self.sm.write(':SYST:COMM:SER:BAUD 19200') ### set baud
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

    def connect(self):
        try:
            rm = visa.ResourceManager('@py')
            self.sm=rm.open_resource(self.K6221Address) ## setting a delay between write and query
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
                    time.sleep(0.2)
                    resp = self.sm.query(':SYST:COMM:SER:ENT?')
                    logging.info('Read from instrument: ' + resp)
                    mData=np.append(mData,np.asarray(re.findall('[+-][0-9\.]+E[+-][0-9]+',resp),dtype=float))
                    logging.info('Adding data' + resp)
                except ValueError:
                    logging.warning('Unable to add the data' + resp)
                timeSlept +=0.5
                time.sleep(0.3)
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
            self.sm.write(':INIT:IMM')
            self.sm.write(':SYST:COMM:SER:SEND ":INIT"') ### reset 2182
            time.sleep(tPoints*(float(stepPeriod) + 0.1) + 5)
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

class B2912B():
    def __init__(self):
        address='USB0::0x2A8D::0x9501::MY61390244::INSTR'
        rm = visa.ResourceManager(r'C:\WINDOWS\system32\visa64.dll')
        self.sm=rm.open_resource(address)
        self.sm.write_termination='\n'
        self.sm.read_termination='\n'
        self.sm.write('*RST')
######### Souce limits need not be Auto. We always know the extents
    def setSourceMode(self,channel,param,lim,comp):
        self.sm.sourcemode=param
        if param == 'I': # source mode
            mod = 'CURR'
        else:
            mod = 'VOLT'
        if channel == 'a':
            chan='1'
        elif channel == 'b':
            chan='2'
        self.sm.write(':SOUR' + chan + ':FUNC:MODE '+mod) 
        if param == 'I': # source mode
            if lim.lower() == 'auto':
                self.sm.write(':SOUR' + chan + ':' + 'CURR' + ':RANG:AUTO ON') 
            else:
                self.sm.write(':SOUR' + chan + ':' + 'CURR' + ':RANG ' + str(lim)) 
            if comp.lower() == 'auto':
                self.sm.write(':SOUR' + chan + ':' + 'VOLT' + ':RANG:AUTO ON') 
            else:
                self.sm.write(':SENS' + chan + ':'+'VOLT'+':PROT '+ str(comp)) #set compliance
        else:
            if lim.lower() == 'auto':
                self.sm.write(':SOUR' + chan + ':' + 'VOLT' + ':RANG:AUTO ON') 
            else:
                self.sm.write(':SOUR' + chan + ':' + 'VOLT' + ':RANG ' + str(lim)) 
            if comp.lower() == 'auto':
                self.sm.write(':SOUR' + chan + ':' + 'CURR' + ':RANG:AUTO ON') 
            else:
                self.sm.write(':SENS' + chan + ':'+'CURR'+':PROT '+ str(comp)) #set compliance

        self.sm.write(':OUTPut' + chan + ':STATe 1')
######### Sense limit has an auto value
    def setSenseMode(self,channel,param,lim,nplc,aver):
        self.sm.sensemode=param
        if param == 'I': # sense mode
            mod = 'CURR'
            autoComp = str(0.1) ## if current is sensed, comp is set to 100 mA
        else:
            mod = 'VOLT'
            autoComp = str(100) ## is volt is sensed, compt is set to 100 V
        if channel == 'a':
            chan='1'
        elif channel == 'b':
            chan='2'
        if lim.lower() == 'auto':
            self.sm.write(':SENS' + chan + ':'+mod+':RANG:AUTO ON') 
            self.sm.write(':SENS' + chan + ':'+mod+':PROT '+ autoComp) #set compliance
        else:
            self.sm.write(':SENS' + chan + ':'+mod+':RANG '+lim) 
            comp = float(lim)*1.1
            self.sm.write(':SENS' + chan + ':'+mod+':PROT '+str(comp)) #set compliance
        self.sm.write(':SENS' + chan + ':FUNC \"' + mod + ':DC\"') 
        self.sm.write(':SENS' + chan + ':'+mod+':DC:NPLC ' + str(nplc)) 

    def doSource(self,channel,param,value):
        if param == 'I': # source mode
            mod = 'CURR'
        else:
            mod = 'VOLT'
        if channel == 'a':
            chan='1'
        elif channel == 'b':
            chan='2'
        self.sm.write(':SOUR' + chan + ':' + mod + ':LEV:IMM:AMPL ' + str(value)) 


    def doMeasure(self,channel,param,aver):
        if param == 'I': # source mode
            mod = 'CURR'
        else:
            mod = 'VOLT'
        val = np.zeros(aver)
        for i in range(aver):
            self.sm.write(':FORM:ELEM:SENS ' + mod)
            resp=self.sm.query(':MEAS:'+mod+'?')
            val[i] = float(resp)
        return np.mean(val)

    def getTraceData(self,smu,param,tPoints):
        if smu == 'a':
            mchan='1'
        elif smu == 'b':
            mchan='2'
        if param == 'I': # source mode
            mmod = 'CURR'
        else:
            mmod = 'VOLT'
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
            else: # see if you can get some data
                try:
                    time.sleep(0.2)
                    resp = self.sm.query(":fetc:arr:"+mmod+"? (@"+mchan+")")
                    mData=np.append(mData,np.asarray(re.findall('[+-][0-9\.]+E[+-][0-9]+',resp),dtype=float))
                    logging.info('Adding data' + resp)
                except Exception as e:
                    logging.warning('Unable to add the data. Got this  ' + resp)
                timeSlept +=0.5
                time.sleep(0.3)
        return mData
   

    def getErrors(self):
        err = self.sm.query(":syst:err:all?")
        return err
#######################################
############# IV sweep is a simple function to conduct IV sweeps on a single terminal that has to be passed via a dictionary
    def IVSweep(self,dcivData):
        sSmu = dcivData["source"]
        mSmu = dcivData["sense"]
        sParam=dcivData["sParam"]
        start=float(dcivData["sStart"])
        stop = float(dcivData["sEnd"])
        points = int(dcivData["sPoints"])
        loop = dcivData["Loop"]
        LoopBiDir = dcivData["LoopBiDir"]
        aver = int(dcivData["aver"])
        nplc = float(dcivData["nplc"])
        sLim = dcivData["slimit"]
        mLim= dcivData["mlimit"]
        stepPeriod=float(dcivData["sDel"])
        pWidth=float(dcivData["pWidth"])
        pPeriod=float(dcivData["pPeriod"])
        pulse = dcivData["Pulse"]
        RB = resultBook()
        if loop: 
            if LoopBiDir:
                sweepList = np.concatenate([np.linspace(0,stop,points),np.linspace(stop,0,points),np.linspace(0,-stop,points),np.linspace(-stop,0,points)])
            else:
                sweepList = np.concatenate([np.linspace(start,stop,points),np.linspace(stop,start,points)])
        else:
            sweepList = np.linspace(start,stop,points)
        logging.info('sweeing list' + str(sweepList))
        tPoints = len(sweepList)
        RB.points = tPoints

        if sParam == 'I': # source mode
            mod = 'CURR'
            mmod='VOLT' # measurement mode
            mParam = 'V'
        else:
            mod = 'VOLT'
            mmod='CURR'
            mParam = 'I'
            RB.V = sweepList

        if sSmu == 'a':
            schan='1'
        elif sSmu == 'b':
            schan='2'
        if mSmu == 'a':
            mchan='1'
        elif mSmu == 'b':
            mchan='2'

        ####### Set source settings
        self.setSourceMode(sSmu,sParam,str(stop),str(mLim))
        self.sm.write(":sour"+schan+":func:mode "+ mod)
        self.sm.write(":sour"+schan+":"+mod+":mode LIST") ## do a list sweep
        self.sm.write(":sour"+schan+":list:"+mod+" "+str(start)) ##reset list value
        for i in range(1,len(sweepList)):
            self.sm.write(":sour"+schan+":LIST:"+ mod+":APP "+str(sweepList[i])) ## do a list sweep
        if not sSmu == mSmu: ### If you want to measure from the other terminal, you also need to source it 
            sValue2=dcivData["sValue2"]
            self.sm.write(":sour"+mchan+":func:mode "+ mod)
            self.sm.write(":sour"+mchan+":"+mod+":mode FIX") ## the second terminal should be fixed
            self.sm.write(":sour"+mchan+":"+mod+":TRIG " + sValue2)

        self.setSenseMode(mSmu,mParam,mLim,nplc,1)
##### some math here for the setting these parameters: 
##3 look at B2900 programming manual page 29
#### trig:tran:del- 0.3 * period -idle wait time for each pulse
### puls:del - 0.1*period - time after idle for the source to be ready
### lets measure after 50% of pulse width - keeping enough time for measurement. Remember this 50% of pulse width should be larger than measurement averaging time. 
## with these, :trig:acq:del - (0.3 + 0.1)*period + 0.5*PW
        if pulse:
            self.sm.write(":sour"+schan+":func:shap puls")
            delay = 0.1*pWidth
            tranDel = 0.3*pWidth
            acqDel = delay + tranDel + 0.5*pWidth
            self.sm.write(":sour"+schan+":puls:del " + str(delay)) # this time is added to trig:trans:del. After this time, the source param is ramped to set value.
            self.sm.write(":sour"+schan+":puls:widt "+ str(pWidth))
            period = pPeriod
        else:
            self.sm.write(":sour"+schan+":func:shap dc")
            delay = 0.1*stepPeriod
            tranDel = 0.3*stepPeriod
            acqDel = delay + tranDel + 0.5*stepPeriod
            period=stepPeriod
########## initially, we had only one channel to be triggered. But for mosfet, we need to trigger and measure both
        if sSmu == mSmu:
            self.sm.write(":trig"+schan+":sour tim") ### the source trigger is internally generated. defined by the period
            self.sm.write(":trig"+schan+":tran:del "+ str(tranDel)) # the from trigger before start of sourcing
            self.sm.write(":trig"+schan+":acq:del "+str(acqDel)) # time from the trigger pulse to measure
            self.sm.write(":trig"+schan+":tim " + str(period)) # period of pulse
            self.sm.write(":trig"+schan+":coun " + str(tPoints)) # number of steps
            self.sm.write(":outp"+schan+" on") 
            self.sm.write(":init (@"+schan+")") 
            time.sleep(tPoints*period + 3)## wait for sweep period and some 3 seconds
            res = self.getTraceData(mSmu,mParam,tPoints)
            if sParam == 'I':
                RB.V = res
                RB.I = sweepList
            else:
                RB.I = res
                RB.V = sweepList
        else: ## synced measurements
            self.sm.write(":trig"+schan+":sour tim") ### the source trigger is internally generated. defined by the period
            self.sm.write(":trig"+mchan+":sour tim") ### the source trigger is internally generated. defined by the period
            self.sm.write(":trig"+schan+":tran:del "+ str(tranDel)) # the from trigger before start of sourcing
            self.sm.write(":trig"+mchan+":tran:del "+ str(tranDel)) # the from trigger before start of sourcing
            self.sm.write(":trig"+schan+":acq:del "+str(acqDel)) # time from the trigger pulse to measure
            self.sm.write(":trig"+mchan+":acq:del "+str(acqDel)) # time from the trigger pulse to measure
            self.sm.write(":trig"+schan+":tim " + str(period)) # period of pulse
            self.sm.write(":trig"+mchan+":tim " + str(period)) # period of pulse
            self.sm.write(":trig"+schan+":coun " + str(tPoints)) # number of steps
            self.sm.write(":trig"+mchan+":coun " + str(tPoints)) # number of steps
            self.sm.write(":outp"+schan+" on") 
            self.sm.write(":outp"+mchan+" on") 
            self.sm.write(":init (@"+schan+',' + mchan+")") 
            time.sleep(tPoints*period + 3)## wait for sweep period and some 3 seconds
            res2 = self.getTraceData(mSmu,mParam,tPoints)
            res1 = self.getTraceData(sSmu,mParam,tPoints)
            if sParam == 'I':
                RB.V = res1 ### from the sourcing terminal
                RB.V2 = res2 ### from the other terminal
                RB.I = sweepList
            else:
                RB.I = res1 ### from the sourcing termina
                RB.I2 = res2 ## from the other terminal
                RB.V = sweepList

        return RB

##########################################
######### IVT is a simple function to do sampling on a single source. 
####################################################

    def ivt(self,ivtData):
        sSmu = ivtData["source"]
        s2 = ivtData["s2"]
        mSmu = ivtData["sense"]
        sParam=ivtData["sParam"]
        s2p=ivtData["s2p"]
        s2enable=ivtData["s2enable"]
        sValue=float(ivtData["sValue"])
        s2Value=float(ivtData["s2Value"])
        tPoints = int(ivtData["tPoints"])
        aver = int(ivtData["aver"])
        nplc = float(ivtData["nplc"])
        sLim = ivtData["slimit"]
        mLim= ivtData["mlimit"]
        tInt=float(ivtData["tInt"])
        RB = resultBook()
        RB.points = tPoints

        if sParam == 'I': # source mode
            mod = 'CURR'
            mmod='VOLT' # measurement mode
            mParam = 'V'
            RB.I = sValue*np.ones(tPoints)
        else:
            mod = 'VOLT'
            mmod='CURR'
            mParam = 'I'
            RB.V = sValue*np.ones(tPoints)

        if sSmu == 'a':
            schan='1'
        elif sSmu == 'b':
            schan='2'
        if mSmu == 'a':
            mchan='1'
        elif mSmu == 'b':
            mchan='2'
        ####### Set source settings
        self.setSourceMode(sSmu,sParam,str(sValue*1.1),str(mLim))
        self.doSource(sSmu,sParam,sValue)
        if s2enable:
            self.setSourceMode(s2,s2p,str(s2Value*1.1),str(mLim))
            self.doSource(s2,s2p,s2Value)

        self.setSenseMode(mSmu,mParam,mLim,nplc,aver)
##### some math here for the setting these parameters: 
##3 look at B2900 programming manual page 29
#### trig:tran:del- 0.3 * period -idle wait time for each pulse
### puls:del - 0.1*period - time after idle for the source to be ready
### lets measure after 50% of pulse width - keeping enough time for measurement. Remember this 50% of pulse width should be larger than measurement averaging time. 
## with these, :trig:acq:del - (0.3 + 0.1)*period + 0.5*PW
        delay = 0.1*tInt
        tranDel = 0.3*tInt
        acqDel = delay + tranDel + 0.5*tInt
        period=tInt
        self.sm.write(":trig"+schan+":sour tim") ### the source trigger is internally generated. defined by the period
        self.sm.write(":trig"+schan+":tran:del "+ str(tranDel)) # the from trigger before start of sourcing
        self.sm.write(":trig"+mchan+":acq:del "+str(acqDel)) # time from the trigger pulse to measure
        self.sm.write(":trig"+schan+":tim " + str(period)) # period of pulse
        self.sm.write(":trig"+schan+":coun " + str(tPoints)) # number of steps
        self.sm.write(":outp"+schan+" on") 
        self.sm.write(":init (@"+schan+")") 
        time.sleep(tPoints*period + 3)## wait for sweep period and some 3 seconds
        res = self.getTraceData(mSmu,mParam,tPoints)
        RB.T = np.linspace(0,tPoints*period,tPoints)
        if sParam == 'I':
            RB.V = res
        else:
            RB.I = res
        return RB

    def turnOffOutputs(self):
        self.sm.write(':OUTPut1:STATe 0')
        self.sm.write(':OUTPut2:STATe 0')



####################################################################################
##### Dummy class to hold all the results ##########################################
##### An object of this class is always returned  from each measurement ##############
###################################################################################
class resultBook:
    def __init__(self):
        logging.info('A result book is created')


##################################################
#### This class is instantiated upon pressing the config button
#############################

class measurements:
    def __init__(self):
        self.active = False
        ################# Queue to hold the measured data from measurement threads ###########
        self.measureData = queue.Queue()

################### function definitions ##############
    def abortMeasurement(self,measFrame,configFrame,PF): ## only IVT frame does this!
        self.active=False ### when this is clicked, bring measurement down
######################## Script to run the actual measurement program ##########################
    def runMeasurement(self,measFrame,configFrame,PF):
        timeElapsed=0
        while self.active: #### is another measurement is running - wait
            if timeElapsed >5:
                return
            else:
                print('measurement running. We wait')
                time.sleep(1)
                timeElapsed +=1
        measData = measFrame.getButtonValues()
        configData = configFrame.getButtonValues()
        measureFile = configData["WD"] + '/' + configData["mName"] + ".csv"
        errFile = configData["WD"] + '/' + configData["mName"] + "err.txt"
        self.MD = configFrame.MD ### get the measurement tool instance
        self.measureData.queue.clear()
        PF.showRunning()

        if configData["mt"] == 'iv':
            plotData = np.zeros((1,2))
            PF.clearPlot()
            f1 = open(measureFile,'w')
            f1.write("Voltage,Current\n")
            t1=threading.Thread(target=self.runDCIV, args=(measData,))
            t1.start()
            while t1.is_alive():
                time.sleep(3)
                while not self.measureData.empty():
                    plotData = self.measureData.get()
                    f1.write(str(plotData[0]) + ',' + str(plotData[1]) + '\n')
                    PF.addPoint(plotData[0],plotData[1],'*k')
                PF.flushPlot()
            #inArray = np.loadtxt('data.csv',delimiter=',')
            t1.join()
            f1.close()
        elif configData["mt"] == 'dIdV':
            plotData = np.zeros((1,2))
            PF.clearPlot()
            f1 = open(measureFile,'w')
            f1.write("dVdI,Current\n")
            t1=threading.Thread(target=self.rundIdV, args=(measData,))
            t1.start()
            while t1.is_alive():
                time.sleep(3)
                while not self.measureData.empty():
                    plotData = self.measureData.get()
                    f1.write(str(plotData[1]) + ',' + str(plotData[0]) + '\n')
                    PF.addPoint(plotData[1],plotData[0])
                PF.flushPlot()
            t1.join()
            f1.close()
        elif configData["mt"] == 'MOSFET':
            plotData = np.zeros((1,2))
            PF.clearPlot()
            f1 = open(measureFile,'w')
            f1.write("GateVoltage,GateCurrent,DrainVoltage,DrainCurrent\n")
            t1=threading.Thread(target=self.runMOSFET, args=(measData,))
            t1.start()
            xIndex = int(measData["xIndex"])
            yIndex = int(measData["yIndex"])
            while t1.is_alive():
                time.sleep(3)
                while not self.measureData.empty():
                    plotData = self.measureData.get()
                    f1.write(str(plotData[0]) + ',' + str(plotData[1]) + ',' + str(plotData[2])+',' + str(plotData[3])+'\n')
                    PF.addPoint(plotData[xIndex],plotData[yIndex])
                PF.flushPlot()
            #inArray = np.loadtxt('data.csv',delimiter=',')
            t1.join()
            f1.close()
        elif configData["mt"] == 'IVT':
            plotData = np.zeros((1,2))
            PF.clearPlot()
            f1 = open(measureFile,'w')
            f1.write("Voltage,Current,Time\n")
            t1=threading.Thread(target=self.runIVT, args=(measData,))
            t1.start()
            while t1.is_alive():
                time.sleep(3)
                while not self.measureData.empty():
                    plotData = self.measureData.get()
                    f1.write(str(plotData[0]) + ',' + str(plotData[1]) + ',' + str(plotData[2])+'\n')
                    if measData["sParam"] == 'I':
                        PF.addPoint(plotData[2],plotData[0],'g-*')
                    else:
                        PF.addPoint(plotData[2],plotData[1],'g-*')
                PF.flushPlot()
            #inArray = np.loadtxt('data.csv',delimiter=',')
            t1.join()
            f1.close()
        else:
            print('yet to be implemented')
        PF.removeRunning()
        ############ get all errors###################
        err=self.MD.getErrors()
        ferr = open(errFile,'w')
        for line in err:
            ferr.write(line + '\n')
        ferr.close()

    def rundIdV(self,dIdVData):
        self.active = True
        indata=self.MD.dodIdV(dIdVData)
        self.MD.turnOffOutputs() 
        self.active = False
        for i in range(indata.points):
            self.measureData.put([indata.dIdV[i],indata.I[i]])
        ### set outputs to off state


    def runDCIV(self,dcivData):
        self.active = True
        measured = self.MD.IVSweep(dcivData) ### got the data in the format of a result book
        self.MD.turnOffOutputs() 
        self.active = False
        for i in range(measured.points):
            self.measureData.put([measured.V[i],measured.I[i]])
        ### set outputs to off state

    def runMOSFET(self,mosfetData):
        logging.info('Entering MOSFET driver')
        self.active = True
        dSMU = mosfetData["drain"]
        dParam=mosfetData["dParam"]
        gParam=mosfetData["gParam"]
        dStart=float(mosfetData["VDs"])
        dStop = float(mosfetData["VDe"])
        gStart=float(mosfetData["VGs"])
        gStop = float(mosfetData["VGe"])
        dPoints = int(mosfetData["dPoints"])
        gPoints = int(mosfetData["gPoints"])
        gSMU = mosfetData["gate"]
        loop = mosfetData["Loop"]
        dLoopDrain = mosfetData["LoopDrain"]
        gLoop = mosfetData["LoopGate"]
        dLoop = mosfetData["LoopDrain"]
        LoopBiDir = mosfetData["LoopBiDir"]
        sweepTerm = mosfetData["sweepTerm"]
        sDel = mosfetData["sDel"]
        aver = int(mosfetData["aver"])
        nplc = float(mosfetData["nplc"])
        dsLimit = mosfetData["dslimit"]
        dmLimit = mosfetData["dmlimit"]
        gsLimit = mosfetData["gslimit"]
        gmLimit = mosfetData["gmlimit"]
        pulse = mosfetData["Pulse"]
        pWidth = float(mosfetData["pWidth"])
        pPeriod = float(mosfetData["pPeriod"])

        if dParam == 'I':
            dsParam='I'
            dmParam='V'
        else:
            dsParam='V'
            dmParam='I'
        if gParam == 'I':
            gsParam='I'
            gmParam='V'
        else:
            gsParam='V'
            gmParam='I'
        ######################## prepare the didvData ###############
        ############## configure source smu#####
        self.MD.setSourceMode(dSMU,dParam,str(dsLimit),str(dmLimit))
        self.MD.setSourceMode(gSMU,gParam,str(gsLimit),str(dmLimit))
        self.MD.setSenseMode(dSMU,dParam,dmLimit,nplc,aver)
        self.MD.setSenseMode(gSMU,gParam,gmLimit,nplc,aver)
############### IDVD measurements ############################        
        if not sweepTerm: ##### sweep drain for every gate potential
            drainData = {
                "source":dSMU,
                "sense":dSMU,
                "sParam":dsParam,
                "mParam":dmParam,
                "sEnd":dStop,
                "sStart":dStart,
                "sPoints":dPoints,
                "sDel":sDel,
                "Loop":dLoop & loop,
                "LoopBiDir":LoopBiDir,
                "Pulse":pulse,
                "pPeriod":pPeriod,
                "pWidth":pWidth,
                "aver":aver,
                "nplc":nplc,
                "slimit":dsLimit,
                "mlimit":dmLimit
            }
            if loop & gLoop: 
                if LoopBiDir: ### bidirectional looping for butterfly loops. start point always zero
                    gateList = np.concatenate([np.linspace(0,gStop,gPoints),np.linspace(gStop,0,gPoints),np.linspace(0,-gStop,gPoints),np.linspace(-gStop,0,gPoints)])
                else:
                    gateList = np.concatenate([np.linspace(gStart,gStop,gPoints),np.linspace(gStop,gStart,gPoints)])
            else:
                gateList = np.linspace(gStart,gStop,gPoints)
            for i in range(len(gateList)):
                self.MD.doSource(gSMU,gsParam,gateList[i])
        ######################## prepare the didvData ###############
                dmeasure = self.MD.IVSweep(drainData) # returns RB class object
                gmeasure = self.MD.doMeasure(gSMU,gmParam,aver) # get gate current/voltage
                for j in range(dmeasure.points):
                    if gParam == 'I':
                        self.measureData.put([gmeasure,gateList[i],dmeasure.V[j],dmeasure.I[j]]) # put all data
                    else:
                        self.measureData.put([gateList[i],gmeasure,dmeasure.V[j],dmeasure.I[j]]) # put all data always as gV,gI,dV,dI
        else: # do ID-VG measurement
            if loop & dLoop: 
                if LoopBiDir: ### bidirectional looping for butterfly loops. start point always zero
                    drainList = np.concatenate([np.linspace(0,dStop,dPoints),np.linspace(dStop,0,dPoints),np.linspace(0,-dStop,dPoints),np.linspace(-dStop,0,dPoints)])
                else:
                    drainList = np.concatenate([np.linspace(dStart,dStop,dPoints),np.linspace(dStop,dStart,dPoints)])
            else:
                drainList = np.linspace(dStart,dStop,dPoints)
            gateData = {
                "source":gSMU,
                "sense":dSMU,
                "sParam":gsParam,
                "mParam":dmParam,
                "sEnd":gStop,
                "sStart":gStart,
                "sPoints":gPoints,
                "sDel":sDel,
                "Loop":gLoop & loop,
                "LoopBiDir":LoopBiDir,
                "Pulse":pulse,
                "pPeriod":pPeriod,
                "pWidth":pWidth,
                "aver":aver,
                "nplc":nplc,
                "slimit":gsLimit,
                "mlimit":dmLimit
            }
            for i in range(len(drainList)):
                self.MD.doSource(dSMU,dsParam,drainList[i])
                gateData["sValue2"] = str(drainList[i]) ### drain value for gate sweep
                gmeasure = self.MD.IVSweep(gateData) # returns only measured value
                dmeasure = self.MD.doMeasure(dSMU,dmParam,aver) # get drain currents
                gateCurrent = self.MD.doMeasure(gSMU,gmParam,aver) # get drain currents
                for j in range(gmeasure.points): 
                    if dParam == 'I':
                        self.measureData.put([gmeasure.V[j],gmeasure.I[j],dmeasure,drainList[i]]) # put all data
                    else: ### This is the true IDVG case. 
                        self.measureData.put([gmeasure.V[j],gmeasure.I[j],drainList[i],gmeasure.I2[j]]) # put all data always as gV,gI,dV,dI
        self.MD.turnOffOutputs()
        self.active = False

    def runIVT(self,ivtData):
        logging.info('Into IVT module')
        self.active = True
        if ivtData["RTD"]:
            sSmu = ivtData["source"]
            s2 = ivtData["s2"]
            mSmu = ivtData["sense"]
            sParam=ivtData["sParam"]
            s2p=ivtData["s2p"]
            s2enable=ivtData["s2enable"]
            sValue=float(ivtData["sValue"])
            s2Value=float(ivtData["s2Value"])
            tPoints = int(ivtData["tPoints"])
            aver = int(ivtData["aver"])
            nplc = float(ivtData["nplc"])
            sLim = ivtData["slimit"]
            mLim= ivtData["mlimit"]
            tInt=float(ivtData["tInt"])
            RB = resultBook()
            RB.points = tPoints
            if sParam == 'I': # source mode
                mod = 'CURR'
                mmod='VOLT' # measurement mode
                mParam = 'V'
                RB.I = sValue*np.ones(tPoints)
            else:
                mod = 'VOLT'
                mmod='CURR'
                mParam = 'I'
                RB.V = sValue*np.ones(tPoints)
            if sSmu == 'a':
                schan='1'
            elif sSmu == 'b':
                schan='2'
            if mSmu == 'a':
                mchan='1'
            elif mSmu == 'b':
                mchan='2'
            ####### Set source settings
            self.MD.setSourceMode(sSmu,sParam,str(sValue*1.1),str(mLim))
            self.MD.doSource(sSmu,sParam,sValue)
            if s2enable:
                self.MD.setSourceMode(s2,s2p,str(s2Value*1.1),str(mLim))
                self.MD.doSource(s2,s2p,s2Value)
            self.MD.setSenseMode(mSmu,mParam,mLim,nplc,aver)
            tElapse = 0
            while self.active:
                readData = self.MD.doMeasure(mSmu,mParam,aver)
                print(readData)
                if mParam == 'V':
                    self.measureData.put([readData,sValue,tElapse])
                else:
                    self.measureData.put([sValue,readData,tElapse])
                time.sleep(tInt)
                tElapse += tInt
        else:
            measuredData=self.MD.ivt(ivtData)
            for i in range(measuredData.points):
                self.measureData.put([measuredData.V[i],measuredData.I[i],measuredData.T[i]])
        self.MD.turnOffOutputs()
        self.active = False

########################################################################





################# Gui part ###############
#######################################


class configFrame(tk.Frame):
    def __init__(self,parent,PF):
        super().__init__(parent)
        self.mt = tk.StringVar()
        self.iName = tk.StringVar()
        rCount = 0
        #### Measurement Name ###################
        label_a = tk.Label(master=self, text="Measurement Configurations", font = ('Calibri',12,'bold'))
        label_a.grid(row=rCount,column = 0)
        rCount = rCount + 1
        lbl_mName = tk.Label(self, text="Measurement Name")
        lbl_mName.grid(row=rCount,column=0,sticky='e')
        self.mName = tk.Entry(master=self, width=10)
        self.mName.grid(row=rCount,column=1,sticky='w')
        rCount = rCount + 1
        #### Working director
        lbl_WD = tk.Label(self, text="Working Directory")
        lbl_WD.grid(row=rCount,column=0,sticky='e')
        self.WD = tk.Entry(master=self, width=10)
        self.WD.grid(row=rCount,column=1,sticky='w')
        rCount = rCount + 1
        #### Instrument Name ###################
        lbl_Iname = tk.Label(master=self, text="Instrument Name")
        lbl_Iname.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="Keithley 2636B", variable=self.iName, value='K2636B')
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="Keysight B2912B", variable=self.iName, value='B2912B')
        r1.grid(row=rCount,column=2)
        r1 = tk.Radiobutton(self, text="Keithley 6221+2182A", variable=self.iName, value='K6221')
        r1.grid(row=rCount,column=3)
        rCount = rCount + 1
        #### Measurement Type ################
        lbl_mt = tk.Label(master=self, text="measurement type")
        lbl_mt.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="DC IV", variable=self.mt, value='iv')
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="MOSFET IDVG", variable=self.mt, value='MOSFET')
        r1.grid(row=rCount,column=2)
        r1 = tk.Radiobutton(self, text="IV-T", variable=self.mt, value='IVT')
        r1.grid(row=rCount,column=3)
        r1 = tk.Radiobutton(self, text="dIdV", variable=self.mt, value='dIdV')
        r1.grid(row=rCount,column=4)
        rCount = rCount + 1
        bt = tk.Button(master=self,text='Set Defaults',command=self.setDefaults)
        bt.grid(row = rCount,column = 0)
        rCount = rCount + 1
        lbl_mp = tk.Label(master=self, text="Press Config to configure measurements")
        lbl_mp.grid(row =rCount,column = 0,sticky = 'e')
        switch=tk.Button(self,text='Config',command= parent.switchFrame)
        switch.grid(row = rCount,column = 1,sticky = 'e')
    def setDefaults(self):
        self.iName.set('K2636B')
        self.mt.set('iv')
        self.mName.delete(0,tk.END)
        self.mName.insert(0,'test')
        self.WD.delete(0,tk.END)
        self.WD.insert(0,'./')
    def getButtonValues(self):
        configData = {
        "inst":self.iName.get(),
        "mt":self.mt.get(),
        "mName":self.mName.get(),
        "WD":self.WD.get()
        }
        return configData



class dIdVFrame(tk.Frame):
    def __init__(self,parent, configFrame, plotFrame):
        self.damp = tk.StringVar()
        self.ddel = tk.StringVar()
        super().__init__(parent)
        self.measure = measurements()
        #### Smu to be used ################
        rCount = 0
        lbl_source = tk.Label(master=self, text="dIdV Control Settings")
        lbl_source.grid(row=rCount,column=0,sticky='e')
        rCount = rCount + 1
        #### Source start ###################
        lbl_sStart = tk.Label(master=self, text="Source Start (V/A)")
        lbl_sStart.grid(row=rCount,column=0,sticky='e')
        self.sStart = tk.Entry(master=self, width=10)
        self.sStart.grid(row=rCount,column=1,sticky='e')
        rCount = rCount + 1
        #### Averaging ###################
        lbl_sEnd = tk.Label(master=self, text="Source End (V/A)")
        lbl_sEnd.grid(row=rCount,column=0,sticky='e')
        self.sEnd = tk.Entry(master=self, width=10)
        self.sEnd.grid(row=rCount,column=1,sticky='e')
        rCount = rCount + 1
        #### Averaging ###################
        lbl_sPoints = tk.Label(master=self, text="Points")
        lbl_sPoints.grid(row=rCount,column=0,sticky='e')
        self.sPoints = tk.Entry(master=self, width=10)
        self.sPoints.grid(row=rCount,column=1,sticky='w')
        rCount = rCount + 1
        #### Averaging ###################
        lbl_mAverage = tk.Label(master=self, text="Manual Averaging")
        lbl_mAverage.grid(row=rCount,column=0,sticky='e')
        self.mAverage = tk.Entry(master=self, width=10)
        self.mAverage.grid(row=rCount,column=1,sticky='e')
        lbl_nAverage = tk.Label(master=self, text=" NPLC (20ms*) ")
        lbl_nAverage.grid(row=rCount,column=2,sticky='e')
        self.nAverage = tk.Entry(master=self, width=10)
        self.nAverage.grid(row=rCount,column=3,sticky='e')
        rCount = rCount + 1
        #### Source parameter ################
        lbl_dampl = tk.Label(master=self, text="Delta ampl")
        lbl_dampl.grid(row=rCount,column=0,sticky='e')
        self.damp = tk.Entry(master=self, width=10)
        self.damp.grid(row=rCount,column=1,sticky='e')
        lbl_ddelay = tk.Label(master=self, text="Delta delay")
        lbl_ddelay.grid(row=rCount,column=2,sticky='e')
        self.ddel = tk.Entry(master=self, width=10)
        self.ddel.grid(row=rCount,column=3,sticky='e')
        rCount = rCount + 1
        #### Limits and ranges #########################
        #### Source limit ###################
        lbl_slimit = tk.Label(master=self, text="source limit (A)")
        lbl_slimit.grid(row=rCount,column=0,sticky='e')
        self.slimit = tk.Entry(master=self, width=10)
        self.slimit.grid(row=rCount,column=1,sticky='w')
        rCount = rCount + 1
        #### measure limit ###################
        lbl_mlimit = tk.Label(master=self, text="measure limit (V/A)")
        lbl_mlimit.grid(row=rCount,column=0,sticky='e')
        self.mlimit = tk.Entry(master=self, width=10)
        self.mlimit.insert(0,'100E-3')
        self.mlimit.grid(row=rCount,column=1,sticky='w')
        rCount = rCount + 1

        btn_run = tk.Button(master=self, text="Run",command=lambda: self.measure.runMeasurement(self,configFrame,plotFrame))
        btn_run.grid(row=rCount,column=0)
        bt = tk.Button(master=self,text='Set Defaults',command=self.setDefaults)
        bt.grid(row = rCount,column = 1)
    def setDefaults(self):
        self.mlimit.delete(0,tk.END)
        self.mlimit.insert(0,'Auto')
        self.slimit.delete(0,tk.END)
        self.slimit.insert(0,'100E-3')
        self.sEnd.delete(0,tk.END)
        self.sEnd.insert(0,'100E-3')
        self.sPoints.delete(0,tk.END)
        self.sStart.delete(0,tk.END)
        self.sStart.insert(0,'0')
        self.mAverage.delete(0,tk.END)
        self.mAverage.insert(0,'1')
        self.nAverage.delete(0,tk.END)
        self.nAverage.insert(0,'1')
        self.sPoints.insert(0,'10')
        self.damp.delete(0,tk.END)
        self.damp.insert(0,'1E-6')
        self.ddel.delete(0,tk.END)
        self.ddel.insert(0,'1E-3')
    def getButtonValues(self):
        dIdVData = {
            "source":'a',
            "sense":'a',
            "sParam":'I',
            "mParam":'V',
            "sEnd":self.sEnd.get(),
            "sStart":self.sStart.get(),
            "sPoints":self.sPoints.get(),
            "ddel":self.ddel.get(),
            "damp":self.damp.get(),
            "aver":self.mAverage.get(),
            "nplc":self.nAverage.get(),
            "slimit":self.slimit.get(),
            "mlimit":self.mlimit.get()
        }
        return dIdVData

class DCIVFrame(tk.Frame):
    def __init__(self,parent, configFrame, plotFrame):
        self.source = tk.StringVar()
        self.sense = tk.StringVar()
        self.mp = tk.StringVar()
        self.sp = tk.StringVar()
        self.iName = tk.StringVar()
        self.Pulse = tk.BooleanVar()
        self.Loop = tk.BooleanVar()
        self.LoopBiDir = tk.BooleanVar()
        super().__init__(parent)
        self.measure = measurements()
        #### Smu to be used ################
        rCount = 0
        lbl_source = tk.Label(master=self, text="DC IV Control Settings")
        lbl_source.grid(row=rCount,column=0,sticky='e')
        rCount = rCount + 1
        lbl_source = tk.Label(master=self, text="Source SMU")
        lbl_source.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="SMU A", variable=self.source, value='a')
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="SMU B", variable=self.source, value='b')
        r1.grid(row=rCount,column=2)
        rCount = rCount + 1
        lbl_source = tk.Label(master=self, text="Sense SMU")
        lbl_source.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="SMU A", variable=self.sense, value='a')
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="SMU B", variable=self.sense, value='b')
        r1.grid(row=rCount,column=2)
        rCount = rCount + 1
        
        #### Source start ###################
        lbl_sStart = tk.Label(master=self, text="Source Start (V/A)")
        lbl_sStart.grid(row=rCount,column=0,sticky='e')
        self.sStart = tk.Entry(master=self, width=10)
        self.sStart.grid(row=rCount,column=1,sticky='e')
        rCount = rCount + 1

        #### Averaging ###################
        lbl_sEnd = tk.Label(master=self, text="Source End (V/A)")
        lbl_sEnd.grid(row=rCount,column=0,sticky='e')
        self.sEnd = tk.Entry(master=self, width=10)
        self.sEnd.grid(row=rCount,column=1,sticky='e')
        rCount = rCount + 1
        #### Averaging ###################
        lbl_sPoints = tk.Label(master=self, text="Points")
        lbl_sPoints.grid(row=rCount,column=0,sticky='e')
        self.sPoints = tk.Entry(master=self, width=10)
        self.sPoints.grid(row=rCount,column=1,sticky='w')
        lbl_sPoints = tk.Label(master=self, text="sweep delay")
        lbl_sPoints.grid(row=rCount,column=2,sticky='e')
        self.sDel = tk.Entry(master=self, width=10)
        self.sDel.grid(row=rCount,column=3,sticky='w')
        rCount = rCount + 1
        #### Averaging ###################
        lbl_mAverage = tk.Label(master=self, text="Manual Averaging count")
        lbl_mAverage.grid(row=rCount,column=0,sticky='e')
        self.mAverage = tk.Entry(master=self, width=10)
        self.mAverage.grid(row=rCount,column=1,sticky='e')
        lbl_nAverage = tk.Label(master=self, text=" NPLC (20ms*)")
        lbl_nAverage.grid(row=rCount,column=2,sticky='e')
        self.nAverage = tk.Entry(master=self, width=10)
        self.nAverage.grid(row=rCount,column=3,sticky='e')
        rCount = rCount + 1
        #### Loop parameter ################
        lbl_sp = tk.Label(master=self, text="Loop")
        lbl_sp.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="True", variable=self.Loop, value=1)
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="False", variable=self.Loop, value=0)
        r1.grid(row=rCount,column=2)
        c1=tk.Checkbutton(self,text="BiDirect",variable=self.LoopBiDir,onvalue=True,offvalue=False)
        c1.grid(row=rCount,column=3)
        rCount = rCount + 1
        #### Source parameter ################
        lbl_sp = tk.Label(master=self, text="Pulsing")
        lbl_sp.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="True", variable=self.Pulse, value=1)
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="False", variable=self.Pulse, value=0)
        r1.grid(row=rCount,column=2)
        rCount = rCount + 1
        #### pulse period ###################
        lbl_pPeriod = tk.Label(master=self, text="pulse period (S)")
        lbl_pPeriod.grid(row=rCount,column=0,sticky='e')
        self.pPeriod = tk.Entry(master=self, width=10)
        self.pPeriod.grid(row=rCount,column=1,sticky='e')
        #### Source limit ###################
        lbl_pWidth = tk.Label(master=self, text="pulse width (S)")
        lbl_pWidth.grid(row=rCount,column=2,sticky='e')
        self.pWidth = tk.Entry(master=self, width=10)
        self.pWidth.grid(row=rCount,column=3,sticky='e')
        rCount = rCount + 1

        #### Source parameter ################
        lbl_sp = tk.Label(master=self, text="Source parameter")
        lbl_sp.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="voltage", variable=self.sp, value='V')
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="current", variable=self.sp, value='I')
        r1.grid(row=rCount,column=2)
        rCount = rCount + 1
        #### Smu to be used ################
        lbl_mp = tk.Label(master=self, text="measure parameter")
        lbl_mp.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="voltage", variable=self.mp, value='V')
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="current", variable=self.mp, value='I')
        r1.grid(row=rCount,column=2)
        rCount = rCount + 1
        #### Limits and ranges #########################
        #### Source limit ###################
        lbl_slimit = tk.Label(master=self, text="source limit (V/A)")
        lbl_slimit.grid(row=rCount,column=0,sticky='e')
        self.slimit = tk.Entry(master=self, width=10)
        self.slimit.grid(row=rCount,column=1,sticky='w')
        rCount = rCount + 1
        #### measure limit ###################
        lbl_mlimit = tk.Label(master=self, text="measure limit (V/A)")
        lbl_mlimit.grid(row=rCount,column=0,sticky='e')
        self.mlimit = tk.Entry(master=self, width=10)
        self.mlimit.insert(0,'100E-3')
        self.mlimit.grid(row=rCount,column=1,sticky='w')
        rCount = rCount + 1

        btn_run = tk.Button(master=self, text="Run",command=lambda: self.measure.runMeasurement(self,configFrame,plotFrame))
        btn_run.grid(row=rCount,column=0)
        bt = tk.Button(master=self,text='Set Defaults',command=self.setDefaults)
        bt.grid(row = rCount,column = 1)
    def setDefaults(self):
        self.mlimit.delete(0,tk.END)
        self.mlimit.insert(0,'Auto')
        self.slimit.delete(0,tk.END)
        self.slimit.insert(0,'100E-3')
        self.sEnd.delete(0,tk.END)
        self.sEnd.insert(0,'100E-3')
        self.sStart.delete(0,tk.END)
        self.sStart.insert(0,'0')
        self.sPoints.delete(0,tk.END)
        self.sDel.delete(0,tk.END)
        self.pWidth.delete(0,tk.END)
        self.pWidth.insert(0,'10E-3')
        self.pPeriod.delete(0,tk.END)
        self.pPeriod.insert(0,'1')
        self.sStart.delete(0,tk.END)
        self.sStart.insert(0,'0')
        self.sPoints.insert(0,'10')
        self.sDel.insert(0,'100E-3')
        self.mAverage.delete(0,tk.END)
        self.mAverage.insert(0,'1')
        self.nAverage.delete(0,tk.END)
        self.nAverage.insert(0,'5')
        self.source.set('a')
        self.sense.set('a')
        self.mp.set('I')
        self.sp.set('V')
        self.Pulse.set(False)
        self.Loop.set(False)
        self.LoopBiDir.set(False)
    def getButtonValues(self):
        dcivData = {
            "source":self.source.get(),
            "sense":self.sense.get(),
            "sParam":self.sp.get(),
            "mParam":self.mp.get(),
            "sEnd":self.sEnd.get(),
            "sStart":self.sStart.get(),
            "sPoints":self.sPoints.get(),
            "sDel":self.sDel.get(),
            "Loop":self.Loop.get(),
            "LoopBiDir":self.LoopBiDir.get(),
            "Pulse":self.Pulse.get(),
            "pPeriod":self.pPeriod.get(),
            "pWidth":self.pWidth.get(),
            "aver":self.mAverage.get(),
            "nplc":self.nAverage.get(),
            "slimit":self.slimit.get(),
            "mlimit":self.mlimit.get(),
        }
        return dcivData

class IVTFrame(tk.Frame):
    def __init__(self,parent, configFrame, plotFrame):
        self.source = tk.StringVar()
        self.sense = tk.StringVar()
        self.s2 = tk.StringVar()
        self.s2p = tk.StringVar()
        self.sValue = tk.StringVar()
        self.s2Value = tk.StringVar()
        self.tPoints = tk.StringVar()
        self.tInt = tk.StringVar()
        self.mp = tk.StringVar()
        self.sp = tk.StringVar()
        self.iName = tk.StringVar()
        self.Pulse = tk.BooleanVar()
        self.s2enable = tk.BooleanVar()
        self.RTD = tk.BooleanVar()
        self.Loop = tk.BooleanVar()
        super().__init__(parent)
        self.measure = measurements()
        #### Smu to be used ################
        rCount = 0
        lbl_source = tk.Label(master=self, text="IVT Control Settings")
        lbl_source.grid(row=rCount,column=0,sticky='e')
        rCount = rCount + 1
        lbl_source = tk.Label(master=self, text="Source SMU")
        lbl_source.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="SMU A", variable=self.source, value='a')
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="SMU B", variable=self.source, value='b')
        r1.grid(row=rCount,column=2)
        rCount = rCount + 1
        lbl_source = tk.Label(master=self, text="Sense SMU")
        lbl_source.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="SMU A", variable=self.sense, value='a')
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="SMU B", variable=self.sense, value='b')
        r1.grid(row=rCount,column=2)
        rCount = rCount + 1
        
        #### Source start ###################
        lbl_sStart = tk.Label(master=self, text="Source Value (V/A)")
        lbl_sStart.grid(row=rCount,column=0,sticky='e')
        self.sValue = tk.Entry(master=self, width=10)
        self.sValue.grid(row=rCount,column=1,sticky='e')
        rCount = rCount + 1
        
        #### Averaging ###################
        lbl_sPoints = tk.Label(master=self, text="Points")
        lbl_sPoints.grid(row=rCount,column=0,sticky='e')
        self.tPoints = tk.Entry(master=self, width=10)
        self.tPoints.grid(row=rCount,column=1,sticky='w')
        lbl_tInt = tk.Label(master=self, text="Time Interval")
        lbl_tInt.grid(row=rCount,column=2,sticky='e')
        self.tInt = tk.Entry(master=self, width=10)
        self.tInt.grid(row=rCount,column=3,sticky='w')
        r1 = tk.Checkbutton(self, text="RTD", variable=self.RTD, onvalue=True,offvalue=False)
        r1.grid(row=rCount,column=4)
        rCount = rCount + 1
        #### Averaging ###################
        lbl_mAverage = tk.Label(master=self, text="Manual Averaging count")
        lbl_mAverage.grid(row=rCount,column=0,sticky='e')
        self.mAverage = tk.Entry(master=self, width=10)
        self.mAverage.grid(row=rCount,column=1,sticky='e')
        lbl_nAverage = tk.Label(master=self, text=" NPLC (20ms*)")
        lbl_nAverage.grid(row=rCount,column=2,sticky='e')
        self.nAverage = tk.Entry(master=self, width=10)
        self.nAverage.grid(row=rCount,column=3,sticky='e')
        rCount = rCount + 1

        #### Source parameter ################
        lbl_sp = tk.Label(master=self, text="Source parameter")
        lbl_sp.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="voltage", variable=self.sp, value='V')
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="current", variable=self.sp, value='I')
        r1.grid(row=rCount,column=2)
        rCount = rCount + 1
        #### Smu to be used ################
        lbl_mp = tk.Label(master=self, text="measure parameter")
        lbl_mp.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="voltage", variable=self.mp, value='V')
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="current", variable=self.mp, value='I')
        r1.grid(row=rCount,column=2)
        rCount = rCount + 1
        ############### Secondary source##############
        chan2_CB = tk.Checkbutton(master=self,text='Secondary source enable',variable=self.s2enable,onvalue=True,offvalue=False)
        chan2_CB.grid(row=rCount,column=0,sticky='e')
        lbl_s2Start = tk.Label(master=self, text="Value (V/A)")
        lbl_s2Start.grid(row=rCount,column=1,sticky='e')
        self.s2Value = tk.Entry(master=self, width=10)
        self.s2Value.grid(row=rCount,column=2,sticky='e')
        rCount = rCount + 1
        lbl_source = tk.Label(master=self, text="Secondary Source SMU")
        lbl_source.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="SMU A", variable=self.s2, value='a')
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="SMU B", variable=self.s2, value='b')
        r1.grid(row=rCount,column=2)
        rCount = rCount + 1
        #### Secondary source parameter ################
        lbl_sp = tk.Label(master=self, text="Source parameter")
        lbl_sp.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="voltage", variable=self.s2p, value='V')
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="current", variable=self.s2p, value='I')
        r1.grid(row=rCount,column=2)
        rCount = rCount + 1
        #### Limits and ranges #########################
        #### Source limit ###################
        lbl_slimit = tk.Label(master=self, text="source limit (V/A)")
        lbl_slimit.grid(row=rCount,column=0,sticky='e')
        self.slimit = tk.Entry(master=self, width=10)
        self.slimit.grid(row=rCount,column=1,sticky='w')
        rCount = rCount + 1
        #### measure limit ###################
        lbl_mlimit = tk.Label(master=self, text="measure limit (V/A)")
        lbl_mlimit.grid(row=rCount,column=0,sticky='e')
        self.mlimit = tk.Entry(master=self, width=10)
        self.mlimit.insert(0,'100E-3')
        self.mlimit.grid(row=rCount,column=1,sticky='w')
        rCount = rCount + 1
        #### Source limit ###################
        lbl_slimit = tk.Label(master=self, text="secondary source limit (V/A)")
        lbl_slimit.grid(row=rCount,column=0,sticky='e')
        self.s2limit = tk.Entry(master=self, width=10)
        self.s2limit.grid(row=rCount,column=1,sticky='w')
        rCount = rCount + 1
        btn_run = tk.Button(master=self, text="Run",command=lambda: self.measure.runMeasurement(self,configFrame,plotFrame))
        btn_run.grid(row=rCount,column=0)
        btn_run = tk.Button(master=self, text="Stop",command=lambda: self.measure.abortMeasurement(self,configFrame,plotFrame))
        btn_run.grid(row=rCount,column=2)
        bt = tk.Button(master=self,text='Set Defaults',command=self.setDefaults)
        bt.grid(row = rCount,column = 3)
    def setDefaults(self):
        self.mlimit.delete(0,tk.END)
        self.mlimit.insert(0,'Auto')
        self.slimit.delete(0,tk.END)
        self.slimit.insert(0,'100E-3')
        self.s2limit.delete(0,tk.END)
        self.s2limit.insert(0,'100E-3')
        self.sValue.delete(0,tk.END)
        self.sValue.insert(0,'1E-3')
        self.s2Value.delete(0,tk.END)
        self.s2Value.insert(0,'1E-3')
        self.tInt.delete(0,tk.END)
        self.tInt.insert(0,'10E-3')
        self.tPoints.delete(0,tk.END)
        self.tPoints.insert(0,'100')
        self.mAverage.delete(0,tk.END)
        self.mAverage.insert(0,'1')
        self.nAverage.delete(0,tk.END)
        self.nAverage.insert(0,'5')
        self.source.set('a')
        self.s2.set('b')
        self.sense.set('a')
        self.s2enable.set(False)
        self.RTD.set(True)
        self.mp.set('I')
        self.sp.set('V')
        self.s2p.set('V')
    def getButtonValues(self):
        ivtData = {
            "source":self.source.get(),
            "sense":self.sense.get(),
            "sParam":self.sp.get(),
            "mParam":self.mp.get(),
            "sValue":self.sValue.get(),
            "s2Value":self.s2Value.get(),
            "tPoints":self.tPoints.get(),
            "tInt":self.tInt.get(),
            "aver":self.mAverage.get(),
            "nplc":self.nAverage.get(),
            "slimit":self.slimit.get(),
            "s2limit":self.s2limit.get(),
            "mlimit":self.mlimit.get(),
            "s2enable":self.s2enable.get(),
            "RTD":self.RTD.get(),
            "s2":self.s2.get(),
            "s2p":self.s2p.get()
        }
        return ivtData



class MOSFETFrame(tk.Frame):
    def __init__(self,parent, configFrame, plotFrame):
        self.drain = tk.StringVar()
        self.gate = tk.StringVar()
        self.dp = tk.StringVar()
        self.gp = tk.StringVar()
        self.iName = tk.StringVar()
        self.Pulse = tk.BooleanVar()
        self.Loop = tk.BooleanVar()
        self.LoopDrain = tk.BooleanVar()
        self.LoopGate = tk.BooleanVar()
        self.LoopBiDir = tk.BooleanVar()
        self.sweepTerm = tk.BooleanVar()
        self.xIndex=tk.IntVar()
        self.yIndex=tk.IntVar()
        super().__init__(parent)
        self.measure=measurements()
        #### Smu to be used ################
        rCount = 0
        lbl_source = tk.Label(master=self, text="MOSFET Control Settings")
        lbl_source.grid(row=rCount,column=0,sticky='e')
        rCount = rCount + 1
        lbl_source = tk.Label(master=self, text="Drain SMU")
        lbl_source.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="SMU A", variable=self.drain, value='a')
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="SMU B", variable=self.drain, value='b')
        r1.grid(row=rCount,column=2)
        rCount = rCount + 1
        lbl_source = tk.Label(master=self, text="Gate SMU")
        lbl_source.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="SMU A", variable=self.gate, value='a')
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="SMU B", variable=self.gate, value='b')
        r1.grid(row=rCount,column=2)
        rCount = rCount + 1
        
        ####  parameter ################
        lbl_dp = tk.Label(master=self, text="Drain Parameter ")
        lbl_dp.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="voltage", variable=self.dp, value='V')
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="current", variable=self.dp, value='I')
        r1.grid(row=rCount,column=2)
        rCount = rCount + 1
        #### Smu to be used ################
        lbl_mp = tk.Label(master=self, text="Gate parameter")
        lbl_mp.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="voltage", variable=self.gp, value='V')
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="current", variable=self.gp, value='I')
        r1.grid(row=rCount,column=2)
        rCount = rCount + 1
        #### VD Settings###################
        lbl_VDs = tk.Label(master=self, text="Drain Start (V/A)")
        lbl_VDs.grid(row=rCount,column=0,sticky='e')
        self.VDs = tk.Entry(master=self, width=10)
        self.VDs.grid(row=rCount,column=1,sticky='e')
        lbl_VDe = tk.Label(master=self, text="Drain END (V/A)")
        lbl_VDe.grid(row=rCount,column=2,sticky='e')
        self.VDe = tk.Entry(master=self, width=10)
        self.VDe.grid(row=rCount,column=3,sticky='e')
        rCount = rCount + 1
#### VG Settings###################
        lbl_VGs = tk.Label(master=self, text="Gate Start (V/A)")
        lbl_VGs.grid(row=rCount,column=0,sticky='e')
        self.VGs = tk.Entry(master=self, width=10)
        self.VGs.grid(row=rCount,column=1,sticky='e')
        lbl_VGe = tk.Label(master=self, text="Gate END (V/A)")
        lbl_VGe.grid(row=rCount,column=2,sticky='e')
        self.VGe = tk.Entry(master=self, width=10)
        self.VGe.grid(row=rCount,column=3,sticky='e')
        rCount = rCount + 1
        #### points ###################
        lbl_dPoints = tk.Label(master=self, text=" Drain Points")
        lbl_dPoints.grid(row=rCount,column=0,sticky='e')
        self.dPoints = tk.Entry(master=self, width=10)
        self.dPoints.grid(row=rCount,column=1,sticky='w')
        lbl_gPoints = tk.Label(master=self, text=" Gate Points")
        lbl_gPoints.grid(row=rCount,column=2,sticky='e')
        self.gPoints = tk.Entry(master=self, width=10)
        self.gPoints.grid(row=rCount,column=3,sticky='w')
        rCount = rCount + 1
        lbl_dPoints = tk.Label(master=self, text="Measurement Type")
        lbl_dPoints.grid(row=rCount,column=0,sticky='e')
        c1=tk.Radiobutton(self,text="IDVD",variable=self.sweepTerm,value=0)
        c1.grid(row=rCount,column=1)
        c1=tk.Radiobutton(self,text="IDVG",variable=self.sweepTerm,value=1)
        c1.grid(row=rCount,column=2)
        lbl_sDel = tk.Label(master=self, text=" sDel")
        lbl_sDel.grid(row=rCount,column=3,sticky='e')
        self.sDel = tk.Entry(master=self, width=10)
        self.sDel.grid(row=rCount,column=4,sticky='w')
        rCount = rCount + 1
        #### Averaging ###################
        lbl_mAverage = tk.Label(master=self, text="Manual Averaging count")
        lbl_mAverage.grid(row=rCount,column=0,sticky='e')
        self.mAverage = tk.Entry(master=self, width=10)
        self.mAverage.grid(row=rCount,column=1,sticky='e')
        lbl_nAverage = tk.Label(master=self, text=" NPLC (20ms*)")
        lbl_nAverage.grid(row=rCount,column=2,sticky='e')
        self.nAverage = tk.Entry(master=self, width=10)
        self.nAverage.grid(row=rCount,column=3,sticky='e')
        rCount = rCount + 1
        #### Loop parameter ################
        lbl_sp = tk.Label(master=self, text="Loop")
        lbl_sp.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="True", variable=self.Loop, value=True)
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="False", variable=self.Loop, value=False)
        r1.grid(row=rCount,column=2)
        c1=tk.Checkbutton(self,text="Drain",variable=self.LoopDrain,onvalue=True,offvalue=False)
        c1.grid(row=rCount,column=3)
        c1=tk.Checkbutton(self,text="Gate",variable=self.LoopGate,onvalue=True,offvalue=False)
        c1.grid(row=rCount,column=4)
        c1=tk.Checkbutton(self,text="BiDirect",variable=self.LoopBiDir,onvalue=True,offvalue=False)
        c1.grid(row=rCount,column=5)
        rCount = rCount + 1
        #### Source parameter ################
        lbl_sp = tk.Label(master=self, text="Pulsing")
        lbl_sp.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="True", variable=self.Pulse, value=True)
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="False", variable=self.Pulse, value=False)
        r1.grid(row=rCount,column=2)
        #### pulse period ###################
        lbl_pPeriod = tk.Label(master=self, text="pulse period (S)")
        lbl_pPeriod.grid(row=rCount,column=3,sticky='e')
        self.pPeriod = tk.Entry(master=self, width=10)
        self.pPeriod.grid(row=rCount,column=4,sticky='e')
        #### Source limit ###################
        lbl_pWidth = tk.Label(master=self, text="pulse width (S)")
        lbl_pWidth.grid(row=rCount,column=5,sticky='e')
        self.pWidth = tk.Entry(master=self, width=10)
        self.pWidth.grid(row=rCount,column=6,sticky='e')
        rCount = rCount + 1

        #### Limits and ranges #########################
        #### drain Source limit ###################
        lbl_dslimit = tk.Label(master=self, text="Drain source limit (V)")
        lbl_dslimit.grid(row=rCount,column=0,sticky='e')
        self.dslimit = tk.Entry(master=self, width=10)
        self.dslimit.grid(row=rCount,column=1,sticky='w')
        lbl_dmlimit = tk.Label(master=self, text="Drain measure limit (V)")
        lbl_dmlimit.grid(row=rCount,column=2,sticky='e')
        self.dmlimit = tk.Entry(master=self, width=10)
        self.dmlimit.grid(row=rCount,column=3,sticky='w')
        rCount = rCount + 1
        #### gate source  limit ###################
        lbl_gslimit = tk.Label(master=self, text="Gate Source limit (V)")
        lbl_gslimit.grid(row=rCount,column=0,sticky='e')
        self.gslimit = tk.Entry(master=self, width=10)
        self.gslimit.grid(row=rCount,column=1,sticky='w')
        lbl_gmlimit = tk.Label(master=self, text="Gate measure limit (V)")
        lbl_gmlimit.grid(row=rCount,column=2,sticky='e')
        self.gmlimit = tk.Entry(master=self, width=10)
        self.gmlimit.grid(row=rCount,column=3,sticky='w')
        rCount = rCount + 1
        #### Choose xaxis ################
        lbl_sp = tk.Label(master=self, text="X axis of the plot")
        lbl_sp.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="VD", variable=self.xIndex, value=2)
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="VG", variable=self.xIndex, value=0)
        r1.grid(row=rCount,column=2)
        r1 = tk.Radiobutton(self, text="ID", variable=self.xIndex, value=3)
        r1.grid(row=rCount,column=3)
        r1 = tk.Radiobutton(self, text="IG", variable=self.xIndex, value=1)
        r1.grid(row=rCount,column=4)
        rCount = rCount + 1
        #### Choose yaxis ################
        lbl_sp = tk.Label(master=self, text="Y axis of the plot")
        lbl_sp.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="VD", variable=self.yIndex, value=2)
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="VG", variable=self.yIndex, value=0)
        r1.grid(row=rCount,column=2)
        r1 = tk.Radiobutton(self, text="ID", variable=self.yIndex, value=3)
        r1.grid(row=rCount,column=3)
        r1 = tk.Radiobutton(self, text="IG", variable=self.yIndex, value=1)
        r1.grid(row=rCount,column=4)
        rCount = rCount + 1

        btn_run = tk.Button(master=self, text="Run",command=lambda: self.measure.runMeasurement(self,configFrame,plotFrame))
        btn_run.grid(row=rCount,column=0)
        bt = tk.Button(master=self,text='Set Defaults',command=self.setDefaults)
        bt.grid(row = rCount,column = 1)
    def setDefaults(self):
        self.dslimit.delete(0,tk.END)
        self.dslimit.insert(0,'10')
        self.gslimit.delete(0,tk.END)
        self.gslimit.insert(0,'100')
        self.dmlimit.delete(0,tk.END)
        self.dmlimit.insert(0,'Auto')
        self.gmlimit.delete(0,tk.END)
        self.gmlimit.insert(0,'Auto')
        self.VDs.delete(0,tk.END)
        self.VDs.insert(0,'0')
        self.VDe.delete(0,tk.END)
        self.VDe.insert(0,'1')
        self.VGs.delete(0,tk.END)
        self.VGs.insert(0,'0')
        self.VGe.delete(0,tk.END)
        self.VGe.insert(0,'1')
        self.dPoints.delete(0,tk.END)
        self.dPoints.insert(0,'10')
        self.gPoints.delete(0,tk.END)
        self.gPoints.insert(0,'2')
        self.pWidth.delete(0,tk.END)
        self.pWidth.insert(0,'10E-3')
        self.pPeriod.delete(0,tk.END)
        self.pPeriod.insert(0,'1')
        self.mAverage.delete(0,tk.END)
        self.mAverage.insert(0,'1')
        self.nAverage.delete(0,tk.END)
        self.nAverage.insert(0,'1')
        self.sDel.delete(0,tk.END)
        self.sDel.insert(0,'100E-3')
        self.drain.set('a')
        self.gate.set('b')
        self.gp.set('V')
        self.dp.set('V')
        self.xIndex.set(2)
        self.yIndex.set(3)
        self.Pulse.set(False)
        self.sweepTerm.set(False)
        self.Loop.set(False)
        self.LoopDrain.set(False)
        self.LoopGate.set(False)
        self.LoopBiDir.set(False)
    def getButtonValues(self):
        mosfetData = {
            "drain":self.drain.get(),
            "gate":self.gate.get(),
            "gParam":self.gp.get(),
            "dParam":self.dp.get(),
            "VDe":self.VDe.get(),
            "VDs":self.VDs.get(),
            "VGe":self.VGe.get(),
            "VGs":self.VGs.get(),
            "dPoints":self.dPoints.get(),
            "gPoints":self.gPoints.get(),
            "Loop":self.Loop.get(),
            "Pulse":self.Pulse.get(),
            "LoopDrain":self.LoopDrain.get(),
            "LoopGate":self.LoopGate.get(),
            "LoopBiDir":self.LoopBiDir.get(),
            "sDel":self.sDel.get(),
            "sweepTerm":self.sweepTerm.get(),
            "pPeriod":self.pPeriod.get(),
            "pWidth":self.pWidth.get(),
            "aver":self.mAverage.get(),
            "nplc":self.nAverage.get(),
            "dmlimit":self.dmlimit.get(),
            "gmlimit":self.gmlimit.get(),
            "dslimit":self.dslimit.get(),
            "gslimit":self.gslimit.get(),
            "xIndex":self.xIndex.get(),
            "yIndex":self.yIndex.get()
        }
        return mosfetData


class plotFrame(tk.Frame):
    def initPlot(self):
        ######## The plot figure #########################################
        self.fig = Figure(figsize=(5,5), dpi = 100,facecolor='lightgrey')
        self.plt1 =self.fig.add_subplot(111, facecolor='lightgrey')
        self.plt1.plot(0,0,'*')
        #####################################################
        ###### A canvas is created to hold the figure ###########
        #######################################################
        self.canvas = FigureCanvasTkAgg(self.fig,master = self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH,expand = True)
        toolbar = NavigationToolbar2Tk(self.canvas,self)
        toolbar.update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH,expand = True)
    def addPoint(self,xData,yData,cl = 'k-*'):
        self.plt1.plot(xData,yData,cl)
    def flushPlot(self):
        self.fig.tight_layout()
        self.canvas.draw_idle()
        self.canvas.flush_events()
    def refreshPlot(self):
        self.fig.tight_layout()
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH,expand = True)

    def clearPlot(self):
        self.plt1.cla()
        #self.initPlot()
    def __init__(self,parent):
        super().__init__(parent)
        label_b = tk.Label(master=self, text="Plot Figures", font = ('Calibri',12,'bold'))
        label_b.pack()
        self.label_run = tk.Label(master=self,text="Running",bg='red')
        self.initPlot()
    def showRunning(self):
        self.label_run.pack()
    def removeRunning(self):
        self.label_run.pack_forget()

class controlFrame(tk.Frame):
    def __init__(self,parent,PF):
        super().__init__(parent,highlightbackground="black", highlightthickness=1, width=100, height=100, bd=0)
        self.PF = PF
        self.CF = configFrame(self,PF)
        self.DCIV = DCIVFrame(self, self.CF, PF)
        self.dIdV = dIdVFrame(self, self.CF, PF)
        self.MOSFET = MOSFETFrame(self, self.CF, PF)
        self.IVT = IVTFrame(self, self.CF, PF)
        self.CF.grid(row = 1,column=0)
        self.CF.setDefaults()
        self.bottomFrame = tk.Frame(self)
        self.bottomFrame.grid(row=2,column=0)
    def switchFrame(self):
        cfData = self.CF.getButtonValues()
        self.bottomFrame.grid_forget()
        if cfData["mt"] == 'iv':
            self.bottomFrame=self.DCIV
        elif cfData["mt"] == 'MOSFET':
            self.bottomFrame=self.MOSFET
        elif cfData["mt"] == 'IVT':
            self.bottomFrame=self.IVT
        elif cfData["mt"] == 'dIdV':
            self.bottomFrame=self.dIdV
        self.bottomFrame.tkraise()
        self.bottomFrame.grid(row=2,column = 0, padx = 10)
        self.bottomFrame.setDefaults()
        ###### instantiate the instruments ###############
        if cfData["inst"] == 'B2912B':
            self.CF.MD = B2912B()
        elif cfData["inst"] == 'K2636B':
            self.CF.MD = K2636B()
        elif cfData["inst"] == 'K6221':
            self.CF.MD = K6221()
#########################################################################################
############ The main class for the windows #########################################
############## Here is the organization
################################### master######################################################
#################################Main Frame##################################################
################TitleFrame#########ControlFrame##########plotFrame#########LegendFrame################
#############################ConfigFrame##DVIV##MOSFET######################
class MainWindow(): ## an Object oriented frame class
    def __init__(self,master):
        mainFrame=tk.Frame(master)
        mainFrame.pack(padx=10,pady=10,fill='both',expand=1)
        self.titleFrame = tk.Frame(mainFrame)
        lbl_1 = tk.Label(master=self.titleFrame, text="Measurement Tool", font = ('Calibri',14,'bold'))
        lbl_1.pack()
        self.titleFrame.grid(row=0,column=0)
        #self.controlFrame = tk.Frame(mainFrame,highlightbackground="black", highlightthickness=1, width=100, height=100, bd=0)
        lbl_1.grid(row=0,column=0)
        self.PF = plotFrame(mainFrame)
        self.PF.grid(row=1,column = 1)
        self.controlFrame = controlFrame(mainFrame,self.PF)
        self.controlFrame.grid(row=1,column=0)
        self.legendFrame = tk.Frame(mainFrame)
        qButton = tk.Button(master=self.legendFrame,text="Quit",command=self._quit)
        qButton.grid(row = 0,column = 0)
        lbl_mp = tk.Label(master=self.legendFrame, text="(c) Krishna Balasubramanian 2022")
        lbl_mp.grid(row =0,column = 1)
        self.legendFrame.grid(row=2,column=0)


    def _quit(self):
        root.quit()
        root.destroy()



#### initiate logging ###########
logging.basicConfig(filename= "logFile.txt", filemode='a',format='%(asctime)s - %(levelname)s -%(message)s',level=logging.INFO)
logging.info('Logging is started')
root = tk.Tk()
window = MainWindow(root)
root.mainloop()
logging.info('Logging ended')

