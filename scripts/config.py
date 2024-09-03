#############################################################################################################
## C O N F I G                                                                                       ##
#############################################################################################################
# Object to retrieve configuration
import configparser

class Config():
    def __init__(self):
        config = configparser.ConfigParser()
        file_path = "scripts.ini"
        # Check if the file exists
        if not os.path.exists(file_path):
            logger.info("Config file not found, creating with defaults.")
            config['DEFAULT'] = {
                'INDI_TELESCOPE_SERVER'	: 'localhost',
    	    	'INDI_DOME_SERVER'	    : 'localhost',
              	'INDI_TELESCOPE_PORT'   : 7624,
                'INDI_DOME_PORT'        : 7624,
             	'INDITELESCOPE'	: 'Telescope Simulator',
                'INDIDOME'	    : 'RollOff Simulator',
                'LATITUDE'      : '49.8954',
                'LONGITUDE'     : '-97.1385',
                'EKOSHOMEPATH'  : '/home/stellarmate/Pictures/schedules/',
                'EKOSPROFILE'   : 'SPAO-PC',
                'EKOSSCHEDULE'  : 'daily.esl',
            }
            with open('MCP.ini', 'w') as configfile:
                config.write(configfile)
                return      
    def get(keyword):
        with open('MCP.ini', 'w') as configfile:
                config.write(configfile)
                return config['DEFAULT'][keyword]

