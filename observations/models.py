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
