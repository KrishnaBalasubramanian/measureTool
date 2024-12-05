class dIdVFrame(tk.Frame):
    def __init__(self,parent, configFrame, plotFrame):
        self.damp = tk.StringVar()
        self.ddel = tk.StringVar()
        super().__init__(parent)
        self.measure = measurements()
        #### Smu to be used ################
        rCount = 0
        lbl_source = tk.Label(master=self, text="dIdV Control Settings")
        lbl_source.grid(row=rCount,column=0,sticky='e')
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
        rCount = rCount + 1
        #### Averaging ###################
        lbl_mAverage = tk.Label(master=self, text="Manual Averaging")
        lbl_mAverage.grid(row=rCount,column=0,sticky='e')
        self.mAverage = tk.Entry(master=self, width=10)
        self.mAverage.grid(row=rCount,column=1,sticky='e')
        lbl_nAverage = tk.Label(master=self, text=" NPLC (20ms*) ")
        lbl_nAverage.grid(row=rCount,column=2,sticky='e')
        self.nAverage = tk.Entry(master=self, width=10)
        self.nAverage.grid(row=rCount,column=3,sticky='e')
        rCount = rCount + 1
        #### Source parameter ################
        lbl_dampl = tk.Label(master=self, text="Delta ampl")
        lbl_dampl.grid(row=rCount,column=0,sticky='e')
        self.damp = tk.Entry(master=self, width=10)
        self.damp.grid(row=rCount,column=1,sticky='e')
        lbl_ddelay = tk.Label(master=self, text="Delta delay")
        lbl_ddelay.grid(row=rCount,column=2,sticky='e')
        self.ddel = tk.Entry(master=self, width=10)
        self.ddel.grid(row=rCount,column=3,sticky='e')
        rCount = rCount + 1
        #### Limits and ranges #########################
        #### Source limit ###################
        lbl_slimit = tk.Label(master=self, text="source limit (A)")
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
        self.sPoints.delete(0,tk.END)
        self.sStart.delete(0,tk.END)
        self.sStart.insert(0,'0')
        self.mAverage.delete(0,tk.END)
        self.mAverage.insert(0,'1')
        self.nAverage.delete(0,tk.END)
        self.nAverage.insert(0,'1')
        self.sPoints.insert(0,'10')
        self.damp.delete(0,tk.END)
        self.damp.insert(0,'1E-6')
        self.ddel.delete(0,tk.END)
        self.ddel.insert(0,'1E-3')
    def getButtonValues(self):
        dIdVData = {
            "source":'a',
            "sense":'a',
            "sParam":'I',
            "mParam":'V',
            "sEnd":self.sEnd.get(),
            "sStart":self.sStart.get(),
            "sPoints":self.sPoints.get(),
            "ddel":self.ddel.get(),
            "damp":self.damp.get(),
            "aver":self.mAverage.get(),
            "nplc":self.nAverage.get(),
            "slimit":self.slimit.get(),
            "mlimit":self.mlimit.get()
        }
        return dIdVData
