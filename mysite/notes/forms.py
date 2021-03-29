from django_registration.forms import RegistrationForm
from django.core.validators import FileExtensionValidator
from django import forms
from .models import User


class UserForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User


class UploadFileForm(forms.Form):
    file_notes = forms.FileField(validators=[FileExtensionValidator(['csv'])])
