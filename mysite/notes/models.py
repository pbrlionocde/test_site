from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class UserNotesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class UserNotesQuerySet(models.QuerySet):
    def not_done(self):
        return self.exclude(date_of_end__isnull=False)

    def done(self):
        return self.exclude(date_of_end__isnull=True)

    def today(self):
        return self.filter(date_of_creation__day=timezone.now().day)


class User(AbstractUser):
    friends = models.ManyToManyField('self', blank=True)


class InviteKey(models.Model):
    key = models.CharField(max_length=300, unique=True)
    inviting_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inviting_user')
    invited_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='invited_user')


class Note(models.Model):

    is_deleted = models.BooleanField(default=False)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    text_note = models.TextField(max_length=300, help_text='Max length note 300 symbols')
    date_of_end = models.DateTimeField(null=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE,)

    objects = UserNotesManager.from_queryset(UserNotesQuerySet)()

    def delete(self):
        self.is_deleted = True
        super().save()

    @property
    def done(self):
        return bool(self.date_of_end)
