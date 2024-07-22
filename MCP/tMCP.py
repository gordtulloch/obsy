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
from mcpConfig import McpConfig
from mcpEkosDbus  import EkosDbus

runMCP			=	True

# Suppress warnings
#warnings.filterwarnings("ignore")

# Set up config
config=McpConfig()

# Set up logging
import logging
if not os.path.exists('tMCP.log'):
	logging.basicConfig(filename='tMCP.log', encoding='utf-8', level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("tMCP")

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
while runMCP:
	# If it's raining or daytime, immediate shut down and wait 5 mins
	if isRaining() or isSun():
		logger.info('Daytime or rain - Closed Roof')
		obsyState = "Closed"
		#obsyClose()
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
#			obsyClose()
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
#			obsyOpen()
			pendingCount=0
   
	logger.info('Obsy state is '+obsyState)
	time.sleep(60)

############################################################################################################
# SHUTDOWN
############################################################################################################
# Stop Ekos on the current computer
#ekos_dbus.stop_ekos()

logger.info('MCP execution terminated')
#cur.close()
#con.close()
