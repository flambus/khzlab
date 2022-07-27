
from ctypes import *
#from pickle import FALSE
import numpy as np
from AqMD3 import *

resourceString = "PXI2::0::0::INSTR"
initOptions = "Simulate=false, DriverSetup= Model=U5310A"

class Acqiris(object):
    def __init__(self):
        self.Status = 0
        self.InstrID = c_uint32(0)
        self.ErrMessage = ''
        #self.driver = AqMD3(resourceString, True, True, initOptions)
        self.timeoutInMs = 5000
        self.driver = 0
        
    # def Error(self, Status):
    #     if self.Status != 0:
    #         tmp = c_int32(self.Status)
    #         Message = create_string_buffer(512)
    #         # F_Error(c_int(0), hex(id(self.Status)), sizeof(Message), Message)
    #         # F_Error(c_int(0), self.Status, sizeof(Message), Message)
    #         F_Error(self.InstrID, byref(tmp), c_int32(sizeof(Message)), Message)
    #         #self.ErrMessage = Message.value.decode("utf-8")
    #         self.ErrMessage = Message.value
    #         print("error: ", self.ErrMessage)

    # def getNbrInst(self):
    #     Nbr = c_int(0)
    #     self.Status = F_getNbrInst(byref(Nbr))
    #     self.Error()
    #     return Nbr.value
        
    def Init(self):
        self.driver = AqMD3(resourceString, True, True, initOptions)
        
        print(self.driver)
        print("init done")
    
    def Calibrate(self):
        self.driver.Calibration.SelfCalibrate()
        print("calibration done")
        
    def Close(self):
        return 0
        
    def Configure(self,SampInt,delay,N_samp,channel,fullscale,offset,trigChannel,fullscaleTrig,offsetTrig,trigLevel):
        print("entering configuration")
        # self.Status = F_ConfigV(self.InstrID, c_char_p(b'Channel2'), c_double(fullscaleTrig), c_double(offsetTrig), AQMD3_VAL_VERTICAL_COUPLING_DC, c_bool(True))
        # self.Error(self.Status)
        # if self.Status != 0:
        #     return
        # print("F_ConfigV done")
        coupling = VerticalCoupling.DC
        
        for channel in self.driver.Channels:
            channel.Configure(1.0, offset, coupling, True)
        
        self.driver.Acquisition.RecordSize = N_samp
        print("self.driver.Acquisition.RecordSize", self.driver.Acquisition.RecordSize)
        
        # self.Status = F_ConfigTrigClass(self.InstrID, b"External1", AQMD3_ATTR_TRIGGER_TYPE, AQMD3_VAL_EDGE_TRIGGER)
        # self.Error(self.Status)
        # if self.Status != 0:
        #     return
        # print("F_ConfigTrigClass done")
        
        sourceName = "External1"
        level = trigLevel
        slope = TriggerSlope.Positive
        self.driver.Trigger.ActiveSource = sourceName
        activeTrigger = self.driver.Trigger.Sources[sourceName]
        activeTrigger.Level = level
        activeTrigger.Edge.Slope = slope
        activeTrigger.Coupling = coupling
        self.driver.Calibration.SelfCalibrate()   
        print("F_ConfigTrigSource done")

        
    def Acquire(self):
        self.driver.Acquisition.Initiate()
        self.driver.Acquisition.WaitForAcquisitionComplete(self.timeoutInMs)
        
        
    def Read(self):
        waveform = None
        self.driver.Acquisition.Initiate()
        self.driver.Acquisition.WaitForAcquisitionComplete(self.timeoutInMs)
        for channel in self.driver.Channels:
            print()
            print("Fetching data from ", channel.Name)
            
            print(self.driver)
            print(self.driver.Acquisition.RecordSize)
            print(self.driver.Trigger.ActiveSource)
            print(self.driver.Trigger.Sources["External1"].Level)
            print(self.driver.Trigger.Sources["External1"].Edge.Slope)
            print(self.driver.Trigger.Sources["External1"].Coupling)

            # Fetch the acquired data
            waveform = channel.Measurement.FetchWaveform(waveform)
            print("First samples:", *waveform[:10])

            print("Processing data fetched from ", channel.Name)
            # Convert data to Volts.
            convertedSamples = []
            for sampleRaw in waveform:
                # the same sample in volts
                sampleInVolts = sampleRaw * waveform.ScaleFactor + waveform.ScaleOffset
                convertedSamples.append(sampleInVolts)
            return convertedSamples
    
        
    def ConfigureExt(self,SampInt,delay,N_samp,channel1,channel2,fullscale1,fullscale2,offset1,offset2,trigLevel):
        print("entering configuration")
        # self.Status = F_ConfigV(self.InstrID, c_char_p(b'Channel2'), c_double(fullscaleTrig), c_double(offsetTrig), AQMD3_VAL_VERTICAL_COUPLING_DC, c_bool(True))
        # self.Error(self.Status)
        # if self.Status != 0:
        #     return
        # print("F_ConfigV done")
        print(offset1)
        print(SampInt)
        coupling = VerticalCoupling.DC
        
        for channel in self.driver.Channels:
            print("Applying on ", channel.Name)
            channel.Configure(1.0, 0.0, coupling, True)
        
        self.driver.Acquisition.RecordSize = N_samp
        print("self.driver.Acquisition.RecordSize", self.driver.Acquisition.RecordSize)
        
        # self.Status = F_ConfigTrigClass(self.InstrID, b"External1", AQMD3_ATTR_TRIGGER_TYPE, AQMD3_VAL_EDGE_TRIGGER)
        # self.Error(self.Status)
        # if self.Status != 0:
        #     return
        # print("F_ConfigTrigClass done")
        
        #trigLevel_pct = 100*trigLevel/fullscaleTrig
        
        slope = TriggerSlope.Positive
        
        self.driver.Trigger.ActiveSource = "External1"
        
        activeTrigger = self.driver.Trigger.Sources["External1"]
        
        activeTrigger.Level = trigLevel
        
        activeTrigger.Edge.Slope = slope
        
        activeTrigger.Coupling = coupling
        print("F_ConfigTrigSource done")