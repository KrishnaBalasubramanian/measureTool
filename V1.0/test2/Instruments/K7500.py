import pyvisa as visa
class K7500():
    def __init__(self):
        self.connected = self.connect()
        self.sm.write(':SYST:PRES')
        time.sleep(1)
        self.sm.write('*RST') ### reset 6221
        self.sm.write('FORM:ELEM READ') ## send out only the reading
        self.sm.write(':SYST:COMM:SER:BAUD 19200') ### set baud
        self.sm.write(':SYST:COMM:SER:TERM LF') ### set termiantion to line feed
        self.sm.write(':SYST:COMM:SER:SEND "*RST"') ### reset 2182
        time.sleep(1)
        self.sm.write(':SYST:COMM:SER:SEND "*CLS"') ### reset 2182
        time.sleep(0.2)
        self.sm.write(':SYST:COMM:SER:SEND ":INIT:CONT OFF;:ABORT"') ### init off
        time.sleep(0.2)
        self.sm.write(':SYST:COMM:SER:SEND ":SYST:BEEP:STAT OFF"') ### init off
        time.sleep(0.2)
        self.sm.write('SYST:COMM:SER:SEND "FORM:ELEM READ"') ## send out only the reading
        time.sleep(0.2)
        self.sm.write('SYST:COMM:SER:SEND "STAT:PRES"') ## send out only the reading
        time.sleep(0.2)
        self.sm.write('SYST:COMM:SER:SEND "STAT:QUE:CLE"') ## send out only the reading
        time.sleep(0.2)

    def connect(self):
        try:
            rm = visa.ResourceManager('@py')
            self.sm=rm.open_resource(KDMMAddress) ## setting a delay between write and query
            self.sm.write_termination='\n'
            self.sm.read_termination='\n'
            self.sm.chunk_size=102400
            logging.debug('Connected to DMM at ' + KDMMAddress)
            return True
        except Exception:
            logging.error('Unable to connect to DMM at ' + KDMMAddress)
            return False

    def setSenseMode(self,chan,param,mlim,nplc,aver):
        if param == "DC":
            fun = 'VOLT:DC'
        elif param =="RES":
            fun = 'RES'
        else:
            print("Wrong mode selected")
            logging.error("Wrong mode selected")
        self.sm.write(':SENS:FUNC "'+fun + '"')
        if mlim == "auto":
            self.sm.write(':SENS:' + fun + ':RANG:AUTO ON')
        else:
            self.sm.write(':SENS:' + fun + ':RANG '+ str(mlim)) 
        self.sm.write(':SENS:' + fun + ':NPLC ' + str(nplc)) #### set the filter cycles
        self.sm.write(':SENS:' + fun + ':COUN' + str(aver)) ### make these many measurements

    def doMeasure(self,chan='A'):
        self.sm.write(':TRAC:CLEAR')
        self.sm.query(':READ?')
        return(self.getTraceData())
    def getTraceData(self):
        return self.sm.query(':TRAC:DATA?')
