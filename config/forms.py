from django import forms
from .models import GeneralConfig, CommunicationsConfig, RepositoryConfig

class GeneralConfigForm(forms.ModelForm):
    class Meta:
        model = GeneralConfig
        fields = '__all__'

class CommunicationsConfigForm(forms.ModelForm):
    class Meta:
        model = CommunicationsConfig
        fields = '__all__'

class RepositoryConfigForm(forms.ModelForm):
    class Meta:
        model = RepositoryConfig
        fields = '__all__'