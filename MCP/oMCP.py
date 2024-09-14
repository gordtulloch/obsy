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
import sys
import os
from mcpConfig import McpConfig
from mcpSmoke  import McpSmoke
from mcpAurora import McpAurora
from mcpClouds import McpClouds
from mcpRain   import McpRain
from mcpSun	   import McpSun
from mcpWeather import McpWeather

# Set up logging
import logging
logFilename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'oMCP.log')
logger = logging.getLogger()
fhandler = logging.FileHandler(filename=logFilename, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.INFO)
logger.info("Program Start - oMCP Obsy Master Control Program v0.1")

# Retrieve config
config=McpConfig()

# Check to make sure we're running the right MCP program
if (config.get('RUNMODE') !='DOME'):
    logging.error('Runmode error, oMCP execution is not permitted in runmode'+config.get('RUNMODE'))
    sys.exit(0)

# Connect the dome
from domeClient import DomeClient
domeClient=DomeClient()
domeClient.setServer(config.get("INDI_DOME_SERVER"),int(config.get("INDI_DOME_PORT")))

if (not(domeClient.connectServer())):
    logger.error("Dome: No indiserver running on "+domeClient.getHost()+":"+str(domeClient.getPort())+" exiting...")
    sys.exit(1)
else:
    logger.info("Dome: connected to "+domeClient.getHost()+":"+str(domeClient.getPort()))

if (not(domeClient.connectDevice())): # Connect to the Dome Device
    logger.error("Dome: Unable to connect to dome device, exiting...")
    sys.exit(1)

# Connect the Scope
from scopeClient import ScopeClient
scopeClient=ScopeClient()
scopeClient.setServer(config.get("INDI_TELESCOPE_SERVER"),int(config.get("INDI_TELESCOPE_PORT")))

if (not(scopeClient.connectServer())):
    logger.error("Telescope: No indiserver running on "+scopeClient.getHost()+":"+str(scopeClient.getPort()))
    sys.exit(1)
else:
    logger.info("Telescope: connected to "+scopeClient.getHost()+":"+str(scopeClient.getPort()))
if (not(scopeClient.connectDevice())): # Connect to the Scope Device
    logger.error("Telescope: Unable to connect to device, exiting...")
    sys.exit(1)
    
# Set up objects with various detectors
smoke=McpSmoke()
aurora=McpAurora()
clouds=McpClouds()
rain=McpRain()
sun=McpSun()
weather=McpWeather()

############################################################################################################
#                                    M  A  I  N  L  I  N  E 
############################################################################################################
runMCP=True
logger.info('Main loop start')
obsyState = "Closed"
maxPending=10
pendingCount=0

while runMCP:
	# If it's raining or daytime, immediate shut down and wait 5 mins
	if rain.isRaining() or sun.isDaytime():
		logger.info('Daytime or rain - Closed Roof')
		if (config.get('ALLSKYOUTPUT') == 'True'):
			filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'allskycam.txt')
			f = open(filename, "w")
			f.write("Closed\nDaytime/Rain")
			f.close()
		obsyState = "Closed"
		logger.info('Confirming telescope park')
		scopeClient.park()
		logger.info('Confirming roof park')
		domeClient.park()
		logger.info('Waiting for 5m to check again...')
		time.sleep(300)
		continue

    # If conditions look unsuitable either stay closed or move to Close Pending if Open
	isClouds,cloudResult=clouds.isCloudy(config.get("ALLSKYSAMPLING"))
	if isClouds or weather.isBadWeather() or aurora.isAurora():
		logger.info('Clouds/Weather not within parameters - Close Roof')
		if obsyState == "Closed":
			logger.info('Obsy state is '+obsyState)
			logger.info('Confirming telescope park')
			scopeClient.park()
			logger.info('Confirming roof park')
			domeClient.park()

		# If Open give it PENDING minutes to change
		if obsyState == "Open":
			obsyState="Close Pending"
			pendingCount=1
			logger.info('Obsy state is '+obsyState)
			logger.info('Waiting for 1m...')

		if obsyState == "Close Pending":
			pendingCount+=1
			logger.info('Obsy state is '+obsyState)
			logger.info('Waiting for 1m...')

		if pendingCount == maxPending:
			obsyState="Closed"
			if not(scopeClient.park()):
				logger.error("Unable to confirm telescope park!")
			if not(domeClient.park()):
				logger.error("Unable to confirm dome park!")
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
			domeClient.unpark()
			scopeClient.unpark()
			pendingCount=0
   
	logger.info('Obsy state is '+obsyState)

	# If Allskyoutput is turned on send results to allskycam.txt
	if (config.get("ALLSKYOUTPUT")):
		f = open("allskycam.txt", "w")
		f.write(cloudResult+'\n'+obsyState)
		f.close()
	logger.info('Waiting for 1m...')
	time.sleep(60)

############################################################################################################
# SHUTDOWN
############################################################################################################
logger.info('MCP execution terminated')
