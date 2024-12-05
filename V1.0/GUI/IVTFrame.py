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

