# OBSY Personal Observatory Management System
![](static/images/github-cover.png)
OBSY is an Open Source observatory management system intended for amateur astronomers who want to automate data collection in their observatories. The system forms a meta layer over the KStars/EKOS imaging and telescope control system, feeding nightly schedules to the EKOS Scheduler and capturing the results. 

NOTE THIS SOFTWARE IS IN ACTIVE DEVELOPMENT AND NO RELEASE CANDIDATE IS AVAILABLE YET.

Detailed documentation has been moved to the project Wiki.

## Features:
Release scope for the free version are as follows:
* Support for operation of remote INDI devices
* Support for automated science and astrophotography imaging using KStars/EKOS on Linux
* Automatic collection of data into data repositories including FITS file metadata
* Automated cloud detection from any allsky camera that can produce a current image on disk
* Support for rain detectors to automatically park the telescope and close the dome/roof of the observatory 
* Support for weather stations to determine if the weather is suitable for imaging operations
* Support for Smoke and Aurora forecasts to assist in determining whether imaging operations can proceed
* Automated calibration, stacking, and processing of images and generation of thumbnails or data summaries
* Integrated image viewer with FITS support

Future commercial (obsy-pro) releases will include:
* Support for multiple workload types, all from the same code base
* Master nodes for data repository, remote nodes for web sites, telescope nodes and observatory nodes. 
* Automated image transfer to master via RabbitMQ
* Live stacking and update of remote sites with current imaging activities using MQTT
* Multiuser support with authentication, plus anonymous "public" access for web sites 
* Automated processing of photometry imaging
* Automated processing of exoplanet imaging
* Automated processing of spectroheliograph captures (Sol'ex)

## Current Status
Currently working on sub-projects as follows:
* OBSY - Building user interface, handling for Target searching and selection, setup configuration tables complete. Working on automated calibration as well as scheduling and building oMCP.py and tMCP.py scripts. Testing in my backyard micro-observatory. 
* [EKOSProcessingScripts](https://github.com/gordtulloch/EKOSProcessingScripts) Scripts to use with EKOS to integrate with OBSY. For example a post-processing script that calibrates images, stores the FITS data files in a repository, and loads summary and image information into the OBSY database. (COMPLETE)
* [Photometry-Pipeline](https://github.com/gordtulloch/Photometry-Pipeline) Python script for processing of images via differential photometry (STARTED)
* [MLCloudDetect](https://github.com/gordtulloch/mlCloudDetect) Machine Learning based cloud detection for allsky cameras (COMPLETE)
* [PythonEkosFiles](https://github.com/gordtulloch/pythonEkosFiles) Python objects for reading and writing Ekos sequence and schedule files (STARTED)

## Other contributors
I stand on the shoulders of:
* **Aaron Morris** (decep on CN) - Aaron's indi-allsky has a lot of functions similar to those needed in oMCP.py so many thanks for allowing me to modify some of the code for my purposes https://github.com/aaronwmorris/indi-allsky
