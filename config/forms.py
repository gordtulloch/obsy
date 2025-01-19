from django import forms
from .models import GeneralConfig, CommunicationsConfig, RepositoryConfig

class GeneralConfigForm(forms.ModelForm):
    class Meta:
        model = GeneralConfig
        fields = '__all__'
        labels = {
            'latitude': 'Default Latitude',
            'longitude': 'Default Longitude',
            'elevation': 'Default Elevation',
        }

class CommunicationsConfigForm(forms.ModelForm):
    class Meta:
        model = CommunicationsConfig
        fields = '__all__'
        # hide the following fields
        exclude = ['email_backend']
        labels = {
            'email_host': 'SMTP Server Host',
            'email_port': 'SMTP Server Port',
            'email_use_tls': 'Use TLS',
            'email_host_user': 'SMTP Server Username',
            'email_host_password': 'SMTP Server Password',
            'sender_email': 'Sender Email Address',
            'recipient_email': 'Recipient Email Address',
        }

class RepositoryConfigForm(forms.ModelForm):
    class Meta:
        model = RepositoryConfig
        fields = '__all__'
        labels = {
            'ppsourcepath': 'Path to load data from to insert into the Repository',
            'pprepopath': 'Repository Path',
        }