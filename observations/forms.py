from django import forms
from .models import observation, scheduleMaster, scheduleDetail,sequenceFile
from targets.models import Target
from setup.models import observatory,telescope,imager 
import datetime

################################################################################################################################
##  ObservationForm - form for adding an observation (allows targetId to be passed to it)                                     ##  
################################################################################################################################
class ObservationForm(forms.ModelForm):
    target_uuid = forms.UUIDField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = observation
        fields = ['targetId','observationDate', 'targetPA','targetInactive','observeOnce','observatoryId',
                  'telescopeId','imagerId','sequenceFileId' ]


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
            'targetPA': 'Rotation for imaging Target', 
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
##  ObservationFormDS - form for adding an observation (allows targetId to be passed to it) for a DS class object             ##  
################################################################################################################################
class ObservationFormDS(forms.ModelForm):
    target_uuid = forms.UUIDField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = observation
        fields = ['targetId','observationDate', 'targetPA','targetInactive','observeOnce','observatoryId',
                  'telescopeId','imagerId','sequenceFileId' ]


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
            'targetPA': 'Rotation for imaging Target', 
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
##  ScheduleMasterForm - form for adding a schedule                                                                           ##
################################################################################################################################
class ScheduleMasterForm(forms.ModelForm):
    class Meta:
        model = scheduleMaster
        fields = ['scheduleDate','scheduleDays','observatoryId']
        labels = {
            'scheduleDate' : 'Schedule Date YYYY-MM-DD',
            'scheduleDays': 'Number of days to schedule',
            'observatoryId': 'Observatory to schedule',
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
## SequenceFileForm - form for adding a sequence                                                                              ##
################################################################################################################################
class SequenceFileForm(forms.ModelForm):
    sequenceFileName = forms.FileField(required=True)
    
    class Meta:
        model = sequenceFile
        fields = ['sequenceFileName','sequenceDuration']
        labels = {'sequenceFileName' : 'Filename of the EKOS Sequence File',
                  'sequenceDuration': 'Total expected duration for the Sequence (in seconds)', 
                 }