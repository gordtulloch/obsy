import uuid
from django.db import models
from django.urls import reverse
from setup.models import observatory, telescope, imager
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime
import csv

##################################################################################################
## target - an object for which we may wish to create an observation                           ##
################################################################################################## 
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
    targetName      = models.CharField(max_length=255)
    targetClass     = models.CharField(max_length=2,choices=TARGET_CLASSES)
    targetType      = models.CharField(max_length=255)
    targetRA2000    = models.CharField(max_length=200)
    targetDec2000   = models.CharField(max_length=200)
    targetConst     = models.CharField(max_length=200)
    targetMag       = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.targetName}"
    def get_absolute_url(self):
        return reverse("target_detail", args=[str(self.targetId)])

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
    
