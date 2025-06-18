import uuid
from targets.models import Target
from setup.models import observatory, telescope, imager
from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime
import pytz
import ephem
from astropy.time import Time
from astropy.coordinates import AltAz, EarthLocation
from datetime import timedelta
from django.db.models import Q
from django.utils import timezone

import logging
logger = logging.getLogger(__name__)

##################################################################################################
## SequenceFile - a EKOS sequence file                                                          ##
##################################################################################################
class sequenceFile(models.Model):
    sequenceId        = models.UUIDField( 
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False)
    sequenceFileName  = models.CharField(max_length=255)
    sequenceData      = models.CharField(max_length=4096)   
    sequenceDuration  = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.sequenceFileName}"
    def get_absolute_url(self):
        return reverse("sequence_detail", args=[str(self.sequenceId)])

##################################################################################################
## Observation - a request and subsequent updates on the observations required of a Target      ##
##################################################################################################    
class Observation(models.Model):
    observationId       = models.UUIDField( 
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False)
    observationDate     = models.DateField(null=True, blank=True)
    targetId        = models.UUIDField()
    targetName      = models.CharField(max_length=255)
    targetClass     = models.CharField(max_length=255,null=True, blank=True)
    userId          = models.CharField(max_length=255)
    targetPA        = models.DecimalField(default=0.0,max_digits=6, decimal_places=2,null=True, blank=True)
    targetInactive  = models.BooleanField(default=False)
    observeOnce     = models.BooleanField(default=False)
    status            = models.CharField(max_length=255,null=True, default="Pending")
    # Additional data selected
    observatoryId     = models.ForeignKey(observatory, on_delete=models.CASCADE,null=True, blank=True)
    telescopeId       = models.ForeignKey(telescope, on_delete=models.CASCADE,null=True, blank=True)
    imagerId          = models.ForeignKey(imager, on_delete=models.CASCADE,null=True, blank=True)
    sequenceFileId    = models.ForeignKey(sequenceFile, on_delete=models.CASCADE,null=True, blank=True)
    # Additional data from the schedule
    scheduleMasterId  = models.ForeignKey('scheduleMaster', on_delete=models.CASCADE,null=True, blank=True) 
    scheduledDateTime = models.DateTimeField(null=True, blank=True)
    actualDateTime    = models.DateTimeField(null=True, blank=True)
    actualDuration    = models.IntegerField(default=0)
    fitsFileSequence  = models.ForeignKey('fitsSequence', on_delete=models.CASCADE,null=True, blank=True)
    
    def __str__(self):
        return f"{self.targetId}"
    
    def get_absolute_url(self):
        return reverse("observation_detail", args=[str(self.observationId)])
    
class ObservationDS(Observation):
    # fields specific to Deep Sky observations
    pass

class ObservationEX(Observation):
    # fields specific to Exoplanet observations
    pass

class ObservationVS(Observation):
    # fields specific to Variable Star observations
    pass

##################################################################################################
## scheduleDetail - this model contains child records for schedule masters that contain         ##
##                  targets and associated Observation strategy information                     ##
##################################################################################################
class scheduleDetail(models.Model):
    scheduleDetailId        = models.UUIDField( 
                                primary_key=True,
                                default=uuid.uuid4,
                                editable=False)
    scheduleMasterId        = models.ForeignKey('scheduleMaster', on_delete=models.CASCADE)
    targetId                = models.ForeignKey(Target, on_delete=models.CASCADE)  
    scheduledDateTime       = models.DateTimeField()
    targetPriority          = models.IntegerField(default=1,validators=[MaxValueValidator(100),MinValueValidator(1)])
    requiredStartTime       = models.DateTimeField()
    requiredStartCulOffset  = models.DecimalField(max_digits=6, decimal_places=2)
    jobConstraintsAlt       = models.DecimalField(max_digits=6, decimal_places=2,default=0.0)
    jobConstraintsMoon      = models.DecimalField(max_digits=6, decimal_places=2,default=0.0)
    jobConstraintsWeather   = models.BooleanField(default=False)
    jobConstraintTwilight   = models.BooleanField(default=False)
    jobConstraintArtHor     = models.BooleanField(default=False)
    jobStepTrack            = models.BooleanField(default=True)
    jobStepFocus            = models.BooleanField(default=True)
    jobStepAlign            = models.BooleanField(default=True)
    jobStepGuide            = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.scheduleDetailId}" 
    def get_absolute_url(self):
        return reverse("schedule_details_item", args=[str(self.scheduleDetailId)]) 
    
##################################################################################################
## scheduleMaster -   this model is the master record for a schedule and has n children         ##
##              consisting of targets and associated Observation strategy information           ##
##################################################################################################
class scheduleMaster(models.Model):
    scheduleMasterId    = models.UUIDField( 
                                primary_key=True,
                                default=uuid.uuid4,
                                editable=False)
    scheduleDate       = models.DateField(default=datetime.now, blank=True)
    scheduleDays       = models.IntegerField(default=1,validators=[MaxValueValidator(365),MinValueValidator(1)])
    observatoryId       = models.ForeignKey(observatory, on_delete=models.CASCADE)
    imagerId            = models.ForeignKey(imager, on_delete=models.CASCADE,null=True, blank=True)
    sequenceFileId      = models.ForeignKey(sequenceFile, on_delete=models.CASCADE,null=True, blank=True)
    observations        = models.ManyToManyField(scheduleDetail)

    def get_absolute_url(self):
        return reverse("scheduleMasterList", args=[str(self.scheduleMasterId)])

    def regenSchedule(self):          
        self.daysToSchedule = self.scheduleDays 
        try:
            observatoryObj = observatory.objects.get(id=self.observatoryId)
        except observatory.DoesNotExist:
            logger.error("Invalid observatory_id")
            return
        
        # Load operations.currentConfig where observatory=observatory_id
        try:
            currentConfig = currentConfig.objects.get().filter(observatoryId=self.observatoryId)
        except currentConfig.DoesNotExist:
            logger.error("No currentConfig found")
            return
            
        # Load the telescope and imager objects from the currentConfig
        telescopeList = []
        imagerList = []
        for thisConfig in currentConfig:
            self.telescopeList.append(thisConfig.telescopeId)
            self.imagerList.append(thisConfig.imagerId)

        # Calculate astronomical twilight and dawn using ephem
        location = ephem.Observer()
        location.lat = str(observatoryObj.latitude)
        location.lon = str(observatoryObj.longitude)
        times = []
        
        for day in range(self.daysToSchedule):
            date = self.scheduleDate + timedelta(days=self.scheduleDays)
            location.date = date
            twilight_evening = location.next_setting(ephem.Sun(), use_center=True)
            twilight_morning = location.next_rising(ephem.Sun(), use_center=True)
            times.append((twilight_evening.datetime(), twilight_morning.datetime()))

        # Query the database and add observations to scheduleDetail records
        for twilight_evening, twilight_morning in times:
            observations = Observation.objects.filter(
                observatory=self.observatoryId,
                telescope=self.telescope_id,
                imager=imager_id,
                observation_date__range=(twilight_evening, twilight_morning)
            )
            for obs in observations:
                obs_time = Time(obs.observation_date)
                obs_altaz = AltAz(obstime=obs_time, location=EarthLocation(lat=observatory_obj.latitude, lon=observatory_obj.longitude))
                obs_altitude = obs.Target.transform_to(obs_altaz).alt

                if obs_altitude > 15 * u.deg:
                    schedule_master.observations.add(obs)

        return

##################################################################################################
## ScheduleManager - this manager class is used to delete all scheduleMaster records            ##
##################################################################################################
class ScheduleManager(models.Manager):
    def delete_everything(self):
        scheduleMaster.objects.all().delete()

##################################################################################################
## fitsFile - this model points to a physical fits file in a repository                         ##
##################################################################################################
class fitsFile(models.Model):
    fitsFileId          = models.UUIDField( 
                                primary_key=True,
                                default=uuid.uuid4,
                                editable=False)
    fitsFileName        = models.CharField(max_length=255, default="None",null=True, blank=True) 
    fitsFileDate        = models.DateTimeField(default=datetime.now().replace(tzinfo=pytz.UTC))
    fitsFileCalibrated  = models.BooleanField(default=False)
    fitsFileType        = models.CharField(max_length=255, default="None",null=True, blank=True)
    fitsFileStacked     = models.BooleanField(default=False)
    fitsFileObject      = models.CharField(max_length=255, default="None",null=True, blank=True)
    fitsFileExpTime     = models.CharField(max_length=255, default="None",null=True, blank=True)
    fitsFileXBinning    = models.CharField(max_length=255, default="None",null=True, blank=True)
    fitsFileYBinning    = models.CharField(max_length=255, default="None",null=True, blank=True)
    fitsFileCCDTemp     = models.CharField(max_length=255, default="None",null=True, blank=True)
    fitsFileTelescop    = models.CharField(max_length=255, default="None",null=True, blank=True)
    fitsFileInstrument  = models.CharField(max_length=255, default="None",null=True, blank=True)
    fitsFileGain        = models.CharField(max_length=255, default="None",null=True, blank=True)
    fitsFileOffset      = models.CharField(max_length=255, default="None",null=True, blank=True)
    fitsFileSequence    = models.UUIDField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.fitsFileName}"
    
    def get_absolute_url(self):
        return reverse("fits_file_detail", kwargs={'pk': self.pk})
    
    def display_name(self):
        if self.fitsFileType in ["Flat", "Dark", "Bias"]:
            return self.fitsFileType
        return self.fitsFileObject
    
##################################################################################################
## fitsSequence - this model records a sequence of files and the calibration master files used  ##
##################################################################################################
class fitsSequence(models.Model):
    fitsSequenceId        = models.UUIDField(
                                primary_key=True,
                                default=uuid.uuid4,
                                editable=False)
    fitsSequenceObjectName = models.CharField(max_length=255, null=True, blank=True)
    fitsSequenceDate      = models.DateTimeField(null=True, blank=True)
    fitsSequenceTelescope = models.CharField(max_length=255, null=True, blank=True)
    fitsSequenceImager    = models.CharField(max_length=255, null=True, blank=True)
    fitsMasterBias       = models.CharField(max_length=255, null=True, blank=True)
    fitsMasterDark       = models.CharField(max_length=255, null=True, blank=True)
    fitsMasterFlat       = models.UUIDField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.fitsSequenceId}"
    
