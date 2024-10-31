#
# This file is part of the measureTool package.
#
# Copyright (c) 2013-2024 measureTool Developers
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
##################################################
#### This class is instantiated upon pressing the config button
#############################
import numpy as np
import os
import threading
import queue
import time
import pdb
import re
import logging
from datetime import datetime
from resultBook import resultBook
import logging
from Instruments.B2912B import B2912B
from Instruments.testTC import testTC
from Instruments.K2636B import K2636B
from Instruments.K6221 import K6221
from Instruments.L336 import L336
from Instruments.K7510 import K7510
logger = logging.getLogger(__name__)
class measurements:
    """
        Any measurement is an instance of this class. All measure frames will make an instance of this class and then do a measurement. 

    """
    def __init__(self):
        self.active = False
        ################# Queue to hold the measured data from measurement threads ###########
        self.measureData = queue.Queue()

################### function definitions ##############
################ Get Tool Instance ######################
    def connectToInstrument(self,cfData):
        ###### instantiate the instruments ###############
        if cfData["inst"] == 'B2912B':
            if not B2912B.instantiated:
                self.MD = B2912B()
            else:
                self.MD=B2912B.instance[0]
        elif cfData["inst"] == 'testTC':
            if not testTC.instantiated:
                self.MD = testTC()
            else:
                self.MD=testTC.instance[0]
        elif cfData["inst"] == 'K2636B':
            if not K2636B.instantiated:
                self.MD = K2636B()
            else:
                self.MD=K2636B.instance[0]
        elif cfData["inst"] == 'K6221-2182A':
            if not K6221.instantiated:
                self.MD = K6221()
            else:
                self.MD=K6221.instance[0]
        elif cfData["inst"] == 'L336':
            if not L336.instantiated:
                self.MD = L336()
            else:
                self.MD=L336.instance[0]
        elif cfData["inst"] == 'L336-DMM':
            if not L336.instantiated:
                self.MD = L336()
            else:
                self.MD=L336.instance[0]
            if not K7510.instantiated:
                self.MD1 = K7510()
            else:
                self.MD1=K7510.instance[0]

        else:
            print("Unknown Instrument accessed")
            logging.error("unknown instrument error")



    def abortMeasurement(self,measFrame,configFrame,PF): ## RTD measurement frames call to this method
        self.active=False ### when this is clicked, bring measurement down
######################## Script to run the actual measurement program ##########################
    def runMeasurement(self,measFrame,configFrame,PF):
        timeElapsed=0
        while self.active: #### is another measurement is running - wait
            if timeElapsed >30:
                print("Something wrong. The previous measurement didnt complete even after 30 seconds")
                return
            else:
                print('A measurement is already running. The current request is queued.')
                time.sleep(1)
                timeElapsed +=1
        ### we start off a new thread that actually does the measurement ####
        logger.info("Starting a new measurement")
        measThread = threading.Thread(target=self.activeMeasurement,args=(measFrame,configFrame,PF,))
        #### Fork of a thread and return back to the GUI state!
        measThread.start()

    def activeMeasurement(self,measFrame,configFrame,PF):	
        measData = measFrame.getButtonValues()
        configData = configFrame.getButtonValues()
        measureFile = configData["WD"] + '/' + configData["mName"] + ".csv"
        f1 = open(measureFile,'a')
        ############ dump some of the config things into the data file #############
        startTime = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        f1.write('Date' + ',' + startTime + '\n') ## date
        f1.write('Measurement Type' + ',' + configData["mt"] + ',' + 'Instrument' +','+ configData["mName"]+ '\n')
        for key,value in measData.items():## write the entire measure frame data into the file
            f1.write('{0},{1},'.format(key,value))
        f1.write('\n')
        ###########################################################################
        errFile = configData["WD"] + '/' + configData["mName"] + "err.txt"
        #self.MD = configFrame.MD[0] ### get the measurement tool instance
        #if len(configFrame.MD) == 2:
        #    self.MD1 = configFrame.MD[1] #### if there is a second tool used
        self.measureData.queue.clear()
        PF.showRunning()
        if configData["mt"] == 'iv':
            plotData = np.zeros((1,2))
            self.connectToInstrument(configData)
            PF.clearPlot()
            LI=PF.addLine(PF.colors[0])
            logger.info('Added a plot line')
            f1.write("Voltage,Current\n")
            t1=threading.Thread(target=self.runDCIV, args=(measData,))
            t1.start()
            while t1.is_alive():
                time.sleep(3)
                while not self.measureData.empty():
                    plotData = self.measureData.get()
                    f1.write(str(plotData[0]) + ',' + str(plotData[1]) + '\n')
                    PF.addPoint(LI,plotData[0],plotData[1])
                    logger.info('adding a plot point')
                PF.flushPlot()
            #inArray = np.loadtxt('data.csv',delimiter=',')
            t1.join()
            f1.close()
        elif configData["mt"] == 'dIdV':
            plotData = np.zeros((1,2))
            self.connectToInstrument(configData)
            PF.clearPlot()
            LI=PF.addLine(PF.colors[0])
            f1.write("dVdI,Current\n")
            t1=threading.Thread(target=self.rundIdV, args=(measData,))
            t1.start()
            while t1.is_alive():
                time.sleep(3)
                while not self.measureData.empty():
                    plotData = self.measureData.get()
                    f1.write(str(plotData[1]) + ',' + str(plotData[0]) + '\n')
                    PF.addPoint(LI,plotData[1],plotData[0])
                PF.flushPlot()
            t1.join()
            f1.close()
        elif configData["mt"] == 'MOSFET':
            plotData = np.zeros((1,2))
            self.connectToInstrument(configData)
            PF.clearPlot()
            LI=PF.addLine(PF.colors[0])
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
                    PF.addPoint(LI,plotData[xIndex],plotData[yIndex])
                PF.flushPlot()
            #inArray = np.loadtxt('data.csv',delimiter=',')
            t1.join()
            f1.close()
            
        elif configData["mt"] == 'IVT':
            plotData = np.zeros((1,2))
            self.connectToInstrument(configData)
            PF.clearPlot()
            LI=PF.addLine(PF.colors[0])
            f1.write("Voltage,Current,Time\n")
            t1=threading.Thread(target=self.runIVT, args=(measData,))
            t1.start()
            while t1.is_alive():
                time.sleep(3)
                while not self.measureData.empty():
                    plotData = self.measureData.get()
                    f1.write(str(plotData[0]) + ',' + str(plotData[1]) + ',' + str(plotData[2])+'\n')
                    if measData["sParam"] == 'I':
                        PF.addPoint(LI,plotData[2],plotData[0])
                    else:
                        PF.addPoint(LI,plotData[2],plotData[1])
                PF.flushPlot()
            #inArray = np.loadtxt('data.csv',delimiter=',')
            t1.join()
            f1.close()

        elif configData["mt"] == 'Tt':
            plotData = np.zeros((1,2))
            self.connectToInstrument(configData)
            PF.clearPlot()
            strWrite = "Time"
            for i in range(1,measData["sensorCount"]): ### number 0 is a NONE sensor
                LI=PF.addLine(PF.colors[i])
                strWrite += "," + measData["sensorName"][i]
            strWrite += "\n"
                
            f1.write(strWrite)
            t1=threading.Thread(target=self.runTt, args=(measData,))
            t1.start()
            while t1.is_alive():
                time.sleep(3)
                while not self.measureData.empty():
                    plotData = self.measureData.get()
                    strWrite = str(plotData[0])
                    for i in range(measData["sensorCount"]-1): ### number 0 is a NONE sensor
                        strWrite += ',' + str(plotData[1][i])
                        if measData["chanList"][i].get():
                            PF.addPoint(i,plotData[0],plotData[1][i])
                    strWrite +='\n'
                    f1.write(strWrite)
                PF.flushPlot()
            #inArray = np.loadtxt('data.csv',delimiter=',')
            t1.join()
            f1.close()
            self.MD.disconnect()
            
            
        elif configData["mt"] == 'RT':
            plotData = np.zeros((1,2))
            self.connectToInstrument(configData)
            PF.clearPlot()
            PF.addLine(PF.colors[1])
            strWrite = "Time"
            for i in range(1,measData["sensorCount"]): ### number 0 is a NONE sensor
                strWrite += "," + measData["sensorName"][i]
            strWrite += ",Resistance\n"  
            f1.write(strWrite)
            t1=threading.Thread(target=self.runRT, args=(measData,))
            t1.start()
            while t1.is_alive():
                time.sleep(3)
                while not self.measureData.empty():
                    plotData = self.measureData.get()
                    strWrite = str(plotData[0])
                    for i in range(measData["sensorCount"]-1): ### number 0 is a NONE sensor
                        strWrite += ',' + str(plotData[1][i])
                    strWrite +=str(plotData[2]) ### resistance average
                    plotIndex = int(measData["chanVar"])
                    PF.addPoint(0,plotData[1][plotIndex],plotData[-1])
                    strWrite +='\n'
                    f1.write(strWrite)
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
        logger.info('Entering MOSFET driver')
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
        self.MD.setSourceMode(gSMU,gParam,str(gsLimit),str(gmLimit))
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
        logger.info('Into IVT module')
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
        self.MD.disconnect()
        self.active = False

    def runTt(self,TtData):
        logger.info('Into Tt module')
        self.active = True
        if TtData["RTD"]:
            tInt=float(TtData["tInt"])
            chanList=TtData["chanList"]
            aver = int(TtData["aver"])
            RB = resultBook()
            RB.points = int(TtData["tPoints"])
            tElapse = 0
            while self.active:
                readData = self.MD.doMeasure()
                self.measureData.put([tElapse,readData])
                time.sleep(tInt)
                tElapse += tInt
        else:
            measuredData=self.MD.Tt(TtData)
            for i in range(measuredData.points):
                self.measureData.put([measuredData.chanData[i],time[i]])
        #self.MD.turnOffOutputs()
        self.MD.disconnect()
        self.active = False
    def runRT(self,RTData):
        logger.info('Into RT module')
        self.active = True
        if RTData["RTD"]:
            tInt=float(RTData["tInt"])
            aver = int(RTData["aver"])
            resAver = int(RTData["RESaver"])
            nplc = int(RTData["RESNPLC"])
            resRange = RTData["RESrange"]
            if bool(RTData["resType"]):
                param = "2-wire"
            else:
                param = "4-wire"
            RB = resultBook()
            RB.points = int(RTData["tPoints"])
            tElapse = 0
            self.MD1.setSenseMode("A",param,resRange,nplc,resAver)
            while self.active:
                measureData = [tElapse]
                measureData.append(self.MD.doMeasure()) ### temperature measure
                time.sleep(1)
                measureData.append(np.mean(self.MD1.doMeasure()))
                time.sleep(1)
                self.measureData.put(measureData)
                time.sleep(tInt)
                tElapse += tInt
        else:
            measuredData=self.MD.Tt(TtData)
            for i in range(measuredData.points):
                self.measureData.put([measuredData.chanData[i],time[i]])
        #self.MD.turnOffOutputs()
        self.MD.disconnect()
        self.MD1.disconnect()
        self.active = False
    def setCryostatHeater(self,measFrame,configFrame,plotFrame):
        logger.info('Entering Heater setting module')
        configData = configFrame.getButtonValues()
        self.connectToInstrument(configData)
        measData = measFrame.getButtonValues()
        
        for i in range(measData["heaterCount"]):
            if measData["heaterVar"][i].get(): ## if the heater is enabled
                heaterIndex=i+1
                sensorName=measData["linkSensor"][i].get()
                setPoint=measData["setPoint"][i].get()
                power=measData["heaterPower"][i].get()
                self.MD.setHeater(heaterIndex,sensorName,setPoint,power) ### heater index starts from 1
                
    def turnOffHeaters(self,measFrame,configFrame,plotFrame):
        logger.info('Turning Off heaters')
        configData = configFrame.getButtonValues()
        self.connectToInstrument(configData)
        self.MD.turnOffHeaters()

