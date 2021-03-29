from django_registration.forms import RegistrationForm
from django.core.validators import FileExtensionValidator
from django import forms
from .models import User


class UserForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User


class UploadFileForm(forms.Form):
    file_notes = forms.FileField(validators=[FileExtensionValidator(['csv'])])


class DateInputAllForm(forms.Form):
    status_selection = (
        (1, 'Date of done'),
        (2, 'Date creation')
    )

    choose = forms.ChoiceField(choices=status_selection)
    start_of_date_range = forms.DateField(widget=forms.SelectDateWidget(years=range(2018, 2024)))
    end_of_date_range = forms.DateField(widget=forms.SelectDateWidget(years=range(2018, 2024)))


class DateInputNotDoneForm(forms.Form):
    start_of_date_range = forms.DateField(widget=forms.SelectDateWidget(years=range(2018, 2024)))
    end_of_date_range = forms.DateField(widget=forms.SelectDateWidget(years=range(2018, 2024)))
