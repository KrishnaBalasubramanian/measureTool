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
        
    def switchFrame(self):
        cfData = self.CF.getButtonValues()
        
############### Now instantiate the right measure frame ################
        self.bottomFrame.grid_forget()
        if cfData["mt"] == 'iv':
            self.DCIV = DCIVFrame(self, self.CF, self.PF)
            self.bottomFrame=self.DCIV
        elif cfData["mt"] == 'MOSFET':
            self.MOSFET = MOSFETFrame(self, self.CF, self.PF)
            self.bottomFrame=self.MOSFET
        elif cfData["mt"] == 'IVT':
            self.IVT = IVTFrame(self, self.CF, self.PF)
            self.bottomFrame=self.IVT
        elif cfData["mt"] == 'dIdV':
            self.dIdV = dIdVFrame(self, self.CF, self.PF)
            self.bottomFrame=self.dIdV
        elif cfData["mt"] == 'Tt':
            self.Tt=TtFrame(self,self.CF,self.PF)
            self.bottomFrame=self.Tt
        elif cfData["mt"] == 'RT':
            self.RT=RTFrame(self,self.CF,self.PF)
            self.bottomFrame=self.RT
        self.bottomFrame.tkraise()
        self.bottomFrame.grid(row=2,column = 0, padx = 10)
        self.bottomFrame.setDefaults()
