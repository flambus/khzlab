from ctypes import *
from os import wait
from time import sleep
import time
import numpy as np
import sys
import matplotlib.pyplot as plt
np.set_printoptions(threshold=sys.maxsize)

acqiris = CDLL("/usr/lib/libAqMD3.so")

print(acqiris)

IVI_ATTR_BASE = c_uint32(1000000)
IVI_INHERENT_ATTR_BASE = c_uint32(IVI_ATTR_BASE.value + c_uint32(50000).value)
IVI_CLASS_ATTR_BASE = c_uint32(IVI_ATTR_BASE.value + c_uint32(250000).value)
AQMD3_ATTR_SAMPLE_RATE = c_uint32(IVI_CLASS_ATTR_BASE.value + c_uint32(15).value)
AQMD3_ATTR_TRIGGER_DELAY = c_uint32(IVI_CLASS_ATTR_BASE.value + c_uint32(17).value)
AQMD3_ATTR_RECORD_SIZE = c_uint32(IVI_CLASS_ATTR_BASE.value + c_uint32(14).value)
AQMD3_ATTR_NUM_RECORDS_TO_ACQUIRE = c_uint32(IVI_CLASS_ATTR_BASE.value + c_uint32(13).value)
AQMD3_ATTR_ACTIVE_TRIGGER_SOURCE = c_uint32(IVI_CLASS_ATTR_BASE.value + c_uint32(1).value)
AQMD3_ATTR_TRIGGER_LEVEL = c_uint32(IVI_CLASS_ATTR_BASE.value + c_uint32(19).value)
AQMD3_ATTR_TRIGGER_SLOPE = c_uint32(IVI_CLASS_ATTR_BASE.value + c_uint32(21).value)
AQMD3_VAL_POSITIVE = c_uint32(1)
AQMD3_VAL_NEGATIVE = c_uint32(2)
AQMD3_ATTR_TRIGGER_COUPLING = c_uint32(IVI_CLASS_ATTR_BASE.value + c_uint32(16).value)
AQMD3_VAL_TRIGGER_COUPLING_DC = c_uint32(1)
AQMD3_ATTR_TRIGGER_TYPE = c_uint32(IVI_CLASS_ATTR_BASE.value + c_uint32(23).value)
AQMD3_VAL_EDGE_TRIGGER = c_int32(1)
AQMD3_VAL_VERTICAL_COUPLING_DC = c_uint32(1)
AQMD3_ATTR_SPECIFIC_DRIVER_PREFIX = c_uint32(IVI_INHERENT_ATTR_BASE.value + c_uint32(302).value)

resource = c_char_p(b'PXI2::0::0::INSTR')
options = c_char_p(b'Simulate=false, DriverSetup= Model=U5310A')

# driver = AqMD3(resource, True, True, options)

# # Configure channel properties.
# range = 1.0
# channelOffset = 0.0
# for channel in driver.Channels:
#     print("Applying on ", channel.Name)
#     channel.Configure(range, channelOffset, AQMD3_VAL_VERTICAL_COUPLING_DC, True)

#F_Prefix = getattr(acqiris, "AqMD3_GetAttributeViString")
#print(F_Prefix())

#General
#F_getNbrInst = getattr(acqiris,"Acqrs_getNbrInstruments")
F_Init = getattr(acqiris,"AqMD3_InitWithOptions")
F_Close = getattr(acqiris,"AqMD3_close")
#Configuration
F_ConfigH = getattr(acqiris,"AqMD3_SetAttributeViReal64")
F_ConfigMem = getattr(acqiris,"AqMD3_SetAttributeViInt64")
F_ConfigV = getattr(acqiris,"AqMD3_ConfigureChannel") #q
F_ConfigTrigClass = getattr(acqiris,"AqMD3_SetAttributeViInt32")
F_ConfigTrigSource1 = getattr(acqiris,"AqMD3_SetAttributeViString")
F_ConfigTrigSource2 = getattr(acqiris,"AqMD3_SetAttributeViReal64")
F_ConfigTrigSource3 = getattr(acqiris,"AqMD3_SetAttributeViInt32")
#F_ConfigMode = getattr(acqiris,"AcqrsD1_configMode")
#F_ConfigAvg = getattr(acqiris,"AcqrsD1_configAvgConfig")
#Aquisition, Processing, Reading
F_Acquire = getattr(acqiris,"AqMD3_InitiateAcquisition")
#F_Process = getattr(acqiris,"AcqrsD1_processData")
F_ForceTrig = getattr(acqiris,"AqMD3_SendSoftwareTrigger")
F_Wait = getattr(acqiris,"AqMD3_WaitForAcquisitionComplete")
F_Read = getattr(acqiris,"AqMD3_FetchWaveformInt32") #q
F_Error = getattr(acqiris,"AqMD3_GetError")
F_Info = getattr(acqiris, "AqMD3_GetAttributeViString")
F_Calibrate = getattr(acqiris, "AqMD3_SelfCalibrate")
F_AqMD3_QueryMinWaveformMemory = getattr(acqiris, "AqMD3_QueryMinWaveformMemory")

class readPar_c(Structure):
    _fields_ = [("dataType",c_int),
                ("readMode",c_int),
                ("firstSegment",c_int),
                ("nbrSegments",c_int),
                ("firstSampleInSeg",c_int),
                ("nbrSamplesInSeg",c_int),
                ("segmentOffset",c_int),
                ("dataArraySize",c_int),
                ("segDescArraySize",c_int),
                ("flags",c_int),
                ("res1",c_int),
                ("res2",c_double),
                ("res3",c_double)]
                
class dataDesc_c(Structure):
    _fields_ = [("returnedSamplesPerSeg",c_int),
                ("indexFirstPoint",c_int),
                ("sampTime",c_double),
                ("vGain",c_double),
                ("vOffset",c_double),
                ("returnedSegments",c_int),
                ("nbrAvgWforms",c_int),
                ("actualTrigLo",c_int),
                ("actualTrigHi",c_int),
                ("actualDataSize",c_int),
                ("res2",c_int),
                ("res3",c_int)
                ]
                
class segDesc_c(Structure):
    _fields_ = [("horPos",c_double),
                ("timeStampLo",c_int),
                ("timeStampHi",c_int),
                ("actualTriggers",c_int),
                ("avgOfl",c_int),
                ("avgStatus",c_int),
                ("avgMax",c_int),
                ("flags",c_int),
                ("res",c_int),
                ]

def Error(InstrID, Status):
    if Status != 0:
        tmp=c_int32(Status)
        Message = create_string_buffer(512)
        print(c_int32(sizeof(Message)))
        F_Error(InstrID, byref(tmp), c_int32(sizeof(Message)), Message)
        ErrMessage = Message.value
        print(ErrMessage)
        print("error check done")


options = c_char_p(b'Simulate=false, DriverSetup= Model=U5310A')
InstrID = c_uint32(0)
Status = c_int32(0)
print(InstrID)
print(type(InstrID))

serial = c_char_p(b'PXI2::0::0::INSTR')
Status = F_Init(resource, c_bool(True), c_bool(1), options, byref(InstrID))
Error(InstrID, Status)
print(InstrID)
print(type(InstrID))
print("init done")

N_samp = 2048
Status = F_ConfigMem(InstrID, c_char_p(''.encode('utf-8')), AQMD3_ATTR_RECORD_SIZE, c_int(N_samp))
Error(InstrID, Status)
print("config mem done")

Status = F_ConfigMem(InstrID, "", AQMD3_ATTR_NUM_RECORDS_TO_ACQUIRE, c_int(1))
Error(InstrID, Status)
print("config mem done")

Status = F_ConfigTrigClass(InstrID, b"External1", AQMD3_ATTR_TRIGGER_TYPE, AQMD3_VAL_EDGE_TRIGGER)
Error(InstrID, Status)
print("config trigclass done")

Status = F_ConfigTrigSource1(InstrID, b"", AQMD3_ATTR_ACTIVE_TRIGGER_SOURCE, b"External1")
Error(InstrID, Status)
print("config trigsource done")

Status = F_ConfigTrigSource2(InstrID, b"External1", AQMD3_ATTR_TRIGGER_LEVEL, c_double(0.1))
Error(InstrID, Status)
print("config trigsource done")

Status = F_ConfigTrigSource3(InstrID, b"External1", AQMD3_ATTR_TRIGGER_SLOPE, AQMD3_VAL_POSITIVE)
Error(InstrID, Status)
print("config trigsource done")

Status = F_ConfigTrigSource3(InstrID, b"External1", AQMD3_ATTR_TRIGGER_COUPLING, AQMD3_VAL_TRIGGER_COUPLING_DC)
Error(InstrID, Status)
print("config trigsource done")

Status = F_Calibrate(InstrID)
Error(InstrID, Status)
if Status != 0:
    print(Status)
    print('fault calibrate')
print("calibration done")

Status = F_Acquire(InstrID)
Error(InstrID, Status)
if Status != 0:
    print(Status)
    print('fault acquire')
print("acquire done")

Status = F_ForceTrig(InstrID)
Error(InstrID, Status)
print("forcetrig done")

range = c_double(1.0)
offset = c_double(0.0)
coupling = AQMD3_VAL_VERTICAL_COUPLING_DC
param = c_bool(True)
Status = F_ConfigV(InstrID, c_char_p(b'Channel1'), range, offset, coupling, param)
Error(InstrID, Status)
print("config vert done")
Status = F_ConfigV(InstrID, c_char_p(b'Channel1'), c_double(0.1), offset, AQMD3_VAL_VERTICAL_COUPLING_DC, param)
Error(InstrID, Status)
print("config vert done")
Status = F_ConfigV(InstrID, c_char_p(b'Channel2'), c_double(1), c_double(0), AQMD3_VAL_VERTICAL_COUPLING_DC, c_bool(True))
Error(InstrID, Status)
print("config vert done")

sampInt = c_double(1.0)
sampRate = c_double(c_double(1.0).value / sampInt.value)
delay = c_double(0.0)
print(InstrID)
print(type(InstrID))
Status = F_ConfigH(InstrID, c_char_p(b''), AQMD3_ATTR_TRIGGER_DELAY, delay)
Error(InstrID, Status)
print("config 1 done")

Timeout = 1000
Status = F_Wait(InstrID,c_int(Timeout))
Error(InstrID, Status)
print("wait done")

#ArrayR = c_double*(N_samp)
#dataArray = ArrayR()
pyarr = [0] * N_samp
seq = c_int16 * len(pyarr)
waveformArray = seq(*pyarr)


#dataArray = Array()

readMode = 0
segDesc = segDesc_c(0,0,0,0,0,0,0,0,0)                
readPar = readPar_c(3, readMode, 0, 1, 0, N_samp, N_samp, sizeof(waveformArray), sizeof(segDesc), 0, 0, 0)
dataDesc = dataDesc_c(0,0,0,0,0,0,0,0,0,0,0,0)

firstRecord = c_int(0)
numRecordsToRead = c_int64(1)
numPointsPerRecordToRead = c_int64(1000)
waveformArrayActualSize = c_int(0)
actualRecords = c_int(0)
actualPoints = c_int64(0)
firstValidPoint = c_int64(0)
initialXOffset = c_double(0)
initialXTimeSeconds = c_double(0)
initialXTimeFraction = c_double(0)
xIncrement = c_double(0)
scaleFactor = c_double(0)
scaleOffset = c_double(0)

sizeOfDataArray = c_int64(0)
F_AqMD3_QueryMinWaveformMemory(InstrID, c_int32(16), numRecordsToRead, c_int64(0), numPointsPerRecordToRead, byref(sizeOfDataArray))

print("sizeOfDataArray: ", sizeOfDataArray)
print(sizeOfDataArray.value)
array = (c_int16* 50000)()
print(type(array))

Data = F_Read(InstrID, b"Channel1", c_int64(sizeOfDataArray.value), array, byref(actualPoints), \
            byref(firstValidPoint), byref(initialXOffset), byref(initialXTimeSeconds), byref(initialXTimeFraction), byref(xIncrement), \
                byref(scaleFactor), byref(scaleOffset))

# Data = F_Read(InstrID, b"Channel1", c_int64(sizeOfDataArray.value), waveformArray, byref(actualPoints), \
#             byref(firstValidPoint), byref(initialXOffset), byref(initialXTimeSeconds), byref(initialXTimeFraction), byref(xIncrement), \
#                 byref(scaleFactor), byref(scaleOffset))

Error(InstrID, Status)
print("read done")
print(Data)
print(sizeOfDataArray)
#print(dataArray)
print(actualPoints)
print(firstValidPoint)
print(initialXOffset)
print(initialXTimeSeconds)
print(initialXTimeFraction)
print(xIncrement)
print(scaleFactor)
print(scaleOffset)

print(array)
print(type(array))
print(np.array(array[:]))
print(len(array))

dataArray = np.array(array[:])

print(scaleFactor.value)

dataArray = dataArray * scaleFactor.value + scaleOffset.value

# for d in array:
#     d = d * scaleFactor.value + scaleOffset.value
    
#print(dataArray) #1.78005909e-307

# print(waveformArray)
# print(type(waveformArray))
# print(np.array(waveformArray[:]))
# print(len(waveformArray))

plt.plot(dataArray)
plt.show()

#ViStatus _VI_FUNC AqMD3_FetchWaveformInt16(ViSession Vi, ViConstString ChannelName, ViInt64 WaveformArraySize, ViInt16 WaveformArray[], ViInt64* ActualPoints, 
# ViInt64* FirstValidPoint, ViReal64* InitialXOffset, ViReal64* InitialXTimeSeconds, ViReal64* InitialXTimeFraction, ViReal64* XIncrement, ViReal64* ScaleFactor, ViReal64* ScaleOffset);





#time.sleep(1)

Status = F_ConfigH(InstrID, c_char_p(b''), AQMD3_ATTR_SAMPLE_RATE, c_double(1e9))
print(Status)
Error(InstrID,Status)
print("config 2 done")
#print(AQMD3_ATTR_SAMPLE_RATE)
#print(sampRate)
#print(type(InstrID))
#print(type(c_char_p(b'')))
string = create_string_buffer(512)
Status = F_Info(InstrID, "", AQMD3_ATTR_SPECIFIC_DRIVER_PREFIX, c_int32(sizeof(string)), string)
print(string.value)
print("info done")
Status = F_Close(InstrID)
print("close done")
