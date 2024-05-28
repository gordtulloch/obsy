import uuid
from django.db import models
from django.urls import reverse

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
    targetId = models.UUIDField( 
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False)
    userId = models.CharField(max_length=255)
    targetName = models.CharField(max_length=255)
    catalogIDs = models.CharField(max_length=255)
    targetClass  =models.CharField(max_length=2,choices=TARGET_CLASSES)
    targetType  =models.CharField(max_length=255)
    targetRA2000 = models.CharField(max_length=200)
    targetDec2000 = models.CharField(max_length=200)
    targetConst = models.CharField(max_length=200)
    targetMag = models.CharField(max_length=200)

    
    def __str__(self):
        return f"{self.targetId}"
    def get_absolute_url(self):
        return reverse("target_detail", args=[str(self.targetId)])

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
    
    label = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=2)
    
    def __str__(self):
        return f"{self.id}"
    def get_absolute_url(self):
        return reverse("target_detail", args=[str(self.id)])