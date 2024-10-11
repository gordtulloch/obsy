import logging
from django.conf import settings

class ServerStartHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        with open('/home/gtulloch/obsy/obsy.log', 'a') as log_file:
            log_file.write(log_entry + '\n')

# Function to log the server start title
def log_server_start_title():
    logger = logging.getLogger('obsy.custom_logging')
    version = settings.VERSION
    logger.info(f'--- Server Started: Obsy (Version {version}) by Gord Tulloch https://github.com/gordtulloch/obsy ---')