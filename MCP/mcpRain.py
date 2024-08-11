#############################################################################################################
## i s R A I N I N G                                                                                       ##
#############################################################################################################
# Get rain indicator from RG-11
# Using circuit and Arduino sketch from 
# https://www.cloudynights.com/topic/792701-arduino-based-rg-11-safety-monitor-for-nina-64bit/

import logging
import serial
from mcpConfig import McpConfig
import time

# Note time.sleep statements are important to ensure the serial port has time to respond
class McpRain:
    def __init__(self):
        self.config=McpConfig()
        self.port = self.config.get("RAINPORT")
        self.bps=self.config.get("RAINBPS")
        self.ser = serial.Serial(self.port,int(self.bps),timeout=1)
        time.sleep(2)
        self.logger = logging.getLogger('mcpRain')
        return
        
    def isRaining(self):
        self.ser.write(b"S#")
        time.sleep(2)
        self.ser.flush()
        time.sleep(2)
        packet=self.ser.readline()

        if (packet != b"safe#"):
            self.logger.info("Rain detected by Hydreon RG-11! ("+str(packet)+")")
            return True
        else:
            self.logger.info("Rain not detected by Hydreon RG-11. ("+str(packet)+")")
            return False
