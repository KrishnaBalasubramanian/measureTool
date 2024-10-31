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
import matplotlib
import numpy as np
from measurements import measurements
from GUI.heaterFrame import heaterFrame
from Instruments.L336 import L336
class RTFrame(tk.Frame):
    def __init__(self,parent, configFrame, plotFrame):
        self.iName = tk.StringVar()
        self.chanVar = tk.IntVar()
        self.resType = tk.IntVar()
        self.sensorCount = L336.sensorCount
        self.heaterCount = L336.heaterCount
        self.color = matplotlib.cm.rainbow(np.linspace(0,1,self.sensorCount))
        self.sensorName =L336.sensorName
        self.heaterName =L336.heaterName
        self.heaterVar = []
        self.setPoint = []
        self.heaterPower = []
        self.RTD = tk.BooleanVar()
        super().__init__(parent)
        self.measure = measurements()
        #### Smu to be used ################
        rCount = 0
        lbl_source = tk.Label(master=self, text="Resistance Temperature Measurement")
        lbl_source.grid(row=rCount,column=0,sticky='e')
        rCount = rCount + 1
        r1 = tk.Checkbutton(self, text="RTD", variable=self.RTD, onvalue=True,offvalue=False)
        r1.grid(row=rCount,column=0)
        lbl_tInt = tk.Label(master=self, text="Time Interval")
        lbl_tInt.grid(row=rCount,column=1,sticky='e')
        self.tInt = tk.Entry(master=self, width=10)
        self.tInt.grid(row=rCount,column=2,sticky='w')
        lbl_tPoints = tk.Label(master=self, text="Time Points")
        lbl_tPoints.grid(row=rCount,column=3,sticky='e')
        self.tPoints = tk.Entry(master=self, width=10)
        self.tPoints.grid(row=rCount,column=4,sticky='w')
        lbl_aver = tk.Label(master=self, text="Average")
        lbl_aver.grid(row=rCount,column=5,sticky='e')
        self.aver = tk.Entry(master=self, width=10)
        self.aver.grid(row=rCount,column=6,sticky='w')
        rCount = rCount + 1
        lbl_tInt = tk.Label(master=self, text="Channel on X axis")
        lbl_tInt.grid(row=rCount,column=1,sticky='e')
        rCount = rCount + 1
        for i in range(1,self.sensorCount):
            r1 = tk.Radiobutton(self, text=self.sensorName[i], variable=self.chanVar, value=i,fg=matplotlib.colors.to_hex(self.color[i]))
            r1.grid(row=rCount,column=i)
        
        rCount = rCount + 1
        lbl_tInt = tk.Label(master=self, text="Resistance Measurement")
        lbl_tInt.grid(row=rCount,column=0,sticky='e')
        r1 = tk.Radiobutton(self, text="2-wire", variable=self.resType, value=0)
        r1.grid(row=rCount,column=1)
        r1 = tk.Radiobutton(self, text="4-wire", variable=self.resType, value=1)
        r1.grid(row=rCount,column=2)
        rCount = rCount + 1
        lbl_aver = tk.Label(master=self, text="Resistance Average")
        lbl_aver.grid(row=rCount,column=0,sticky='e')
        self.RESaver = tk.Entry(master=self, width=10)
        self.RESaver.grid(row=rCount,column=1,sticky='w')
        lbl_range = tk.Label(master=self, text="Resistance Range")
        lbl_range.grid(row=rCount,column=2,sticky='e')
        self.RESrange = tk.Entry(master=self, width=10)
        self.RESrange.grid(row=rCount,column=3,sticky='w')
        lbl_NPLC = tk.Label(master=self, text="Resistance NPLC")
        lbl_NPLC.grid(row=rCount,column=4,sticky='e')
        self.RESNPLC = tk.Entry(master=self, width=10)
        self.RESNPLC.grid(row=rCount,column=5,sticky='w')
        rCount = rCount + 1
        btn_run = tk.Button(master=self, text="Run",command=lambda: self.measure.runMeasurement(self,configFrame,plotFrame))
        btn_run.grid(row=rCount,column=0)
        btn_run = tk.Button(master=self, text="Stop",command=lambda: self.measure.abortMeasurement(self,configFrame,plotFrame))
        btn_run.grid(row=rCount,column=2)
        bt = tk.Button(master=self,text='Set Defaults',command=self.setDefaults)
        bt.grid(row = rCount,column = 3)
        rCount = rCount + 1
        self.heaterFrame=heaterFrame(self,configFrame,plotFrame) 
        self.heaterFrame.grid(row=rCount,column=0,columnspan=5)
        
    def setDefaults(self): 
        self.tInt.delete(0,tk.END)
        self.tInt.insert(0,'10E-3')
        self.tPoints.delete(0,tk.END)
        self.tPoints.insert(0,'100')
        self.aver.delete(0,tk.END)
        self.aver.insert(0,'1')
        self.RESaver.delete(0,tk.END)
        self.RESaver.insert(0,'1')
        self.RESNPLC.delete(0,tk.END)
        self.RESNPLC.insert(0,'5')
        self.RESrange.delete(0,tk.END)
        self.RESrange.insert(0,'auto')
        self.chanVar.set(1)
        self.resType.set(0)
        self.RTD.set(True)
    def getButtonValues(self):
        RTData = {
            "sensorName":self.sensorName,
            "sensorCount":self.sensorCount,
            "heaterCount":self.heaterCount,
            "tInt":self.tInt.get(),
            "tPoints":self.tPoints.get(),
            "aver":self.aver.get(),
            "RESaver":self.RESaver.get(),
            "RESNPLC":self.RESNPLC.get(),
            "RESrange":self.RESrange.get(),
            "chanVar":self.chanVar.get(),
            "resType":self.resType,
            "RTD":self.RTD.get()
        }
        return RTData
