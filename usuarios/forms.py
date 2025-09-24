from django import forms
from .models import Clientes
import re


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = ['nome', 'cpf', 'email', 'telefone', 'endereco']

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            cpf_limpo = re.sub(r'\D', '', cpf)

            if len(cpf_limpo) != 11 or len(set(cpf_limpo)) == 1:
                raise forms.ValidationError("CPF inválido.")
            
            soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
            digito1 = (soma * 10) % 11
            if digito1 == 10:
                digito1 = 0
            if digito1 != int(cpf_limpo[9]):
                raise forms.ValidationError("CPF inválido.")
            
            soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
            digito2 = (soma * 10) % 11
            if digito2 == 10:
                digito2 = 0
            if digito2 != int(cpf_limpo[10]):
                raise forms.ValidationError("CPF inválido.")
            return cpf_limpo
        return cpf
    

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Clientes.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este email já está em uso por outro cliente.")
        return email