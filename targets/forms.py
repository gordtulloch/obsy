from django import forms
from .models import target, scheduleFile,sequenceFile

class TargetUpdateForm(forms.ModelForm):
     template_name = 'targets/target_form.html'
     class Meta:
        model = target  # Specify the model class
        #fields = '__all__'
        exclude = ('userId',) 
        
class scheduleFileForm(forms.ModelForm):
     template_name = 'targets/schedule_upload.html'
     class Meta:
        model = scheduleFile  # Specify the model class
        fields = '__all__'

class sequenceFileForm(forms.ModelForm):
     template_name = 'targets/sequence_upload.html'
     class Meta:
        model = sequenceFile  # Specify the model class
        fields = '__all__'