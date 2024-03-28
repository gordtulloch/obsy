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
    zs