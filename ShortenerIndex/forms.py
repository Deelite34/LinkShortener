from django import forms
from django.forms import TextInput

from .models import Link


class ShortenLinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = [
            'url_input',
        ]

        widgets = {
            'url_input': TextInput(attrs={'class': 'form-horizontal form-input-url'})
        }

