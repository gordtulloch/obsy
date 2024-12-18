import uuid
from django.db import models
from django.conf import settings
from django.urls import reverse
from setup.models import observatory, telescope, imager
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime
import csv
import os
import logging
import requests
from astropy.io import fits
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

##################################################################################################
## Target - an object for which we may wish to create an observation                           ##
################################################################################################## 
class Target(models.Model):
    TARGET_CLASSES=(
    ("VS", "Variable Star"),
    ("EX", "Exoplanet"),
    ("DS", "Deep Sky Object"),
    ("PL", "Planet"),
    ("LU", "Luna"),
    ("SU", "Sun"),
    ("SA", "Satellite"),
    ("OT", "Other")
    )
    targetId        = models.UUIDField( 
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False)
    targetName      = models.CharField(max_length=255)
    targetClass     = models.CharField(max_length=2,choices=TARGET_CLASSES,default="DS")
    targetType      = models.CharField(max_length=255)
    targetRA2000    = models.CharField(max_length=255)
    targetDec2000   = models.CharField(max_length=255)
    targetConst     = models.CharField(max_length=200)
    targetMag       = models.CharField(max_length=200)
    targetDefaultThumbnail = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return f"{self.targetId}"
    
    def get_absolute_url(self):
        return reverse("target_detail", args=[str(self.targetId)])
    
    # On create or update, generate the thumbnail file
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Create relative path with no extension (used for fits and jpg)
        relative_path = os.path.join('static','images', 'thumbnails', self.targetName)  
        if self.targetDefaultThumbnail:
            try:
                os.remove(relative_path+'.jpg')
            except:
                logger.error("Failed to remove thumbnail file "+relative_path+'.jpg')

        # Add a default thumbnail from SDSS/SS for the Target
        width = 15 # Width of the image in arcmin
        height = 15  # Height of the image in arcmin
        
        # Construct the URL for the STSCI Digitized Sky Survey (DSS) image
        logger.debug("Constructing URL for image")
        url = 'https://archive.stsci.edu/cgi-bin/dss_search?r='+self.targetRA2000+'&d='+self.targetDec2000+'&w='+str(width)+'&h='+str(height)+'&e=J2000'
        logger.debug("Requesting image "+url)

        # Create an appropriate filename for the image
        jpg_filename = os.path.join(settings.BASE_DIR, relative_path)+'.jpg'
        fits_filename = os.path.join(settings.BASE_DIR, relative_path)+'.fits'
        logger.debug("Will save image "+fits_filename+" as "+jpg_filename)

        # Make the request to fetch the image
        try:
            response = requests.get(url)
        except Exception as e:
            logger.error("Failed to retrieve image "+fits_filename+"with error "+str(e))
        logger.debug("Response code "+str(response.status_code))

        # Check if the request was successful
        if response.status_code == 200:
            with open(fits_filename, 'wb') as f:
                f.write(response.content)
                logger.debug("Image saved as "+fits_filename)
            # Open the FITS file and save as jpg
            with fits.open(fits_filename) as hdul:
                logger.debug("Opened FITS file "+fits_filename)
                # Get the image data from the primary HDU
                image_data = hdul[0].data
                logger.debug("Got image data from FITS file")

                # Normalize the image data to the range 0-255
                logger.debug("Normalizing image data")
                image_data = image_data - np.min(image_data)
                image_data = (image_data / np.max(image_data) * 255).astype(np.uint8)

                # Convert to a PIL image
                logger.debug("Converting image to PIL")
                image = Image.fromarray(image_data)
                logger.debug("Converted image to PIL")

                # Resize the image to 150x150
                logger.debug("Resizing image")
                image = image.resize((150, 150))

                # Save as JPG
                logger.debug("Saving image as JPG")
                image.save(jpg_filename)

            # Remove the temporary FITS file
            logger.debug("Removing FITS file "+fits_filename)
            os.remove(fits_filename)
        else:
            logger.error("Failed to retrieve image "+fits_filename)


    ##############################################################################################
    # On delete, remove the thumbnail file                                                      ##       
    def delete(self, *args, **kwargs):
        relative_path = os.path.join('static','images', 'thumbnails', self.targetName)
        jpg_filename = os.path.join(settings.BASE_DIR, relative_path)+'.jpg'
        logger.debug("Deleting thumbnail file "+jpg_filename)
        if self.targetDefaultThumbnail:
            try:
                os.remove(jpg_filename)
            except:
                logger.warning("Failed to remove thumbnail file "+jpg_filename)
        super().delete(*args, **kwargs)

##################################################################################################
## simbadType - this model allows mapping between SIMBAD object types and obsy object classes   ##
##################################################################################################
class simbadType(models.Model):
    def populate_db():
        with open('catalog\targets_simbadtype.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                _, created = simbadType.objects.get_or_create(
                label=row[0],
                description=row[1],
                category=row[2],
                )
        return
    
    label       = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    category    = models.CharField(max_length=2)
    
    def __str__(self):
        return f"{self.id}"
    def get_absolute_url(self):
        return reverse("target_detail", args=[str(self.id)])
    
