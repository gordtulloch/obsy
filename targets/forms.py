from django import forms
from .models import target,importTarget 
import datetime

class TargetUpdateForm(forms.ModelForm):
     template_name = 'targets/target_form.html'
     class Meta:
        model = target 
        fields = '__all__'


class TargetImportForm(forms.ModelForm):
    class Meta:
        model = importTarget
        fields = ('document',)