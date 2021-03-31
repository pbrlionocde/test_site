from ast import Str
import csv
from typing import Dict, Any
from datetime import datetime
from django.views.generic.edit import FormMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import RedirectView
from django.views.generic.list import BaseListView
from django.http import HttpResponse
from django.views.generic.edit import FormView
from .models import Note
from .forms import UploadFileForm, DateInputAllForm, DateInputNotDoneForm


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

  #  def get_context_data(self, **kwargs):
     #   return super().get_context_data(**kwargs)

    def get_queryset(self):
        if self.params is not None:
            return super().get_queryset().filter(**self.params)
        return super().get_queryset()

    def get(self, request, *args, **kwargs):
        form = self.form_class(self.request.GET)
        if form.is_valid():
            self.params = {key: value for key, value in form.cleaned_data.items() if value}
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
        self.model.objects.filter(pk=self.kwargs.get(self.pk_url_kwarg)).update(date_of_end=now) #ignore

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
        for note in reader:
            if not note['date of end']:
                date_of_end = None
            else:
                date_of_end = datetime.strptime(note['date of end'], self.date_format)

            self.model.objects.create(
                date_of_creation=datetime.strptime(note['date of creation'], self.date_format),
                text_note=note['text note'],
                date_of_end=date_of_end,
                user=self.request.user
            )

    def form_valid(self, form):
        self.import_notes(self.request.FILES['file_notes'].read().decode())
        return super().form_valid(form)
