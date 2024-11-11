from django.db import models
from django.urls import reverse
import uuid

class observatory(models.Model):
    observatoryId  = models.UUIDField( 
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False)
    name      =models.CharField(max_length=200)
    shortname =models.CharField(max_length=200)
    latitude  =models.DecimalField(max_digits = 8,decimal_places = 6,default=0.0)
    longitude =models.DecimalField(max_digits = 9,decimal_places = 6,default=0.0)
    elevation =models.DecimalField(max_digits = 6,decimal_places = 2,default=0.0)
    tz        =models.CharField(max_length=200)
    
    def __str__(self):
        return self.shortname
    
    def get_absolute_url(self):
        return reverse("observatory_detail", args=[self.observatoryId])
    
 
class telescope(models.Model):
    TELESCOPE_TYPES=(
        ("NE", "Newtonian"),
        ("SC", "Schmidt-Cassegrain"),
        ("CC", "Classical Cassegrain"),
        ("RC", "Ritchey Cretien Cassegrain"), 
        ("MC", "Mak-Cassegrain"),
        ("RE","Refractor"),
        ("OT", "Other"),
    )
    
    telescopeId   =models.UUIDField( 
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False)
    name      =models.CharField(max_length=200)
    shortname =models.CharField(max_length=200)
    telescopeType=models.CharField(max_length=2,choices=TELESCOPE_TYPES, default='NE')
    aperture    =models.DecimalField(max_digits = 6,decimal_places = 2)
    focalLength =models.DecimalField(max_digits = 6,decimal_places = 2)
    observatoryId =models.ForeignKey('observatory', on_delete=models.CASCADE,null=True, blank=True)
    
    def __str__(self):
        return self.shortname
    
    def get_absolute_url(self):
        return reverse("telescope_detail", args=[self.telescopeId])
    
class imager(models.Model):
    IMAGER_TYPES=(
        ("CMOS", "CMOS"),
        ("CCD", "CCD"),
        )
    imagerId  = models.UUIDField( 
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False)
    name      =models.CharField(max_length=200)
    shortname =models.CharField(max_length=200)
    imagerType=models.CharField(max_length=4,choices=IMAGER_TYPES, default='CMOS')
    xDim=models.DecimalField(max_digits = 5,decimal_places = 0)
    yDim=models.DecimalField(max_digits = 5,decimal_places = 0)
    xPixelSize=models.DecimalField(max_digits = 6,decimal_places = 2)
    yPixelSize=models.DecimalField(max_digits = 6,decimal_places = 2)
   
    def __str__(self):
        return self.shortname
    def get_absolute_url(self):
        return reverse("imager_detail", args=[self.imagerId])

