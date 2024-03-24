from django.db import models

class TargetModel(models.Model):
    id = models.AutoField(primary_key=True)
    target = models.CharField(max_length=255)
    catalogID = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.target} ({self.id})"