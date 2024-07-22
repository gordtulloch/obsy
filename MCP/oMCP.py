#!/usr/bin/env python
# -*- coding: utf-8 -*-
############################################################################################################
#
# Name        : oMCP.py
# Purpose     : The Master Control Program (nods to TRON) coordinates all recurring activities for OBSY for
#				observatory operations. A similar script runs on telescope computers to manage telescope 
#				operations
# Author      : Gord Tulloch
# Date        : July 21 2024
# License     : GPL v3
# Dependencies: Requires KStars/EKOS, DBUS, and an INDI Server local or remote
# Usage       : Run as a service
#
############################################################################################################
import time
from mcpConfig import McpConfig
from mcpSmoke  import mcpSmoke
from mcpAurora import mcpAurora

# Functions 
from oMCPFunctions import isRaining, isSun, isBadWeather

# Retrieve config
config=McpConfig()

# Set up logging
import logging
if not os.path.exists('oMCP.log'):
	logging.basicConfig(filename='oMCP.log', encoding='utf-8', level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("oMCP")

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
    
# Set up Smoke object
import mcpSmoke
smoke=McpSmoke()

# Set up Aurora object
import mcpAurora
aurora=McpAurora

############################################################################################################
#                                    M  A  I  N  L  I  N  E 
############################################################################################################
while runMCP:
	logger.info('Main loop start')
	obsyState = "Closed"
	# If it's raining or daytime, immediate shut down and wait 5 mins
	if isRaining() or isSun():
		logger.info('Daytime or rain - Closed Roof')
		obsyState = "Closed"
		#scopeClient.park()
		#domeClient.park()
		time.sleep(300)
		continue

    # If weather looks unsuitable either stay closed or move to Close Pending if Open
	if isCloudy() or isBadWeather():
		logger.info('Clouds/Weather not within parameters - Closed Roof')
		if obsyState == "Closed":
			continue
		# If Open give it PENDING minutes to change
		if obsyState == "Open":
			obsyState="Close Pending"
			pendingCount=1
		if obsyState == "Close Pending":
			pendingCount+=1
		if pendingCount == maxPending:
			obsyState="Closed"
			#scopeClient.park
			#domeClient.park()
			pendingCount=0
	else:
		# Good weather so set to Open Pending or Open
		logger.info('Clouds/Weather within parameters - Open Roof')
		if obsyState != "Open":
			obsyState="Open Pending"
			pendingCount=1
		if obsyState == "Open Pending":
			pendingCount=1
		if pendingCount==maxPending: 
			obsyState="Open"
			#domeClient.unpark()
			#scopeClient.unpark()
			pendingCount=0
   
	logger.info('Obsy state is '+obsyState)
	time.sleep(60)

############################################################################################################
# SHUTDOWN
############################################################################################################
logger.info('MCP execution terminated')
