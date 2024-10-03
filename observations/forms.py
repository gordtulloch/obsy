from django import forms
from .models import observation

class ObservationUpdateForm(forms.ModelForm):
     template_name = 'observations/observation_form.html'
     class Meta:
        model = observation
        #fields = '__all__'
        exclude = ('userId',) 

class ObservationForm(forms.ModelForm):
    class Meta:
        model = observation
        #fields = '__all__'
        exclude = ('userId',) 