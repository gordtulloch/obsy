# filepath: /home/gtulloch/obsy.dev/obsy/config.py
#############################################################################################################
## C O N F I G                                                                                       ##
#############################################################################################################
import logging
from config.models import GeneralConfig, CommunicationsConfig, RepositoryConfig

logger = logging.getLogger('obsy.config')

class Config():
    def __init__(self):
        self.general_config = GeneralConfig.objects.first()
        self.communications_config = CommunicationsConfig.objects.first()
        self.repository_config = RepositoryConfig.objects.first()

    def get(self, key):
        if hasattr(self.general_config, key):
            return getattr(self.general_config, key)
        elif hasattr(self.communications_config, key):
            return getattr(self.communications_config, key)
        elif hasattr(self.repository_config, key):
            return getattr(self.repository_config, key)
        else:
            logger.error(f"Config key '{key}' not found.")
            return None