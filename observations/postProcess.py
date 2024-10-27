############################################################################################################
## P O S T P R O C E S S                                                                                  ##
############################################################################################################
# Functions to import fits file data into the database while renaming files and moving them to a repository, 
# calibrate images, create thumbnails linked to test stacks, and send the user an email with a summary of 
# the work done.
#
import os
from astropy.io import fits
import shutil
from math import cos,sin
from datetime import datetime
import logging
from django.conf import settings
from .models import fitsFile, fitsHeader
from django.utils import timezone
import pysiril

# After images are obtained move them to a reporsitory and add them to the database
class registerFitsFiles(object):
    def __init__(self):
        self.logging = logging.getLogger('postProcess')
        self.sourceFolder=settings.SOURCEPATH
        self.fileRepoFolder=settings.REPOPATH
        self.logging.info("Post Processing object initialized")

    # Function definitions
    def submitFileToDB(self,fileName,hdr):
        if "DATE-OBS" in hdr:
            # Create new fitsFile record
            newfile=fitsFile(fitsFileName=fileName,fitsFileDate=hdr["DATE-OBS"],fitsFileType=hdr["FRAME"])
            newfile.save()

            # Add the header information to the database
            for card in hdr:
                if type(hdr[card]) not in [bool,int,float]:
                    keywordValue=str(hdr[card]).replace('\'',' ')
                else:
                    keywordValue = hdr[card]
                newheader=fitsHeader(fitsHeaderKey=card,fitsHeaderValue=keywordValue,fitsFileId=newfile)
                newheader.save()
        else:
            self.logging.error("Error: File not added to repo due to missing date is "+fileName)
            return False
        return True


    def registerFitsImages(self):
        # Scan the pictures folder
        self.logging.info("Processing images in "+self.sourceFolder)
        for root, dirs, files in os.walk(os.path.abspath(self.sourceFolder)):
            for file in files:
                self.logging.info("Processing file "+os.path.join(root, file))
                file_name, file_extension = os.path.splitext(os.path.join(root, file))

                # Ignore everything not a *fit* file
                if "fit" not in file_extension:
                    self.logging.info("Ignoring file "+os.path.join(root, file)+" with extension -"+file_extension+"-")
                    continue

                try:
                    hdul = fits.open(os.path.join(root, file), mode='update')
                except ValueError as e:
                    self.logging.warning("Invalid FITS file. File not processed is "+str(os.path.join(root, file)))
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
                        self.logging.warning("Invalid date format in header. File not processed is "+str(os.path.join(root, file)))
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
                                self.logging.warning("No WCS information in header, file not updated is "+str(os.path.join(root, file)))

                        # Assign a new name
                        if ("OBJECT" in hdr):
                            if ("FILTER" in hdr):
                                newName="{0}-{1}-{2}-{3}-{4}-{5}s-{6}x{7}-t{8}.fits".format(hdr["OBJECT"].replace(" ", "_"),hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                            hdr["INSTRUME"].replace(" ", "_"),hdr["FILTER"],fitsDate,hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["CCD-TEMP"])
                            else:
                                newName=newName="{0}-{1}-{2}-{3}-{4}-{5}s-{6}x{7}-t{8}.fits".format(hdr["OBJECT"].replace(" ", "_"),hdr["TELESCOP"].replace(" ", "_").replace("\\", "_"),
                                            hdr["INSTRUME"].replace(" ", "_"),"OSC",fitsDate,hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["CCD-TEMP"])
                        else:
                            self.logging.warning("Invalid object name in header. File not processed is "+str(os.path.join(root, file)))
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
                        self.logging.warning("File not processed as FRAME not recognized: "+str(os.path.join(root, file)))
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
                        self.logging.info(moveInfo)
                        shutil.move(os.path.join(root, file),newPath+newName)
                    else:
                        self.logging.warning("Warning: File not added to repo is "+str(os.path.join(root, file)))
                else:
                    self.logging.warning("File not added to repo - no FRAME card - "+str(os.path.join(root, file)))
        return
    
    def calibrateImages(self):
        # Query for Light frames that are not calibrated
        light_frames = fitsFile.objects.filter(fitsFileType="Light", fitsFileCalibrated=False)
    
        # How many light_frames are there?
        self.logging("calibrateImages found "+str(len(light_frames))+" light frames to calibrate")

        for light_frame in light_frames:
            # Get the header information for the Light frame
            light_header = fitsHeader.objects.filter(fitsFileId=light_frame.fitsFileId)
            light_header_dict = {header.key: header.value for header in light_header}

            '''
            # Query for MasterDark frames
            dark_frames = fitsFile.objects.filter(
                    fitsFileType="DarkMaster",
                    fitsFileHeader__TELESCOP=light_header_dict.get('TELESCOP'),
                    fitsFileHeader__INSTRUME=light_header_dict.get('INSTRUME'),
                    fitsFileHeader__EXPTIME=light_header_dict.get('EXPTIME'),
                    fitsFileHeader__XBINNING=light_header_dict.get('XBINNING'),
                    fitsFileHeader__YBINNING=light_header_dict.get('YBINNING')
                )
                
            # Query for MasterBias frames
            bias_frames = fitsFile.objects.filter(
                    fitsFileType="MasterBias",
                    fitsFileHeader__TELESCOP=light_header_dict.get('TELESCOP'),
                    fitsFileHeader__INSTRUME=light_header_dict.get('INSTRUME'),
                    fitsFileHeader__XBINNING=light_header_dict.get('XBINNING'),
                    fitsFileHeader__YBINNING=light_header_dict.get('YBINNING')
                )
                
            # Query for MasterFlat frames
            flat_frames = fitsFile.objects.filter(
                    fitsFileType="MasterFlat",
                    fitsFileHeader__TELESCOP=light_header_dict.get('TELESCOP'),
                    fitsFileHeader__INSTRUME=light_header_dict.get('INSTRUME'),
                    fitsFileHeader__FILTER=light_header_dict.get('FILTER'),
                    fitsFileHeader__XBINNING=light_header_dict.get('XBINNING'),
                    fitsFileHeader__YBINNING=light_header_dict.get('YBINNING')
                )
                
            # Apply calibration using PySiril
            light_file_path = light_frame.filePath
            dark_file_paths = [dark.filePath for dark in dark_frames]
            bias_file_paths = [bias.filePath for bias in bias_frames]
            flat_file_paths = [flat.filePath for flat in flat_frames]
                
            # Create a PySiril script to calibrate the Light frame
            script = pysiril.Script()
            script.load(light_file_path)
            for dark in dark_file_paths:
                script.dark(dark)
            for bias in bias_file_paths:
                script.bias(bias)
            for flat in flat_file_paths:
                script.flat(flat)
            script.save(f"{light_file_path}_calibrated")
                
            # Mark the Light frame as calibrated
            light_frame.fitsFileCalibrated = True
            light_frame.save()
            '''

    def stackImages(self):
        '''
        # Query for Light frames that are not stacked
        light_frames = fitsFile.objects.filter(fitsFileType="Light", fitsFileStacked=False)
        
        # Group images into sequences
        sequences = []
        for light_frame in light_frames:
            # Get the header information for the Light frame
            light_header = fitsHeader.objects.filter(fitsFileId=light_frame.fitsFileId)
            light_header_dict = {header.key: header.value for header in light_header}
            
            # Find matching sequences
            matched = False
            for sequence in sequences:
                seq_header = sequence[0]['header']
                if (light_header_dict.get('OBJECT') == seq_header.get('OBJECT') and
                    light_header_dict.get('TELESCOP') == seq_header.get('TELESCOP') and
                    light_header_dict.get('INSTRUME') == seq_header.get('INSTRUME') and
                    light_header_dict.get('EXPTIME') == seq_header.get('EXPTIME') and
                    light_header_dict.get('XBINNING') == seq_header.get('XBINNING') and
                    light_header_dict.get('YBINNING') == seq_header.get('YBINNING') and
                    abs((light_header_dict.get('DATE-OBS') - seq_header.get('DATE-OBS')).total_seconds()) <= 16 * 3600):
                    sequence.append({'frame': light_frame, 'header': light_header_dict})
                    matched = True
                    break
            
            if not matched:
                sequences.append([{'frame': light_frame, 'header': light_header_dict}])
        
        # Process each sequence
        for sequence in sequences:
            light_file_paths = [item['frame'].filePath for item in sequence]
            
            # Create a PySiril script to stack the Light frames
            script = pysiril.Script()
            for light in light_file_paths:
                script.load(light)
            script.stack()
            stacked_file_path = f"{light_file_paths[0]}_stacked"
            script.save(stacked_file_path)
            
            # Create a new FitsFile entry for the stacked image
            fitsFile.objects.create(
                fitsFileName=f"{sequence[0]['header'].get('OBJECT')}_stacked.fits",
                fitsFileType="StackedLight",
                fitsFilePath=stacked_file_path,
                fitsFileDate=timezone.now(),
                fitsFileCalibrated=True,
                fitsFileStacked=True
            )
            
            # Mark all Light frames in the sequence as stacked
            for item in sequence:
                item['frame'].fitsFileStacked = True
                item['frame'].save()
            '''