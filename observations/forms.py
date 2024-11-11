from django import forms
from .models import observation, scheduleMaster, scheduleDetail,sequenceFile
from targets.models import target
from setup.models import observatory,telescope,imager 
import datetime

################################################################################################################################
##  ObservationForm - form for adding an observation (allows targetId to be passed to it)                                     ##  
################################################################################################################################
class ObservationForm(forms.ModelForm):
    target_uuid = forms.UUIDField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = observation
        fields = ['targetId','observationDate', 'targetPA','targetInactive','observeOnce','observatoryId','telescopeId','imagerId','sequenceId' ]  # Include other fields as necessary


    def __init__(self, *args, **kwargs):
        target_uuid = kwargs.pop('target_uuid', None)
        super().__init__(*args, **kwargs)
        if target_uuid:
            self.fields['targetId'].initial = target_uuid

    observatoryId = forms.ModelChoiceField(
        queryset=observatory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Requested Observatory'
    )
    telescopeId = forms.ModelChoiceField(
        queryset=telescope.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Requested Telescope'
    )
    imagerId = forms.ModelChoiceField(
        queryset=imager.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Requested Imager'
        )
    
    sequenceFileId = forms.ModelChoiceField(
        queryset=sequenceFile.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Requested Sequence File'
        )
    
    class Meta:
        model = observation
        #fields = '__all__'
        fields = ['targetId','observationDate','targetPA','targetInactive','observeOnce','observatoryId','telescopeId','imagerId','sequenceFileId']
        labels = {
            'observationDate' : 'Requested Date YYYY-MM-DD HH:MM (or blank for any)',
            'targetPA': 'Rotation for imaging target', 
            'targetInactive': 'Create observation but do not schedule',
            'observeOnce' : 'Do not include in repeated schedules',
        }
        widgets = {
            'observationDate': forms.TextInput(attrs={'class': 'form-control datetimepicker', 'placeholder': 'Enter observation date'}),
            'targetPA': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter rotation angle'}),
            'targetInactive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observeOnce': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

################################################################################################################################
##  ScheduleQueryForm - form for querying the schedule                                                                        ##  
################################################################################################################################
class ScheduleQueryForm(forms.ModelForm):
     template_name = 'observations/schedule_query.html'
     class Meta:
        model = scheduleMaster
        fields = '__all__'
        scheduleDate = forms.DateField(initial=datetime.date.today)

################################################################################################################################
##  ScheduleDetailForm - form for displaying the schedule details                                                             ## 
################################################################################################################################
class ScheduleEditForm(forms.ModelForm):
     template_name = 'observations/schedule_edit.html'
     class Meta:
        model = scheduleMaster
        fields = '__all__'

################################################################################################################################
## SequenceForm - form for adding a sequence                                                                                  ##
###############################################################################################################################
class SequenceFileForm(forms.ModelForm):
    sequenceFileName = forms.FileField(required=True)
    
    class Meta:
        model = sequenceFile
        fields = ['sequenceFileName','sequenceDuration']