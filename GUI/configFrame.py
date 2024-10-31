
#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
class configFrame(tk.Frame):
    def __init__(self,parent,PF):
        super().__init__(parent)
        self.mt = tk.StringVar()
        self.iName = tk.StringVar()
        rCount = 0
        #### Measurement Name ###################
        label_a = tk.Label(master=self, text="Measurement Configurations", font = ('Calibri',12,'bold'))
        label_a.grid(row=rCount,column = 0)
        rCount = rCount + 1
        lbl_mName = tk.Label(self, text="Measurement Name")
        lbl_mName.grid(row=rCount,column=0,sticky='e')
        self.mName = tk.Entry(master=self, width=10)
        self.mName.grid(row=rCount,column=1,sticky='w')
        rCount = rCount + 1
        #### Working director
        lbl_WD = tk.Label(self, text="Working Directory")
        lbl_WD.grid(row=rCount,column=0,sticky='e')
        self.WD = tk.Entry(master=self, width=10)
        self.WD.grid(row=rCount,column=1,sticky='w')
        rCount = rCount + 1
        #### Instrument Name ###################
        lbl_Iname = tk.Label(master=self, text="Instrument Name")
        lbl_Iname.grid(row=rCount,column=0,sticky='e')
        options = ["K2636B","B2912B","K6221-2182A","L336","L336-DMM","testTC"]
        self.iName.set(options[0])
        instrumentOption = tk.OptionMenu(self,self.iName,*options)	
        instrumentOption.grid(row=rCount,column=1)
        rCount = rCount + 1
        #### Measurement Type ################
        lbl_mt = tk.Label(master=self, text="measurement type")
        lbl_mt.grid(row=rCount,column=0,sticky='e')
        options = ["iv","MOSFET","IVT","dIdV","Tt","RT"]
        self.mt.set(options[0])
        measureOption = tk.OptionMenu(self,self.mt,*options)	
        measureOption.grid(row=rCount,column=1)
        rCount = rCount + 1
        bt = tk.Button(master=self,text='Set Defaults',command=self.setDefaults)
        bt.grid(row = rCount,column = 0)
        rCount = rCount + 1
        lbl_mp = tk.Label(master=self, text="Press Config to configure measurements")
        lbl_mp.grid(row =rCount,column = 0,sticky = 'e')
        switch=tk.Button(self,text='Config',command= parent.switchFrame)
        switch.grid(row = rCount,column = 1,sticky = 'e')
    def setDefaults(self):
        self.iName.set('K2636B')
        self.mt.set('iv')
        self.mName.delete(0,tk.END)
        self.mName.insert(0,'test')
        self.WD.delete(0,tk.END)
        self.WD.insert(0,'./')
    def getButtonValues(self):
        configData = {
        "inst":self.iName.get(),
        "mt":self.mt.get(),
        "mName":self.mName.get(),
        "WD":self.WD.get()
        }
        return configData

