#!/usr/bin/env python
# -*- coding: utf-8 -*-
############################################################################################################
#
# Name        : tMCP.py
# Purpose     : The Master Control Program (nods to TRON) coordinates all recurring activities for OBSY for
#				telescope operations. A similar script runs on observatory computers to manage observatory 
#				operations
# Author      : Gord Tulloch
# Date        : July 22 2024
# License     : GPL v3
# Dependencies: Requires KStars/EKOS, DBUS, and an INDI Server local or remote
# Usage       : Run as a service
#
############################################################################################################

# A whole bunch of setup and function definition happens here
import time
import sys
from mcpObsy import McpObsy
from mcpConfig import McpConfig
from mcpEkosDbus  import EkosDbus

obsy=McpObsy()

# Suppress warnings
#warnings.filterwarnings("ignore")

# Set up logging
import logging
if not os.path.exists('tMCP.log'):
	logging.basicConfig(filename='tMCP.log', encoding='utf-8', level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("tMCP")

# Set up config
config=McpConfig()

# Check to make sure we're running the right MCP program
if (config.get('RUNMODE') !='TELESCOPE'):
    logging.error('Runmode error, tMCP execution is not permitted in runmode'+config.get('RUNMODE'))
    sys.exit(0)

# Connect the dome
from domeClient import DomeClient
domeClient=DomeClient()
domeClient.setServer(config.get("INDI_DOME_SERVER"),int(config.get("INDI_DOME_PORT")))

if (not(domeClient.connectServer())):
    logger.error("Dome: No indiserver running on "+domeClient.getHost()+":"+str(domeClient.getPort()))
    sys.exit(1)
else:
    logger.info("Dome: connected to "+domeClient.getHost()+":"+str(domeClient.getPort()))
if (not(domeClient.connectDevice())): # Connect to the Dome Device
    logger.error("Dome: No indiserver running on "+domeClient.getHost()+":"+str(domeClient.getPort()))
    sys.exit(1)

# Connect the Scope
from scopeClient import ScopeClient
scopeClient=ScopeClient()
scopeClient.setServer(config.get("INDI_SCOPE_SERVER"),int(config.get("INDI_SCOPE_PORT")))

if (not(scopeClient.connectServer())):
    logger.error("Telescope: No indiserver running on "+scopeClient.getHost()+":"+str(scopeClient.getPort()))
    sys.exit(1)
else:
    logger.info("Telescope: connected to "+scopeClient.getHost()+":"+str(scopeClient.getPort()))
if (not(domeClient.connectDevice())): # Connect to the Dome Device
    logger.error("Telescope: No indiserver running on "+scopeClient.getHost()+":"+str(scopeClient.getPort()))
    sys.exit(1)

# Ensure Ekos is running or exit
ekosDbus=EkosDbus()
ekosStartCounter=0
while not ekos_dbus.is_ekos_running():
	logger.info('DBus starting Ekos')
	ekos_dbus.start_ekos()
	time.sleep(5)
	if ekosStartCounter > 5:
		logger.error('Unable to start Ekos')
		exit(1)

############################################################################################################
#                                    M  A  I  N  L  I  N  E 
############################################################################################################
runMCP=True
while runMCP:
    # If the scope is parked nothing to do, wait ten minutes and try again
    # Dome client is reponsible for parking both Dome and Telescope 
    if scopeClient.isParked():
        time.sleep(300)
        continue
    else:
        # Any jobs to run?
        if (obsy.isJobs() > 0):
            # Download jobs into a schedule file
            if (not obsy.getSchedule(config.get("EKOSHOMEPATH")+'autoschedule.esl')):
                logger.error('Unable to get schedule file')
            else:
                # Run the daily.esl schedule
                ekosDbus.load_and_start_profile(config.get("EKOSPROFILE"))
                ekosDbus.load_schedule(config.get("EKOSHOMEPATH")+'autoschedule.esl')
                ekosDbus.start_scheduler()
                # Loop until the scope is parked by the observatory controller
                while not scopeClient.isParked():
                    time.sleep(1)
                # Shut down the schedule
                ekosDbus.stop_scheduler()

############################################################################################################
# SHUTDOWN
############################################################################################################
# Stop Ekos on the current computer
ekosDbus.stop_ekos()

logger.info('MCP execution terminated')
#cur.close()
#con.close()
