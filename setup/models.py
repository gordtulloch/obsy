from django.db import models

class fitsFile(models.Model):
    fitsFileId=models.CharField(max_length=200,primary_key=True)
    date    =models.DateField()
    filename=models.CharField(max_length=512)
    
    def __str__(self):
        return self.thisUNID
    
class fitsHeader(models.Model):
    fitsHeaderId  =models.CharField(max_length=200,primary_key=True)
    parentUNID=models.ForeignKey(fitsFile, on_delete=models.CASCADE)
    keyword   =models.CharField(max_length=200)
    value     =models.CharField(max_length=200)
    
    def __str__(self):
        return self.thisUNID
    
class observatory(models.Model):
    observatoryId  =models.CharField(max_length=200,primary_key=True)
    name      =models.CharField(max_length=200)
    shortname =models.CharField(max_length=200)
    latitude  =models.DecimalField(max_digits = 6,decimal_places = 2,default=0.0)
    longitude =models.DecimalField(max_digits = 6,decimal_places = 2,default=0.0)
    elevation =models.DecimalField(max_digits = 6,decimal_places = 2,default=0.0)
    tz        =models.CharField(max_length=200)
    def __str__(self):
        return self.name
    
class observer(models.Model):
    observerId  =models.CharField(max_length=200,primary_key=True)
    firstname  =models.CharField(max_length=200)
    middlename =models.CharField(max_length=200)
    lastname   =models.CharField(max_length=200)
    observatory=models.ForeignKey(observatory, on_delete=models.CASCADE)
    tz         =models.CharField(max_length=200)
    
    def __str__(self):
        return self.thisUNID
    
class instrument(models.Model):
    ALLSKYCAM="AS"
    WEATHER="WE"
    INSTRUMENT_TYPES = (
        (ALLSKYCAM,"AllSkyCam"),
        (WEATHER,"Weather Station")
    )
    instrumentId  =models.CharField(max_length=200,primary_key=True)
    name      =models.CharField(max_length=200)
    shortname =models.CharField(max_length=200)
    instType  =models.CharField(max_length=2,choices=INSTRUMENT_TYPES, default='AS')
    observatory=models.ForeignKey(observatory, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.thisUNID
    
class telescope(models.Model):
    TELESCOPE_TYPES=(
        ("NE", "Newtonian"),
        ("SC", "Schmidt-Cassegrain"),
        ("CC", "Classical Cassegrain"),
        ("RC", "Ritchey Cretien Cassegrain"),
        ("MC", "Mak-Cassegrain"),
        ("OT", "Other"),
    )
    
    telescopeId   =models.CharField(max_length=200,primary_key=True)
    name      =models.CharField(max_length=200)
    shortname =models.CharField(max_length=200)
    telescopeType=models.CharField(max_length=2,choices=TELESCOPE_TYPES, default='NE')
    aperture    =models.DecimalField(max_digits = 6,decimal_places = 2)
    focalLength =models.DecimalField(max_digits = 6,decimal_places = 2)
    observatory =models.ForeignKey(observatory, on_delete=models.CASCADE)
    
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
    instrument=models.ForeignKey(instrument, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name


