from django_registration.forms import RegistrationForm
from django.core.validators import FileExtensionValidator
from django import forms
from django.utils import timezone
from .models import User


class UserForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User


class UploadFileForm(forms.Form):
    file_notes = forms.FileField(validators=[FileExtensionValidator(['csv'])])


class DateInputAllForm(forms.Form):
    start_date_of_creation_range = forms.DateField(
        widget=forms.SelectDateWidget(years=range(2018, 2024),
        attrs={'class': 'form-control', 'style':'width:8%'}))
    end_date_of_creation_range = forms.DateField(
        widget=forms.SelectDateWidget(years=range(2018, 2024),
        attrs={'class': 'form-control', 'style':'width:8%'}), initial=timezone.now())
    start_date_of_end_range = forms.DateField(
        widget=forms.SelectDateWidget(years=range(2018, 2024),
        attrs={'class': 'form-control', 'style':'width:8%'}))
    end_date_of_end_range = forms.DateField(
        widget=forms.SelectDateWidget(years=range(2018, 2024),
        attrs={'class': 'form-control', 'style':'width:8%'}), initial=timezone.now())

class DateInputNotDoneForm(forms.Form):
    start_date_of_creation_range = forms.DateField(
        widget=forms.SelectDateWidget(years=range(2018, 2024),
        attrs={'class': 'form-control', 'style':'width:8%'}))
    end_date_of_creation_range = forms.DateField(
        widget=forms.SelectDateWidget(years=range(2018, 2024),
        attrs={'class': 'form-control', 'style':'width:8%'}))
