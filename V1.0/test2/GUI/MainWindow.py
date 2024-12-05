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
import matplotlib
import matplotlib.pyplot as plt
from GUI.plotFrame import plotFrame
from GUI.controlFrame import controlFrame
matplotlib.use('TkAgg')
#########################################################################################
############ The main class for the windows #########################################
############## Here is the organization
################################### master######################################################
#################################Main Frame##################################################
################TitleFrame#########ControlFrame##########plotFrame#########LegendFrame################
#############################ConfigFrame##DVIV##MOSFET######################
class MainWindow(): ## an Object oriented frame class
    def __init__(self,master):
        self.root = master
        mainFrame=tk.Frame(master)
        mainFrame.pack(padx=10,pady=10,fill='both',expand=1)
        self.titleFrame = tk.Frame(mainFrame)
        lbl_1 = tk.Label(master=self.titleFrame, text="Measurement Tool", font = ('Calibri',14,'bold'))
        lbl_1.pack()
        self.titleFrame.grid(row=0,column=0)
        #self.controlFrame = tk.Frame(mainFrame,highlightbackground="black", highlightthickness=1, width=100, height=100, bd=0)
        lbl_1.grid(row=0,column=0)
        self.PF = plotFrame(mainFrame)
        self.PF.grid(row=1,column = 1)
        self.controlFrame = controlFrame(mainFrame,self.PF)
        self.controlFrame.grid(row=1,column=0)
        self.legendFrame = tk.Frame(mainFrame)
        qButton = tk.Button(master=self.legendFrame,text="Quit",command=self._quit)
        qButton.grid(row = 0,column = 0)
        lbl_mp = tk.Label(master=self.legendFrame, text="(c) Krishna Balasubramanian 2022")
        lbl_mp.grid(row =0,column = 1)
        self.legendFrame.grid(row=2,column=0)


    def _quit(self):
        self.root.quit()
        self.root.destroy()

