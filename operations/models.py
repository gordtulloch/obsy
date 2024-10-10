from django.db import models
from setup.models import observatory, telescope, imager
import uuid

class currentConfig(models.Model):
    currentConfigId  = models.UUIDField( 
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False)
    observatoryId = models.ForeignKey(observatory, on_delete=models.CASCADE)
    telescopeId = models.ForeignKey(telescope, on_delete=models.CASCADE)
    imagerId = models.ForeignKey(imager, on_delete=models.CASCADE)

    def __str__(self):
        return f"Config: {self.observatoryId.name}, {self.telescopeId.name}, {self.imagerId.name}"
