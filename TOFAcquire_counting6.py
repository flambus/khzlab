# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 11:21:12 2014

@author: Atze
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 15:17:00 2014

@author: Atze
"""

#Imports for Gui
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from TOF6_ui import Ui_TOFMain #Reitsma: slightly modified GUI
import sys
#sys.path.append('C:/Software/Libraries')
#imports for Acqiris card
from Acqiris import Acqiris

import matplotlib.pyplot as plt

#Other Imports
import numpy as np
import time
import json
import os
from PyQtTCP import Server
np.set_printoptions(threshold=sys.maxsize)

#Create instance of Acqiris Instrument
Acqrs=Acqiris()

"""
In this version the digitizer is triggered from the external source and both channels are used
"""


#Backgroun Thread handling the acqisition and reading
class AcquisitionThread(QtCore.QThread):
    
    ErrorSignal = QtCore.pyqtSignal()
    DataReady = QtCore.pyqtSignal()
    
    def __init__(self):
        #Initialize with Control=False
        QtCore.QThread.__init__(self)
        self.Control = False
        self.Counter = 0 #Counter for summing up acquisitions
        self.Params = (1,0,2048,500) #Channel, ReadMode, Nsamp, TimeOut
        self.Data = np.zeros(self.Params[2])
        self.Data_2 = np.zeros(self.Params[2])        
        self.Data_count = np.zeros(self.Params[2])
        self.Data_2_count = np.zeros(self.Params[2])
        self.AccOver = 0 #Accumulate Over#
        self.CountingParams = []
        self.AcqMode= 0 #Reitsma: single,average,counting,covariance
        self.ExtTrigg= False        
        self.Intensity=0
        #print('Initialized')        
        
    def __del__(self):
        self.Control = False
        self.wait()
        
    def run(self):
        print("entered run")
        #Run continously
        while self.Control == True:
            try:
                #For single Acquisition
                if self.AccOver == 0:
                    print("entered if")
                    Acqrs.Calibrate()
                    Acqrs.Acquire()
                    print("Acquire done")
                    print(Acqrs.Status)
                    if Acqrs.Status != 0:
                        print("entered if")
                        self.Control = False
                        self.ErrorSignal.emit()
                        break
                    self.DataReady.emit()
                    print("emit done")
                    #print(self.Params)                    
                    #if self.ExtTrigg==True:
                        #print('15')                        
                        #self.Data,self.Data_2 = Acqrs.Read_dual(self.Params[1],self.Params[2],self.Params[3])
                        #print('16')
                        #print('Hi')
                    #else:
                    self.Data = Acqrs.Read(self.Params[0],self.Params[1],self.Params[2],self.Params[3])
                    print("data: ", Data)
                    print(len(Data))
                    print(type(Data))
                    print(type(Data[0]))
                    print("read done")
                    self.Control = False
                    if Acqrs.Status != 0:
                        self.ErrorSignal.emit()
                else:
                    print("entered else ye")
                #For averaged acqisition
                    if self.Counter < self.AccOver:
                        #print('17')
                        #Acqrs.Close()
                        Acqrs.Init()
                        Acqrs.Calibrate()
                        Acqrs.Acquire()
                        print("Acquire done")
                        #print('18')
                        print(Acqrs.Status)
                        if Acqrs.Status != 0:
                            self.Control = False
                            self.ErrorSignal.emit()
                            break
                        #if self.ExtTrigg==True:
                            #print('19')
                            #Data,Data_2 = Acqrs.Read_dual(self.Params[1],self.Params[2],self.Params[3])
                            #print('20')
                        # else:
                        # self.Params = (1,0,2048,500) #Channel, ReadMode, Nsamp, TimeOut
                        Data = Acqrs.Read(self.Params[0],self.Params[1],self.Params[2],self.Params[3])
                        print("data: ", Data)
                        # if Acqrs.Status != 0:
                        #     self.Control = False
                        #     self.ErrorSignal.emit()
                        #     print("emitted")
                        if self.Counter == 0:
                            print("if self.Counter == 0:")
                            # Start new after AccOver Acquisitions
                            self.Data=Data
                            #print('21')
                            self.Intensity=0
                            #print('counter0')                            
                            #if self.ExtTrigg==True:
                                #self.Data_2 = Data_2
                                #print('22')
                                
                            # if self.AcqMode==3:
                            #     print("if self.AcqMode==3:")
                            #     self.Data_count=np.array([])
                            #     #print('23')
                            #     if self.ExtTrigg==True:
                            #         self.Data_2_count=np.array([])
                            #         self.Intensity=np.sum(self.Data_2)
                            #         #print('24')
                            # else:
                            print("else")
                            self.Data_count=np.zeros(self.Params[2])
                            # if self.ExtTrigg==True:
                            #     self.Data_2_count=np.zeros(self.Params[2])
                        else:
                            print("else")
                            self.Data+=Data
                            
                            #if self.ExtTrigg == True:
                                #self.Intensity=np.sum(Data_2)
                                #print('25')
                                #print('counterisnot0')
                                #self.Data_2 += Data_2
                                #print('26')
                                
                        # if np.size(self.CountingParams) != 0:
                        #     print("if np.size(self.CountingParams) != 0:")
                        #     #Counting Mode #Reitsma: and the covariance mode
                        #     Low = self.CountingParams[0]
                        #     print("Low: ", Low)
                        #     High = self.CountingParams[1]
                        #     print("High: ", High)
                        #     Data[Low-10:Low+10]=0
                        #     print("Data: ", Data)
                        #     print("self.CountingParams[2]: ", self.CountingParams[2])
                        #     print("self.CountingParams: ", self.CountingParams)
                        #     print("Data[Low:High-1]: ", Data[Low:High-1])
                        #     print("Data[Low+1:High]: ", Data[Low+1:High])
                        #     LE = np.nonzero((Data[Low:High-1]>self.CountingParams[2])*(Data[Low+1:High]<self.CountingParams[2]))[0]
                        #     print("LE: ", LE)
                        #     TE = np.nonzero((Data[Low:High-1]<self.CountingParams[2])*(Data[Low+1:High]>self.CountingParams[2]))[0]
                        #     print("TE: ", TE)
                        #     #print('0')
                        #     #print(np.size(LE))
                        #     #print(np.size(TE))
                        #     print(np.size(LE)==np.size(TE))
                        #     if np.size(LE)==np.size(TE):
                        #         print("if np.size(LE)==np.size(TE):")
                        #         Pos = 0.5*(LE+TE)+0.5+Low
                        #         print(Pos)
                        #     else:
                        #         print("else")
                        #         Pos = 0.5*(LE[:-1]+TE)+0.5+Low
                        #         #print(Pos)
                        #     #print('27')
                        #     print(self.AcqMode)
                        #     if self.AcqMode==2: #Reitsma: for the counting mode everything is as usual, spectra saved with number of counts
                        #         #print('1')                                
                        #         self.Data_count[Pos.astype(int)]+=1
                        #         print(self.Data_count)
                        #         #print('2')
                        #     if self.AcqMode==3: #Reitsma: for the covariance mode only the positions with a count are saved with a -1 every cycle in order to separate shots
                        #         #print('3')
                        #         self.Data_count=np.append(self.Data_count,Pos)
                        #         #print('4')                                
                        #         self.Data_count=np.append(self.Data_count,-1)
                        #         #print('5')
                        #     #print('28')
                        #     if self.ExtTrigg==True:
                        #         print("if self.ExtTrigg==True:")
                        #         #print('6')
                        #         #Data_2[Low-10:Low+10]=0
                        #         #print('7')                                
                        #         #print('high='+str(High))
                        #         #LE = np.nonzero((Data_2[Low:High-1]>self.CountingParams[2])*(Data_2[Low+1:High]<self.CountingParams[2]))[0]
                        #         #TE = np.nonzero((Data_2[Low:High-1]<self.CountingParams[2])*(Data_2[Low+1:High]>self.CountingParams[2]))[0]
                        #         #print(np.size(LE))
                        #         #print(np.size(TE))
                        #         if np.size(LE)==np.size(TE):
                        #             print("if np.size(LE)==np.size(TE):")
                        #             Pos = 0.5*(LE+TE)+0.5+Low
                        #             #print(Pos)
                        #         else:
                        #             Pos = 0.5*(LE[:-1]+TE)+0.5+Low #Reitsma: works only for negative input signals!!!!
                        #             #print(Pos)            
                        #         #print('size='+str(np.size(self.Data_count)))
                        #         #print('size2='+str(np.size(self.Data_2_count)))
                        #         if self.AcqMode==2: #Reitsma: for the counting mode everything is as usual, spectra saved with number of counts
                        #             self.Data_2_count[Pos.astype(int)]+=1
                        #             #print('10')
                        #         if self.AcqMode==3: #Reitsma: for the covariance mode only the positions with a count are saved with a -1 every cycle in order to separate shots
                        #             self.Data_2_count=np.append(self.Data_2_count,self.Intensity)
                        #             #print('11')
                        #             #print('counter='+str(self.Counter))
                        #     #print('29')
                        self.Counter += 1
                    else:
                        self.Data = self.Data/self.AccOver
                        if self.ExtTrigg == True:
                            self.Data_2 = self.Data_2/self.AccOver                        
                        self.Counter = 0
                        self.Control = False
                        self.DataReady.emit()
                        #print('30')
            except:
                self.Counter = 0
                self.Control = False
                Acqrs.ErrMessage = 'Unknown Error in Acquisition Thread'
                self.ErrorSignal.emit()
                    

    
        

#UI Class
class MainUI(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.UI = Ui_TOFMain()
        self.UI.setupUi(self)
        self.toolbar = NavigationToolbar2QT(self.UI.Plot,self)
        self.UI.LayToolbar.addWidget(self.toolbar)
        self.toolbar_2 = NavigationToolbar2QT(self.UI.Plot_ch2,self)       
        self.UI.LayToolbar_2.addWidget(self.toolbar_2)        
        self.SetupPlot()
        self.LoadParameters()
        self.CreateFolder()
        self.AcqThread = AcquisitionThread()
        self.Time = np.zeros_like(self.AcqThread.Data)
        self.Data = self.AcqThread.Data
        self.Data_2=self.AcqThread.Data_2       
        #self.Data_2_count=self.AcqThread.Data_2_count
        #self.Data_count=self.AcqThread.Data_count        
        #self.PlotData=self.Data #Reitsma:create dummy for plotting
        self.ConnectSignals()
        self.Init = False
        self.UI.ErrLight.show()
        self.UI.ErrLightOn.hide() 
        self.TCPServer = Server.TCPServer()
        self.Ref = np.array([])
        self.BG = np.array([])
        self.Ref_2 = np.array([])
        self.BG_2 = np.array([])
        self.UI.BtnSave.setDisabled(True)
        self.LogTime = np.array([])
        self.LogData = np.array([])
        self.External = False
        self.ExtCounter = 0
        self.UI.update_1.isChecked()
        self.UI.update_2.isChecked()
        #print('Initialized')
        
    def SetupPlot(self):
        #Setting up the plot layout
        self.UI.Plot.figure.clear()
        self.UI.Plot.figure.set_facecolor('k')
        self.ax = self.UI.Plot.figure.add_axes((0.08,0.09,0.88,0.86),facecolor='k')
        for axx in ['top','bottom','left','right']:
            self.ax.spines[axx].set(linewidth=2,color='w')
        self.ax.tick_params(width=2,color='w')
        self.ax.yaxis.label.set_color('w')
        self.ax.xaxis.label.set_color('w')
        self.ax.set(xlabel='Time [ns]',ylabel='Signal [V]')
        self.ax.xaxis.grid(True,color='w')
        self.ax.yaxis.grid(True,color='w')
        [i.set_color('w') for i in self.ax.xaxis.get_ticklabels()]
        [i.set_color('w') for i in self.ax.yaxis.get_ticklabels()]
        self.UI.Plot_ch2.figure.clear()
        self.UI.Plot_ch2.figure.set_facecolor('k')
        self.ax2 = self.UI.Plot_ch2.figure.add_axes((0.08,0.09,0.88,0.86),facecolor='k')
        for axx in ['top','bottom','left','right']:
            self.ax2.spines[axx].set(linewidth=2,color='w')
        self.ax2.tick_params(width=2,color='w')
        self.ax2.yaxis.label.set_color('w')
        self.ax2.xaxis.label.set_color('w')
        self.ax2.set(xlabel='Time [s]',ylabel='Signal in region')
        self.ax2.xaxis.grid(True,color='w')
        self.ax2.yaxis.grid(True,color='w')
        [i.set_color('w') for i in self.ax2.xaxis.get_ticklabels()]
        [i.set_color('w') for i in self.ax2.yaxis.get_ticklabels()]
        
    def RefreshPlot(self):          #Reitsma: for the covarinace mode the average data is displayed
        try:
            if self.UI.update_1.isChecked():
                if self.UI.SlctMode.currentIndex()==2:
                    Data = self.Data[1,:]
                else:
                    if self.UI.SlctMode.currentIndex()==3:
                        #Data = self.AcqThread.Data
                        Data = self.PlotData #Reitsma: Quick hack, refresh the plotting data from the acq thread
                        Data = Data-self.BG #Reitsma: Quick hack, refresh
                    else:
                        Data = self.Data #Reitsma: try plotting
                self.ax.clear()
                #i1 = self.UI.IntTLow.value()
                #i2 = self.UI.IntTHigh.value()
                print("self.Time: ", self.Time)
                print(len(self.Time))
                if np.size(self.Ref) != 0:
                    self.ax.plot(self.RefTime,self.Ref,'b',scalex=False,scaley=False)
                if self.UI.AutoscaleX.isChecked():
                    if self.UI.AutoscaleY.isChecked():
                        self.ax.plot(self.Time,Data,'y',scalex=True,scaley=True)
                    else:
                        self.ax.plot(self.Time,Data,'y',scalex=True,scaley=False)
                elif self.UI.AutoscaleY.isChecked():
                    self.ax.plot(self.Time,Data,'y',scalex=False,scaley=True)
                else:
                    self.ax.plot(self.Time,Data,'y',scalex=False,scaley=False)
                #self.ax.plot([i1,i1],[-100,100],'w',scalex=False,scaley=False)
                #self.ax.plot([i2,i2],[-100,100],'w',scalex=False,scaley=False)
                self.ax.yaxis.label.set_color('w')
                self.ax.xaxis.label.set_color('w')
                self.ax.set(xlabel='Time [ns]',ylabel='Signal [V]')
                self.ax.xaxis.grid(True,color='w')
                self.ax.yaxis.grid(True,color='w')
                [i.set_color('w') for i in self.ax.xaxis.get_ticklabels()]
                [i.set_color('w') for i in self.ax.yaxis.get_ticklabels()]
                self.UI.Plot.draw()
            if self.UI.update_2.isChecked():
                if self.UI.SlctTrigg.currentIndex()==0:
                    if self.UI.SlctMode.currentIndex()==2:
                        Data = self.Data_2[1,:]
                    else:
                        if self.UI.SlctMode.currentIndex()==3:
                            #Data = self.AcqThread.Data
                            Data = self.PlotData_2 #Reitsma: Quick hack, refresh the plotting data from the acq thread
                            Data = Data-self.BG_2 #Reitsma: Quick hack, refresh
                        else:
                            Data = self.Data_2 #Reitsma: try plotting
                    self.ax2.clear()
                    #i1 = self.UI.IntTLow.value()
                    #i2 = self.UI.IntTHigh.value()
                    if np.size(self.Ref_2) != 0:
                        self.ax2.plot(self.RefTime,self.Ref_2,'b',scalex=False,scaley=False)
                    if self.UI.AutoscaleX_2.isChecked():
                        if self.UI.AutoscaleY_2.isChecked():
                            self.ax2.plot(self.Time,Data,'y',scalex=True,scaley=True)
                        else:
                            self.ax2.plot(self.Time,Data,'y',scalex=True,scaley=False)
                    elif self.UI.AutoscaleY_2.isChecked():
                        self.ax2.plot(self.Time,Data,'y',scalex=False,scaley=True)
                    else:
                        self.ax2.plot(self.Time,Data,'y',scalex=False,scaley=False)
                    #self.ax2.plot([i1,i1],[-100,100],'w',scalex=False,scaley=False)
                    #self.ax2.plot([i2,i2],[-100,100],'w',scalex=False,scaley=False)
                    self.ax2.yaxis.label.set_color('w')
                    self.ax2.xaxis.label.set_color('w')
                    self.ax2.set(xlabel='Time [ns]',ylabel='Signal [V]')
                    self.ax2.xaxis.grid(True,color='w')
                    self.ax2.yaxis.grid(True,color='w')
                    [i.set_color('w') for i in self.ax2.xaxis.get_ticklabels()]
                    [i.set_color('w') for i in self.ax2.yaxis.get_ticklabels()]
                    self.UI.Plot_ch2.draw()
        except:
            print('plotting failed')
            sys.stdout.flush()
        
#    def Log(self):
#        if False:#self.UI.ChkLog.isChecked():
#            i1 = self.UI.IntTLow.value()
#            i2 = self.UI.IntTHigh.value()
#            self.LogTime=np.append(self.LogTime,time.clock())
#            self.LogData=np.append(self.LogData,np.sum(self.Data[i1:i2]))
#            if np.size(self.LogTime)>5:
#                if time.clock()-self.LogTime[0] > self.UI.IntSecShow.value():
#                    ind = np.argmin(abs(self.LogTime-(time.clock()-self.LogTime[0])))
#                    self.LogTime = self.LogTime[ind:]
#                    self.LogData = self.LogData[ind:]
#            self.ax2.clear()
#            self.ax2.plot(self.LogTime,self.LogData,'oy')
#            self.ax2.set(xlabel='Time [s]',ylabel='Sum Signal [V]')
#            [i.set_color('w') for i in self.ax2.xaxis.get_ticklabels()]
#            [i.set_color('w') for i in self.ax2.yaxis.get_ticklabels()]
#            self.UI.PltLog.draw()
        
#    def ClearLog(self):
#        self.LogTime = np.array([])
#        self.LogData = np.array([])
        
    def TakeRef(self):                      #Reitsma: for the covariance mode it plots the averaged data
        if self.UI.SlctMode.currentIndex()==2:
            self.Ref = self.Data[1,:]
        else:
            self.Ref = self.Data
        self.RefTime = self.Time
        
    def TakeRef_2(self):        
        if self.UI.SlctMode.currentIndex()==2:
            self.Ref_2 = self.Data_2[1,:]
        else:
            self.Ref_2 = self.Data_2
        self.RefTime = self.Time    
            
            
        
        # Could be improved to work like AcquireSingle
        
    def TakeBG(self):
        if self.AcqThread.Control == True:
            self.AcqThread.wait()
        if self.UI.SlctMode.currentIndex()==2:
            self.BG = self.AcqThread.Data_count
        else:
            self.BG = self.AcqThread.Data
        
    def TakeBG_2(self) : 
        if self.AcqThread.Control == True:
            self.AcqThread.wait()
        if self.UI.SlctMode.currentIndex()==2:
            self.BG_2 = self.AcqThread.Data_2_count
        else:
            self.BG_2 = self.AcqThread.Data_2

        
        
        # Could be improved to work like AcquireSingle
            
    def ClearRef(self):
        self.Ref = np.array([])
    
    def ClearRef_2(self):
        self.Ref_2 = np.array([])
        
    def ConnectSignals(self):
        #Custon Signals for Acquisition
        self.AcqThread.ErrorSignal.connect(self.Error)
        self.AcqThread.DataReady.connect(self.Restart)
        #Buttons
        self.UI.BtnStart.clicked.connect(self.Start)
        self.UI.BtnStop.clicked.connect(self.Stop)
        self.UI.BtnQuit.clicked.connect(self.Quit)
        self.UI.BtnSave.clicked.connect(self.SaveData)
        self.UI.BtnAcquire.clicked.connect(self.AcquireSingle)
        self.UI.BtnTakeRef.clicked.connect(self.TakeRef)
        self.UI.BtnTakeRef_2.clicked.connect(self.TakeRef_2)        
        self.UI.BtnClearRef.clicked.connect(self.ClearRef)
        self.UI.BtnClearRef_2.clicked.connect(self.ClearRef_2)
        self.UI.BtnTakeBG.clicked.connect(self.TakeBG)
        self.UI.BtnTakeBG_2.clicked.connect(self.TakeBG_2)
        self.UI.BtnExternal.clicked.connect(self.EnableExternal)
        #ValueChanges
        self.UI.SlctMode.currentIndexChanged.connect(self.ParameterChange)
        self.UI.SlctTrigg.currentIndexChanged.connect(self.ParameterChange)
        self.UI.DblDelay.valueChanged.connect(self.ParameterChange)
        self.UI.DblIntTime.valueChanged.connect(self.ParameterChange)
        self.UI.DblOffset.valueChanged.connect(self.ParameterChange)
        self.UI.DblOffset_2.valueChanged.connect(self.ParameterChange)
        self.UI.IntInterval.valueChanged.connect(self.ParameterChange)
        self.UI.IntMeasurements.valueChanged.connect(self.ParameterChange)
        self.UI.IntSamples.valueChanged.connect(self.ParameterChange)
        self.UI.DblTrigLevel.valueChanged.connect(self.ParameterChange)
        self.UI.DblFullscale.valueChanged.connect(self.ParameterChange)
        self.UI.DblFullscale_2.valueChanged.connect(self.ParameterChange)
        
    def Configure(self):
        #Configure the Measurement
        Intervals = np.array([1,2,5,10,20,50,100,200,500,1000,2000,5000])
        SampInt = self.UI.IntInterval.value()
        if SampInt in Intervals:
            pass
        else:
            #Change Sample Interval to an allowed value
            ind = np.argmin(abs(Intervals-self.UI.IntInterval.value()))
            SampInt = Intervals[ind]
            self.UI.IntInterval.setValue(Intervals[ind])
        Delay = self.UI.DblDelay.value()*1e-6
        Nsamp = int(self.UI.IntSamples.value()/32)*32+32
        self.Time = np.arange(0,Nsamp*SampInt,SampInt)
        Channel = 1
        if self.UI.SlctTrigg.currentIndex()==1:
            Channel = 2
        Fullscale = self.UI.DblFullscale.value()
        Offset = self.UI.DblOffset.value()        
        TrigChannel = 1
        if self.UI.SlctTrigg.currentIndex()==2:
            TrigChannel = 2
        elif self.UI.SlctTrigg.currentIndex()==0:
            Fullscale_2 = self.UI.DblFullscale_2.value()
            Offset_2 = self.UI.DblOffset_2.value()
            self.AcqThread.ExtTrigg=True
        TrigLevel = self.UI.DblTrigLevel.value()
        self.AcqThread.AccOver = 0      
        self.AcqThread.AcqMode = self.UI.SlctMode.currentIndex()    #Reitsma: single,average,counting,covariance
        print("stage 1 done")
        if self.UI.SlctMode.currentIndex() in (0,2,3): #Reitsma: Added the 3rd mode to this list
            self.AcqThread.CountingParams = []
            if self.AcqThread.Params[1] == 2:
                #Reinitialize if going from averaged to normal
                Acqrs.Close()
                print("Acqrs.Close() done")
                Acqrs.Init()
                print("Acqrs.Init() done")
            if self.UI.SlctMode.currentIndex() in (2,3): #Reitsma: Added the 3rd mode here, as we want to use the counting mode here as well
                print("self.UI.SlctMode.currentIndex() in (2,3):")
                self.AcqThread.AccOver = self.UI.IntMeasurements.value()
                print("SampInt: ",SampInt)
                print("type(SampInt): ", type(SampInt))
                print("self.UI.IntCountLimitLow.value(): ", self.UI.IntCountLimitLow.value())
                print("type(self.UI.IntCountLimitLow.value()): ", type(self.UI.IntCountLimitLow.value()))
                Low = int(self.UI.IntCountLimitLow.value()/SampInt)
                print("Low: ", Low)
                print("self.UI.IntCountLimitHigh.value(): ", self.UI.IntCountLimitHigh.value())
                High = int(self.UI.IntCountLimitHigh.value()/SampInt)
                print("High: ", High)
                self.AcqThread.CountingParams = [Low,High,self.UI.DblCountThreshold.value()]
            self.AcqThread.Params = (Channel,0,Nsamp,500)
            if self.UI.SlctTrigg.currentIndex()==0:       
                print("if")
                Acqrs.ConfigureExt(SampInt,Delay,Nsamp,1,2,Fullscale,Fullscale_2,Offset,Offset_2,TrigLevel)
                print("Acqrs.ConfigureExt done")
            else:   
                print("if")
                Acqrs.Configure(SampInt,Delay,Nsamp,Channel,Fullscale,Offset,TrigChannel,1.0,0.0,TrigLevel)
                print("Acqrs.Configure done")
            if Acqrs.Status != 0:
                self.Error()
        print(self.UI.SlctMode.currentIndex())
        if self.UI.SlctMode.currentIndex()==1:
            print("if self.UI.SlctMode.currentIndex()==1:")
            if self.AcqThread.Params[1] == 0:
                #Reinitialize if going from normal to averaged
                Acqrs.Close()
                Acqrs.Init() 
            if self.UI.SlctTrigg.currentIndex()==0:
                Acqrs.ConfigureExt(SampInt,Delay,Nsamp,1,2,Fullscale,Fullscale_2,Offset,Offset_2,TrigLevel)
                print("Acqrs.ConfigureExt done")
            else:
                Acqrs.Configure(SampInt,Delay,Nsamp,Channel,Fullscale,Offset,TrigChannel,1.0,0.0,TrigLevel)
                print("Acqrs.Configure done")
            if Acqrs.Status != 0:
                self.Error()
            self.AcqThread.CountingParams == []
            if self.UI.DblIntTime.value()==0.0:
                print("if self.UI.DblIntTime.value()==0.0:")
                Acqrs.Close()
                Acqrs.Init()
                if self.UI.SlctTrigg.currentIndex()==0:
                    Acqrs.ConfigureExt(SampInt,Delay,Nsamp,1,2,Fullscale,Fullscale_2,Offset,Offset_2,TrigLevel)
                    print("Acqrs.ConfigureExt done")
                else:
                    Acqrs.Configure(SampInt,Delay,Nsamp,Channel,Fullscale,Offset,TrigChannel,1.0,0.0,TrigLevel)
                    print("Acqrs.Configure done")
                self.AcqThread.Params = (Channel,0,Nsamp,500)
                self.AcqThread.AccOver = self.UI.IntMeasurements.value()
            # else:
            #     #Set up averaged acquisition
            #     Waveforms = int(self.UI.DblIntTime.value()*1000)
            #     self.AcqThread.Params = (Channel,2,Nsamp,Waveforms+500)
            #     self.AcqThread.AccOver = self.UI.IntMeasurements.value()
            #     DitherRange = 0
            #     TrigResync = 0
            #     Acqrs.ConfigureAvg(Nsamp,Waveforms,DitherRange,TrigResync)
            #     if Acqrs.Status != 0:
            #         self.Error()
        print('configured')        
                
    def ParameterChange(self):
        if self.AcqThread.Control == True:
            self.Stop()
            self.Start()
        
    def Start(self):
        #self.ClearLog()
        self.UI.BtnSave.setDisabled(True)
#        if self.UI.SlctTrigg.currentIndex()!= 0:       
#            self.UI.DblFullscale_2.setDisabled(True)
#            self.UI.DblOffset_2.setDisabled(True)
#            self.UI.BtnTakeBG_2.setDisabled(True)
#            self.UI.BtnTakeRef_2.setDisabled(True)
#            self.UI.BtnClearRef_2.setDisabled(True)
        if self.UI.ErrLight.isHidden():
            #Get rid of error
            self.UI.ErrLight.show()
            self.UI.ErrLightOn.hide()
            self.UI.ErrLine.clear()
            self.UI.ErrLine.insert("All is well!")
        if self.AcqThread.Control == False:
            self.AcqThread.wait()
            if self.Init == False:
                print("entered start if if")
                #Initialize if not initialized
                Acqrs.Init()
                #if Acqrs.Status != 0:
                #    self.Error()
                self.Init = True
            #print('click start')
            self.Configure()
            print("self.Configure() done")
            self.AcqThread.Counter = 0
            if not self.External:            
                self.AcqThread.Control = True
                self.AcqThread.start()
            
    
    def EnableExternal(self):
        self.ExtCounter = 0
        self.External = True
        self.UI.BtnQuit.setDisabled(True)
        self.UI.BtnStart.setDisabled(True)
        self.UI.SlctMode.setDisabled(True)
        self.UI.IntSamples.setDisabled(True)
        self.UI.IntInterval.setDisabled(True)
        self.UI.DblDelay.setDisabled(True)
        self.UI.DblOffset.setDisabled(True)
        self.UI.DblOffset_2.setDisabled(True)
        self.UI.DblFullscale.setDisabled(True)
        self.UI.DblFullscale_2.setDisabled(True)
        self.UI.DblIntTime.setDisabled(True)
        self.UI.IntMeasurements.setDisabled(True)
        self.UI.SlctTrigg.setDisabled(True)
        self.UI.DblTrigLevel.setDisabled(True)
        self.UI.BtnAcquire.setDisabled(True)
        self.UI.BtnStop.setDisabled(True)
        self.UI.IntCountLimitLow.setDisabled(True)
        self.UI.IntCountLimitHigh.setDisabled(True)
        self.UI.DblCountThreshold.setDisabled(True)
        self.UI.BtnExternal.clicked.disconnect()
        self.UI.BtnExternal.clicked.connect(self.Verify)
        self.UI.BtnExternal.setText("Stop External")
        self.UI.RecCh1.setChecked(True)
        self.UI.RecCh2.setChecked(True)
        self.Stop()
        #self.ClearLog()
        self.Start()
        #self.TCPServer.Hostname = 'Atze'
        self.TCPServer.Hostname = 'localhost'
        self.TCPServer.Port = 10102
        self.TCPServer.DataReceived.connect(self.StartExternal)
        self.TCPServer.TCPError.connect(self.Error)
        self.TCPServer.Start()
                
    def StartExternal(self):
        self.AcqThread.Control = True
        self.AcqThread.start()
        
    def AcquireSingle(self):
        self.Stop()
        self.AcqThread.DataReady.disconnect()
        self.AcqThread.DataReady.connect(self.ReconnectDR)
        self.Start()
        
    def ReconnectDR(self):
        self.UI.BtnSave.setDisabled(False)
        self.Restart()
        self.AcqThread.DataReady.disconnect()        
        self.AcqThread.DataReady.connect(self.Restart)
        
            
    def Stop(self):
        self.UI.BtnSave.setDisabled(True)
#        self.UI.DblFullscale_2.setDisabled(False)
#        self.UI.DblOffset_2.setDisabled(False)
#        self.UI.BtnTakeBG_2.setDisabled(False)
#        self.UI.BtnTakeRef_2.setDisabled(False)
#        self.UI.BtnClearRef_2.setDisabled(False)        
        self.AcqThread.Control = False
        self.AcqThread.wait()
        self.AcqThread.DataReady.disconnect()
        self.AcqThread.DataReady.connect(self.Restart)

            
    def Quit(self):
        if self.AcqThread.Control == True:
            self.AcqThread.Control = False
        self.AcqThread.wait()
        Acqrs.Close()
        self.SaveParameters()
        self.close()
        
    def Restart(self):
        try:
            if self.UI.SlctMode.currentIndex() == 2:
                self.Data = np.vstack((self.AcqThread.Data,self.AcqThread.Data_count))
                if self.UI.SlctTrigg.currentIndex()==0:
                    self.Data_2 = np.vstack((self.AcqThread.Data_2,self.AcqThread.Data_2_count))
            else:
                if self.UI.SlctMode.currentIndex() == 3:        #Reitsma: only save counting data for covariance mode in order to be efficient
                    self.PlotData=self.AcqThread.Data           #Reitsma: create dummy array for plotting data                    
                    self.Data = self.AcqThread.Data_count
                    if self.UI.SlctTrigg.currentIndex()==0:
                        self.PlotData_2=self.AcqThread.Data_2           #Reitsma: create dummy array for plotting data                    
                        self.Data_2 = self.AcqThread.Data_2_count
                else:
                    self.Data = self.AcqThread.Data
                    if self.UI.SlctTrigg.currentIndex()==0:
                        self.Data_2 = self.AcqThread.Data_2
            #print('31')
            #restart
            if self.External:
                #Restart TCP for external
                if self.UI.IntExtAcq.value() == 1:
                    filepath = self.TCPServer.Data
                    filepath_2= filepath[:(len(filepath)-4)]+'_XUV.dat'                    
                    self.TCPServer.Send(str(self.AcqThread.AccOver))
                    #print('32')
                else:
                    name = self.TCPServer.Data
                    #print('33')
                    filepath = name[:(len(name)-4)]+'_'+str(self.ExtCounter)+'.dat'
                    filepath_2= name[:(len(name)-4)]+'_'+str(self.ExtCounter)+'_XUV.dat'                   
                    if self.ExtCounter < self.UI.IntExtAcq.value()-1:
                        self.ExtCounter += 1
                        self.AcqThread.Control = True
                        self.AcqThread.start()
                    else:
                        self.ExtCounter = 0
                        self.TCPServer.Send(str(self.AcqThread.AccOver))
                        #self.RefreshPlot()
                    #print('34')
            elif not self.UI.BtnSave.isEnabled():
                #restart live if not acquire single
                self.AcqThread.wait()
                self.AcqThread.Control = True
                self.AcqThread.start()
            #BG Subtraction
            #print('35')
            if self.UI.ChkSubtract.isChecked():
                if not self.UI.SlctMode.currentIndex() in (2,3):    #Reitsma: Exclude BG subtraction also in covariance mode 3
                    if np.size(self.BG) == np.size(self.Data):
                        self.Data = self.Data-self.BG
                    if self.UI.SlctTrigg.currentIndex()==0:
                        if np.size(self.BG_2) == np.size(self.Data_2):
                            self.Data_2 = self.Data_2-self.BG_2
            #print('36')
            if self.External:
                #Save Data if external                                          
                Header='Fullscale: '+str(self.UI.DblFullscale.value())
                Header+=' Offset: '+str(self.UI.DblOffset.value())                
                Header+=' AccOver: '+str(self.UI.IntMeasurements.value())
                Header_2='Fullscale: '+str(self.UI.DblFullscale_2.value())
                Header_2+=' Offset: '+str(self.UI.DblOffset_2.value())
                Header_2+=' AccOver: '+str(self.UI.IntMeasurements.value())               
                if self.UI.SlctMode.currentIndex()==3:              #Reitsma: Do not save a time-axis for the covariance mode
                    Header+=' CountTh: '+str(self.UI.DblCountThreshold.value())
                    Header_2+=' CountTh: '+str(self.UI.DblCountThreshold.value())
                    if self.UI.RecCh1.isChecked():                    
                        np.savetxt(filepath,np.transpose(self.Data),header=Header)
                    if self.UI.SlctTrigg.currentIndex()==0:
                        if self.UI.RecCh2.isChecked():
                            np.savetxt(filepath_2,np.transpose(self.Data_2),header=Header_2)
                else:
                    if self.UI.SlctMode.currentIndex()==1:
                        Header+=' IntTime: '+str(self.UI.DblIntTime.value())
                        Header_2+=' IntTime: '+str(self.UI.DblIntTime.value())
                    elif self.UI.SlctMode.currentIndex()==2:
                        Header+=' CountTh: '+str(self.UI.DblCountThreshold.value())
                        Header_2+=' CountTh: '+str(self.UI.DblCountThreshold.value())
                    if self.UI.RecCh1.isChecked():
                        np.savetxt(filepath,np.transpose(np.vstack((self.Time,self.Data))),header=Header)
                    if self.UI.SlctTrigg.currentIndex()==0:
                        if self.UI.RecCh2.isChecked():
                            np.savetxt(filepath_2,np.transpose(np.vstack((self.Time,self.Data_2))),header=Header_2)
                #print('37')
            #Plot and Log
            self.RefreshPlot()
            #self.Log()
        except:
            self.Error()

            
    def SaveData(self):
        self.AcqThread.wait()
        filepath = self.DataFolder+self.UI.LeName.text()
        filepath_2 = self.DataFolder+self.UI.LeName_2.text()        
        Header='Fullscale: '+str(self.UI.DblFullscale.value())
        Header+=' Offset: '+str(self.UI.DblOffset.value())                
        Header+=' AccOver: '+str(self.UI.IntMeasurements.value())
        Header_2='Fullscale: '+str(self.UI.DblFullscale_2.value())
        Header_2+=' Offset: '+str(self.UI.DblOffset_2.value())
        Header_2+=' AccOver: '+str(self.UI.IntMeasurements.value())               
        if self.UI.SlctMode.currentIndex()==3:              #Reitsma: Do not save a time-axis for the covariance mode
            Header+=' CountTh: '+str(self.UI.DblCountThreshold.value())
            Header_2+=' CountTh: '+str(self.UI.DblCountThreshold.value())
            if self.UI.RecCh1.isChecked():            
                np.savetxt(str(filepath),np.transpose(self.Data),header=Header)
            if self.UI.SlctTrigg.currentIndex()==0:
                if self.UI.RecCh2.isChecked():
                    np.savetxt(str(filepath_2),np.transpose(self.Data_2),header=Header_2)    
        else:        
            if self.UI.SlctMode.currentIndex()==1:
                Header+=' IntTime: '+str(self.UI.DblIntTime.value())
                Header_2+=' IntTime: '+str(self.UI.DblIntTime.value())
            elif self.UI.SlctMode.currentIndex()==1:
                Header+=' CountTh: '+str(self.UI.DblCountThreshold.value())
                Header_2+=' CountTh: '+str(self.UI.DblCountThreshold.value())
            if self.UI.RecCh1.isChecked():
                np.savetxt(str(filepath),np.transpose(np.vstack((self.Time,self.Data))),header=Header)
            if self.UI.SlctTrigg.currentIndex()==0:
                if self.UI.RecCh2.isChecked():                
                    np.savetxt(str(filepath_2),np.transpose(np.vstack((self.Time,self.Data_2))),header=Header_2)
        self.FileNumber += 1
        self.UI.LeName.clear()
        self.UI.LeName_2.clear()        
        self.UI.LeName.insert('TOF_'+str(self.FileNumber)+'.dat')
        self.UI.LeName_2.insert('XUV_'+str(self.FileNumber)+'.dat')
        self.UI.BtnSave.setDisabled(True)

        
    def Error(self):
        self.Stop()
        Acqrs.Close()
        self.Init = False
        if self.External:
            self.TCPServer.Stop()
            #Write Error in Log and try to restart the measurment
            if os.path.isfile(self.DataFolder+'ErrorLog.txt'):
                ErrorLog = open(self.DataFolder+'ErrorLog.txt','a')
            else:
                ErrorLog = open(self.DataFolder+'ErrorLog.txt','w')
            if Acqrs.ErrMessage:
                ErrorLog.write(time.strftime('%H-%M-%S')+' Acqiris: '+Acqrs.ErrMessage+'\n')
            elif self.TCPServer.ErrorMessage:
                ErrorLog.write(time.strftime('%H-%M-%S')+' TCP: '+self.TCPServer.ErrorMessage+'\n')
            else:
                ErrorLog.write(time.strftime('%H-%M-%S')+' Unknown Error\n')
            ErrorLog.close()
            self.Start()
            self.EnableExternal()
        else:            
            self.UI.ErrLight.hide()
            self.UI.ErrLightOn.show()
            self.UI.ErrLine.clear()
            if Acqrs.ErrMessage:
                self.UI.ErrLine.insert('Acqiris: '+Acqrs.ErrMessage)
            elif self.TCPServer.ErrorMessage:
                self.UI.ErrLine.insert('TCP: '+self.TCPServer.ErrorMessage)
            else:
                self.UI.ErrLine.insert('Unknown Error')

        
    def SaveParameters(self):
        Params = (self.UI.SlctMode.currentIndex(),\
                self.UI.IntSamples.value(),\
                self.UI.IntInterval.value(),\
                self.UI.DblDelay.value(),\
                self.UI.DblOffset.value(),\
                self.UI.DblOffset_2.value(),\
                self.UI.DblFullscale.value(),\
                self.UI.DblFullscale_2.value(),\
                self.UI.DblIntTime.value(),\
                self.UI.IntMeasurements.value(),\
                self.UI.SlctTrigg.currentIndex(),\
                self.UI.DblTrigLevel.value(),\
                self.UI.IntCountLimitLow.value(),\
                self.UI.IntCountLimitHigh.value(),\
                self.UI.DblCountThreshold.value(),\
                )
        ParaFile = open('Parameters','w')
        json.dump(Params,ParaFile)
        ParaFile.close()
        
    def LoadParameters(self):
        if os.path.isfile('Parameters'):
            ParaFile = open('Parameters','r')
            Params = json.load(ParaFile)
            ParaFile.close()
            self.UI.SlctMode.setCurrentIndex(Params[0])
            self.UI.IntSamples.setValue(Params[1])
            self.UI.IntInterval.setValue(Params[2])
            self.UI.DblDelay.setValue(Params[3])
            self.UI.DblOffset.setValue(Params[4])
            self.UI.DblOffset_2.setValue(Params[5])            
            self.UI.DblFullscale.setValue(Params[6])
            self.UI.DblFullscale_2.setValue(Params[7])
            self.UI.DblIntTime.setValue(Params[8])
            self.UI.IntMeasurements.setValue(Params[9])
            self.UI.SlctTrigg.setCurrentIndex(int(Params[10]))
            self.UI.DblTrigLevel.setValue(Params[11])
            self.UI.IntCountLimitLow.setValue(Params[12])
            self.UI.IntCountLimitHigh.setValue(int(Params[13]))
            self.UI.DblCountThreshold.setValue(Params[14])
            
    def CreateFolder(self):
        self.DataFolder = 'Z:\\'+time.strftime('%y-%m-%d\\')
        self.UI.LeFolder.clear()
        self.UI.LeFolder_2.clear()        
        self.UI.LeFolder.insert(self.DataFolder)
        self.UI.LeFolder_2.insert(self.DataFolder)
        if os.path.exists(self.DataFolder):
            self.FileNumber = int(np.sum([name[0:3]=='TOF' for name in os.listdir(self.DataFolder)]))
        else:
            os.makedirs(self.DataFolder)
            self.FileNumber = 0
        self.UI.LeName.clear()
        self.UI.LeName_2.clear()
        self.UI.LeName.insert('TOF_'+str(self.FileNumber)+'.dat')
        self.UI.LeName_2.insert('XUV_'+str(self.FileNumber)+'.dat')    
            
    def Verify(self):
        reply = QtGui.QMessageBox.question(self, \
        'Stop Acquisition?',"Are you sure you want to stop the Acquisition?", \
        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)        
        if reply == QtGui.QMessageBox.Yes:
            self.External=False
            self.Stop()
            self.TCPServer.Stop()
            self.UI.BtnQuit.setDisabled(False)
            self.UI.BtnStart.setDisabled(False)
            self.UI.SlctMode.setDisabled(False)
            self.UI.IntSamples.setDisabled(False)
            self.UI.IntInterval.setDisabled(False)
            self.UI.DblDelay.setDisabled(False)
            self.UI.DblOffset.setDisabled(False)
            self.UI.DblOffset_2.setDisabled(False)
            self.UI.DblFullscale.setDisabled(False)
            self.UI.DblFullscale_2.setDisabled(False)
            self.UI.DblIntTime.setDisabled(False)
            self.UI.IntMeasurements.setDisabled(False)
            self.UI.SlctTrigg.setDisabled(False)
            self.UI.DblTrigLevel.setDisabled(False)
            self.UI.BtnAcquire.setDisabled(False)
            self.UI.BtnStop.setDisabled(False)
            self.UI.IntCountLimitLow.setDisabled(False)
            self.UI.IntCountLimitHigh.setDisabled(False)
            self.UI.DblCountThreshold.setDisabled(False)
            self.UI.BtnExternal.setText("Start External")
            self.UI.BtnExternal.clicked.disconnect()
            self.UI.BtnExternal.clicked.connect(self.EnableExternal)
        else:
            pass
        
      
        
            
            
            
        
        
        
            
        

#Starting the Application        
if __name__ == "__main__":
    App = QtWidgets.QApplication(sys.argv)
    Window = MainUI()
    Window.show()
    App.exec_()
    