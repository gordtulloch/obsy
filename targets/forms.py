from django import forms
from .models import Target
import datetime

class TargetUpdateForm(forms.ModelForm):
     template_name = 'targets/target_form.html'
     class Meta:
        model = Target 
        fields = '__all__'

class UploadFileForm(forms.Form):
    file = forms.FileField()

