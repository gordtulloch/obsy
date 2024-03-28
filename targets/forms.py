from django import forms
from .models import target

class targetQueryForm(forms.Form):
    queryTarget=forms.CharField(label="Target", max_length=100)
    
class targetForm(forms.ModelForm):
    class Meta:
        model = target
        fields = ["targetName", "catalogIDs"]