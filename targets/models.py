import uuid
from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator

class target(models.Model):
    
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
    userId          = models.CharField(max_length=255)
    targetName      = models.CharField(max_length=255)
    targetClass     = models.CharField(max_length=2,choices=TARGET_CLASSES)
    targetType      = models.CharField(max_length=255)
    targetRA2000    = models.CharField(max_length=200)
    targetDec2000   = models.CharField(max_length=200)
    targetConst     = models.CharField(max_length=200)
    targetMag       = models.CharField(max_length=200)
    targetPA        = models.DecimalField(default=0.0,max_digits=6, decimal_places=2)
    targetInactive  = models.BooleanField(default=False)
    observeOnce     = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.targetId}"
    def get_absolute_url(self):
        return reverse("target_detail", args=[str(self.targetId)])

##################################################################################################
## schedule -   this model is the master record for a schedule and has n children consisting of ##
##              targets and associated observation strategy information                         ##
##################################################################################################
class scheduleMaster(models.Model):
    
    scheduleId              = models.UUIDField( 
                                primary_key=True,
                                default=uuid.uuid4,
                                editable=False)
    userId                  = models.CharField(max_length=255)
    scheduleDate            = models.DateField()
    startUpUnparkDome       = models.BooleanField(default=False)
    startUpUnparkMount      = models.BooleanField(default=False)
    startUpUnCap            = models.BooleanField(default=False)
    onAbortJobMgmt          = models.CharField(max_length=10,choices=[("None","None"),("Queue","Queue"),("Immediate","Immediate")],default="None")
    rescheduleErrorsSecs    = models.IntegerField(default=0)
    jobConstraintsAlt       = models.DecimalField(default=0.0,max_digits=6, decimal_places=2)
    jobConstraintsMoon      = models.DecimalField(default=0.0,max_digits=6, decimal_places=2)
    jobConstraintsWeather   = models.BooleanField(default=False)
    jobConstraintTwilight   = models.BooleanField(default=False)
    jobConstraintArtHor     = models.BooleanField(default=False)
    jobCompleteCondSeq      = models.BooleanField(default=False)
    jobCompleteCondRepeatNo = models.IntegerField(default=0)  
    jobCompleteCondRepeatAll    = models.BooleanField(default=False)
    jobCompleteCondRepeatUntil  = models.DateField() 
    ShutDownParkDome       = models.BooleanField(default=False)
    ShutDownParkMount      = models.BooleanField(default=False)
    ShutDownCap            = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.scheduleId}"
    def get_absolute_url(self):
        return reverse("schedule_detail", args=[str(self.targetId)])

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
    scheduleId              = models.ForeignKey(scheduleMaster, on_delete=models.CASCADE)
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
        return reverse("schedule_detail", args=[str(self.scheduleDetailId)])

##################################################################################################
## sequenceFile - this model allows storage of XML EKOS Sequence Files                          ##
##################################################################################################
class sequenceFile(models.Model):
    MAX_FILE_SIZE=4096
    sequenceFileId        = models.UUIDField( 
                                primary_key=True,
                                default=uuid.uuid4,
                                editable=False)
    sequenceFilePath      = models.FileField(max_length=MAX_FILE_SIZE,upload_to="sequence/")
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
    scheduleFilePath        = models.FileField(max_length=MAX_FILE_SIZE,upload_to="schedule/") 
    scheduleFileData       = models.CharField(max_length=MAX_FILE_SIZE)
    
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