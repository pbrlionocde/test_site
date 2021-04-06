from ast import Str
from datetime import datetime
import string
import random
import csv
from typing import Dict, Any, List
from django.views import View
from django.views.generic.edit import FormMixin, CreateView, DeleteView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic.list import ListView, BaseListView
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import RedirectView, TemplateView, TemplateResponseMixin
from .forms import UploadFileForm, DateInputAllForm, DateInputNotDoneForm
from .models import Note, User, InviteKey


class UserObjectMixin:
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    fields = ['text_note']
    success_url = reverse_lazy('list_notes')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class NoteDeleteView(UserObjectMixin, LoginRequiredMixin, DeleteView):
    model = Note
    success_url = reverse_lazy('list_notes')


class NoteUpdateView(UserObjectMixin, LoginRequiredMixin, UpdateView):
    model = Note
    fields = ['text_note']
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('list_notes')


class NoteListView(UserObjectMixin, LoginRequiredMixin, FormMixin, ListView):
    model = Note
    paginate_by = 6
    ordering = '-pk'
    form_class = DateInputAllForm
    context_object_name = 'list_note_display'
    template_name = 'list_notes.html'
    params: Dict[Str, Any] = dict()
    form = None

    def get_context_data(self, **kwargs):
        return super().get_context_data(form=self.form, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(**self.params)

    def get(self, request, *args, **kwargs):
        self.form = self.form_class(self.request.GET)
        if self.form.is_valid():
            self.params = {key: value for key, value in self.form.cleaned_data.items() if value}
            return super().get(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)


class DoneListView(NoteListView):

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user).exclude(date_of_end__isnull=True)


class NotDoneListView(NoteListView):
    form_class = DateInputNotDoneForm

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user).exclude(date_of_end__isnull=False)


class NoteDoneView(LoginRequiredMixin, SingleObjectMixin, RedirectView):
    model = Note
    query_string = True
    url = reverse_lazy('list_notes')

    def make_done(self):
        now = timezone.now()
        self.model.objects.filter(pk=self.kwargs.get(self.pk_url_kwarg)).update(date_of_end=now) #type: ignore

    def post(self, request, *args, **kwargs):
        self.make_done()
        return super().post(request, *args, **kwargs)


class CsvResponseView(UserObjectMixin, BaseListView):
    model = Note
    date_format = '%Y-%m-%d %H:%M:%S'

    def render_to_response(self, context):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="notes.csv"'
        writer = csv.writer(response)  # type:ignore
        writer.writerow(['date of creation', 'text note', 'date of end'])
        for note in context['object_list']:
            date_of_end = ''
            if note.date_of_end:
                date_of_end = note.date_of_end.strftime(self.date_format)
            writer.writerow([
                note.date_of_creation.strftime(self.date_format),
                note.text_note,
                date_of_end
            ])
        return response


class UploadFileFormView(FormView):
    model = Note
    template_name = 'import.html'
    form_class = UploadFileForm
    success_url = reverse_lazy('list_notes')
    date_format = '%Y-%m-%d %H:%M:%S'

    def import_notes(self, notes):
        reader = csv.DictReader(notes.split('\n'), delimiter=',')
        notes = []
        for note in reader:
            if note['date of end']:
                date_of_end = datetime.strptime(note['date of end'], self.date_format)
            else:
                date_of_end = None

            notes.append(
                self.model(
                    date_of_creation = datetime.strptime(note['date of creation'], self.date_format),
                    text_note = note['text note'],
                    date_of_end = date_of_end,
                    user = self.request.user
                )
            )
        self.model.objects.bulk_create(notes)

    def form_valid(self, form):
        self.import_notes(self.request.FILES['file_notes'].read().decode())
        return super().form_valid(form)


class FriendsListView(ListView):
    template_name = 'friends.html'
    context_object_name = 'friends'
    model = User
    queryset:List [Any] = []

    def get_queryset(self):
        self.queryset = self.request.user.friends.all()
        return super().get_queryset()


class NewInvitationTemplateView(TemplateView):
    template_name = 'invitation.html'
    model = InviteKey

    def get_key_invite(self, request):
        current_time = str(datetime.now().timestamp())
        symbols = ''.join(
            random.choices(string.ascii_lowercase, k=len(current_time))
            )

        key = ''.join([i+j for i, j in zip(current_time,symbols)])

        #user = request.user
        self.model.objects.create(key=key, inviting_user=request.user)
        return key

    def get_context_data(self, **kwargs):
        key = self.get_key_invite(self.request)
        return super().get_context_data(key=key, **kwargs)


class ConfirmationRequestFriendshipView(TemplateResponseMixin, SingleObjectMixin, View):
    template_name = 'confirmation_friendship.html'
    model = InviteKey
    success_url = reverse_lazy('list_friends')

    def confirmation_friendship(self, key):
        invite_obj = self.model.objects.get(key=key, friends_id__isnull=True)
        if invite_obj:
            #inviting_user = invite_obj.inviting_user
            self.request.user.friends.add(invite_obj.inviting_user)
            invite_obj.friends_id = invite_obj.inviting_user.id
            invite_obj.save()
            #friends_id = inviting_user.id
            #self.model_invite.objects.update(friends_id=friends_id)

    def get(self, **kwargs):
        context = kwargs
        return self.render_to_response(context)

    def post(self, **kwargs):
        self.confirmation_friendship(kwargs['key'])
        return HttpResponseRedirect(self.success_url)
