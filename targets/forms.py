from django import forms
from .models import TargetModel

class TargetModelForm(forms.ModelForm):
    class Meta:
        model = TargetModel
        fields = ["target", "catalogID"]