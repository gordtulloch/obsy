from django import forms
from .models import target, scheduleFile,sequenceFile

class TargetUpdateForm(forms.ModelForm):
     template_name = 'targets/target_form.html'
     class Meta:
        model = target 
        #fields = '__all__'
        exclude = ('userId',) 
        
class scheduleFileForm(forms.ModelForm):
     class Meta:
          model=scheduleFile
          fields = ['scheduleFileName']

class sequenceFileForm(forms.ModelForm):
     template_name = 'targets/sequence_upload.html' 
     class Meta:
          model=sequenceFile
          fields = ['sequenceFileName']