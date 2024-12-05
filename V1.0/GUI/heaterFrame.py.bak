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
from Instruments.L336 import L336
class heaterFrame(tk.Frame):
    def __init__(self,parent, configFrame, plotFrame):
        super().__init__(parent,highlightbackground="black", highlightthickness=1, width=100, height=100, bd=0)
        self.sensorCount = L336.sensorCount
        self.sensorName=L336.sensorName
        self.heaterCount = L336.heaterCount
        self.heaterName=L336.heaterName
        self.heaterPower = []
        self.linkSensor=[]
        self.heaterVar = []
        self.setPoint = []
        self.measure = measurements()
        self.color = matplotlib.cm.rainbow(np.linspace(0,1,self.sensorCount))
        rCount = 0
        lbl_setPoint = tk.Label(master=self, text="Heater Control")
        lbl_setPoint.grid(row=rCount,column=0,sticky='e')
        rCount = rCount + 1
        for i in range(self.heaterCount):
            self.heaterVar.append(tk.BooleanVar())
            r1 = tk.Checkbutton(self, text=self.heaterName[i], variable=self.heaterVar[-1], onvalue=True,offvalue=False,fg=matplotlib.colors.to_hex(self.color[i]))
            r1.grid(row=rCount,column=0)
            lbl_C1setPoint = tk.Label(master=self, text="setPoint")
            lbl_C1setPoint.grid(row=rCount,column=1,sticky='e')
            self.setPoint.append(tk.Entry(master=self, width=10))
            self.setPoint[-1].grid(row=rCount,column=2,sticky='w')
            lbl_C1heaterPower = tk.Label(master=self, text="Linked Sensor")
            lbl_C1heaterPower.grid(row=rCount,column=3,sticky='e')
            self.linkSensor.append(tk.StringVar())
            heaterSelecter = tk.OptionMenu(self,self.linkSensor[-1],*self.sensorName)
            heaterSelecter.grid(row=rCount,column=4,sticky='w')
            lbl_C1heaterPower = tk.Label(master=self, text="HeaterPower")
            lbl_C1heaterPower.grid(row=rCount,column=5,sticky='e')
            self.heaterPower.append(tk.StringVar())
            options = ["LOW","MEDIUM","HIGH","OFF"]
            heaterSelecter = tk.OptionMenu(self,self.heaterPower[-1],*options)
            heaterSelecter.grid(row=rCount,column=6,sticky='w')
            rCount += 1
        btn_run = tk.Button(master=self, text="Update",command=lambda: self.measure.setCryostatHeater(self,configFrame,plotFrame))
        btn_run.grid(row=rCount,column=2)
        btn_offHeater = tk.Button(master=self, text="turnOffHeaters",command=lambda: self.measure.turnOffHeaters(self,configFrame,plotFrame))
        btn_offHeater.grid(row=rCount,column=3)
        self.setDefaults()

    def setDefaults(self): 
        for i in range(self.heaterCount):
            self.heaterVar[i].set(False)
            self.setPoint[i].delete(0,tk.END)
            self.setPoint[i].insert(0,'290')
            #self.setPoint[i].set("273")
            self.heaterPower[i].set("OFF")
            self.linkSensor[i].set(self.sensorName[i+1])

    def getButtonValues(self):
        heaterData = {
            "sensorName":self.sensorName,
            "sensorCount":self.sensorCount,
            "heaterCount":self.heaterCount,
            "heaterVar":self.heaterVar,
            "heaterPower":self.heaterPower,
            "linkSensor":self.linkSensor,
            "setPoint":self.setPoint
        }
        return heaterData
