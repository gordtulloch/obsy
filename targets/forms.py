from django import forms
from .models import target

class SimbadSearchForm(forms.Form):
    search_term = forms.CharField(label='Enter an astronomical object name', max_length=100)