############################################################################################################
#
# Name        : postProcess.py
# Purpose     : Script to call after an image is taken to give it a standard name, add it to an index 
#               database, and move it to a repository
# Author      : Gord Tulloch
# Date        : January 25 2024
# License     : GPL v3
# Dependencies: Imagemagick and SIRIL needs to be install for live stacking
#               Tested with EKOS, don't know if it'll work with other imaging tools 
# Usage       : This script could be run after an image (single image) or after a sequence if live stacking  
#               is also being run
# TODO:
#      - Calibrate image prior to storing and stacking it (master dark/flat/bias)
#
############################################################################################################ 
import os
from astropy.io import fits
import logging
import sqlite3
import shutil
import uuid
from pathlib import Path
from datetime import datetime
from config import Config

DEBUG=True
# Set up logging
import logging
if not os.path.exists('postProcess.log'):
	logging.basicConfig(filename='postProcess.log', encoding='utf-8', level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("postProcess")

# Retrieve config
config=Config()

# Function definitions
def submitFile(fileName, hdr):
    if "DATE-OBS" in hdr:
        uuidStr=uuid.uuid4()
        sqlStmt="INSERT INTO fitsFile (unid, date, filename) VALUES ('{0}','{1}','{2}')".format(uuidStr,hdr["DATE-OBS"],fileName)

        try:
            cur.execute(sqlStmt)
            con.commit()
        except sqlite3.Error as er:
            logging.error('SQLite error: %s' % (' '.join(er.args)))
            logging.error("Exception class is: ", er.__class__)
            logging.error('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            logging.error(traceback.format_exception(exc_type, exc_value, exc_tb))
            
        for card in hdr:
            if type(hdr[card]) not in [bool,int,float]:
                keywordValue=str(hdr[card]).replace('\'',' ')
            else:
                keywordValue = hdr[card]
            sqlStmt="INSERT INTO fitsHeader (thisUNID, parentUNID, keyword, value) VALUES ('{0}','{1}','{2}','{3}')".format(uuid.uuid4(),uuidStr,card,keywordValue)

            try:
                cur.execute(sqlStmt)
                con.commit()
            except sqlite3.Error as er:
                logging.error('SQLite error: %s' % (' '.join(er.args)))
                logging.error("Exception class is: ", er.__class__)
                logging.error('SQLite traceback: ')
                exc_type, exc_value, exc_tb = sys.exc_info()
                logging.error(traceback.format_exception(exc_type, exc_value, exc_tb))
    else:
        logging.error("Error: File not added to repo due to missing date is "+fileName)
        return 0
    
    return 1

def createTables():
    #if DEBUG:
    #    cur.execute("DROP TABLE if exists fitsFile")
    #    cur.execute("DROP TABLE if exists fitsHeader")
    cur.execute("CREATE TABLE if not exists fitsFile(unid, date, filename)")
    cur.execute("CREATE TABLE if not exists fitsHeader(thisUNID, parentUNID, keyword, value)")
    return

# Variable Declarations paths must have trailing /!
sourceFolder="K:/Astronomy/00 Telescope Data/SPAO/"
repoFolder="D:/Dropbox/Astronomy/00 Data Repository/"
dbName = repoFolder+"obsy.db"

# Set up Database
con = sqlite3.connect(dbName)
cur = con.cursor()
createTables()

# Set up logging
logging.basicConfig(level=logging.DEBUG,filename='postProcess.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.info('Started')

# Scan the pictures folder
for root, dirs, files in os.walk(os.path.abspath(sourceFolder)):
    for file in files:
        file_name, file_extension = os.path.splitext(os.path.join(root, file))
        # Ignore everything not a *fit* file
        if "fit" not in file_extension:
            logging.warning("Invalid FITS extension ("+file_extension+"). File not processed is "+str(os.path.join(root, file)))
            continue

        try:
            hdul = fits.open(os.path.join(root, file))
        except ValueError as e:
            logging.warning("Invalid FITS file. File not processed is "+str(os.path.join(root, file)))
            continue   
        
        hdr = hdul[0].header

        if "FRAME" in hdr:
            print(os.path.join(root, file))

            # Create an os-friendly date
            if not "DATE-OBS" in hdr.keys():
                logging.info("Missing date element in header. File not processed is "+str(os.path.join(root, file)))
                continue
            try:
                datestr=hdr["DATE-OBS"].replace("T", " ")
                datestr=datestr[0:datestr.find('.')]
                dateobj=datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
                fitsDate=dateobj.strftime("%Y%m%d%H%M%S")
            except ValueError as e:
                logging.info("Invalid date format in header. File not processed is "+str(os.path.join(root, file)))
                if DEBUG:
                    print("Invalid date format in header. File not processed is "+str(os.path.join(root, file)))
                continue
            # 
            if not "FILTER" in hdr.keys():
                filterName="OSC"
            else:
                filterName=hdr["FILTER"]

            # Create a new standard name for the file based on what it is
            if (hdr["FRAME"]=="Light"):
                if ("OBJECT" in hdr):
                    newName=newName="{0}-{1}-{2}-{3}s-{4}x{5}-t{6}.fits".format(hdr["OBJECT"].replace(" ", ""),filterName,fitsDate,hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["CCD-TEMP"])
                else:
                    logging.warning("Invalid object name in header. File not processed is "+str(os.path.join(root, file)))
                    continue
            elif hdr["FRAME"]=="Flat":
                newName="{0}-{1}-{2}s-{3}-{4}x{5}-t{6}.fits".format(hdr["FRAME"],filterName,fitsDate,hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["CCD-TEMP"])
            elif hdr["FRAME"]=="Dark" or hdr["FRAME"]=="Bias":
                newName="{0}-{1}-{2}s-{3}x{4}-t{5}.fits".format(hdr["FRAME"],fitsDate,hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["CCD-TEMP"])
            else:
                logging.warning("File not processed as FRAME not recognized: "+str(os.path.join(root, file)))
            hdul.close()

            # Create the folder structure (if needed)
            fitsDate=dateobj.strftime("%Y%m%d")
            if (hdr["FRAME"]=="Light"):
                newPath=repoFolder+"Light/{0}/{1}/{2}/".format(hdr["OBJECT"].replace(" ", ""),fitsDate,filterName)
            elif hdr["FRAME"]=="Dark":
                newPath=repoFolder+"Calibrate/{0}/{1}/{2}x{3}/{4}/".format(hdr["FRAME"],hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],fitsDate)
            elif hdr["FRAME"]=="Flat":
                newPath=repoFolder+"Calibrate/{0}/{1}/{2}x{3}/{4}/".format(hdr["FRAME"],filterName,hdr["XBINNING"],hdr["YBINNING"],fitsDate)
            elif hdr["FRAME"]=="Bias":
                newPath=repoFolder+"Calibrate/{0}/{1}x{2}/{3}/".format(hdr["FRAME"],hdr["XBINNING"],hdr["YBINNING"],fitsDate)

            if not os.path.isdir(newPath):
                os.makedirs (newPath)

            # If we can add the file to the database move it to the repo
            if (submitFile(newPath+newName.replace(" ", ""),hdr)):
                moveInfo="Moving {0} to {1}\n".format(os.path.join(root, file),newPath+newName)
                logging.info(moveInfo)
                shutil.move(os.path.join(root, file),newPath+newName)
            else:
                logging.warning("Warning: File not added to repo is "+str(os.path.join(root, file)))
        else:
            logging.warning("File not added to repo - no FRAME card - "+str(os.path.join(root, file)))

logging.info('Finished')