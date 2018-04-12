from django import forms
from django.forms import ValidationError
import json

class UploadFileForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        try:
            return json.load(self.cleaned_data['file'])
        except:
            raise ValidationError("Must be proper json", code='badjson')
