from django import forms
from .models import observation, scheduleMaster, scheduleDetail
from targets.models import target
from setup.models import observatory,telescope,imager 
import datetime
 
class ObservationUpdateForm(forms.ModelForm):
     template_name = 'observations/observation_form.html'
     class Meta:
        model = observation
        #fields = '__all__'
        exclude = ('userId',) 

class ObservationForm(forms.ModelForm):
    targetId = forms.ModelChoiceField(
        queryset=target.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Requested Target'
    )
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
    class Meta:
        model = observation
        #fields = '__all__'
        fields = ['targetId','observationDate','targetPA','targetInactive','observeOnce','observatoryId','telescopeId','imagerId']
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

class ScheduleQueryForm(forms.ModelForm):
     template_name = 'observations/schedule_query.html'
     class Meta:
        model = scheduleMaster
        fields = '__all__'
        scheduleDate = forms.DateField(initial=datetime.date.today)
        
class ScheduleEditForm(forms.ModelForm):
     template_name = 'observations/schedule_edit.html'
     class Meta:
        model = scheduleMaster
        fields = '__all__'