from django import forms
from .models import Target,GCVS
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