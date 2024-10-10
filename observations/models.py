import uuid
from targets.models import target  
from django.db import models
from setup.models import observatory, telescope, imager
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime

##################################################################################################
## observation - a request and subsequent updates on the observations required of a target      ##
##################################################################################################    
class observation(models.Model):
    observationId        = models.UUIDField( 
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False)
    observationDate     = models.DateField(null=True, blank=True)
    targetId        = models.ForeignKey(target, on_delete=models.CASCADE,null=True, blank=True)
    userId          = models.CharField(max_length=255)
    targetPA        = models.DecimalField(default=0.0,max_digits=6, decimal_places=2,null=True, blank=True)
    targetInactive  = models.BooleanField(default=False)
    observeOnce     = models.BooleanField(default=False)
    # Additional data selected
    observatoryId     = models.ForeignKey(observatory, on_delete=models.CASCADE,null=True, blank=True)
    telescopeId       = models.ForeignKey(telescope, on_delete=models.CASCADE,null=True, blank=True)
    imagerId          = models.ForeignKey(imager, on_delete=models.CASCADE,null=True, blank=True)
    
    def __str__(self):
        return f"{self.targetId}"
    def get_absolute_url(self):
        return reverse("observation_detail", args=[str(self.observationId)])
    
##################################################################################################
## scheduleMaster -   this model is the master record for a schedule and has n children         ##
##              consisting of targets and associated observation strategy information           ##
##################################################################################################
class scheduleMaster(models.Model):
    
    scheduleMasterId              = models.UUIDField( 
                                primary_key=True,
                                default=uuid.uuid4,
                                editable=False)
    userId                  = models.CharField(max_length=255,null=True, blank=True)
    scheduleDate            = models.DateField(null=True, blank=True)
    scheduleDays            = models.IntegerField(null=True, blank=True) 
    observatoryId           = models.ForeignKey(observatory, on_delete=models.CASCADE,null=True, blank=True)
    telescopeId             = models.ForeignKey(telescope, on_delete=models.CASCADE,null=True, blank=True)
    imagerId                = models.ForeignKey(imager, on_delete=models.CASCADE,null=True, blank=True)
    startUpUnparkDome       = models.BooleanField(default=False,null=True, blank=True)
    startUpUnparkMount      = models.BooleanField(default=False,null=True, blank=True)
    startUpUnCap            = models.BooleanField(default=False,null=True, blank=True)
    onAbortJobMgmt          = models.CharField(max_length=10,choices=[("None","None"),("Queue","Queue"),("Immediate","Immediate")],default="None",null=True, blank=True)
    rescheduleErrorsSecs    = models.IntegerField(default=0,null=True, blank=True)
    jobConstraintsAlt       = models.DecimalField(default=0.0,max_digits=6, decimal_places=2,null=True, blank=True)
    jobConstraintsMoon      = models.DecimalField(default=0.0,max_digits=6, decimal_places=2,null=True, blank=True)
    jobConstraintsWeather   = models.BooleanField(default=False,null=True, blank=True)
    jobConstraintTwilight   = models.BooleanField(default=False,null=True, blank=True)
    jobConstraintArtHor     = models.BooleanField(default=False,null=True, blank=True)
    jobCompleteCondSeq      = models.BooleanField(default=False,null=True, blank=True)
    jobCompleteCondRepeatNo = models.IntegerField(default=0,null=True, blank=True)  
    jobCompleteCondRepeatAll    = models.BooleanField(default=False,null=True, blank=True)
    jobCompleteCondRepeatUntil  = models.DateField(null=True, blank=True) 
    ShutDownParkDome       = models.BooleanField(default=False,null=True, blank=True)
    ShutDownParkMount      = models.BooleanField(default=False,null=True, blank=True)
    ShutDownCap            = models.BooleanField(default=False,null=True, blank=True)
   
    def __str__(self):
        return f"{self.scheduleMasterId}"
    
    def get_absolute_url(self):
        return reverse("schedule_details", args=[str(self.scheduleMasterId)])

class ScheduleManager(models.Manager):
    def delete_everything(self):
        scheduleMaster.objects.all().delete()

##################################################################################################
## scheduleDetail - this model contains child records for schedule masters that contain         ##
##                  targets and associated observation strategy information                     ##
##################################################################################################
class scheduleDetail(models.Model):
    scheduleDetailId        = models.UUIDField( 
                                primary_key=True,
                                default=uuid.uuid4,
                                editable=False)
    scheduleMasterId              = models.ForeignKey(scheduleMaster, on_delete=models.CASCADE)
    scheduledDateTime       = models.DateTimeField()
    targetPriority          = models.IntegerField(default=1,validators=[MaxValueValidator(100),MinValueValidator(1)])
    targetId                = models.ForeignKey(target, on_delete=models.CASCADE)
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
## sequenceFile - this model allows storage of XML EKOS Sequence Files                          ##
##################################################################################################
class sequenceFile(models.Model):
    MAX_FILE_SIZE=4096
    sequenceFileId        = models.UUIDField( 
                                primary_key=True,
                                default=uuid.uuid4,
                                editable=False)
    sequenceFileName      = models.FileField(max_length=MAX_FILE_SIZE,upload_to='sequence')
    sequenceFileData      = models.CharField(max_length=MAX_FILE_SIZE)
    
##################################################################################################
## scheduleFile - this model allows storage of XML EKOS Sequence Files                          ##
##################################################################################################
class scheduleFile(models.Model):
    MAX_FILE_SIZE=4096
    scheduleFileId          = models.UUIDField( 
                                primary_key=True,
                                default=uuid.uuid4,
                                editable=False)
    scheduleFileName        = models.FileField(max_length=MAX_FILE_SIZE,upload_to='schedule') 
    scheduleFileData        = models.CharField(max_length=MAX_FILE_SIZE)
