from django import forms
from .models import target

class targetForm(forms.ModelForm):
    class Meta:
        model = target
        fields = ["targetName", "catalogIDs"]