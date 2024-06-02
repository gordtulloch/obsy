from django import forms
from .models import target, scheduleFile,sequenceFile

class TargetUpdateForm(forms.ModelForm):
     template_name = 'targets/target_form.html'
     class Meta:
        model = target  # Specify the model class
        #fields = '__all__'
        exclude = ('userId',) 
        
class scheduleFileForm(forms.Form):
     file = forms.FileField()

class sequenceFileForm(forms.Form):
     file = forms.FileField()