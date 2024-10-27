#############################################################################################################
## C O N F I G                                                                                       ##
#############################################################################################################
# Object to retrieve configuration
import configparser
import os

import logging
logger = logging.getLogger('config')

class Config():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'scripts.ini')
        # Check if the file exists
        if not os.path.exists(self.file_path):
            logger.info("Config file not found, creating with defaults.")
            self.config['DEFAULT'] = {
                'REPOSTORE'     : 'File',   # File or GCS for Google Cloud Storage
                'SOURCEPATH'	: '/home/gtulloch/Dropbox/Astronomy/',
                'REPOPATH'	    : '/home/gtulloch/REPOSITORY/',
                'DBPATH'	    : '/home/gtulloch/obsy/db.sqlite3',
                }
            with open(self.file_path, 'w') as configfile:
                self.config.write(configfile)
                return      
    def get(self,keyword):
                self.config = configparser.ConfigParser()
                self.config.read(self.file_path)
                return self.config['DEFAULT'][keyword]
