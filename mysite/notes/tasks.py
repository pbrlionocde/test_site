#from django.template import Template, Context
from django.conf import settings
from django.core.mail import send_mail
from mysite.celery import app
#from notes.models import Note, User


@app.task
def send_not_end_notes():
    send_mail(
            'Your QuickPublisher Activity',
            'text_email',
            settings.EMAIL_HOST_USER,
            ['gorbachenkomisha@gmail.com'],
            fail_silently=False,
        )
