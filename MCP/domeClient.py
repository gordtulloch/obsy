# INDI Client Definition
import PyIndi
import sys, time

import logging


from mcpConfig import McpConfig

class DomeClient(PyIndi.BaseClient):
  
    def __init__(self):
        super(DomeClient, self).__init__()
        self.config = McpConfig()
        self.dome=self.config.get("INDIDOME")
        self.device_dome=None
        self.dome_connect=None
        self.MAXLOOPS=10
        self.logger = logging.getLogger('oMCP')
        
    # Methods for MCP
    # connect the dome
    def connectDevice(self):
        # get the dome device
        self.device_dome=self.getDevice(self.dome)
        loopCount=0
        while not(self.device_dome) and (loopCount<=self.MAXLOOPS):
            self.logger.info("Dome: Attempting to get device "+self.dome)
            time.sleep(0.5)
            self.device_dome=self.getDevice(self.dome)
            loopCount+=1
        if not(self.device_dome):
            self.logger.error("Dome: Unable to get device "+self.dome)
            exit(0)
        self.logger.info("Dome: Connected to device "+self.dome)

        # wait CONNECTION property be defined for dome
        self.dome_connect=self.device_dome.getSwitch("CONNECTION")
        loopCount=0
        while not(self.dome_connect) and (loopCount <= self.MAXLOOPS):
            time.sleep(0.5)
            self.dome_connect=self.device_dome.getSwitch("CONNECTION")
            loopCount+=1
        if not(self.dome_connect):
            self.logger.error("Dome: Unable to connect to device "+self.dome)
            exit(0)
        self.logger.info("Dome: Connected to device "+self.dome)

        # if the dome device is not connected, we do connect it
        if not(self.device_dome.isConnected()):
            self.dome_connect[0].s=PyIndi.ISS_ON  # the "CONNECT" switch
            self.dome_connect[1].s=PyIndi.ISS_OFF # the "DISCONNECT" switch
            self.sendNewSwitch(self.dome_connect) # send this new value to the device
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
            self.logger.info("Dome UnParking")
            time.sleep(2)
            
        return
            
    def park(self):
        # Close the dome
        dome_parkstatus=self.device_dome.getSwitch("DOME_PARK")
        while not(dome_parkstatus):
            time.sleep(0.5)
            dome_parkstatus=self.device_dome.getSwitch("DOME_PARK")

        dome_parkstatus[0].s=PyIndi.ISS_ON   # the "PARK" switch
        dome_parkstatus[1].s=PyIndi.ISS_OFF  # the "UNPARKED" switch
        self.sendNewSwitch(dome_parkstatus) # send this new value to the device
        dome_parkstatus=self.device_dome.getSwitch("DOME_PARK")
        while not(dome_parkstatus):
            time.sleep(0.5)
            dome_parkstatus=self.device_dome.getSwitch("DOME_PARK")

        # Wait til the dome is finished moving
        while (dome_parkstatus.getState()==PyIndi.IPS_BUSY):
            self.logger.info("Dome Parking")
            time.sleep(2)
            
        return
    
    # Standard INDI methods    
    def newDevice(self, d):
        '''Emmited when a new device is created from INDI server.'''
        self.logger.debug(f"new device {d.getDeviceName()}")

    def removeDevice(self, d):
        '''Emmited when a device is deleted from INDI server.'''
        self.logger.debug(f"remove device {d.getDeviceName()}")

    def newProperty(self, p):
        '''Emmited when a new property is created for an INDI driver.'''
        self.logger.debug(f"new property {p.getName()} as {p.getTypeAsString()} for device {p.getDeviceName()}")

    def updateProperty(self, p):
        '''Emmited when a new property value arrives from INDI server.'''
        self.logger.debug(f"update property {p.getName()} as {p.getTypeAsString()} for device {p.getDeviceName()}")

    def removeProperty(self, p):
        '''Emmited when a property is deleted for an INDI driver.'''
        self.logger.debug(f"remove property {p.getName()} as {p.getTypeAsString()} for device {p.getDeviceName()}")

    def newMessage(self, d, m):
        '''Emmited when a new message arrives from INDI server.'''
        self.logger.debug(f"new Message {d.messageQueue(m)}")

    def serverConnected(self):
        '''Emmited when the server is connected.'''
        self.logger.debug(f"Server connected ({self.getHost()}:{self.getPort()})")

    def serverDisconnected(self, code):
        '''Emmited when the server gets disconnected.'''
        self.logger.debug(f"Server disconnected (exit code = {code},{self.getHost()}:{self.getPort()})")
