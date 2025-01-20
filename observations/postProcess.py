############################################################################################################
## P O S T P R O C E S S                                                                                  ##
############################################################################################################
# Functions to import fits file data into the database while renaming files and moving them to a repository, 
# calibrate images, create thumbnails linked to test stacks, and send the user an email with a summary of 
# the work done.
#
from obsy import config
from observations.models import fitsFile,fitsSequence
from django.utils import timezone
from django.db import IntegrityError
from django.http import HttpResponse

from datetime import datetime,timedelta
import numpy as np
import matplotlib.pyplot as plt
import uuid
import os
from math import cos,sin 
from astropy.io import fits
import shutil
import pytz

from obsy.config import Config

import logging
logging=logging.getLogger(__name__)

################################################################################################################
## PostProcess - all the functions needed to import fits file data into the database while renaming files and ##
## moving them to a repository, calibrate images, create thumbnails linked to test stacks, and send the user  ##
## an email with a summary of the work done.                                                                  ##
################################################################################################################
class PostProcess(object):
    def __init__(self):
        self.config = Config()
        self.sourceFolder=self.config.get('ppsourcepath')
        self.repoFolder=self.config.get('pprepopath')
        logging.info("Post Processing object initialized")

    #################################################################################################################
    ## submitFileToDB - this function submits a fits file to the database                                          ##
    #################################################################################################################
    def submitFileToDB(self,fileName,hdr):
        if "DATE-OBS" in hdr:
            # Create new fitsFile record
            if "OBJECT" in hdr:
                newfile=fitsFile(fitsFileName=fileName,fitsFileDate=hdr["DATE-OBS"],fitsFileType=hdr["FRAME"],
                            fitsFileObject=hdr["OBJECT"],fitsFileExpTime=hdr["EXPTIME"],fitsFileXBinning=hdr["XBINNING"],
                            fitsFileYBinning=hdr["YBINNING"],fitsFileCCDTemp=hdr["CCD-TEMP"],fitsFileTelescop=hdr["TELESCOP"],
                            fitsFileInstrument=hdr["INSTRUME"],
                            fitsFileSequence=None)
            else:
                newfile=fitsFile(fitsFileName=fileName,fitsFileDate=hdr["DATE-OBS"],fitsFileType=hdr["FRAME"],
                            fitsFileExpTime=hdr["EXPTIME"],fitsFileXBinning=hdr["XBINNING"],
                            fitsFileYBinning=hdr["YBINNING"],fitsFileCCDTemp=hdr["CCD-TEMP"],fitsFileTelescop=hdr["TELESCOP"],
                            fitsFileInstrument=hdr["INSTRUME"],
                            fitsFileSequence=None)
            newfile.save()
            return newfile.fitsFileId
        else:
            logging.error("Error: File not added to repo due to missing date is "+fileName)
            return None
        return True

    #################################################################################################################
    ## registerFitsImage - this functioncalls a function to registers each fits files in the database              ##
    ## and also corrects any issues with the Fits header info (e.g. WCS)                                           ##
    #################################################################################################################
    # Note: Movefiles means we are moving from a source folder to the repo, otherwise we are syncing the repo database
    def registerFitsImage(self,root,file,moveFiles):
        newFitsFileId=None
        file_name, file_extension = os.path.splitext(os.path.join(root,file))

        # Ignore everything not a *fit* file
        if "fit" not in file_extension:
            logging.info("Ignoring file "+os.path.join(root, file)+" with extension -"+file_extension+"-")
            return False

        try:
            hdul = fits.open(os.path.join(root, file), mode='update')
        except ValueError as e:
            logging.warning("Invalid FITS file. File not processed is "+str(os.path.join(root, file)))
            return False

        hdr = hdul[0].header
        if "FRAME" in hdr:
            # Create an os-friendly date
            try:
                if "DATE-OBS" not in hdr:
                    logging.warning("No DATE-OBS card in header. File not processed is "+str(os.path.join(root, file)))
                    return False
                datestr=hdr["DATE-OBS"].replace("T", " ")
                datestr=datestr[0:datestr.find('.')]
                dateobj=datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
                fitsDate=dateobj.strftime("%Y%m%d%H%M%S")
            except ValueError as e:
                logging.warning("Invalid date format in header. File not processed is "+str(os.path.join(root, file)))
                return False

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
                    return False
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
            newPath=""

            # Create the folder structure (if needed)
            fitsDate=dateobj.strftime("%Y%m%d")
            if (hdr["FRAME"]=="Light"):
                newPath=self.repoFolder+"Light/{0}/{1}/{2}/{3}/".format(hdr["OBJECT"].replace(" ", ""),hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                    hdr["INSTRUME"].replace(" ", "_"),fitsDate)
            elif hdr["FRAME"]=="Dark":
                newPath=self.repoFolder+"Calibrate/{0}/{1}/{2}/{3}/{4}/".format(hdr["FRAME"],hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                    hdr["INSTRUME"].replace(" ", "_"),hdr["EXPTIME"],fitsDate)
            elif hdr["FRAME"]=="Flat":
                if ("FILTER" in hdr):
                    newPath=self.repoFolder+"Calibrate/{0}/{1}/{2}/{3}/{4}/".format(hdr["FRAME"],hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                    hdr["INSTRUME"].replace(" ", "_"),hdr["FILTER"],fitsDate)
                else:
                    newPath=self.repoFolder+"Calibrate/{0}/{1}/{2}/{3}/{4}/".format(hdr["FRAME"],hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                    hdr["INSTRUME"].replace(" ", "_"),"OSC",fitsDate)
            elif hdr["FRAME"]=="Bias":
                newPath=self.repoFolder+"Calibrate/{0}/{1}/{2}/{3}/".format(hdr["FRAME"],hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                    hdr["INSTRUME"].replace(" ", "_"),fitsDate)
            else:
                logging.warning("File not processed as FRAME not recognized: "+str(os.path.join(root, file)))
                return None

            if not os.path.isdir(newPath) and moveFiles:
                os.makedirs (newPath)

            # If we can add the file to the database move it to the repo
            if moveFiles:
                newFitsFileId=self.submitFileToDB(newPath+newName.replace(" ", "_"),hdr)
            else:
                newFitsFileId=self.submitFileToDB(os.path.join(root, file),hdr)

            # Add the file to the list of registered files
            if (newFitsFileId != None):
                if moveFiles:
                    moveInfo="Moving {0} to {1}\n".format(os.path.join(root, file),newPath+newName)
                    logging.info(moveInfo)
                    shutil.move(os.path.join(root, file),newPath+newName)
                    message = os.path.join(root, file)
                else:
                    logging.info("File not moved in repo is "+str(os.path.join(root, file)))
            else:
                logging.warning("Warning: File not added to repo is "+str(os.path.join(root, file)))
        else:
            logging.warning("File not added to repo - no FRAME card - "+str(os.path.join(root, file)))

        return newFitsFileId

    #################################################################################################################
    ## registerFitsImages - this function scans the images folder and registers all fits files in the database     ##
    #################################################################################################################
    def registerFitsImages(self,moveFiles=True):
        registeredFiles=[]
        newFitsFileId=None
        
        # Scan the pictures folder
        if moveFiles:
            logging.info("Processing images in "+self.sourceFolder)
            workFolder=self.sourceFolder
        else:
            logging.info("Syncronizing images in "+os.path.abspath(self.repoFolder))
            workFolder=self.repoFolder

        for root, dirs, files in os.walk(os.path.abspath(workFolder)):
            for file in files:
                logging.info("Processing file "+os.path.join(root, file))
                if (newFitsFileId := self.registerFitsImage(root,file,moveFiles)) != None:
                    # Add the file to the list of registered files
                    registeredFiles.append(newFitsFileId)
                    self.createThumbnail(newFitsFileId)
                else:
                    logging.warning("File not added to repo - no FRAME card - "+str(os.path.join(root, file)))
        return registeredFiles

    #################################################################################################################
    ## createThumbnail - this function creates a thumbnail image for a fits file and saves it to the repository    ##
    #################################################################################################################
    def createThumbnail(self,fitsFileId):
        # Load the fits file
        fits_file = fitsFile.objects.filter(fitsFileId=fitsFileId).first()
        if not fits_file:
            logging.info(f"Failed to load fits file: {fitsFileId}")
            return
        
        # Read the data from the fits file
        try:
            with fits.open(fits_file.fitsFileName) as hdul:
                data = hdul[0].data
        except Exception as e:
            logging.info(f"Failed to read fits file: {e}")
            return
        
        # Create a thumbnail image
        thumbnail_data = data[::10, ::10]

        # Stretch the image to 0-100
        thumbnail_data = (thumbnail_data - np.min(thumbnail_data)) / (np.max(thumbnail_data) - np.min(thumbnail_data)) * 100
        
        # Save the thumbnail image as a JPG file
        thumbnail_path = os.path.join(self.repoFolder+'Thumbnails/', f'thumbnail_{fits_file.fitsFileId}.jpg')

        try:
            plt.imsave(thumbnail_path, thumbnail_data, cmap='gray')
            logging.info(f"Thumbnail image saved to: {thumbnail_path}")
        except Exception as e:
            logging.info(f"Failed to save thumbnail image: {e}")
        
        return

    #################################################################################################################
    ## createLightSequences - this function creates sequences for all files not currently assigned to one          ##
    #################################################################################################################
    def createLightSequences(self):
        sequencesCreated=[]
        
        # Query for all fits files that are not assigned to a sequence
        unassigned_files = fitsFile.objects.filter(fitsFileSequence__isnull=True,fitsFileType="Light")
        
        # How many unassigned_files are there?
        logging.info("createSequences found "+str(len(unassigned_files))+" unassigned files to sequence")

        # Loop through each unassigned file and create a sequence each time the object changes
        currentObject= ""
      
        for currentFitsFile in unassigned_files:
            logging.info("Current Object is "+currentFitsFile.fitsFileObject)
            logging.info("Processing "+str(currentFitsFile.fitsFileName))

            # If the object name has changed, create a new sequence
            if str(currentFitsFile.fitsFileObject) != currentObject:
                # Create a new fitsSequence record
                currentSequenceId = uuid.uuid4()
                try:
                    newFitsSequence=fitsSequence(fitsSequenceId=currentSequenceId,
                                                 fitsSequenceObjectName=currentFitsFile.fitsFileObject,
                                                 fitsSequenceTelescope=currentFitsFile.fitsFileTelescop,
                                                 fitsSequenceImager=currentFitsFile.fitsFileInstrument,
                                                 fitsSequenceDate=currentFitsFile.fitsFileDate.replace(tzinfo=pytz.UTC),
                                                 fitsMasterBias=None,fitsMasterDark=None,fitsMasterFlat=None)
                    newFitsSequence.save()
                    sequencesCreated.append(currentSequenceId)
                    logging.info("New sequence created for "+str(newFitsSequence.fitsSequenceId))
                except IntegrityError as e:
                    # Handle the integrity error
                    logging.error("IntegrityError: "+str(e))
                    continue     
                currentObject = str(currentFitsFile.fitsFileObject)
            # Assign the current sequence to the fits file
            currentFitsFile.fitsFileSequence=currentSequenceId
            currentFitsFile.save()
            logging.info("Assigned "+str(currentFitsFile.fitsFileName)+" to sequence "+str(currentSequenceId))
            sequencesCreated.append(currentSequenceId)
            
        return sequencesCreated
        
    #################################################################################################################
    ## sameDay - this function returns True if two dates are within 12 hours of each other, False otherwise        ##
    #################################################################################################################
    def sameDay(self,Date1,Date2): # If Date1 is within 12 hours of Date2
        current_date = datetime.strptime(Date1, '%Y-%m-%d')
        target_date = datetime.strptime(Date2, '%Y-%m-%d')
        time_difference = abs(current_date - target_date)
        return time_difference <= timedelta(hours=12)
    
    #################################################################################################################
    ## createCalibrationSequences - this function creates sequences for all calibration files not currently        ##
    ##                              assigned to one                                                                ##
    #################################################################################################################
    def createCalibrationSequences(self):
        createdCalibrationSequences=[]
        
        # Query for all calibration files that are not assigned to a sequence
        unassignedBiases = fitsFile.objects.filter(fitsFileSequence__isnull=True,fitsFileType="Bias")
        unassignedDarks  = fitsFile.objects.filter(fitsFileSequence__isnull=True,fitsFileType="Dark")
        unassignedFlats  = fitsFile.objects.filter(fitsFileSequence__isnull=True,fitsFileType="Flat")
        
        # How many unassigned_files are there?
        logging.info("createCalibrationSequences found "+str(len(unassignedBiases))+" unassigned Bias calibration files to sequence")
        logging.info("createCalibrationSequences found "+str(len(unassignedDarks))+" unassigned Dark calibration files to sequence")
        logging.info("createCalibrationSequences found "+str(len(unassignedFlats))+" unassigned Flat calibration files to sequence")

        # Bias calibration files
        currDate="0001-01-01"
        uuidStr=uuid.uuid4()
                        
        for biasFitsFile in unassignedBiases:
            if not self.sameDay(biasFitsFile.fitsFileDate.strftime('%Y-%m-%d'),currDate):
                currDate=biasFitsFile.fitsFileDate.strftime('%Y-%m-%d')
                uuidStr=uuid.uuid4() # New sequence
                newFitsSequence=fitsSequence(fitsSequenceId=uuidStr,
                                             fitsSequenceDate=biasFitsFile.fitsFileDate.replace(tzinfo=pytz.UTC),
                                             fitsSequenceObjectName='Flat',
                                             fitsMasterBias=None,
                                             fitsMasterDark=None,
                                             fitsMasterFlat=None)
                newFitsSequence.save()
                logging.info("New date for bias "+currDate) 
            biasFitsFile.fitsFileSequence=uuidStr
            biasFitsFile.save()   
            logging.info("Set sequence for bias "+biasFitsFile.fitsFileName+" to "+str(uuidStr))
            createdCalibrationSequences.append(uuidStr)
            
        # Dark calibration files
        currDate="0001-01-01"
        uuidStr=uuid.uuid4()
        for darkFitsFile in unassignedDarks:
            if not self.sameDay(darkFitsFile.fitsFileDate.strftime('%Y-%m-%d'),currDate):
                currDate=darkFitsFile.fitsFileDate.strftime('%Y-%m-%d')
                uuidStr=uuid.uuid4() # New sequence
                newFitsSequence=fitsSequence(fitsSequenceId=uuidStr,
                                             fitsSequenceDate=darkFitsFile.fitsFileDate.replace(tzinfo=pytz.UTC),
                                             fitsSequenceObjectName='Dark',
                                             fitsMasterBias=None,
                                             fitsMasterDark=None,
                                             fitsMasterFlat=None)
                newFitsSequence.save()
                logging.info("New date "+currDate) 
            darkFitsFile.fitsFileSequence=uuidStr
            darkFitsFile.save()   
            logging.info("Set sequence for dark "+darkFitsFile.fitsFileName+" to "+str(uuidStr))
            createdCalibrationSequences.append(uuidStr)
            
        # Flat calibration files
        currDate="0001-01-01"
        uuidStr=uuid.uuid4()
        for flatFitsFile in unassignedFlats:
            if not self.sameDay(flatFitsFile.fitsFileDate.strftime('%Y-%m-%d'),currDate):
                currDate=flatFitsFile.fitsFileDate.strftime('%Y-%m-%d')
                uuidStr=uuid.uuid4() # New sequence
                newFitsSequence=fitsSequence(fitsSequenceId=uuidStr,
                                fitsSequenceDate=flatFitsFile.fitsFileDate.replace(tzinfo=pytz.UTC),
                                fitsSequenceObjectName='Flat',
                                fitsMasterBias=None,
                                fitsMasterDark=None,
                                fitsMasterFlat=None)
                newFitsSequence.save()
                logging.info("New date "+currDate) 
            flatFitsFile.fitsFileSequence=uuidStr
            flatFitsFile.save()   
            logging.info("Set sequence for flat "+flatFitsFile.fitsFileName+" to "+str(uuidStr))
            createdCalibrationSequences.append(uuidStr)
            
        return createdCalibrationSequences

    #################################################################################################################
    ## calibrateFitsFile - this function calibrates a light frame using master bias, dark, and flat frames. If     ##
    ##                     the master frames do not exist, they are created for the sequence.                      ##
    #################################################################################################################
    def calibrateFitsImage(self,fitsFileId):
        # Load the light frame
        light_frame = fitsFile.objects.filter(fitsFileId=fitsFileId).first()
        if not light_frame:
            logging.info(f"Failed to load light frame: {fitsFileId}")
            return
        
        # Check for a fitsSequence record for the light frame
        currFitsSequence = fitsSequence.objects.filter(fitsSequenceId=light_frame.fitsFileSequence).first()
        if not currFitsSequence:
            logging.info(f"No fitsSequence record found for light frame: {light_frame.fitsFileId}, run the sync_repo command")
            return

        # If the master bias, dark, and flat frames do not exist, create them
        if not currFitsSequence.fitsMasterBias:
            currFitsSequence.fitsMasterBias = self.createMasterBias(light_frame.fitsFileId)
        if not currFitsSequence.fitsMasterDark:
            currFitsSequence.fitsMasterDark = self.createMasterDark(light_frame.fitsFileId)
        if not currFitsSequence.fitsMasterFlat:
            currFitsSequence.fitsMasterFlat = self.createMasterFlat(light_frame.fitsFileId)   

        # Save the fitsSequence record in the database
        try:
            currFitsSequence.save()
            logging.info(f"fitsSequence record saved: {currFitsSequence.fitsSequenceId}")
        except Exception as e:
            logging.info(f"Failed to save fitsSequence record: {e}")
            return
        
        # Load the master bias, dark, and flat frames
        master_bias = fitsFile.objects.filter(fitsFileName=currFitsSequence.fitsMasterBias).first()
        master_dark = fitsFile.objects.filter(fitsFileName=fitsSequence.fitsMasterDark).first()
        master_flat = fitsFile.objects.filter(fitsFileName=fitsSequence.fitsMasterFlat).first()

        # Read the data from the light frame
        try:
            with fits.open(light_frame.fitsFileName) as hdul:
                light_data = hdul[0].data
        except Exception as e:
            logging.info(f"Failed to read light frame: {e}")
            return
        
        # Calibrate the light frame
        calibrated_data = (light_data - master_bias) / (master_flat - master_dark)

        # Save the calibrated light frame
        calibrated_path = os.path.join(self.repoFolder, f'calibrated_{light_frame.fitsFileName}')
        try:
            hdu = fits.PrimaryHDU(calibrated_data)
            hdu.writeto(calibrated_path, overwrite=True)
            logging.info(f"Calibrated light frame saved to: {calibrated_path}")
        except Exception as e:
            logging.info(f"Failed to save calibrated light frame: {e}")

        # Update the light frame record in the database
        newFitsFile=fitsFile(fitsFileName=calibrated_path,fitsFileCalibrated=True)
        # Copy the rest of the fields from the original light frame
        newFitsFile.fitsFileDate=light_frame.fitsFileDate
        newFitsFile.fitsFileType="CalibratedLight"
        newFitsFile.fitsFileStacked="False"
        newFitsFile.fitsFileObject=light_frame.fitsFileObject
        newFitsFile.fitsFileExpTime=light_frame.fitsFileExpTime
        newFitsFile.fitsFileXBinning=light_frame.fitsFileXBinning
        newFitsFile.fitsFileYBinning=light_frame.fitsFileYBinning
        newFitsFile.fitsFileCCDTemp=light_frame.fitsFileCCDTemp
        newFitsFile.fitsFileTelescop=light_frame.fitsFileTelescop
        newFitsFile.fitsFileInstrument=light_frame.fitsFileInstrument
        newFitsFile.fitsFileGain=light_frame.fitsFileGain
        newFitsFile.fitsFileOffset=light_frame.fitsFileOffset
        newFitsFile.fitsFileSequence=light_frame.fitsFileSequence
        newFitsFile.save()
        logging.info(f'Light frame calibrated: {calibrated_path}')

    #################################################################################################################
    ## CreateMasterBias - this function creates a master bias frame from a set of bias frames for a given sequence ##
    #################################################################################################################
    def createMasterBias(self,targetFitsFileId):
        # Load the fits file that we need the master bias for
        light_frame = fitsFile.objects.filter(fitsFileType="Light", fitsFileId=targetFitsFileId)

        # Query to get bias frames for the file - just need one to get the sequence number
        bias_frame = fitsFile.objects.filter(fitsFileType="Bias", 
                                             fitsFileInstrument=light_frame.fitsFileInstrument, 
                                             fitsFileGain=light_frame.fitsFileGain,
                                             fitsFileOffset=light_frame.fitsFileOffset,
                                             fitsFileDate__lt=light_frame.fitsFileDate).order_by('fitsFileDate').first()

        # If we have the sequence number, get all the bias frames
        targetSequenceNo=bias_frame.fitsFileSequence
        if bias_frame:
            bias_frames = fitsFile.objects.filter(fitsFileType="Bias",fitsFileSequence=bias_frame.fitsFileSequence).order_by('fitsFileDate')
        else:
            logging.info('No bias frames found')
        
        # Read all bias frames
        bias_data = []
        for bias_frame in bias_frames:
            try:
                with fits.open(bias_frame['fits']) as hdul:
                    logging.info(f"Reading bias frame {bias_frame[2]}")
                    bias_data.append(hdul[0].data)
            except Exception as e:
                logging.info(f"Failed to read bias frame {bias_frame[2]}: {e}")

        if not bias_data:
            logging.info('No valid bias frames found')
            return
        
        # Calculate the master bias frame (median of all bias frames)
        master_bias_data = np.median(bias_data, axis=0)
        
        # Save the master bias frame
        master_bias_path = os.path.join(self.repoFolder, f'master_bias_{targetSequenceNo}.fits')
        try:
            hdu = fits.PrimaryHDU(master_bias_data)
            hdu.writeto(master_bias_path, overwrite=True)
            logging.info(f"Master bias frame saved to: {master_bias_path}")
        except Exception as e:
            logging.info(f"Failed to save master bias frame: {e}")
        
        # Save the master bias filename in the database
        newfile=fitsFile(fitsFileName=master_bias_path,fitsFileType="MasterBias",fitsFileSequence=targetSequenceNo)
        newfile.save()
        logging.info(f'Master bias frame created: {master_bias_path}')

        return newfile.fitsFileId

    #################################################################################################################
    ## CreateMasterDark - this function creates a master dark frame from a set of dark frames for a given sequence ##
    #################################################################################################################
    def createMasterDark(self,targetFitsFileId):
        # Load the fits file that we need the master dark for
        light_frame = fitsFile.objects.filter(fitsFileType="Light", fitsFileId=targetFitsFileId)

        # Query to get dark frames for the file - just need one to get the sequence number
        dark_frame = fitsFile.objects.filter(fitsFileType="dark", 
                                            fitsFileInstrument=light_frame.fitsFileInstrument, 
                                            fitsFileGain=light_frame.fitsFileGain,
                                            fitsFileOffset=light_frame.fitsFileOffset,
                                            fitsFileDate__lt=light_frame.fitsFileDate).order_by('fitsFileDate').first()

        # If we have the sequence number, get all the dark frames
        targetSequenceNo=dark_frame.fitsFileSequence
        if dark_frame:
            dark_frames = fitsFile.objects.filter(fitsFileType="Dark",fitsFileSequence=dark_frame.fitsFileSequence).order_by('fitsFileDate')
        else:
            logging.info('No dark frames found')
        
        # Read all dark frames
        dark_data = []
        for dark_frame in dark_frames:
            try:
                with fits.open(dark_frame['fits']) as hdul:
                    logging.info(f"Reading dark frame {dark_frame[2]}")
                    dark_data.append(hdul[0].data)
            except Exception as e:
                logging.info(f"Failed to read dark frame {dark_frame[2]}: {e}")

        if not dark_data:
            logging.info('No valid dark frames found')
            return
        
        # Calculate the master dark frame (median of all dark frames)
        master_dark_data = np.median(dark_data, axis=0)
        
        # Save the master dark frame
        master_dark_path = os.path.join(self.repoFolder, f'master_dark_{targetSequenceNo}.fits')
        try:
            hdu = fits.PrimaryHDU(master_dark_data)
            hdu.writeto(master_dark_path, overwrite=True)
            logging.info(f"Master dark frame saved to: {master_dark_path}")
        except Exception as e:
            logging.info(f"Failed to save master dark frame: {e}")
        
        # Save the master dark filename in the database
        newfile=fitsFile(fitsFileName=master_dark_path,fitsFileType="Masterdark",fitsFileSequence=targetSequenceNo)
        newfile.save()
        logging.info(f'Master dark frame created: {master_dark_path}')

        return newfile.fitsFileId

    #################################################################################################################
    ## CreateMasterFlat - this function creates a master flat frame from a set of flat frames for a given sequence ##
    #################################################################################################################
    def createMasterFlat(self,targetFitsFileId):
        # Load the fits file that we need the master flat for
        light_frame = fitsFile.objects.filter(fitsFileType="Light", fitsFileId=targetFitsFileId)

        # Query to get flat frames for the file - just need one to get the sequence number
        flat_frame = fitsFile.objects.filter(fitsFileType="flat", 
                                             fitsFileInstrument=light_frame.fitsFileInstrument, 
                                             fitsFileGain=light_frame.fitsFileGain,
                                             fitsFileOffset=light_frame.fitsFileOffset,
                                             fitsFileDate__lt=light_frame.fitsFileDate).order_by('fitsFileDate').first()

        # If we have the sequence number, get all the flat frames
        targetSequenceNo=flat_frame.fitsFileSequence
        if flat_frame:
            flat_frames = fitsFile.objects.filter(fitsFileType="Flat",fitsFileSequence=flat_frame.fitsFileSequence).order_by('fitsFileDate')
        else:
            logging.info('No flat frames found')
        
        # Read all flat frames
        flat_data = []
        for flat_frame in flat_frames:
            try:
                with fits.open(flat_frame['fits']) as hdul:
                    logging.info(f"Reading flat frame {flat_frame[2]}")
                    flat_data.append(hdul[0].data)
            except Exception as e:
                logging.info(f"Failed to read flat frame {flat_frame[2]}: {e}")

        if not flat_data:
            logging.info('No valid flat frames found')
            return
        
        # Calculate the master flat frame (median of all flat frames)
        master_flat_data = np.median(flat_data, axis=0)
        
        # Save the master flat frame
        master_flat_path = os.path.join(self.repoFolder, f'master_flat_{targetSequenceNo}.fits')
        try:
            hdu = fits.PrimaryHDU(master_flat_data)
            hdu.writeto(master_flat_path, overwrite=True)
            logging.info(f"Master flat frame saved to: {master_flat_path}")
        except Exception as e:
            logging.info(f"Failed to save master flat frame: {e}")
        
        # Save the master flat filename in the database
        newfile=fitsFile(fitsFileName=master_flat_path,fitsFileType="Masterflat",fitsFileSequence=targetSequenceNo)
        newfile.save()
        logging.info(f'Master flat frame created: {master_flat_path}')

        return newfile.fitsFileId