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
## Exoplanet - this model is used to store the CalTech Exoplanet Archive data                   ##
##################################################################################################
class Exoplanet(models.Model):
    targetId            = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    targetClass         = models.CharField(max_length=255,default="EX")
    targetName          = models.CharField(max_length=255) # pl_name,
    targetOrbPer        = models.FloatField(null=True) # pl_orbper,  	Orbital Period 
    targetOrbPerErr1    = models.FloatField(null=True) # pl_orbpererr1, 
    targetOrbPerErr2    = models.FloatField(null=True) # pl_orbpererr2,
    targetOrbSMAxis     = models.FloatField(null=True) # pl_orbsmax,  	Orbit Semi-Major Axis [au]
    targetOrbIncl       = models.FloatField(null=True) # pl_orbincl,     Inclination [deg]
    targetRAStr         = models.CharField(max_length=255,null=True) # rastr,          Right Ascension of the planetary system in sexagesimal format
    targetDecStr        = models.CharField(max_length=255,null=True) # decstr,         Declination of the planetary system in sexagesimal notation
    targetRA2000        = models.FloatField(null=True) # ra,             Right Ascension of the planetary system in decimal degrees
    targetDec2000       = models.FloatField(null=True) # dec,            Declination of the planetary system in decimal degrees
    targetStelRadius    = models.FloatField(null=True) # st_rad,         Stellar Radius [Solar Radius]
    targetPlRadius      = models.FloatField(null=True) # pl_radj,        Planet Radius [Jupiter Radius]
    targetTrDepth       = models.FloatField(null=True) # pl_trandep,     Transit Depth [ppm]
    targetTrDur         = models.FloatField(null=True) # pl_trandur,     Transit Duration [hours]
    targetTrDurErr1     = models.FloatField(null=True) # pl_trandurerr1, 
    targetTrDurErr2     = models.FloatField(null=True) # pl_trandurerr2,
    targetTrMid         = models.FloatField(null=True) # pl_tranmid,     Transit Midpoint [BJD]
    targetTrMidErr1     = models.FloatField(null=True) # pl_tranmiderr1,
    targetTrMidErr2     = models.FloatField(null=True) # pl_tranmiderr2,
    targetImpPar        = models.FloatField(null=True) # pl_imppar,      Impact Parameter
    targetRatDor        = models.FloatField(null=True) # pl_ratdor,      Ratio of Distance to Stellar Radius
    targetRarRor        = models.FloatField(null=True) # pl_ratror,      Ratio of Planet to Stellar Radius
    targetVMag          = models.FloatField(null=True) # sy_vmag,        V-band Magnitude
    targetGaiaMag       = models.FloatField(null=True) # sy_gaiamag      Gaia Magnitude

    def __str__(self):
        return f"{self.targetName}"
    
    ##################################################################################################
    ## Refresh Exoplanet Archive - this manager class is used to refresh the NASA Exoplanet db      ##
    ##################################################################################################
    import requests
    import csv
    # Allow the method to be called without an instance of the class

    @classmethod
    def refresh_exoplanet_db(self):
        logger.info("Refreshing Exoplanet data")
        logger.info("Requesting data from NASA Exoplanet Archive")
        url = 'https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+pl_name,pl_orbper,pl_orbpererr1,pl_orbpererr2,pl_orbsmax,pl_orbincl,rastr,decstr,ra,dec,st_rad,pl_radj,pl_trandep,pl_trandur,pl_trandurerr1,pl_trandurerr2,pl_tranmid,pl_tranmiderr1,pl_tranmiderr2,pl_imppar,pl_ratdor,pl_ratror,sy_vmag,sy_gaiamag+from+ps+where+tran_flag=1&format=csv'
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        logger.info("Response code "+str(response.status_code))
        logger.info("Processing data from NASA Exoplanet Archive")
        from io import StringIO
        csv_data = response.text
        csv_reader = csv.DictReader(StringIO(csv_data))

        for row in csv_reader:
            # Map CSV columns to model fields
            data = {
                'targetName'        :   row['pl_name']                  if row['pl_name'] else None,
                'targetOrbPer'      :   float(row['pl_orbper'])         if row['pl_orbper'] else None,
                'targetOrbPerErr1'  :   float(row['pl_orbpererr1'])     if row['pl_orbpererr1'] else None,
                'targetOrbPerErr2'  :   float(row['pl_orbpererr2'])     if row['pl_orbpererr2'] else None,
                'targetOrbSMAxis'   :   float(row['pl_orbsmax'])        if row['pl_orbsmax'] else None,
                'targetOrbIncl'     :   float(row['pl_orbincl'])        if row['pl_orbincl'] else None,
                'targetRAStr'       :   row['rastr']                    if row['rastr'] else None,
                'targetDecStr'      :   row['decstr']                   if row['decstr'] else None,
                'targetRA2000'      :   float(row['ra'])                if row['ra'] else None,
                'targetDec2000'     :   float(row['dec'])               if row['dec'] else None,
                'targetStelRadius'  :   float(row['st_rad'])            if row['st_rad'] else None,
                'targetPlRadius'    :   float(row['pl_radj'])           if row['pl_radj'] else None,
                'targetTrDepth'     :   float(row['pl_trandep'])        if row['pl_trandep'] else None,
                'targetTrDur'       :   float(row['pl_trandur'])        if row['pl_trandur'] else None,
                'targetTrDurErr1'   :   float(row['pl_trandurerr1'])    if row['pl_trandurerr1'] else None,
                'targetTrDurErr2'   :   float(row['pl_trandurerr2'])    if row['pl_trandurerr2'] else None,
                'targetTrMid'       :   float(row['pl_tranmid'])        if row['pl_tranmid'] else None,
                'targetTrMidErr1'   :   float(row['pl_tranmiderr1'])    if row['pl_tranmiderr1'] else None,
                'targetTrMidErr2'   :   float(row['pl_tranmiderr2'])    if row['pl_tranmiderr2'] else None,
                'targetImpPar'      :   float(row['pl_imppar'])         if row['pl_imppar'] else None,
                'targetRatDor'      :   float(row['pl_ratdor'])         if row['pl_ratdor'] else None,
                'targetRarRor'      :   float(row['pl_ratror'])         if row['pl_ratror'] else None,
                'targetVMag'        :   float(row['sy_vmag'])           if row['sy_vmag'] else None,
                'targetGaiaMag'     :   float(row['sy_gaiamag'])        if row['sy_gaiamag'] else None         
            }
            Exoplanet.objects.create(**data)
    
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

class GCVS(models.Model):
    CONSTELLATIONS = {
    '01': 'AND',
    '02': 'ANT',
    '03': 'APS',
    '04': 'AQR',
    '05': 'AQL',
    '06': 'ARA',
    '07': 'ARI',
    '08': 'AUR',
    '09': 'BOO',
    '10': 'CAE',
    '11': 'CAM',
    '12': 'CNC',
    '13': 'CVN',
    '14': 'CMA',
    '15': 'CMI',
    '16': 'CAP',
    '17': 'CAR',
    '18': 'CAS',
    '19': 'CEN',
    '20': 'CEP',
    '21': 'CET',
    '22': 'CHA',
    '23': 'CIR',
    '24': 'COL',
    '25': 'COM',
    '26': 'CRA',
    '27': 'CRB',
    '28': 'CRV',
    '29': 'CRT',
    '30': 'CRU',
    '31': 'CYG',
    '32': 'DEL',
    '33': 'DOR',
    '34': 'DRA',
    '35': 'EQU',
    '36': 'ERI',
    '37': 'FOR',
    '38': 'GEM',
    '39': 'GRU',
    '40': 'HER',
    '41': 'HOR',
    '42': 'HYA',
    '43': 'HYI',
    '44': 'IND',
    '45': 'LAC',
    '46': 'LEO',
    '47': 'LMI',
    '48': 'LEP',
    '49': 'LIB',
    '50': 'LUP',
    '51': 'LYN',
    '52': 'LYR',
    '53': 'MEN',
    '54': 'MIC',
    '55': 'MON',
    '56': 'MUS',
    '57': 'NOR',
    '58': 'OCT',
    '59': 'OPH',
    '60': 'ORI',
    '61': 'PAV',
    '62': 'PEG',
    '63': 'PER',
    '64': 'PHE',
    '65': 'PIC',
    '66': 'PSC',
    '67': 'PSA',
    '68': 'PUP',
    '69': 'PYX',
    '70': 'RET',
    '71': 'SGE',
    '72': 'SGR',
    '73': 'SCO',
    '74': 'SCL',
    '75': 'SCT',
    '76': 'SER',
    '77': 'SEX',
    '78': 'TAU',
    '79': 'TEL',
    '80': 'TRI',
    '81': 'TRA',
    '82': 'TUC',
    '83': 'UMA',
    '84': 'UMI',
    '85': 'VEL',
    '86': 'VIR',
    '87': 'VOL',
    '88': 'VUL',
    }
    CONSTELLATION_SHORT = [
        ('All', 'All'),
        ('AND', 'Andromeda'),
        ('ANT', 'Antlia'),
        ('APS', 'Apus'),
        ('AQR', 'Aquarius'),
        ('AQL', 'Aquila'),
        ('ARA', 'Ara'),
        ('ARI', 'Aries'),
        ('AUR', 'Auriga'),
        ('BOO', 'Boötes'),
        ('CAE', 'Caelum'),
        ('CAM', 'Camelopardalis'),
        ('CNC', 'Cancer'),
        ('CVN', 'Canes Venatici'),
        ('CMA', 'Canis Major'),
        ('CMI', 'Canis Minor'),
        ('CAP', 'Capricornus'),
        ('CAR', 'Carina'),
        ('CAS', 'Cassiopeia'),
        ('CEN', 'Centaurus'),
        ('CEP', 'Cepheus'),
        ('CET', 'Cetus'),
        ('CHA', 'Chamaeleon'),
        ('CIR', 'Circinus'),
        ('COL', 'Columba'),
        ('COM', 'Coma Berenices'),
        ('CRA', 'Corona Australis'),
        ('CRB', 'Corona Borealis'),
        ('CRV', 'Corvus'),
        ('CRT', 'Crater'),
        ('CRU', 'Crux'),
        ('CYG', 'Cygnus'),
        ('DEL', 'Delphinus'),
        ('DOR', 'Dorado'),
        ('DRA', 'Draco'),
        ('EQU', 'Equuleus'),
        ('ERI', 'Eridanus'),
        ('FOR', 'Fornax'),
        ('GEM', 'Gemini'),
        ('GRU', 'Grus'),
        ('HER', 'Hercules'),
        ('HOR', 'Horologium'),
        ('HYA', 'Hydra'),
        ('HYI', 'Hydrus'),
        ('IND', 'Indus'),
        ('LAC', 'Lacerta'),
        ('LEO', 'Leo'),
        ('LMI', 'Leo Minor'),
        ('LEP', 'Lepus'),
        ('LIB', 'Libra'),
        ('LUP', 'Lupus'),
        ('LYN', 'Lynx'),
        ('LYR', 'Lyra'),
        ('MEN', 'Mensa'),
        ('MIC', 'Microscopium'),
        ('MON', 'Monoceros'),
        ('MUS', 'Musca'),
        ('NOR', 'Norma'),
        ('OCT', 'Octans'),
        ('OPH', 'Ophiuchus'),
        ('ORI', 'Orion'),
        ('PAV', 'Pavo'),
        ('PEG', 'Pegasus'),
        ('PER', 'Perseus'),
        ('PHE', 'Phoenix'),
        ('PIC', 'Pictor'),
        ('PSC', 'Pisces'),
        ('PSA', 'Piscis Austrinus'),
        ('PUP', 'Puppis'),
        ('PYX', 'Pyxis'),
        ('RET', 'Reticulum'),
        ('SGE', 'Sagitta'),
        ('SGR', 'Sagittarius'),
        ('SCO', 'Scorpius'),
        ('SCL', 'Sculptor'),
        ('SCT', 'Scutum'),
        ('SER', 'Serpens'),
        ('SEX', 'Sextans'),
        ('TAU', 'Taurus'),
        ('TEL', 'Telescopium'),
        ('TRI', 'Triangulum'),
        ('TRA', 'Triangulum Australe'),
        ('TUC', 'Tucana'),
        ('UMA', 'Ursa Major'),
        ('UMI', 'Ursa Minor'),
        ('VEL', 'Vela'),
        ('VIR', 'Virgo'),
        ('VOL', 'Volans'),
        ('VUL', 'Vulpecula'),
    ]
    TRANSLATION_MAP = {ord(ch): None for ch in '():/'}
    targetId            = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    constellation       = models.CharField(max_length=255, choices=CONSTELLATION_SHORT)
    name                = models.CharField(max_length=255)
    ra                  = models.FloatField(null=True)
    dec                 = models.FloatField(null=True)
    variable_type       = models.CharField(max_length=255,null=True)
    max_magnitude       = models.CharField(max_length=255,null=True)
    min_magnitude       = models.CharField(max_length=255,null=True)
    epoch               = models.CharField(max_length=255,null=True)
    period              = models.FloatField(null=True)
    targetClass         = models.CharField(max_length=255,default="VS")

    def __str__(self):
        return f"{self.name}"
    
    def row_to_dict(self, row):
        """
        Converts a raw GCVS record to a dictionary of star data.
        """
        constellation = self.parse_constellation(self,row[0])
        name = self.parse_name(self,row[1])
        ra, dec = self.parse_coordinates(self,row[2])
        variable_type = row[3].strip()
        max_magnitude, symbol = self.parse_magnitude(self,row[4])
        min_magnitude, symbol = self.parse_magnitude(self,row[5])
        if symbol == '(' and max_magnitude is not None:
            # this is actually amplitude
            min_magnitude = max_magnitude + min_magnitude
        epoch = self.parse_epoch(self,row[8])
        period = self.parse_period(self,row[10])
        return {
            'constellation': constellation,
            'name': name,
            'ra': ra,
            'dec': dec,
            'variable_type': variable_type,
            'max_magnitude': max_magnitude,
            'min_magnitude': min_magnitude,
            'epoch': epoch,
            'period': period,
        }

    def parse_constellation(self, constellation_str):
        constellation_num = constellation_str[:2]
        return self.CONSTELLATIONS[constellation_num]

    def parse_name(self, name_str):
        """
        Normalizes variable star designation (name).
        """
        name = name_str[:9]
        return ' '.join(name.split()).upper()

    def parse_coordinates(self, coords_str):
        """
        Returns a pair of floats (Ra, Dec) in deimcal hours and decimal degrees.

        If the star has no coordinates in GCVS (there are such cases), a pair
        of None values is returned.
        """
        if coords_str.strip() == '':
            return (None, None)
        ra = float(coords_str[0:2])+float(coords_str[2:4])/60.0+float(coords_str[4:8])/3600.0
        dec = float(coords_str[8:11])+float(coords_str[11:13])/60.0+float(coords_str[13:15])/3600.0
        return (ra, dec)

    def parse_magnitude(self, magnitude_str):
        """
        Converts magnitude field to a float value, or ``None`` if GCVS does
        not list the magnitude.

        Returns a tuple (magnitude, symbol), where symbol can be either an
        empty string or a single character - one of '<', '>', '('.
        """
        symbol = magnitude_str[0].strip()
        magnitude = magnitude_str[1:6].strip()
        return magnitude if magnitude else None, symbol

    def parse_epoch(self, epoch_str):
        """
        Converts epoch field to a float value (adding 24... prefix), or
        ``None`` if there is no epoch in GCVS record.
        """
        epoch = epoch_str.translate(self.TRANSLATION_MAP)[:10].strip()
        # remove any non-numeric characters
        import re
        epoch=re.sub("[^\d\.]", "", epoch)
        return 2400000.0 + float(epoch) if epoch else None

    def parse_period(self, period_str):
        """
        Converts period field to a float value or ``None`` if there is
        no period in GCVS record.
        """
        period = period_str.translate(self.TRANSLATION_MAP)[3:14].strip()
        return float(period) if period else None
    
    @classmethod
    def populate_db(self):
        logger.info("Populating GCVS data")
        stars = []
        try:
            with open('standard_data/iii.txt', 'r') as fp:
                reader = csv.reader(fp, delimiter=str('|'))
                # skip two initial lines
                next(reader)
                next(reader)

                for row in reader:
                    if len(row) != 15:
                        continue
                    try:
                        # Append to dict  
                        row_dict=self.row_to_dict(self,row)
                        logger.debug("Row inserted: %s", row_dict['name'])
                        GCVS.objects.create(**row_dict)
                    except Exception as e:
                        logger.exception("Error %s in row: %s",str(e), row)
                        continue
        except Exception as e:
            logger.error("Error reading GCVS file: %s", e)
        return

##################################################################################################
## ExoplanetFilter - this model is used to store the filter settings for the Exoplanet db       ##
##################################################################################################
class ExoplanetFilter(models.Model):
    configId                = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    min_transit_duration    = models.FloatField(null=True, blank=True)
    max_transit_duration    = models.FloatField(null=True, blank=True)
    min_depth               = models.FloatField(null=True, blank=True)
    max_depth               = models.FloatField(null=True, blank=True)
    min_altitude            = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Exoplanet Filter {self.configId}"
    