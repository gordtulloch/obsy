import time
import sys
import os


from mcpConfig  import McpConfig
from mcpWeather  import McpWeather
# Set up logging
import logging
logFilename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'oMCP.log')
logger = logging.getLogger()
fhandler = logging.FileHandler(filename=logFilename, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

# Retrieve config
config=McpConfig()
print("Weather port: "+config.get("WEATHERPORT"))
print("Weather bps: "+config.get("WEATHERBPS"))

weather=McpWeather()
if (weather.isBadWeather()):
    print("Weather is bad")
else:
    print("Weather is ok")
