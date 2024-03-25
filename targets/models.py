from django.db import models

class target(models.Model):
    TARGET_TYPES=(
        ("VS", "Variable Star"),
        ("EX", "Exoplanet"),
        ("DS", "Deep Sky Object"),
        ("PL", "Planet"),
        ("LU", "Luna"),
        ("SU", "Sun"),
        ("SA", "Satellite"),
        ("OT", "Other")
    )
    id = models.AutoField(primary_key=True)
    targetName = models.CharField(max_length=255)
    catalogIDs = models.CharField(max_length=255)
    targetType  =models.CharField(max_length=2,choices=TARGET_TYPES)
    
    def __str__(self):
        return f"{self.id}"
    
class  targetDetail(models.Model):
    id = models.AutoField(primary_key=True)
    ra = models.CharField(max_length=200)
    dec = models.CharField(max_length=200)
    const = models.CharField(max_length=200)
    
    def __str__(self):
        return f"{self.id}"
    
class gvcsStarNo(models.Model):
    starName            = models.CharField(max_length=6)
    const               = models.CharField(max_length=5)
    
class gvcsRemarks(models.Model):
    starNo              = models.IntegerField(primary_key=True)
    starName            = models.CharField(max_length=3)
    remarks             = models.CharField(max_length=80)     
    
class gvcsRef(models.Model):
    referenceNo         = models.IntegerField(primary_key=True)
    reference           = models.CharField(max_length=80)
    
class gvcsCatalog(models.Model):
    constCode           = models.IntegerField()
    starNo              = models.ForeignKey(gvcsStarNo, on_delete=models.CASCADE)
    compNo              = models.CharField(max_length=1)
    gvcsNo              = models.CharField(primary_key=True,max_length=10)
    noteFlag            = models.CharField(max_length=1)
    RAh2000             = models.IntegerField()
    RAm2000             = models.IntegerField()
    RAs2000             = models.DecimalField(max_digits=4, decimal_places=1)
    DECdeg2000          = models.IntegerField()
    DECmin2000          = models.IntegerField()
    DECsec2000          = models.DecimalField(max_digits=4, decimal_places=1)
    posnAccuracyFlag    = models.CharField(max_length=1)
    varType             = models.CharField(max_length=10)
    lMagMax             = models.CharField(max_length=1)
    magMax              = models.DecimalField(max_digits=6, decimal_places=3)
    magMaxUncertainty   = models.CharField(max_length=1)
    magMin1BrightLimit  = models.CharField(max_length=2)
    magMin1             = models.DecimalField(max_digits=6, decimal_places=3)
    magMin1Uncertainty  = models.CharField(max_length=1)
    magMin1AltPhot      = models.CharField(max_length=1)
    magMin1AmplitudeFlag= models.CharField(max_length=1)
    magMin2BrightLimit  = models.CharField(max_length=2)
    magMin2             = models.DecimalField(max_digits=6, decimal_places=3)
    magMin2Uncertainty  = models.CharField(max_length=1)
    magMin2AltPhot      = models.CharField(max_length=1)
    magMin2AmplitudeFlag= models.CharField(max_length=1)
    photSystem          = models.CharField(max_length=2)
    epochForMaxLight    = models.DecimalField(max_digits=11, decimal_places=5)
    epochQualityFlag    = models.CharField(max_length=1)
    yearOfOutburst      = models.CharField(max_length=4 )
    yearOfOutburstQualityFlag  = models.CharField(max_length=1)
    upperLowerLimitCode = models.CharField(max_length=1)
    period              = models.CharField(max_length=200)
    periodUncertaintyFlag  = models.CharField(max_length=200)
    nPeriod             = models.DecimalField(max_digits=16, decimal_places=10)
    nPeriodUncertaintyFlag  = models.CharField(max_length=1)
    risingTimeOrDuration= models.CharField(max_length=2)
    risingTimeOrDurationUncertaintyFlag  = models.CharField(max_length=3)
    eclipsingVarNote    = models.CharField(max_length=1)
    spectralType        = models.CharField(max_length=1)
    ref1                = models.CharField(max_length=5)
    ref2                = models.CharField(max_length=5)
    exists              = models.CharField(max_length=12)
    properMotionRA      = models.DecimalField(max_digits=6, decimal_places=3)
    properMotionDEC     = models.DecimalField(max_digits=6, decimal_places=3)
    coordEpoch          = models.DecimalField(max_digits=8, decimal_places=3)
    identUncertaintyFlag= models.CharField(max_length=1)
    astrometrySource    = models.CharField(max_length=12)
    varType2            = models.CharField(max_length=10)
    gvcs2No             = models.CharField(max_length=10)
