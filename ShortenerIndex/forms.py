from django import forms
from .models import Link


class ShortenLinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = [
            'url_input',
        ]
