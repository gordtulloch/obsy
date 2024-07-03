#!/usr/bin/env python
# -*- coding: utf-8 -*-
############################################################################################################
#
# Name        : MCP.py
# Purpose     : The Master Control Program (nods to TRON) coordinates all recurring activities for OBSY
# Author      : Gord Tulloch
# Date        : February 14 2024
# License     : GPL v3
# Dependencies: Requires KStars/EKOS, DBUS, and an INDI Server local or remote
# Usage       : Run as a service
#
############################################################################################################

# A whole bunch of setup and function definition happens here
from MCPFunctions import isRaining, isSun, isCloudy, isBadWeather, obsyOpen, obsyClose, ekos_dbus

############################################################################################################
# CONFIGURATION AND SETUP
############################################################################################################
debug			=	True
homedir			=	"/home/gtulloch/Projects/EKOSProcessingScripts/"
long			=	-97.1385
lat				=	 49.8954
runMCP			=	True
maxPending		=	5
ekosProfile		=	"NTT8"

# Suppress warnings
#warnings.filterwarnings("ignore")

# Set up database
dbName = homedir+"obsy.db"
con = sqlite3.connect(dbName)
cur = con.cursor()

# Set up logging
import logging
logger = logging.getLogger('MCP.py')
logger.basicConfig(filename='MCP.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.info('MCP starting')

# Ensure Ekos is running or exit
ekosStartCounter=0
while not ekos_dbus.is_ekos_running():
	ekos_dbus.start_ekos()
	time.sleep(5)
	if ekosStartCounter > 5:
		logger.error('Unable to start Ekos')
		exit(1)

############################################################################################################
#                                    M  A  I  N  L  I  N  E 
############################################################################################################
while runMCP:
	# If it's raining or daytime, immediate shut down and wait 5 mins
	if isRaining() or isSun():
		obsyState = "Closed"
		obsyClose()
		time.sleep(300)
		continue

    # If weather looks unsuitable either stay closed or move to Close Pending if Open
	if isCloudy() or isBadWeather():
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
			obsyClose()
			pendingCount=0
	else:
		# Good weather so set to Open Pending or Open
		if obsyState != "Open":
			obsyState="Open Pending"
			pendingCount=1
		if obsyState == "Open Pending":
			pendingCount=1
		if pendingCount==maxPending: 
			obsyState="Open"
			obsyOpen()
			pendingCount=0
   
	logger.info('Obsy state is '+obsyState)
	time.sleep(60)

############################################################################################################
# SHUTDOWN
############################################################################################################
# Stop Ekos on the current computer
ekos_dbus.stop_ekos()

logger.info('MCP execution terminated')
cur.close()
con.close()
