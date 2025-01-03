from django import forms
from .models import Target,GCVS,ExoplanetFilter
import datetime

class TargetUpdateForm(forms.ModelForm):
     template_name = 'targets/target_form.html'
     class Meta:
        model = Target 
        fields = '__all__'

class UploadFileForm(forms.Form):
    file = forms.FileField()

class VSFilterForm(forms.Form):
    ALL_CONSTELLATIONS = GCVS.CONSTELLATION_SHORT

    constellation = forms.ChoiceField(choices=GCVS.CONSTELLATION_SHORT,required=False, initial='AND')
    variable_type = forms.CharField(max_length=255, required=False)
    max_magnitude = forms.FloatField(required=False)
    min_magnitude = forms.FloatField(required=False)

class ExoplanetFilterForm(forms.ModelForm):
    class Meta:
        model = ExoplanetFilter
        fields = ['min_transit_duration', 'max_transit_duration', 'min_depth', 'max_depth', 'min_altitude']
        labels = {
            'min_transit_duration': 'Minimum Transit Duration (hours)',
            'max_transit_duration': 'Maximum Transit Duration (hours)',
            'min_depth': 'Minimum Depth (ppm)',
            'max_depth': 'Maximum Depth (ppm)',
            'min_altitude': 'Minimum Target Altitude (degrees)'
        }