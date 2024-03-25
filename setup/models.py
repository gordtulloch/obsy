from django.db import models

class openNGC(models.Model):
    id = models.CharField(max_length=200,primary_key=True)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    ra = models.CharField(max_length=200)
    dec = models.CharField(max_length=200)
    const = models.CharField(max_length=200)
    majax = models.CharField(max_length=200)
    minax = models.CharField(max_length=200)
    pa = models.CharField(max_length=200)
    bmag = models.CharField(max_length=200)
    vmag = models.CharField(max_length=200)
    jmag = models.CharField(max_length=200)
    hmag = models.CharField(max_length=200)
    kmag = models.CharField(max_length=200)
    sbrightn = models.CharField(max_length=200)
    hubble = models.CharField(max_length=200)
    parallax = models.CharField(max_length=200)
    pmra = models.CharField(max_length=200)
    pmdec = models.CharField(max_length=200)
    radvel = models.CharField(max_length=200)
    redshift = models.CharField(max_length=200)
    cstarumag = models.CharField(max_length=200)
    cstarbmag = models.CharField(max_length=200)
    cstarvmag = models.CharField(max_length=200)
    messier = models.CharField(max_length=200)
    ngc = models.CharField(max_length=200)
    ic = models.CharField(max_length=200)
    cstarnames = models.CharField(max_length=200)
    identifiers = models.CharField(max_length=200)
    commonnames = models.CharField(max_length=200)
    nednotes = models.CharField(max_length=200)
    ongcnotes = models.CharField(max_length=200)
    notngc = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class fitsFile(models.Model):
    thisUNID=models.CharField(max_length=200,primary_key=True)
    date    =models.DateField()
    filename=models.CharField(max_length=512)
    
    def __str__(self):
        return self.thisUNID
    
class fitsHeader(models.Model):
    thisUNID  =models.CharField(max_length=200,primary_key=True)
    parentUNID=models.ForeignKey(fitsFile, on_delete=models.CASCADE)
    keyword   =models.CharField(max_length=200)
    value     =models.CharField(max_length=200)
    
    def __str__(self):
        return self.thisUNID
    
class observatory(models.Model):
    thisUNID  =models.CharField(max_length=200,primary_key=True)
    name      =models.CharField(max_length=200)
    shortname =models.CharField(max_length=200)
    latitude  =models.DecimalField(max_digits = 6,decimal_places = 2)
    longitude =models.DecimalField(max_digits = 6,decimal_places = 2)
    tz        =models.CharField(max_length=200)
    def __str__(self):
        return self.name
    
class observer(models.Model):
    thisUNID   =models.CharField(max_length=200,primary_key=True)
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
    thisUNID  =models.CharField(max_length=200,primary_key=True)
    name      =models.CharField(max_length=200)
    shortname =models.CharField(max_length=200)
    instType  =models.CharField(max_length=2,choices=INSTRUMENT_TYPES)
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
    thisUNID   =models.CharField(max_length=200,primary_key=True)
    name      =models.CharField(max_length=200)
    shortname =models.CharField(max_length=200)
    telescopeType=models.Charfield(max_length=2,choices=TELESCOPE_TYPES)
    aperture    =models.DecimalField(max_digits = 6,decimal_places = 2)
    focalLength =models.DecimalField(max_digits = 6,decimal_places = 2)
    observatory =models.ForeignKey(observatory, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
class imager(models.Model):
    thisUNID   =models.CharField(max_length=200,primary_key=True)
    name      =models.CharField(max_length=200)
    shortname =models.CharField(max_length=200)
    class imagerType(models.TextChoices):
        CMOS = "CMOS", "CMOS"
        CCD  = "CCD", "CCD"
    xDim=models.DecimalField(max_digits = 5,decimal_places = 0)
    yDim=models.DecimalField(max_digits = 5,decimal_places = 0)
    xPixelSize=models.DecimalField(max_digits = 6,decimal_places = 2)
    yPixelSize=models.DecimalField(max_digits = 6,decimal_places = 2)
    instrument=models.ForeignKey(instrument, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name


