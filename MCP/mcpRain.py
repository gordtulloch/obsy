#############################################################################################################
## i s R A I N I N G                                                                                       ##
#############################################################################################################
# Get rain indicator from RG-11
# Using circuit and Arduino sketch from 
# https://www.cloudynights.com/topic/792701-arduino-based-rg-11-safety-monitor-for-nina-64bit/

import logging
import serial
from mcpConfig import McpConfig

class McpRain:
    def __init__(self):
        self.config=McpConfig()
        self.port = self.config.get("RAINPORT")
        #self.port = "/dev/ttyUSB0"
        self.ser = serial.Serial(self.port,int(self.config.get("RAINBPS")),timeout=1)
        self.ser.flush()
        packet=self.ser.readline()
        self.logger = logging.getLogger('oMCP')
        return
        
    def isRaining(self):
        packet=""
        self.logger.info("Running getRain on "+self.port)
        try:  
            #self.ser.flush()
            packet=self.ser.readline()
        except Exception as msg:
            self.logger.error("getRain error: "+str(msg))

        if (packet != b"safe#"):
            self.logger.info("Rain detected by Hydreon RG-11! ("+str(packet)+")")
            return True
        else:
            self.logger.info("Rain not detected by Hydreon RG-11. ("+str(packet)+")")
            return False
