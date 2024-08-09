# INDI Client Definition
import PyIndi
import sys
import logging
from mcpConfig import McpConfig
import time

class ScopeClient(PyIndi.BaseClient):
    MAXLOOPS=10
    
    def __init__(self):
        super(ScopeClient, self).__init__()
        self.logger = logging.getLogger('oMCP')
        self.config = McpConfig()
        self.device_scope=None
        self.scope_connect=None
        self.MAXLOOPS = 10
        
    # Methods for MCP
    # connect the scope
    def connectDevice(self):
        scope=self.config.get("INDITELESCOPE")
        self.device_scope=None
        self.scope_connect=None

        # get the scope device
        self.device_scope=self.getDevice(scope)
        loopCount=0
        while not(self.device_scope) and (loopCount<=self.MAXLOOPS):
            self.logger.info("Scope: Attempting to get device "+scope)
            time.sleep(0.5)
            self.device_scope=self.getDevice(scope)
            loopCount+=1
        if not(self.device_scope):
            self.logger.info("Scope: Unable to get device "+scope)
            exit(0)
        self.logger.info("Scope: Connected to device "+scope)

        # wait CONNECTION property be defined for scope
        self.scope_connect=self.device_scope.getSwitch("CONNECTION")
        loopCount=0
        while not(self.scope_connect) and (loopCount<=self.MAXLOOPS):
            time.sleep(0.5)
            self.scope_connect=self.device_scope.getSwitch("CONNECTION")
            loopCount+=1
        if not(self.scope_connect):
            self.logger.info("Scope: Unable to connect to device "+scope)
            exit(0)
        self.logger.info("Scope: Connected to device "+scope)

        # if the scope device is not connected, we do connect it
        if not(self.device_scope.isConnected()):
            self.scope_connect[0].s=PyIndi.ISS_ON  # the "CONNECT" switch
            self.scope_connect[1].s=PyIndi.ISS_OFF # the "DISCONNECT" switch
            self.sendNewSwitch(self.scope_connect) # send this new value to the device
        return True
    
    def unpark(self):
        # Open the scope
        scope_parkstatus=self.device_scope.getSwitch("SCOPE_PARK")
        while not(scope_parkstatus):
            time.sleep(0.5)
            scope_parkstatus=self.device_scope.getSwitch("SCOPE_PARK")

        scope_parkstatus[0].s=PyIndi.ISS_OFF   # the "PARK" switch
        scope_parkstatus[1].s=PyIndi.ISS_ON    # the "UNPARKED" switch
        self.sendNewSwitch(scope_parkstatus) # send this new value to the device

        scope_parkstatus=self.device_scope.getSwitch("SCOPE_PARK")
        while not(scope_parkstatus):
            time.sleep(0.5)
            scope_parkstatus=self.device_scope.getSwitch("SCOPE_PARK")

        # Wait til the scope is finished moving
        while (scope_parkstatus.getState()==PyIndi.IPS_BUSY):
            self.logger.info("Scope UnParking")
            time.sleep(2)
            
        return
            
    def park(self):
        # Close the scope
        scope_parkstatus=self.device_scope.getSwitch("SCOPE_PARK")
        while not(scope_parkstatus):
            time.sleep(0.5)
            scope_parkstatus=self.device_scope.getSwitch("SCOPE_PARK")

        scope_parkstatus[0].s=PyIndi.ISS_ON   # the "PARK" switch
        scope_parkstatus[1].s=PyIndi.ISS_OFF  # the "UNPARKED" switch
        self.sendNewSwitch(scope_parkstatus) # send this new value to the device
        scope_parkstatus=self.device_scope.getSwitch("SCOPE_PARK")
        while not(scope_parkstatus):
            time.sleep(0.5)
            scope_parkstatus=self.device_scope.getSwitch("SCOPE_PARK")

        # Wait til the scope is finished moving
        while (scope_parkstatus.getState()==PyIndi.IPS_BUSY):
            self.logger.info("Scope Parking")
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
