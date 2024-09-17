from django import forms
from .models import InfosPecas, AnalisePeca

class UploadForm(forms.Form):
    file = forms.FileField(label='Escolha o arquivo')
    idPeca = forms.ModelChoiceField(
        queryset=InfosPecas.objects.all(),
        label='Selecione a Peça:',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
class InfosPecasForm(forms.ModelForm):
    class Meta:
        model = InfosPecas
        fields = ['nomePeca', 'situPeca', 'fornecedorPeca']
        widgets = {
            'nomePeca': forms.TextInput(attrs={'class': 'form-control'}),
            'situPeca': forms.NumberInput(attrs={'class': 'form-control'}),
            'fornecedorPeca': forms.TextInput(attrs={'class': 'form-control'}),
        }


