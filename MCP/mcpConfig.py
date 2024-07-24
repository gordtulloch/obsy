#############################################################################################################
## C O N F I G                                                                                       ##
#############################################################################################################
# Object to retrieve configuration
import configparser

class McpConfig():
    def __init__(self):
        config = configparser.ConfigParser()
        file_path = "MCP.ini"
        # Check if the file exists
        if not os.path.exists(file_path):
            logger.info("Config file not found, creating with defaults.")
            config['DEFAULT'] = {
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
                config.write(configfile)
                return      
    def get(keyword):
        with open('MCP.ini', 'w') as configfile:
                config.write(configfile)
                return config['DEFAULT'][keyword]

