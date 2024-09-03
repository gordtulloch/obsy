import os 
from mcpConfig  import McpConfig
from mcpAurora  import McpAurora

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
print("Max Aurora: "+config.get("MAXAURORAKPI"))

aurora=McpAurora()
if (aurora.isAurora()):
    print("Current Aurora is > Max")
else:
    print("Current Aurora is < Max")
