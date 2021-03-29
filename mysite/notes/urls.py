from django.contrib import admin
from django.urls import path, include
from django_registration.backends.one_step.views import RegistrationView
from .forms import UserForm

from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/register/', RegistrationView.as_view(form_class=UserForm), name='register',),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('', views.NoteListView.as_view(), name='list_notes'),
    path('done/', views.DoneListView.as_view(), name='done'),
    path('not_done/', views.NotDoneListView.as_view(), name='not_done'),
    path('createnote/', views.NoteCreateView.as_view(), name='create_new_note'),
    path('updatenote/<int:pk>/', views.NoteUpdateView.as_view(), name='update_note'),
    path('deletenote/<int:pk>/', views.NoteDeleteView.as_view(), name='delete_note'),
    path('donenote/<int:pk>/', views.NoteDoneView.as_view(), name='done_note'),
    path('downloadcsv/', views.CsvResponseView.as_view(), name='download'),
    path('importcsv/', views.UploadFileFormView.as_view(), name='import_notes')

]
