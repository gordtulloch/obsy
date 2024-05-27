from django.db import models

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
    targetId = models.AutoField(primary_key=True)
    userId = models.CharField(max_length=255)
    targetName = models.CharField(max_length=255)
    catalogIDs = models.CharField(max_length=255)
    targetClass  =models.CharField(max_length=2,choices=TARGET_CLASSES)
    targetType  =models.CharField(max_length=255)
    objID = models.CharField(max_length=200)
    objName = models.CharField(max_length=200)
    objRA2000 = models.CharField(max_length=200)
    objDec2000 = models.CharField(max_length=200)
    objConst = models.CharField(max_length=200)
    objMag = models.CharField(max_length=200)
    objSize = models.CharField(max_length=200)
    objType = models.CharField(max_length=200)
    objClass = models.CharField(max_length=200)
    objCatalogs = models.CharField(max_length=200)
    
    def __str__(self):
        return f"{self.id}"
