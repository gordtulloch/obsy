############################################################################################################
## P O S T   P R O C E S S                                                               ##
############################################################################################################
# Description : This script is used to process images taken by Ekos and store them in a repository.       
# Author      : Gord Tulloch
# Date        : October 25 2024
# TODO:
#      - Add support for non-FITS images like JPG and TIFF Exif data
#      - Add support for other databases like MySQL
#      - Calibrate image prior to storing and stacking it (master dark/flat/bias)
#      - Add support for GCS storage
#      - Email summary of processing to user
############################################################################################################ 
import os
from astropy.io import fits
import sqlite3
import shutil
import uuid
from math import cos,sin
from pathlib import Path
from datetime import datetime
from config import Config

DEBUG=False
VERSION="0.1"

# Set up logging
import logging
logFilename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'scripts.log')
logger = logging.getLogger()
fhandler = logging.FileHandler(filename=logFilename, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.INFO)
logger.info("Program Start - Obsy PostProcessing Program "+VERSION)


class PostProcess(object):
    def __init__(self):
        logging.info("Initializing Post Processing object")
        self.config=Config()
        self.repoStore = self.config.get("REPOSTORE")
        self.sourceFolder=self.config.get("SOURCEPATH")
        self.fileRepoFolder=self.config.get("REPOPATH")
        self.dbName = self.config.get("DBPATH")
        self.con = sqlite3.connect(self.dbName)
        self.cur = self.con.cursor()
        if DEBUG:
            # Clear the tables
            sqlstmt="DELETE from observations_fitsHeader where 1;"
            self.cur.execute(sqlstmt)
            self.con.commit()
            sqlstmt="DELETE from observations_fitsFile where 1;"
            self.cur.execute(sqlstmt)
            self.con.commit()

    # Function definitions
    def submitFileToDB(self,fileName,hdr):
        con = sqlite3.connect(self.dbName)
        cur = con.cursor()
        if "DATE-OBS" in hdr:
            uuidStr=uuid.uuid4()
            sqlStmt="INSERT INTO observations_fitsFile (fitsFileId, fitsFileName,fitsFileDate) VALUES ('{0}','{1}','{2}')".format(uuidStr,fileName,hdr["DATE-OBS"])
            try:
                self.cur.execute(sqlStmt)
                self.con.commit()
            except sqlite3.Error as er:
                logging.error('SQLite error: %s' % (' '.join(er.args)))
                logging.error("Exception class is: ", er.__class__)
                logging.error('SQLite traceback: ')           

            for card in hdr:
                if type(hdr[card]) not in [bool,int,float]:
                    keywordValue=str(hdr[card]).replace('\'',' ')
                else:
                    keywordValue = hdr[card]
                sqlStmt="INSERT INTO observations_fitsHeader (fitsHeaderId, fitsFileId_id, fitsHeaderKey, fitsHeaderValue) VALUES ('{0}','{1}','{2}','{3}')".format(uuid.uuid4(),uuidStr,card,keywordValue)
                try:
                    self.cur.execute(sqlStmt)
                    self.con.commit()
                except sqlite3.Error as er:
                    logging.error('SQLite error: %s' % (' '.join(er.args)))
                    logging.error("Exception class is: ", er.__class__)
        else:
            logging.error("Error: File not added to repo due to missing date is "+fileName)
            return False
        return True

    def processImage(self):
        # Scan the pictures folder
        logging.info("Processing images in "+self.sourceFolder)
        for root, dirs, files in os.walk(os.path.abspath(self.sourceFolder)):
            for file in files:
                logging.info("Processing file "+os.path.join(root, file))
                file_name, file_extension = os.path.splitext(os.path.join(root, file))

                # Ignore everything not a *fit* file
                if "fit" not in file_extension:
                    logger.info("Ignoring file "+os.path.join(root, file)+" with extension -"+file_extension+"-")
                    continue

                try:
                    hdul = fits.open(os.path.join(root, file), mode='update')
                except ValueError as e:
                    logging.warning("Invalid FITS file. File not processed is "+str(os.path.join(root, file)))
                    continue   
        
                hdr = hdul[0].header
                if "FRAME" in hdr:
                    # Create an os-friendly date
                    try:
                        if "DATE-OBS" not in hdr:
                            logging.warning("No DATE-OBS card in header. File not processed is "+str(os.path.join(root, file)))
                            continue
                        datestr=hdr["DATE-OBS"].replace("T", " ")
                        datestr=datestr[0:datestr.find('.')]
                        dateobj=datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
                        fitsDate=dateobj.strftime("%Y%m%d%H%M%S")
                    except ValueError as e:
                        logging.warning("Invalid date format in header. File not processed is "+str(os.path.join(root, file)))
                        continue

                    # Create a new standard name for the file based on what it is
                    if (hdr["FRAME"]=="Light"):
                        # Adjust the WCS for the image
                        if "CD1_1" not in hdr:
                            if "CDELT1" in hdr:
                                fitsCDELT1=float(hdr["CDELT1"])
                                fitsCDELT2=float(hdr["CDELT2"])
                                fitsCROTA2=float(hdr["CROTA2"])
                                fitsCD1_1 =  fitsCDELT1 * cos(fitsCROTA2)
                                fitsCD1_2 = -fitsCDELT2 * sin(fitsCROTA2)
                                fitsCD2_1 =  fitsCDELT1 * sin (fitsCROTA2)
                                fitsCD2_2 = fitsCDELT2 * cos(fitsCROTA2)
                                hdr.append(('CD1_1', str(fitsCD1_1), 'Adjusted via MCP'), end=True)
                                hdr.append(('CD1_2', str(fitsCD1_2), 'Adjusted via MCP'), end=True)
                                hdr.append(('CD2_1', str(fitsCD2_1), 'Adjusted via MCP'), end=True)
                                hdr.append(('CD2_2', str(fitsCD2_2), 'Adjusted via MCP'), end=True)
                                hdul.flush()  # changes are written back to original.fits
                            else:
                                logging.warning("No WCS information in header, file not updated is "+str(os.path.join(root, file)))

                        # Assign a new name
                        if ("OBJECT" in hdr):
                            if ("FILTER" in hdr):
                                newName="{0}-{1}-{2}-{3}-{4}-{5}s-{6}x{7}-t{8}.fits".format(hdr["OBJECT"].replace(" ", "_"),hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                            hdr["INSTRUME"].replace(" ", "_"),hdr["FILTER"],fitsDate,hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["CCD-TEMP"])
                            else:
                                newName=newName="{0}-{1}-{2}-{3}-{4}-{5}s-{6}x{7}-t{8}.fits".format(hdr["OBJECT"].replace(" ", "_"),hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                            hdr["INSTRUME"].replace(" ", "_"),"OSC",fitsDate,hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["CCD-TEMP"])
                        else:
                            logging.warning("Invalid object name in header. File not processed is "+str(os.path.join(root, file)))
                            continue
                    elif hdr["FRAME"]=="Flat":
                        if ("FILTER" in hdr):
                            newName="{0}-{1}-{2}-{3}-{4}-{5}s-{6}x{7}-t{8}.fits".format(hdr["FRAME"],hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                            hdr["INSTRUME"].replace(" ", "_"),hdr["FILTER"],fitsDate,hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["CCD-TEMP"])
                        else:
                            newName=newName="{0}-{1}-{2}-{3}-{4}-{5}s-{6}x{7}-t{8}.fits".format(hdr["FRAME"],hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                            hdr["INSTRUME"].replace(" ", "_"),"OSC",fitsDate,hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["CCD-TEMP"])
                    elif hdr["FRAME"]=="Dark" or hdr["FRAME"]=="Bias":
                        newName="{0}-{1}-{1}-{2}-{3}s-{4}x{5}-t{6}.fits".format(hdr["FRAME"],hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                            hdr["INSTRUME"].replace(" ", "_"),fitsDate,hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["CCD-TEMP"])
                    else:
                        logging.warning("File not processed as FRAME not recognized: "+str(os.path.join(root, file)))
                    hdul.close()

                    # Create the folder structure (if needed)
                    fitsDate=dateobj.strftime("%Y%m%d")
                    if (hdr["FRAME"]=="Light"):
                        newPath=self.fileRepoFolder+"Light/{0}/{1}/{2}/{3}/".format(hdr["OBJECT"].replace(" ", ""),hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                            hdr["INSTRUME"].replace(" ", "_"),fitsDate)
                    elif hdr["FRAME"]=="Dark":
                        newPath=self.fileRepoFolder+"Calibrate/{0}/{1}/{2}/{3}/{4}/".format(hdr["FRAME"],hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                            hdr["INSTRUME"].replace(" ", "_"),hdr["EXPTIME"],fitsDate)
                    elif hdr["FRAME"]=="Flat":
                        if ("FILTER" in hdr):
                            newPath=self.fileRepoFolder+"Calibrate/{0}/{1}/{2}/{3}/{4}/".format(hdr["FRAME"],hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                            hdr["INSTRUME"].replace(" ", "_"),hdr["FILTER"],fitsDate)
                        else:
                            newPath=self.fileRepoFolder+"Calibrate/{0}/{1}/{2}/{3}/{4}/".format(hdr["FRAME"],hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                            hdr["INSTRUME"].replace(" ", "_"),"OSC",fitsDate)
                    elif hdr["FRAME"]=="Bias":
                        newPath=self.fileRepoFolder+"Calibrate/{0}/{1}/{2}/{3}/".format(hdr["FRAME"],hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                            hdr["INSTRUME"].replace(" ", "_"),fitsDate)

                    if not os.path.isdir(newPath):
                        os.makedirs (newPath)

                    # If we can add the file to the database move it to the repo
                    if (self.submitFileToDB(newPath+newName.replace(" ", "_"),hdr)):
                        moveInfo="Moving {0} to {1}\n".format(os.path.join(root, file),newPath+newName)
                        logging.info(moveInfo)
                        shutil.move(os.path.join(root, file),newPath+newName)
                    else:
                        logging.warning("Warning: File not added to repo is "+str(os.path.join(root, file)))
                else:
                    logging.warning("File not added to repo - no FRAME card - "+str(os.path.join(root, file)))
    
    
if __name__ == "__main__":
    postProcess=PostProcess()
    config=Config()
    source=config.get("SOURCEPATH")
    if (config.get("REPOSTORE")=="GCS"):
        logging.info("Processing images with GCS from "+source)
        logging.error("GCS not implemented yet")
    elif (config.get("REPOSTORE")=="File"):
        logging.info("Processing images with File Processing from "+source)
        postProcess.processImage()
    logging.info("Finished processing images")
    exit(0)