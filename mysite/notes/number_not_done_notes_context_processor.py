from .models import Note

def number_not_done_notes_context_processor(request):
    if request.user.is_authenticated:
        return {
            'number_not_done_notes': Note.objects.all().not_done().today().filter(user=request.user).count()
        }

    return {}
