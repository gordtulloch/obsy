#############################################################################################################
## C O N F I G                                                                                       ##
#############################################################################################################
# Object to retrieve configuration
import configparser
import os
import logging
logger = logging.getLogger('obsy.config')

class Config():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'private.ini')
        # Check if the file exists
        if not os.path.exists(self.file_path):
            logger.info("Config file not found, creating with defaults.")
            self.config['DEFAULT'] = {
                'EMAIL_BACKEND'       :   'django.core.mail.backends.smtp.EmailBackend',
                'EMAIL_HOST'          :   'smtp.gmail.com',
                'EMAIL_PORT '         :    587,
                'EMAIL_USE_TLS'       :    True,
                'EMAIL_HOST_USER '    :   'email@gmail.com',  
                'EMAIL_HOST_PASSWORD' :   'secret',  
                'SENDER_EMAIL '       :   'email@gmail.com',  
                'RECIPIENT_EMAIL'     :   'email@gmail.com', 
                'LATITUDE'            :    49.9,
                'LONGITUDE'           :   -97.1,
                'PPSOURCEPATH'        :   '/home/stellarmate/Projects/obsy/sample_data/Processing/input',
                'PPREPOPATH'          :   '/home/stellarmate/Projects/obsy/sample_data/Processing/repo',
                'TWILIO_SID'          :   'secret',
                'TWILIO_TOKEN'        :   'secret',
            }
            with open(self.file_path, 'w') as configfile:
                self.config.write(configfile)
                return      
    def get(self,keyword):
                self.config = configparser.ConfigParser()
                self.config.read(self.file_path)
                return self.config['DEFAULT'][keyword]
