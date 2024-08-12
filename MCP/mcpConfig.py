#############################################################################################################
## C O N F I G                                                                                       ##
#############################################################################################################
# Object to retrieve configuration
import configparser
import os
import logging
logger = logging.getLogger('mcpConfig')

class McpConfig():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'MCP.ini')
        # Check if the file exists
        if not os.path.exists(self.file_path):
            logger.info("Config file not found, creating with defaults.")
            self.config['DEFAULT'] = {
                'RUNMODE': 'DOME',                          # Can be MASTER, DOME, TELESCOPE, or REMOTE
                'MCPHOME': '/home/stellarmate/obsy/MCP/',   # MCP home folder
                'INDI_TELESCOPE_SERVER'	: 'localhost',      # INDI server for Telescope
    	    	'INDI_DOME_SERVER'	    : 'localhost',      # INDI server for observatory
              	'INDI_TELESCOPE_PORT'   : '7624',           # Port for Telescope
                'INDI_DOME_PORT'        : '7624',           # Port for observatory
             	'INDITELESCOPE'	: 'Telescope Simulator',    # Driver to use for telescope
                'INDIDOME'	    : 'RollOff Simulator',      # Driver to use for Observatory
                'WEATHERPORT'	: '/dev/ttyUSB1',           # Port weather station connected to
                'RAINPORT'	    : '/dev/ttyUSB0',           # Port rain detector connected to
                'LATITUDE'      : '49.8954',                # Observatory latitude
                'LONGITUDE'     : '-97.1385',               # Observatory longitude
                'EKOSHOMEPATH'  :                           # EKOS path to store schedules
                  '/home/stellarmate/Pictures/schedules/',
                'EKOSPROFILE'   : 'SPAO-PC',                # EKOS Profile to run in tMCP
                'EKOSSCHEDULE'  : 'daily.esl',              # EKOS schedule file to create
                'ALLSKY_IMAGE'  : 'latest.jpg',             # Allskycam image name (non-indi-allsky)
                'MAXAURORAKPI'  : '5.0',                    # How high can aurora kpi be before we just won't bother opening the roof?
                'ALLSKYCAM'     : 'INDI-ALLSKY',            # Can be one of INDI-ALLSKY, TJ, or NONE
                'ALLSKYCAMNO'   : '1',                      # indi-allsky camera number
                'RAINBPS'       : '9600',                   # Rain detector bps 
                'WEATHERBPS'    : '2400',                   # Weather station bps
                'MAXWIND'       : '10',                     # Max wind before closing
                'MAXAVWIND'     : '10',                     # Max average wind before closing
                'ALLSKYOUTPUT'  : 'True',                   # Output an allskycam.txt file
                'ALLSKYSAMPLING'  : 'True',                 # Create sample images from allskycam every n images
                'ALLSKYSAMPLEDIR'  : 
                  '/home/stellarmate/allskyimages',         # Directory for sample images from allskycam
                'ALLSKYSAMPLERATE'  : '10',                 # How many images to wait before sampling
            }
            with open(self.file_path, 'w') as configfile:
                self.config.write(configfile)
                return      
    def get(self,keyword):
                self.config = configparser.ConfigParser()
                self.config.read(self.file_path)
                return self.config['DEFAULT'][keyword]

