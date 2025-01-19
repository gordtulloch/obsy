from django.db import models

class GeneralConfig(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    elevation = models.IntegerField()

class CommunicationsConfig(models.Model):
    email_backend = models.CharField(max_length=255)
    email_host = models.CharField(max_length=255)
    email_port = models.IntegerField()
    email_use_tls = models.BooleanField()
    email_host_user = models.CharField(max_length=255)
    email_host_password = models.CharField(max_length=255)
    sender_email = models.CharField(max_length=255)
    recipient_email = models.CharField(max_length=255)
    twilio_sid = models.CharField(max_length=255)
    twilio_token = models.CharField(max_length=255)

class RepositoryConfig(models.Model):
    ppsourcepath = models.CharField(max_length=255)
    pprepopath = models.CharField(max_length=255)