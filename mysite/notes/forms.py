from django_registration.forms import RegistrationForm
from django.core.validators import FileExtensionValidator
from django import forms
from .models import User


class UserForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User


class UploadFileForm(forms.Form):
    file_notes = forms.FileField(validators=[FileExtensionValidator(['csv'])])


class Html5DateInput(forms.DateInput):
    input_type = 'date'


class DateInputAllForm(forms.Form):
    date_of_creation__lt = forms.DateField(widget=Html5DateInput, label='Until the date of creation', required=False)
    date_of_creation__gt = forms.DateField(widget=Html5DateInput, label='From the date of creation', required=False)
    date_of_end__lt = forms.DateField(widget=Html5DateInput, label='Until the date of end', required=False)
    date_of_end__gt = forms.DateField(widget=Html5DateInput, label='From the date of end', required=False)


class DateInputNotDoneForm(forms.Form):
    date_of_creation__lt = forms.DateField(widget=Html5DateInput, label='Until the date of creation', required=False)
    date_of_creation__gt = forms.DateField(widget=Html5DateInput, label='From the date of creation', required=False)
