from django.db import models

class observatory(models.Model):
    observatoryId  =models.CharField(max_length=200,primary_key=True)
    name      =models.CharField(max_length=200)
    shortname =models.CharField(max_length=200)
    latitude  =models.DecimalField(max_digits = 8,decimal_places = 6,default=0.0)
    longitude =models.DecimalField(max_digits = 9,decimal_places = 6,default=0.0)
    elevation =models.DecimalField(max_digits = 6,decimal_places = 2,default=0.0)
    tz        =models.CharField(max_length=200)
    telescopeId  = models.ForeignKey('telescope', on_delete=models.CASCADE,null=True, blank=True)
    imagerId      = models.ForeignKey('imager', on_delete=models.CASCADE,null=True, blank=True)
    
    def __str__(self):
        return self.name
    
class observer(models.Model):
    observerId  =models.CharField(max_length=200,primary_key=True)
    firstname  =models.CharField(max_length=200)
    middlename =models.CharField(max_length=200,blank=True)
    lastname   =models.CharField(max_length=200)
    tz         =models.CharField(max_length=200) 
    observatoryId=models.ForeignKey('observatory', on_delete=models.CASCADE,null=True, blank=True)
        
    def __str__(self):
        return self.observerId
    
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
    
    telescopeId   =models.CharField(max_length=200,primary_key=True)
    name      =models.CharField(max_length=200)
    shortname =models.CharField(max_length=200)
    telescopeType=models.CharField(max_length=2,choices=TELESCOPE_TYPES, default='NE')
    aperture    =models.DecimalField(max_digits = 6,decimal_places = 2)
    focalLength =models.DecimalField(max_digits = 6,decimal_places = 2)
    observatoryId =models.ForeignKey('observatory', on_delete=models.CASCADE,null=True, blank=True)
    
    def __str__(self):
        return self.name
    
class imager(models.Model):
    IMAGER_TYPES=(
        ("CMOS", "CMOS"),
        ("CCD", "CCD"),
        )
    imagerId  =models.CharField(max_length=200,primary_key=True)
    name      =models.CharField(max_length=200)
    shortname =models.CharField(max_length=200)
    imagerType=models.CharField(max_length=4,choices=IMAGER_TYPES, default='CMOS')
    xDim=models.DecimalField(max_digits = 5,decimal_places = 0)
    yDim=models.DecimalField(max_digits = 5,decimal_places = 0)
    xPixelSize=models.DecimalField(max_digits = 6,decimal_places = 2)
    yPixelSize=models.DecimalField(max_digits = 6,decimal_places = 2)
   
    def __str__(self):
        return self.name


