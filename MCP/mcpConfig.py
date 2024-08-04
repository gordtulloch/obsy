#############################################################################################################
## C O N F I G                                                                                       ##
#############################################################################################################
# Object to retrieve configuration
import configparser
import os
import logging
logger = logging.getLogger('oMCP')

class McpConfig():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.file_path = "MCP.ini"
        # Check if the file exists
        if not os.path.exists(self.file_path):
            logger.info("Config file not found, creating with defaults.")
            self.config['DEFAULT'] = {
                'RUNMODE': 'DOME',                         # Can be MASTER, DOME, TELESCOPE, or REMOTE
                'MCPHOME': '/home/stellarmate/obsy/MCP/',
                'INDI_TELESCOPE_SERVER'	: 'localhost',
    	    	'INDI_DOME_SERVER'	    : 'localhost',
              	'INDI_TELESCOPE_PORT'   : 7624,
                'INDI_DOME_PORT'        : 7624,
             	'INDITELESCOPE'	: 'Telescope Simulator',
                'INDIDOME'	    : 'RollOff Simulator',
                'WEATHERPORT'	: '/dev/ttyUSB0',
                'RAINPORT'	    : '/dev/ttyUSB1',
                'LATITUDE'      : '49.8954',
                'LONGITUDE'     : '-97.1385',
                'EKOSHOMEPATH'  : '/home/stellarmate/Pictures/schedules/',
                'EKOSPROFILE'   : 'SPAO-PC',
                'EKOSSCHEDULE'  : 'daily.esl',
                'ALLSKY_IMAGE'  : 'latest.jpg',
                'MAX_AURORA_KPI': 5.0,
                'ALLSKYCAM'     : 'INDI-ALLSKY', # Can be one of INDI-ALLSKY, TJ, or NONE
                'ALLSKYCAMNO'   : '1' # indi-allsky camera number
            }
            with open('MCP.ini', 'w') as configfile:
                self.config.write(configfile)
                return      
    def get(self,keyword):
                self.config = configparser.ConfigParser()
                self.config.read(self.file_path)
                return self.config['DEFAULT'][keyword]

