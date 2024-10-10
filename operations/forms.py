from django import forms
from .models import currentConfig
from setup.models import observatory, telescope, imager

class CurrentConfigForm(forms.ModelForm): 
    class Meta:
        model = currentConfig
        fields = ['observatoryId', 'telescopeId', 'imagerId']
        labels = {
            'observatoryId': 'Observatory',
            'telescopeId': 'Telescope',
            'imagerId': 'Imager',
        }
        widgets = {
            'observatory': forms.Select(attrs={'class': 'form-control'}),
            'telescope': forms.Select(attrs={'class': 'form-control'}),
            'imager': forms.Select(attrs={'class': 'form-control'}),
        }