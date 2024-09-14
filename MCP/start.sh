#!/bin/bash
# 
# Clean up log file
mv oMCP.log "logs/oMCP.$(date +"%Y_%m_%d_%I_%M_%p").log"
touch oMCP.log
#
# Run the oMCP program
source .venv/bin/activate
python oMCP.py &> /dev/null &
#
# Show the log
clear
tail -f oMCP.log
