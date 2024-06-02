from django.db import models
import uuid

class fitsFile(models.Model):
    fitsFileId= models.UUIDField( 
                                primary_key=True,
                                default=uuid.uuid4,
                                editable=False)
    date    =models.DateField()
    filename=models.CharField(max_length=512)
    
    def __str__(self):
        return self.fitsFileId
    
class fitsHeader(models.Model):
    fitsHeaderId = models.UUIDField( 
                                primary_key=True,
                                default=uuid.uuid4,
                                editable=False)
    parentUUID=models.ForeignKey(fitsFile, on_delete=models.CASCADE)
    keyword   =models.CharField(max_length=200)
    value     =models.CharField(max_length=200)
    
    def __str__(self):
        return self.fitsHeaderId
