#
# Acqiris IVI-Python AqMD3 Driver Example Program
#
# Creates a driver object, reads a few Identity interface properties, and performs a simple
# acquisition.
#
# See http://www.ivifoundation.org/resources/ for additional programming information.
#
# Runs in simulation mode without an instrument.
#
# Requires a working installation of the IVI-C driver.
#

from AqMD3 import *
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Edit resource and options as needed. Resource is ignored if option Simulate=True.
resourceString = "PXI2::0::0::INSTR"
initOptions = "Simulate=false, DriverSetup= Model=U5310A"
idquery = True
reset = True

try:
    print("IVI-Python SimpleAcquisition")
    print()

    with AqMD3( resourceString, True, True, initOptions ) as driver:
        print(driver)
        print("Driver initialized")

        # Print a few IIviDriverIdentity properties.
        #print("Driver identifier:  ", driver.Identity.Identifier)
        #print("Driver revision:    ", driver.Identity.Revision)
        #print("Driver vendor:      ", driver.Identity.Vendor)
        #print("Driver description: ", driver.Identity.Description)
        print("Instrument manufact:", driver.Identity.InstrumentManufacturer)
        print("Instrument model:   ", driver.Identity.InstrumentModel)
        print("Firmware revision:  ", driver.Identity.InstrumentFirmwareRevision)
        print("Serial number:      ", driver.InstrumentInfo.SerialNumberString)
        print("Options:            ", driver.InstrumentInfo.Options)
        print("Simulate:           ", driver.DriverOperation.Simulate)
        print()

        # Configure channel properties.
        range = 1.0
        offset = 0.0
        coupling = VerticalCoupling.DC
        print("Configuring channel properties")
        print("Range:              ", range)
        print("Offset:             ", offset)
        print("Coupling:           ", coupling)
        for channel in driver.Channels:
            print("Applying on ", channel.Name)
            channel.Configure(range, offset, coupling, True)

        # Configure the acquisition.
        numPointsPerRecord = 1000000000

        print()
        print("Configuring acquisition")
        print("Record size:        ", numPointsPerRecord)
        driver.Acquisition.RecordSize = numPointsPerRecord
        
        print("driver.Acquisition.RecordSize: ", driver.Acquisition.RecordSize)

        # Configure the trigger.
        sourceName = "External1"
        level = 0.1
        slope = TriggerSlope.Positive

        print()
        print("Configuring trigger")
        print("Active source:      ", sourceName)
        driver.Trigger.ActiveSource = sourceName
        activeTrigger = driver.Trigger.Sources[sourceName]
        print("Level:              ", level)
        activeTrigger.Level = level
        print("activeTrigger.Level:              ", activeTrigger.Level)
        print("Slope:              ", slope)
        activeTrigger.Edge.Slope = slope
        activeTrigger.Coupling = coupling
        print("Coupling:           ", coupling)

        # Calibrate the instrument.
        print()
        print("Performing self-calibration")
        driver.Calibration.SelfCalibrate()
        
        data = np.zeros(100000000)
        arr=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
        
        waveforms = []
        for k in arr:
            print(k)
            print(datetime.now().strftime("%H:%M:%S"))

            # Perform the acquisition.
            print()
            print("Performing acquisition")
            driver.Acquisition.Initiate()
            timeoutInMs = 10000
            driver.Acquisition.WaitForAcquisitionComplete(timeoutInMs)
            print("Acquisition completed")

            waveform = None
            for channel in driver.Channels:
                print()
                print("Fetching data from ", channel.Name)

                # Fetch the acquired data
                waveform = channel.Measurement.FetchWaveform(waveform)
                print("First samples:", *waveform[:10])

                print("Processing data fetched from ", channel.Name)
                # Convert data to Volts.
                
                # convertedSamples = []
                # for sampleRaw in waveform:
                #     # the same sample in volts
                #     sampleInVolts = sampleRaw * waveform.ScaleFactor + waveform.ScaleOffset
                #     convertedSamples.append(sampleInVolts)
                # data += convertedSamples
                
                # waveformNP = []
                # for sample in waveform:
                #     waveformNP.append(sample)
                # waveformNP = np.array(waveformNP)
                # waveformNP = waveformNP * waveform.ScaleFactor + waveform.ScaleOffset
                waveforms.append(waveform)
                # plt.plot(convertedSamples)
                # plt.show()
                break
        
            print("Processing completed. ")
            
        plt.plot(data)
        plt.show()

    # Automaticaly close the driver at end of with clause.
    print("Driver closed")

except RuntimeError as e:
    print( e )

print("\nDone - Press enter to exit")
print()

