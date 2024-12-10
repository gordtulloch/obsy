from django import forms
from .models import target
import datetime

class TargetUpdateForm(forms.ModelForm):
     template_name = 'targets/target_form.html'
     class Meta:
        model = target 
        fields = '__all__'

class UploadFileForm(forms.Form):
    file = forms.FileField()
