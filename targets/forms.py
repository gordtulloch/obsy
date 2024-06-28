from django import forms
from .models import target, scheduleMaster 
import datetime

class TargetUpdateForm(forms.ModelForm):
     template_name = 'targets/target_form.html'
     class Meta:
        model = target 
        #fields = '__all__'
        exclude = ('userId',) 

class ScheduleQueryForm(forms.ModelForm):
     template_name = 'targets/schedule_query.html'
     class Meta:
        model = scheduleMaster
        fields = ('scheduleDate','scheduleDays','observatoryId','telescopeId','imagerId')
        scheduleDate = forms.DateField(initial=datetime.date.today)
        
class ScheduleEditForm(forms.ModelForm):
     template_name = 'targets/schedule_edit.html'
     class Meta:
        model = scheduleMaster
        fields = '__all__'