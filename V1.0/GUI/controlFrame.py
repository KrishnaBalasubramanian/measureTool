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
import tkinter as tk
from .configFrame import configFrame
from .DCIVFrame import DCIVFrame
from .MOSFETFrame import MOSFETFrame
from .dIdVFrame import dIdVFrame
from .IVTFrame import IVTFrame
from .TtFrame import TtFrame
from .RTFrame import RTFrame
import pdb
import logging
from Instruments.B2912B import B2912B
from Instruments.testTC import testTC
from Instruments.K2636B import K2636B
from Instruments.K6221 import K6221
from Instruments.L336 import L336
from Instruments.K7510 import K7510
from Instruments.UNO import UNO
from Instruments.NULLInstrument import NULLInstrument
logger = logging.getLogger(__name__)

##########################################################################
############## Frame which controls the measurement #######################
################ chooses which measurement to make and the instruments used ######
#############################################################################################
class controlFrame(tk.Frame):
    def __init__(self,parent,PF):
        super().__init__(parent,highlightbackground="black", highlightthickness=1, width=100, height=100, bd=0)
        self.PF = PF
        self.CF = configFrame(self,PF)
        self.CF.grid(row = 1,column=0)
        self.CF.setDefaults()
        self.bottomFrame = tk.Frame(self)
        self.bottomFrame.grid(row=2,column=0)
        ######## Instrumens Instances ##########
        self.MD = []
        
################### function definitions ##############
    def switchFrame(self):
        cfData = self.CF.getButtonValues()
        ################## Instantiate the right instrument class ###############
        self.MD = []
        for var in cfData["inst"]:
            inst = var.get()
            self.connectToInstrument([inst])
        measurementType=cfData["mt"].get()
############### Now instantiate the right measure frame ################
        self.bottomFrame.grid_forget()
        if measurementType == 'iv':
            self.DCIV = DCIVFrame(self, self.CF, self.PF)
            self.bottomFrame=self.DCIV
        elif measurementType == 'MOSFET':
            self.MOSFET = MOSFETFrame(self, self.CF, self.PF)
            self.bottomFrame=self.MOSFET
        elif measurementType == 'IVT':
            self.IVT = IVTFrame(self, self.CF, self.PF)
            self.bottomFrame=self.IVT
        elif measurementType == 'dIdV':
            self.dIdV = dIdVFrame(self, self.CF, self.PF)
            self.bottomFrame=self.dIdV
        elif measurementType == 'Tt':
            self.Tt=TtFrame(self,self.CF,self.PF)
            self.bottomFrame=self.Tt
        elif measurementType == 'RT':
            self.RT=RTFrame(self,self.CF,self.PF)
            self.bottomFrame=self.RT
        self.bottomFrame.tkraise()
        self.bottomFrame.grid(row=2,column = 0, padx = 10)
        self.bottomFrame.setDefaults()

################ Get Tool Instance ######################
    def connectToInstrument(self,instruments):
        ###### instantiate the instruments ###############
        for instrument in instruments:
            if instrument == 'B2912B':
                if not B2912B.instantiated:
                    self.MD.append(B2912B())
                else:
                    logger.info('Already instantiated; reusing')
                    self.MD.append(B2912B.instance[0])
            elif instrument == 'testTC':
                if not testTC.instantiated:
                    self.MD.append(testTC())
                else:
                    logger.info('Already instantiated; reusing')
                    self.MD.append(testTC.instance[0])
            elif instrument == 'K2636B':
                if not K2636B.instantiated:
                    self.MD.append(K2636B())
                else:
                    logger.info('Already instantiated; reusing')
                    self.MD.append(K2636B.instance[0])
            elif instrument == 'K6221-2182A':
                if not K6221.instantiated:
                    self.MD.append(K6221())
                else:
                    logger.info('Already instantiated; reusing')
                    self.MD=K6221.instance[0]
            elif instrument == 'L336':
                if not L336.instantiated:
                    self.MD.append(L336())
                else:
                    logger.info('Already instantiated; reusing')
                    self.MD.append(L336.instance[0])
            elif instrument == 'UNO':
                if not UNO.instantiated:
                    self.MD.append(UNO())
                else:
                    logger.info('Already instantiated; reusing')
                    self.MD.append(UNO.instance[0])
            elif instrument == 'DMM':
                if not K7510.instantiated:
                    self.MD.append(K7510())
                else:
                    logger.info('Already instantiated; reusing')
                    self.MD.append(instance[0])

            elif instrument == 'NONE': ### instantiate a null instrument
                self.MD.append(NULLInstrument())
            else:
                print("Unknown Instrument accessed")
                logging.error("unknown instrument error")
            if self.MD[-1].connected == False:
                print('atleast one equipment is not connected')
                return False
        return True
    def disconnectInstruments(self):
        for md in self.MD:
            md.disconnect()
        self.MD = []
