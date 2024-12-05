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
