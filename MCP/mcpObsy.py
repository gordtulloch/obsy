#############################################################################################################
## M C P O B S Y                                                                                           ##
#############################################################################################################
# McpObsy - functions to integrate with obsy observatory control front end

# Set up logging
import logging
logger = logging.getLogger("mcpObsy")

from mcpConfig import McpConfig

class Obsy():
    def __init__(self):
        self.config = McpConfig()

    def isJobs(self):
        return

    def getSchedule(self,filepath):
        return