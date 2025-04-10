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

from obsy.config import GeneralConfig
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import EarthLocation, SkyCoord
from astroplan import Observer, FixedTarget
import pytz

logger = logging.getLogger(__name__)

##################################################################################################
## Target - an object for which we may wish to create an Observation                           ##
################################################################################################## 
class Target(models.Model):
    targetId        = models.UUIDField( 
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False)
    targetName      = models.CharField(max_length=255)
    targetClass     = models.CharField(max_length=255,default="DS")
    targetType      = models.CharField(max_length=255)
    targetRA2000    = models.CharField(max_length=255)
    targetDec2000   = models.CharField(max_length=255)
    targetConst     = models.CharField(max_length=200)
    targetMag       = models.CharField(max_length=200)
    targetDefaultThumbnail = models.ImageField(upload_to='thumbnails/')
    targetRise      = models.DateTimeField(null=True, blank=True)
    targetTransit   = models.DateTimeField(null=True, blank=True)
    targetSet       = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.targetName}"
    
    def get_absolute_url(self):
        return reverse("target_detail", args=[str(self.targetId)])
    
    # On create or update, generate the thumbnail file
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Check if the thumbnail folder exists
        if not os.path.exists('media/images/thumbnails'):
            os.makedirs('media/images/thumbnails')
        # Create relative path with no extension (used for fits and jpg)
        relative_path = os.path.join('media/images/thumbnails', f"{self.targetName}") 
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
        relative_path = os.path.join('media/images/thumbnails', f"{self.targetName}") 
        jpg_filename = relative_path+'.jpg'
        logger.debug("Deleting thumbnail file "+jpg_filename)
        if self.targetDefaultThumbnail:
            try:
                os.remove(jpg_filename)
            except:
                logger.warning("Failed to remove thumbnail file "+jpg_filename)
        super().delete(*args, **kwargs)
        return 
    
    ##############################################################################################
    # Set Rise / Transit / Set times for the Target                                             ##
    ##############################################################################################
    def set_rise_transit_set(self):
         # Get General config
        genSettings = GeneralConfig.objects.first()
        if genSettings == None:
            logger.info("[*]  Unable to load settings, aborting")
            return False
        
        # Define the observer's location
        location = EarthLocation(lat=float(genSettings.latitude) * u.deg, lon=float(genSettings.longitude) * u.deg, height=float(genSettings.elevation) * u.m)
        observer = Observer(location=location, timezone=settings.TIME_ZONE, name="Observer")
        
        # Define the current time in UTC
        utc_now = datetime.now(pytz.UTC)
        time = Time(utc_now)

        # Convert RA and Dec to decimal degrees
        raList = self.targetRA2000.split(' ')
        if len(raList) == 3:
            ra_hrs, ra_min, ra_sec = raList
        else:
            ra_hrs, ra_min = raList
            ra_sec = 0  
        ra_decimal = (float(ra_hrs) + float(ra_min)/60 + float(ra_sec)/3600) * 15
        
        decList = self.targetDec2000.split(' ')
        if len(decList) == 3:
            dec_deg, dec_min, dec_sec = decList
        else:
            dec_deg, dec_min = decList
            dec_sec = 0       
        dec_decimal = float(dec_deg) + float(dec_min)/60 + float(dec_sec)/3600

        # Create a SkyCoord object for the target
        target_coord = SkyCoord(ra=ra_decimal * u.deg, dec=dec_decimal * u.deg, frame='icrs')
        target_fixed = FixedTarget(coord=target_coord, name=self.targetName)

        # Calculate rise, transit, and set times
        local_tz = pytz.timezone(settings.TIME_ZONE)
        rise_timeJD = observer.target_rise_time(time, target_fixed, which='next')
        rise_timeUTC = rise_timeJD.to_datetime()
        transit_timeJD = observer.target_meridian_transit_time(time, target_fixed, which='next')
        transit_timeUTC = transit_timeJD.to_datetime()
        set_timeJD = observer.target_set_time(time, target_fixed, which='next')
        set_timeUTC = set_timeJD.to_datetime()
        
        logger.info("Processing object name: "+self.targetName)
        
        # Convert to local time and assign to object attributes
        if type(rise_timeUTC) == datetime:
            self.targetRise=rise_timeUTC.replace(tzinfo=pytz.UTC).astimezone(local_tz)
        else:
            self.targetRise=None
        if type(transit_timeUTC) == datetime:
            self.targetTransit=transit_timeUTC.replace(tzinfo=pytz.UTC).astimezone(local_tz)
        else:
            self.targetTransit=None
        if type(set_timeUTC) == datetime:
            self.targetSet=set_timeUTC.replace(tzinfo=pytz.UTC).astimezone(local_tz)
        else:
            self.targetSet=None

        self.save()

        return