from AqMD3 import *

resourceString = "PXI2::0::0::INSTR"
initOptions = "Simulate=false, DriverSetup= Model=U5310A"
idquery = True
reset = True

driver = AqMD3(resourceString, True, True, initOptions)
print(driver)
print("Driver initialized")
coupling = VerticalCoupling.DC
print(coupling)