import time
import sys
import os
from mcpRain import McpRain

# Set up logging
import logging
logFilename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'oMCP.log')
logger = logging.getLogger()
fhandler = logging.FileHandler(filename=logFilename, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

rain=McpRain()
result = rain.isRaining()
if result==b'':
    logger.error("Rain detector: No Data")
    print("Rain detector reports no data.")
if (result):
    logger.info("Rain detector reports True")
else:
    logger.info("Rain detector reports False")

print("Rain detector reports ",result)