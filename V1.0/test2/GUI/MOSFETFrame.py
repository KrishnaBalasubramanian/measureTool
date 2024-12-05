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

