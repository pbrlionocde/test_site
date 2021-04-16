from notes.models import Note, User
from django.conf import settings
from django.core.mail import send_mail
from mysite.celery import app


@app.task
def send_not_end_notes():
    for user in User.objects.all():
        notes = Note.objects.all().not_done()
        tasks = ''
        for note in notes:
            tasks += note.text_note + ' ' + str(note.date_of_creation) + '\n'
        send_mail(
                'Your QuickPublisher Activity',
                'Hello!It`s your not done tasks: {}'.format(tasks),
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
