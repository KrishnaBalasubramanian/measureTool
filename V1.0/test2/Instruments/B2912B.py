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
from resultBook import resultBook
logger = logging.getLogger(__name__)
class B2912B():
    instantiated=False
    instance=[]
    def __init__(self):
        self.connect('USB0::0x2A8D::0x9501::MY61390244::INSTR')
        B2912B.instantiated=True
        B2912B.instance.append(self)
    def connect(self,address='USB0::0x2A8D::0x9501::MY61390244::INSTR'):
        rm = visa.ResourceManager(r'C:\WINDOWS\system32\visa64.dll')
        self.sm=rm.open_resource(address)
        self.sm.write_termination='\n'
        self.sm.read_termination='\n'
        self.sm.write('*RST')
    def disconnect(self):
        self.sm.close()
        B2912B.instantiated=False
        B2912.instance=[]
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
                    #mData=np.append(mData,np.asarray(re.findall('[+-][0-9\.]+E[+-][0-9]+',resp),dtype=float))
                    mData=np.append(mData,np.fromstring(resp,dtype=float,sep=','))
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

