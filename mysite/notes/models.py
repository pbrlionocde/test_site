from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    pass


class Note(models.Model):
    date_of_creation = models.DateTimeField(auto_now_add=True)
    text_note = models.TextField(max_length=300, help_text='Max length note 300 symbols')
    date_of_end = models.DateTimeField(null=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE,)

    @property
    def done(self):
        return bool(self.date_of_end)
