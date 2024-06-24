from django import forms
from .models import target 

class TargetUpdateForm(forms.ModelForm):
     template_name = 'targets/target_form.html'
     class Meta:
        model = target 
        #fields = '__all__'
        exclude = ('userId',) 
