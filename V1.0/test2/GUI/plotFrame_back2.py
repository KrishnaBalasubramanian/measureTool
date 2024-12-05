
#
# This file is part of the measureTool package.
#
# Copyright (c) 2013-2024 measureTOol Developers
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
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
from memory_profiler import profile
class plotFrame(tk.Frame):
    def initPlot(self):
        ######## The plot figure #########################################
        self.fig = Figure(figsize=(5,5), dpi = 100,facecolor='lightgrey')
        self.plt1 =self.fig.add_subplot(111, facecolor='lightgrey')
        self.xData=[]
        self.yData=[]
        self.line = self.plt1.plot(self.xData,self.yData,'*') ## added for blitting
        #####################################################
        ###### A canvas is created to hold the figure ###########
        #######################################################
        self.canvas = FigureCanvasTkAgg(self.fig,master = self)
        self.canvas.draw()
        self.background=self.canvas.copy_from_bbox(self.plt1.bbox)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH,expand = True)
        toolbar = NavigationToolbar2Tk(self.canvas,self)
        toolbar.update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH,expand = True)
        self.colors = matplotlib.cm.rainbow(np.linspace(0,1,10))
    def addLine(self,color,marker='*',linestyle='dashed',label=""):
        self.line.append(self.plt1.plot(self.xData,self.yData,color=color,marker=marker,linestyle=linestyle,label=label)) ## added for blitting
    def updateLine(self,lineIndex,xData,yData):
        self.line[lineIndex].set_data(xData,yData)
        
    def addPoint(self,xData,yData,color, marker='*',linestyle='dashed',label=""):
        self.xData.append(xData)
        self.yData.append(yData)
        self.line=self.plt1.plot(self.yData,self.yData,color=color,marker=marker,linestyle=linestyle,label=label)
    #################################################
    ############# Here adding things for blitting. 
    ####################################################
    @profile
    def flushPlot(self):
        self.fig.tight_layout()
        self.canvas.restore_region(self.background)
        self.plt1.draw_artist(self.line[0])
        self.canvas.blit(self.plt1.bbox)
        #self.canvas.draw_idle()
        self.canvas.flush_events()
    def refreshPlot(self):
        self.fig.tight_layout()
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH,expand = True)

    def clearPlot(self):
        self.plt1.cla()
        #self.initPlot()
    def __init__(self,parent):
        super().__init__(parent)
        label_b = tk.Label(master=self, text="Plot Figures", font = ('Calibri',12,'bold'))
        label_b.pack()
        self.label_run = tk.Label(master=self,text="Running",bg='red')
        self.initPlot()
    def showRunning(self):
        self.label_run.pack()
    def removeRunning(self):
        self.label_run.pack_forget()
