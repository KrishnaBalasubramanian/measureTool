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
class K2636B():
    def __init__(self):
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

