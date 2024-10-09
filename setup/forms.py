from django import forms
from .models import observatory, telescope, imager
import pytz

class ObservatoryForm(forms.ModelForm):
    tz = forms.ChoiceField(
        choices=[(tz, tz) for tz in pytz.all_timezones],
        label='Timezone'
    )
    class Meta:
        model = observatory
        fields = '__all__'
        exclude = ('observatoryId',) 
        labels = {
            'name': 'Observatory Name',
            'shortname': 'Short name or acronym',
            'location': 'Location', 
            'description': 'Description',
            'tz': 'Timezone',
        }
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter observatory name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'tz':forms.Select(attrs={'class': 'form-control'}),
        }

class TelescopeForm(forms.ModelForm):
    class Meta:
        model = telescope
        fields = '__all__'
        exclude = ('telescopeId',) 
        labels = {
            'name': 'Telescope Name',
            'shortname' : 'Short name or acronym',
            'telescopeType': 'Type of optical system',
            'aperture': 'Aperture (mm)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter telescope name'}),
            'type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter type'}),
            'aperture': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter aperture'}),
        }

class ImagerForm(forms.ModelForm):
    class Meta:
        model = imager
        fields = '__all__'
        labels = {
            'name': 'Imager Name',
            'resolution': 'Resolution',
            'sensor_size': 'Sensor Size',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter imager name'}),
            'resolution': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter resolution'}),
            'sensor_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter sensor size'}),
        }