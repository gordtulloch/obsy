from django.db import models

class GeneralConfig(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    elevation = models.IntegerField()

class CommunicationsConfig(models.Model):
    email_host = models.CharField(max_length=255)
    email_port = models.IntegerField(blank=True, null=True)
    email_use_tls = models.BooleanField(blank=True, null=True)
    email_host_user = models.CharField(max_length=255, blank=True, null=True)
    email_host_password = models.CharField(max_length=255, blank=True, null=True)
    sender_email = models.CharField(max_length=255, blank=True, null=True)
    recipient_email = models.CharField(max_length=255, blank=True, null=True)

class RepositoryConfig(models.Model):
    ppsourcepath = models.CharField(max_length=255)
    pprepopath = models.CharField(max_length=255)