# INDI Client Definition
import PyIndi
import sys, time

import logging


from mcpConfig import McpConfig

logger = logging.getLogger('domeClient')

class DomeClient(PyIndi.BaseClient):
  
    def __init__(self):
        super(DomeClient, self).__init__()
        self.config = McpConfig()
        self.dome=self.config.get("INDIDOME")
        self.device_dome=None
        self.dome_connect=None
        self.MAXLOOPS=10
        
    # Methods for MCP
    # connect the dome
    def connectDevice(self):
        # get the dome device
        self.device_dome=self.getDevice(self.dome)
        loopCount=0
        while not(self.device_dome) and (loopCount<=self.MAXLOOPS):
            logger.info("Dome: Attempting to get device "+self.dome)
            time.sleep(0.5)
            self.device_dome=self.getDevice(self.dome)
            loopCount+=1
        if not(self.device_dome):
            logger.error("Dome: Unable to get device "+self.dome)
            exit(0)
        logger.info("Dome: Connected to device "+self.dome)

        # wait CONNECTION property be defined for dome
        self.dome_connect=self.device_dome.getSwitch("CONNECTION")
        loopCount=0
        while not(self.dome_connect) and (loopCount <= self.MAXLOOPS):
            time.sleep(0.5)
            self.dome_connect=self.device_dome.getSwitch("CONNECTION")
            loopCount+=1
        if not(self.dome_connect):
            logger.error("Dome: Unable to connect to device "+self.dome)
            exit(0)
        logger.info("Dome: Connected to device "+self.dome)

        # if the dome device is not connected, we do connect it
        loopCount=0
        if not(self.device_dome.isConnected())  and (loopCount <= self.MAXLOOPS):
            self.dome_connect[0].s=PyIndi.ISS_ON  # the "CONNECT" switch
            self.dome_connect[1].s=PyIndi.ISS_OFF # the "DISCONNECT" switch
            self.sendNewSwitch(self.dome_connect) # send this new value to the device
            loopCount+=1
        if not(self.device_dome.isConnected()):
            logger.error("Dome: Unable to connect to device "+self.dome)
            exit(0)
        
        return True
    
    def unpark(self):
        # Open the dome
        dome_parkstatus=self.device_dome.getSwitch("DOME_PARK")
        while not(dome_parkstatus):
            time.sleep(0.5)
            dome_parkstatus=self.device_dome.getSwitch("DOME_PARK")

        dome_parkstatus[0].s=PyIndi.ISS_OFF   # the "PARK" switch
        dome_parkstatus[1].s=PyIndi.ISS_ON    # the "UNPARKED" switch
        self.sendNewSwitch(dome_parkstatus) # send this new value to the device

        dome_parkstatus=self.device_dome.getSwitch("DOME_PARK")
        while not(dome_parkstatus):
            time.sleep(0.5)
            dome_parkstatus=self.device_dome.getSwitch("DOME_PARK")

        # Wait til the dome is finished moving
        while (dome_parkstatus.getState()==PyIndi.IPS_BUSY):
            logger.info("Dome UnParking")
            time.sleep(2)
            
        return
            
    def park(self):
        # Close the dome
        logger.info("Dome Parking")
        dome_parkstatus=self.device_dome.getSwitch("DOME_PARK")
        loopCount=0
        while not(dome_parkstatus) and (loopCount <= self.MAXLOOPS):
            time.sleep(0.5)
            dome_parkstatus=self.device_dome.getSwitch("DOME_PARK")
            loopCount+=1
        if not(dome_parkstatus):
            logger.error("Unable to obtain Dome Park Status")
            return False

        dome_parkstatus[0].s=PyIndi.ISS_ON   # the "PARK" switch
        dome_parkstatus[1].s=PyIndi.ISS_OFF  # the "UNPARKED" switch
        self.sendNewSwitch(dome_parkstatus) # send this new value to the device

        dome_parkstatus=self.device_dome.getSwitch("DOME_PARK")
        loopCount=0
        while not(dome_parkstatus) and (loopCount <= self.MAXLOOPS):
            time.sleep(0.5)
            dome_parkstatus=self.device_dome.getSwitch("DOME_PARK")
            loopCount+=1
        if not(dome_parkstatus):
            logger.error("Unable to set Dome Park Status")
            return False
        
        # Wait til the dome is finished moving
        while (dome_parkstatus.getState()==PyIndi.IPS_BUSY) and (loopCount <= self.MAXLOOPS):
            logger.info("Dome Parking...")
            time.sleep(5)
            loopCount+=1
        if (dome_parkstatus.getState()==PyIndi.IPS_BUSY):
            logger.error("Timeout waiting for Dome park")
            return False
        
        logger.info("Dome parked successfully...")
        return True           
        
        return True
    
    # Standard INDI methods    
    def newDevice(self, d):
        '''Emmited when a new device is created from INDI server.'''
        logger.debug(f"new device {d.getDeviceName()}")

    def removeDevice(self, d):
        '''Emmited when a device is deleted from INDI server.'''
        logger.debug(f"remove device {d.getDeviceName()}")

    def newProperty(self, p):
        '''Emmited when a new property is created for an INDI driver.'''
        logger.debug(f"new property {p.getName()} as {p.getTypeAsString()} for device {p.getDeviceName()}")

    def updateProperty(self, p):
        '''Emmited when a new property value arrives from INDI server.'''
        logger.debug(f"update property {p.getName()} as {p.getTypeAsString()} for device {p.getDeviceName()}")

    def removeProperty(self, p):
        '''Emmited when a property is deleted for an INDI driver.'''
        logger.debug(f"remove property {p.getName()} as {p.getTypeAsString()} for device {p.getDeviceName()}")

    def newMessage(self, d, m):
        '''Emmited when a new message arrives from INDI server.'''
        logger.debug(f"new Message {d.messageQueue(m)}")

    def serverConnected(self):
        '''Emmited when the server is connected.'''
        logger.debug(f"Server connected ({self.getHost()}:{self.getPort()})")

    def serverDisconnected(self, code):
        '''Emmited when the server gets disconnected.'''
        logger.debug(f"Server disconnected (exit code = {code},{self.getHost()}:{self.getPort()})")
