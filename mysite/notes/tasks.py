from notes.models import Note, User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import send_mail
from mysite.celery import app


@app.task
def send_not_end_notes():
    for user in User.objects.all():
        notes = Note.objects.filter(user=user).not_done()[0:5]
        subject = 'Not done notes'
        html_message = render_to_string('email_template.html', {'notes': notes})
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to = [user.email]   #pylint: disable=C0103
        send_mail(
                subject ,
                plain_message,
                from_email,
                to,
                html_message = html_message,
            )
