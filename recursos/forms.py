from django import forms
from .models import Exemplares

class ExemplarCreateForm(forms.ModelForm):
    class Meta:
        model = Exemplares
        fields = ['recurso', 'status', 'data_aquisicao']

class ExemplarUpdateForm(forms.ModelForm):
    class Meta:
        model = Exemplares
        fields = ['status']