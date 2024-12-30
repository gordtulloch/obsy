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
## Target - an object for which we may wish to create an Observation                           ##
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
    targetClass     = models.CharField(max_length=255,choices=TARGET_CLASSES,default="DS")
    targetType      = models.CharField(max_length=255)
    targetRA2000    = models.CharField(max_length=255)
    targetDec2000   = models.CharField(max_length=255)
    targetConst     = models.CharField(max_length=200)
    targetMag       = models.CharField(max_length=200)
    targetDefaultThumbnail = models.ImageField(upload_to='thumbnails/')
    def __str__(self):
        return f"{self.targetId}"
    
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
    
##################################################################################################
## SimbadType - this model allows mapping between SIMBAD object types and obsy object classes   ##
##################################################################################################
class SimbadType(models.Model):
    label       = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    targetClass = models.CharField(max_length=2)
    
    def __str__(self):
        return f"{self.label}"
    def populate_db():
        with open('standard_data/targets_simbadtype.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                _, created = SimbadType.objects.get_or_create(
                label=row[1],
                description=row[2],
                targetClass=row[3],
                )
        return
    
##################################################################################################
## NasaExplanetArchive - this model is used to store the NASA Exoplanet Archive data            ##
##################################################################################################
class NasaExplanetArchive(models.Model):
    kepid               = models.CharField(max_length=255, null=True, blank=True)   # KepID
    kepoi_name          = models.CharField(max_length=255, null=True, blank=True)   # KOI Name
    kepler_name         = models.CharField(max_length=255, null=True, blank=True)   # Kepler Name
    koi_disposition     = models.CharField(max_length=255, null=True, blank=True)   # Exoplanet Archive Disposition
    koi_pdisposition    = models.CharField(max_length=255, null=True, blank=True)   # Disposition Using Kepler Data
    koi_score           = models.FloatField(max_length=255, null=True, blank=True)   # Disposition Score
    koi_fpflag_nt       = models.BooleanField(max_length=255, null=True, blank=True)   # Not Transit-Like False Positive Flag
    koi_fpflag_ss       = models.BooleanField(max_length=255, null=True, blank=True)   # Stellar Eclipse False Positive Flag
    koi_fpflag_co       = models.BooleanField(max_length=255, null=True, blank=True)   # Centroid Offset False Positive Flag
    koi_fpflag_ec       = models.BooleanField(max_length=255, null=True, blank=True)   # Ephemeris Match Indicates Contamination False Positive Flag
    koi_period          = models.FloatField(max_length=255, null=True, blank=True)   # Orbital Period [days]
    koi_period_err1     = models.FloatField(max_length=255, null=True, blank=True)   # Orbital Period Upper Unc. [days]
    koi_period_err2     = models.FloatField(max_length=255, null=True, blank=True)  # Orbital Period Lower Unc. [days]
    koi_time0bk         = models.FloatField(max_length=255, null=True, blank=True)  # Transit Epoch [BKJD]
    koi_time0bk_err1    = models.FloatField(max_length=255, null=True, blank=True)  # Transit Epoch Upper Unc. [BKJD]
    koi_time0bk_err2    = models.FloatField(max_length=255, null=True, blank=True)  #  Transit Epoch Lower Unc. [BKJD]
    koi_impact          = models.FloatField(max_length=255, null=True, blank=True)  #      Impact Parameter
    koi_impact_err1     = models.FloatField(max_length=255, null=True, blank=True)  #  Impact Parameter Upper Unc.
    koi_impact_err2     = models.FloatField(max_length=255, null=True, blank=True)  #  Impact Parameter Lower Unc.
    koi_duration        = models.FloatField(max_length=255, null=True, blank=True)  #    Transit Duration [hrs]
    koi_duration_err1   = models.FloatField(max_length=255, null=True, blank=True)  # Transit Duration Upper Unc. [hrs]
    koi_duration_err2   = models.FloatField(max_length=255, null=True, blank=True)  # Transit Duration Lower Unc. [hrs]
    koi_depth           = models.FloatField(max_length=255, null=True, blank=True)  #       Transit Depth [ppm]
    koi_depth_err1      = models.FloatField(max_length=255, null=True, blank=True)  # Transit Depth Upper Unc. [ppm]
    koi_depth_err2      = models.FloatField(max_length=255, null=True, blank=True)  # Transit Depth Lower Unc. [ppm]
    koi_prad            = models.FloatField(max_length=255, null=True, blank=True)  # Planetary Radius [Earth radii]
    koi_prad_err1       = models.FloatField(max_length=255, null=True, blank=True)  # Planetary Radius Upper Unc. [Earth radii]
    koi_prad_err2       = models.FloatField(max_length=255, null=True, blank=True)  # Planetary Radius Lower Unc. [Earth radii]
    koi_teq             = models.FloatField(max_length=255, null=True, blank=True)  # Equilibrium Temperature [K]
    koi_teq_err1        = models.FloatField(max_length=255, null=True, blank=True)  # Equilibrium Temperature Upper Unc. [K]
    koi_teq_err2        = models.FloatField(max_length=255, null=True, blank=True)  # Equilibrium Temperature Lower Unc. [K]
    koi_insol           = models.FloatField(max_length=255, null=True, blank=True)  # Insolation Flux [Earth flux]
    koi_insol_err1      = models.FloatField(max_length=255, null=True, blank=True)  # Insolation Flux Upper Unc. [Earth flux]
    koi_insol_err2      = models.FloatField(max_length=255, null=True, blank=True)  # Insolation Flux Lower Unc. [Earth flux]
    koi_model_snr       = models.FloatField(max_length=255, null=True, blank=True)  # Transit Signal-to-Noise
    koi_tce_plnt_num    = models.FloatField(max_length=255, null=True, blank=True)  # TCE Planet Number
    koi_tce_delivname   = models.CharField(max_length=255, null=True, blank=True)   # TCE Delivery
    koi_steff           = models.FloatField(max_length=255, null=True, blank=True)  # Stellar Effective Temperature [K]
    koi_steff_err1      = models.FloatField(max_length=255, null=True, blank=True)  # Stellar Effective Temperature Upper Unc. [K]
    koi_steff_err2      = models.FloatField(max_length=255, null=True, blank=True)  # Stellar Effective Temperature Lower Unc. [K]
    koi_slogg           = models.FloatField(max_length=255, null=True, blank=True)  # Stellar Surface Gravity [log10(cm/s**2)]
    koi_slogg_err1      = models.FloatField(max_length=255, null=True, blank=True)  # Stellar Surface Gravity Upper Unc. [log10(cm/s**2)]
    koi_slogg_err2      = models.FloatField(max_length=255, null=True, blank=True)  # Stellar Surface Gravity Lower Unc. [log10(cm/s**2)]
    koi_srad            = models.FloatField(max_length=255, null=True, blank=True)  # Stellar Radius [Solar radii]
    koi_srad_err1       = models.FloatField(max_length=255, null=True, blank=True)  # Stellar Radius Upper Unc. [Solar radii]
    koi_srad_err2       = models.FloatField(max_length=255, null=True, blank=True)  # Stellar Radius Lower Unc. [Solar radii]
    ra                  = models.FloatField(max_length=255, null=True, blank=True)  # RA [decimal degrees]
    dec                 = models.FloatField(max_length=255, null=True, blank=True)  # Dec [decimal degrees]
    koi_kepmag          = models.FloatField(max_length=255, null=True, blank=True)  # Kepler-band [mag]

    def __str__(self):
        return f"{self.kepoi_name}"
    
    def get_absolute_url(self):
        return reverse("nasa_exoplanet_archive_detail", kwargs={'pk': self.pk}) 
    
    ##################################################################################################
    ## Refresh NASA Exoplanet Archive - this manager class is used to refresh the NASA Exoplanet db ##
    ##################################################################################################
    import requests
    import csv
    # Allow the method to be called without an instance of the class

    @classmethod
    def refresh_exoplanet_db(self):
        url = 'https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=cumulative&format=csv'
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        from io import StringIO
        csv_data = response.text
        csv_reader = csv.DictReader(StringIO(csv_data))

        for row in csv_reader:
            # Map CSV columns to model fields
            data = {
                'kepid': row['kepid'] ,
                'kepoi_name': row['kepoi_name'],
                'kepler_name': row['kepler_name'],
                'koi_disposition': row['koi_disposition'],
                'koi_pdisposition': row['koi_pdisposition'],
                'koi_score': row['koi_score'] if row['koi_score'] else None,
                'koi_fpflag_nt': self.str_to_bool(self,row['koi_fpflag_nt']),
                'koi_fpflag_ss': self.str_to_bool(self,row['koi_fpflag_ss']),
                'koi_fpflag_co': self.str_to_bool(self,row['koi_fpflag_co']),
                'koi_fpflag_ec': self.str_to_bool(self,row['koi_fpflag_ec']),
                'koi_period': float(row['koi_period']) if row['koi_period'] else None,
                'koi_period_err1': float(row['koi_period_err1']) if row['koi_period_err1'] else None,
                'koi_period_err2': float(row['koi_period_err2']) if row['koi_period_err2'] else None,
                'koi_time0bk': float(row['koi_time0bk']) if row['koi_time0bk'] else None,
                'koi_time0bk_err1': float(row['koi_time0bk_err1']) if row['koi_time0bk_err1'] else None,
                'koi_time0bk_err2': float(row['koi_time0bk_err2']) if row['koi_time0bk_err2'] else None,
                'koi_impact': float(row['koi_impact']) if row['koi_impact'] else None,
                'koi_impact_err1': float(row['koi_impact_err1']) if row['koi_impact_err1'] else None,
                'koi_impact_err2': float(row['koi_impact_err2']) if row['koi_impact_err2'] else None,
                'koi_duration': float(row['koi_duration']) if row['koi_duration'] else None,
                'koi_duration_err1': float(row['koi_duration_err1']) if row['koi_duration_err1'] else None,
                'koi_duration_err2': float(row['koi_duration_err2']) if row['koi_duration_err2'] else None,
                'koi_depth': float(row['koi_depth']) if row['koi_depth'] else None,
                'koi_depth_err1': float(row['koi_depth_err1']) if row['koi_depth_err1'] else None,
                'koi_depth_err2': float(row['koi_depth_err2']) if row['koi_depth_err2'] else None,
                'koi_prad': float(row['koi_prad']) if row['koi_prad'] else None,
                'koi_prad_err1': float(row['koi_prad_err1']) if row['koi_prad_err1'] else None,
                'koi_prad_err2': float(row['koi_prad_err2']) if row['koi_prad_err2'] else None,
                'koi_teq': float(row['koi_teq']) if row['koi_teq'] else None,
                'koi_teq_err1': float(row['koi_teq_err1']) if row['koi_teq_err1'] else None,
                'koi_teq_err2': float(row['koi_teq_err2']) if row['koi_teq_err2'] else None,
                'koi_insol': float(row['koi_insol']) if row['koi_insol'] else None,
                'koi_insol_err1': float(row['koi_insol_err1']) if row['koi_insol_err1'] else None,
                'koi_insol_err2': float(row['koi_insol_err2']) if row['koi_insol_err2'] else None,
                'koi_model_snr': float(row['koi_model_snr']) if row['koi_model_snr'] else None,
                'koi_tce_plnt_num': float(row['koi_tce_plnt_num']) if row['koi_tce_plnt_num'] else None,
                'koi_tce_delivname': row['koi_tce_delivname'],
                'koi_steff': float(row['koi_steff']) if row['koi_steff'] else None,
                'koi_steff_err1': float(row['koi_steff_err1']) if row['koi_steff_err1'] else None,
                'koi_steff_err2': float(row['koi_steff_err2']) if row['koi_steff_err2'] else None,
                'koi_slogg': float(row['koi_slogg']) if row['koi_slogg'] else None,
                'koi_slogg_err1': float(row['koi_slogg_err1']) if row['koi_slogg_err1'] else None,
                'koi_slogg_err2': float(row['koi_slogg_err2']) if row['koi_slogg_err2'] else None,
                'koi_srad': float(row['koi_srad']) if row['koi_srad'] else None,
                'koi_srad_err1': float(row['koi_srad_err1']) if row['koi_srad_err1'] else None,
                'koi_srad_err2': float(row['koi_srad_err2']) if row['koi_srad_err2'] else None,
                'ra': self.ra_to_decimal_hours(self,row['ra_str']) if row['ra_str'] else None,
                'dec':self.dec_to_decimal_degrees(self,row['dec_str']) if row['dec_str'] else None,
                'koi_kepmag': float(row['koi_kepmag']) if row['koi_kepmag'] else None,
            }
            NasaExplanetArchive.objects.create(**data)
    
    def str_to_bool(self,value):
        return value.lower() in ('true', '1', 't', 'y', 'yes')
    
    def ra_to_decimal_hours(self,ra_str):
        import re
        match = re.match(r'(\d+)h(\d+)m([\d.]+)s', ra_str)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            seconds = float(match.group(3))
            decimal_hours = hours + minutes / 60 + seconds / 3600
            return decimal_hours
        else:
            raise ValueError(f"Invalid RA format: {ra_str}")
        
    def dec_to_decimal_degrees(self,dec_str):
        import re
        match = re.match(r'([+-]?\d+)d(\d+)m([\d.]+)s', dec_str)
        if match:
            degrees = int(match.group(1))
            minutes = int(match.group(2))
            seconds = float(match.group(3))
            decimal_degrees = degrees + minutes / 60 + seconds / 3600
            return decimal_degrees
        else:
            raise ValueError(f"Invalid DEC format: {dec_str}")
