# INDI Client Definition
import PyIndi
import sys

class ScopeClient(PyIndi.BaseClient):
    MAXLOOPS=10
    tries=0
    
    def __init__(self):
        super(domeClient, self).__init__()
        
    # Methods for MCP
    # connect the dome
    def connectDevice():
        dome=config.get("INDIDOME")
        device_dome=None
        dome_connect=None

        # get the dome device
        device_dome=domeClient.getDevice(dome)
        tries=0
        while not(device_dome) and (tries<=MAPLOOPS):
            logger.info("Dome: Attempting to get device "+dome)
            time.sleep(0.5)
            device_dome=domeClient.getDevice(dome)
            tries+=1
        logger.info("Dome: Connected to device "+dome)

        # wait CONNECTION property be defined for dome
        dome_connect=device_dome.getSwitch("CONNECTION")
        while not(dome_connect):
            time.sleep(0.5)
            dome_connect=device_dome.getSwitch("CONNECTION")
        logger.info("Dome: Connected to device "+dome)

        # if the dome device is not connected, we do connect it
        if not(device_dome.isConnected()):
            dome_connect[0].s=PyIndi.ISS_ON  # the "CONNECT" switch
            dome_connect[1].s=PyIndi.ISS_OFF # the "DISCONNECT" switch
            domeClient.sendNewSwitch(dome_connect) # send this new value to the device
        return True
    
    def unpark():
        # Open the dome
        dome_parkstatus=device_dome.getSwitch("DOME_PARK")
        while not(dome_parkstatus):
            time.sleep(0.5)
            dome_parkstatus=device_dome.getSwitch("DOME_PARK")

        dome_parkstatus[0].s=PyIndi.ISS_OFF   # the "PARK" switch
        dome_parkstatus[1].s=PyIndi.ISS_ON    # the "UNPARKED" switch
        domeClient.sendNewSwitch(dome_parkstatus) # send this new value to the device

        dome_parkstatus=device_dome.getSwitch("DOME_PARK")
        while not(dome_parkstatus):
            time.sleep(0.5)
            dome_parkstatus=device_dome.getSwitch("DOME_PARK")

        # Wait til the dome is finished moving
        while (dome_parkstatus.getState()==PyIndi.IPS_BUSY):
            logger.info("Dome UnParking")
            time.sleep(2)
            
        return
            
    def park():
        # Close the dome
        dome_parkstatus=device_dome.getSwitch("DOME_PARK")
        while not(dome_parkstatus):
            time.sleep(0.5)
            dome_parkstatus=device_dome.getSwitch("DOME_PARK")

        dome_parkstatus[0].s=PyIndi.ISS_ON   # the "PARK" switch
        dome_parkstatus[1].s=PyIndi.ISS_OFF  # the "UNPARKED" switch
        domeClient.sendNewSwitch(dome_parkstatus) # send this new value to the device
        dome_parkstatus=device_dome.getSwitch("DOME_PARK")
        while not(dome_parkstatus):
            time.sleep(0.5)
            dome_parkstatus=device_dome.getSwitch("DOME_PARK")

        # Wait til the dome is finished moving
        while (dome_parkstatus.getState()==PyIndi.IPS_BUSY):
            logger.info("Dome Parking")
            time.sleep(2)
            
        return
    
    # Standard INDI methods    
    def newDevice(self, d):
        pass
    def newProperty(self, p):
        pass
    def removeProperty(self, p):
        pass
    def newSwitch(self, svp):
        pass
    def newNumber(self, nvp):
        pass
    def newText(self, tvp):
        pass
    def newLight(self, lvp):
        pass
    def newMessage(self, d, m):
        pass
    def serverConnected(self):
        pass
    def serverDisconnected(self, code):
        pass