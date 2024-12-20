
##############################################################################
##############################################################################
# Moving to versioning V1_0#
## moving out various classes to different files ##
##############################################################################
######### Version 8###############################
######## Making some changes in the GUI. Including the temperature related measurements
##################################################

import tkinter as tk
import numpy as np
import os
import threading
import queue
import time
import pdb
import re
import logging
import pyvisa as visa
from datetime import datetime
from keithley2600 import Keithley2600
from matplotlib.figure import Figure
from lakeshore import Model336
from GUI.MainWindow import MainWindow

#######################################################################
############### Global Constants ######################################
####### Not modified through GUI ##############################
filterCount =1 ### measurement filter count
autoComp = '1E-3' ### auto range compliance
K2636BAddress='GPIB::26::INSTR'
K6221Address='GPIB::12::INSTR'
rCount = 0

        





########################################################################
################# Gui part ###############
#######################################

#### initiate logging ###########
logging.basicConfig(filename= "logFile.txt", filemode='a',format='%(asctime)s - %(levelname)s -%(message)s',level=logging.INFO)
logging.info('Logging is started')
root = tk.Tk()
window = MainWindow(root)
root.mainloop()
logging.info('Logging ended')

