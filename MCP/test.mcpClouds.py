import time
import sys
import os
from mcpClouds import McpClouds

# Set up logging
import logging
logFilename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'oMCP.log')
logger = logging.getLogger()
fhandler = logging.FileHandler(filename=logFilename, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

clouds=McpClouds()
result = clouds.isCloudy(allSkyOutput=True)
if (result):
    logger.info("Cloud detector reports True")
else:
    logger.info("Cloud detector reports False")

print("Cloud detector reports ",result)
