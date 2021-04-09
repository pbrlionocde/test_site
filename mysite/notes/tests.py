# pylint: skip-file
import datetime
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.contrib.auth.models import User
from notes.views import NoteCreateView
from notes.models import Note, User


class NoteModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        User.objects.create(username='new_user1', email='kdjkjh@gmail.com', password='G-617425')
        Note.objects.create(text_note='new_notes', user=User.objects.get(username='new_user1'))

    def test_tex_note_length(self):
        note = Note.objects.get(text_note='new_notes')
        max_length = note._meta.get_field('text_note').max_length
        self.assertEquals(max_length, 300)

    def test_is_delete(self):
        note = Note.objects.get(text_note='new_notes')
        note.delete()
        self.assertEquals(note.is_deleted, True)


class TestMixIn:
    def initialize_get(self, username, url):
        self.client.force_login(User.objects.get_or_create(username=username)[0])
        content = self.client.get(url)
        return content.context['object_list']

    def initialize_delete_update_done_post(self, name_reverse_url):
        self.client.force_login(User.objects.get_or_create(username='pbrlionocde')[0])
        note = Note.objects.get(text_note='text_note0')
        response = self.client.post(reverse(name_reverse_url, kwargs={'pk':note.pk}))
        self.assertRedirects(response, reverse('list_notes'), 302)


class TestUserMixIn:
    def create_users(self):
        self.user1 = User.objects.create_user(username='pbrlionocde', email='kdjkjh@gmail.com', password='G-617123')
        self.user2 = User.objects.create_user(username='prince_blood', email='kdjkjh@gmail.com', password='12345')


class UploadFileFormViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='pbrlionocde', email='kdjkjh@gmail.com', password='G-617123')

    def test_anonymous_user(self):
        response = self.client.get(reverse('import_notes'))
        self.assertRedirects(response, reverse('login')+'?next=/importcsv/' , 302)

    def test_upload_file(self):
        with open ('notes.csv') as f:
            self.client.force_login(User.objects.get_or_create(username='pbrlionocde')[0])
            response = self.client.post(reverse('import_notes'), {'file_notes': f})
            self.assertRedirects(response, reverse('list_notes'), 302)
            note = Note.objects.get(date_of_end__isnull=False)
            self.assertEquals(note.text_note, 'new note 2')

    def test_fail_upload_file(self):
        with open ('file_upload.txt') as f:
            self.client.force_login(User.objects.get_or_create(username='pbrlionocde')[0])
            response = self.client.post(reverse('import_notes'), {'file_notes': f})
            self.assertEquals(response.status_code, 200)


class NoteCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='pbrlionocde', email='kdjkjh@gmail.com', password='G-617123')

    def test_anonymous_user(self):
        response = self.client.get(reverse('create_new_note'))
        self.assertRedirects(response, reverse('login')+'?next=/createnote/', 302)

    def test_create_new_note(self):
        request = self.factory.post(reverse('create_new_note'), {'text_note': 'New note'})
        request.user = self.user
        response = NoteCreateView.as_view()(request)
        note = Note.objects.get(user=self.user)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(note.text_note, 'New note')

    def test_fail_create_new_note(self):
        request = self.factory.post(reverse('create_new_note'), {'text_note': ''})
        request.user = self.user
        response = NoteCreateView.as_view()(request)
        self.assertEquals(response.status_code, 200)


class ListNotesTest(TestUserMixIn, TestMixIn, TestCase):
    def setUp(self):
        self.create_users()
        for i in range(0, 13):
            Note.objects.create(text_note='text_note'+str(i), user=self.user1)
            Note.objects.create(text_note='text_note usernote2'+str(i), user=self.user2)
        self.client = Client()

    def test_anonymous_list_notes(self):
        response = self.client.get(reverse('list_notes'))
        self.assertRedirects(response, reverse('login')+'?next=/', 302)

    def test_owner_notes(self):
        object_list = self.initialize_get('pbrlionocde', reverse('list_notes'))
        for note in object_list:
            self.assertEquals(note.user, self.user1)
        object_list = self.initialize_get('prince_blood', reverse('list_notes'))
        for note in object_list:
            self.assertEquals(note.user, self.user2)

    def test_pagination(self):
        object_list = self.initialize_get('pbrlionocde', reverse('list_notes'))
        self.assertEquals(len(object_list), 6)
        object_list = self.initialize_get('pbrlionocde', reverse('list_notes')+'?page=3')
        self.assertEquals(len(object_list), 1)
        response = self.client.get(reverse('list_notes')+'?page=4')
        self.assertEquals(response.status_code, 404)

    def test_filter_date_of_creation(self):
        filter_str = '?date_of_creation__lt={dc_lt}&date_of_creation__gt={dc_gt}&date_of_end__lt=&date_of_end__gt='
        self.client.force_login(User.objects.get_or_create(username='pbrlionocde')[0])
        Note.objects.filter(text_note='text_note3').update(date_of_creation=datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(days=3))
        response = self.client.get(reverse('list_notes')+filter_str.format(dc_lt='2021-04-09', dc_gt=''))
        self.assertEquals(len(response.context_data['object_list']), 1)
        response = self.client.get(reverse('list_notes')+filter_str.format(dc_lt='', dc_gt='2021-05-01'))
        self.assertEquals(len(response.context_data['object_list']), 0)
        response = self.client.get(reverse('list_notes')+filter_str.format(dc_lt='', dc_gt='2021-04-06'))
        self.assertEquals(len(response.context_data['object_list']), 6)
        response = self.client.get(reverse('list_notes')+filter_str.format(dc_lt='2021-04-09', dc_gt='2021-04-06'))
        self.assertEquals(len(response.context_data['object_list']), 1)

    def test_filter_date_of_end(self):
        filter_str = '?date_of_creation__lt=&date_of_creation__gt=&date_of_end__lt={de_lt}&date_of_end__gt={de_gt}'
        self.client.force_login(User.objects.get_or_create(username='pbrlionocde')[0])
        Note.objects.filter(text_note='text_note3').update(date_of_end=datetime.datetime.now(datetime.timezone.utc))
        response = self.client.get(reverse('list_notes')+filter_str.format(de_lt='', de_gt='2021-04-08'))
        self.assertEquals(len(response.context_data['object_list']), 1)
        response = self.client.get(reverse('list_notes')+filter_str.format(de_lt='', de_gt='2021-04-10'))
        self.assertEquals(len(response.context_data['object_list']), 0)
        response = self.client.get(reverse('list_notes')+filter_str.format(de_lt='2021-04-08', de_gt=''))
        self.assertEquals(len(response.context_data['object_list']), 0)
        response = self.client.get(reverse('list_notes')+filter_str.format(de_lt='2021-04-10', de_gt=''))
        self.assertEquals(len(response.context_data['object_list']), 1)
        response = self.client.get(reverse('list_notes')+filter_str.format(de_lt='2021-04-10', de_gt='2021-04-08'))
        self.assertEquals(len(response.context_data['object_list']), 1)


class DeleteUpdateDoneListNotesTest(TestMixIn, TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='pbrlionocde', email='kdjkjh@gmail.com', password='G-617123')
        for i in range(0, 2):
            Note.objects.create(text_note='text_note'+str(i), user=self.user1)
        self.client = Client()

    def test_delete(self):
        self.initialize_delete_update_done_post('delete_note')
        object_list = self.initialize_get('pbrlionocde', reverse('list_notes'))
        self.assertEquals(len(object_list), 1)
        self.assertNotEquals(object_list[0], 'text_note0')

    def test_update(self, **kwargs):
        self.client.force_login(User.objects.get_or_create(username='pbrlionocde')[0])
        note = Note.objects.get(text_note='text_note0')
        self.client.post(reverse('update_note', kwargs={'pk':note.pk}), {'text_note': 'updated_text'})
        note = Note.objects.get(pk=note.pk)
        self.assertEquals(note.text_note, 'updated_text')

    def test_done(self):
        self.initialize_delete_update_done_post('done_note')
        note = Note.objects.get(text_note='text_note0')
        self.assertEquals(bool(note.date_of_end), True)

    def test_done_ivlid_pk(self):
        self.client.force_login(User.objects.get_or_create(username='pbrlionocde')[0])
        response = self.client.post(reverse('done_note', kwargs={'pk':1000}))
        self.assertRedirects(response, reverse('list_notes'), 302)

    def test_invalid_pk_update(self):
        self.client.force_login(User.objects.get_or_create(username='pbrlionocde')[0])
        response = self.client.post(reverse('update_note', kwargs={'pk': 99}))
        self.assertEqual(response.status_code, 404)

    def test_invalid_pk_delete(self):
        self.client.force_login(User.objects.get_or_create(username='pbrlionocde')[0])
        response = self.client.post(reverse('delete_note', kwargs={'pk':100}))
        self.assertEquals(response.status_code, 404)


class DoneNotDoneTabTest(TestUserMixIn, TestMixIn, TestCase):
    def setUp(self):
        self.create_users()
        for i in range(0, 13):
            Note.objects.create(text_note='text_note'+str(i), user=self.user1)
            Note.objects.create(text_note='text_note usernote2'+str(i), user=self.user2)
        self.client.force_login(User.objects.get_or_create(username='pbrlionocde')[0])
        for i in range(0,6):
            note = Note.objects.get(text_note='text_note'+str(i))
            self.client.post(reverse('done_note', kwargs={'pk': note.pk}))
        self.client = Client()

    def test_owner_done_notes(self):
        """first user get done list_note"""
        object_list = self.initialize_get('pbrlionocde', reverse('done'))
        for note in object_list:
            self.assertEquals(note.user, self.user1)
        """second user get done list_note"""
        object_list = self.initialize_get('prince_blood', reverse('done'))
        for note in object_list:
            self.assertEquals(note.user, self.user2)

    def test_owner_not_done_notes(self):
        """first user get not_done list_note"""
        object_list = self.initialize_get('pbrlionocde', reverse('not_done'))
        for note in object_list:
            self.assertEquals(note.user, self.user1)
        """second user get not_done list_note"""
        object_list = self.initialize_get('prince_blood', reverse('not_done'))
        for note in object_list:
            self.assertEquals(note.user, self.user2)

    def test_pagination_done(self):
        """done tab"""
        object_list = self.initialize_get('pbrlionocde', reverse('done'))
        self.assertEquals(len(object_list), 6)
        response = self.client.get(reverse('done')+'?page=2')
        self.assertEquals(response.status_code, 404)

    def test_pagination_not_done(self):
        """not done tab"""
        object_list = self.initialize_get('pbrlionocde', reverse('not_done'))
        self.assertEquals(len(object_list), 6)
        response = self.client.get(reverse('not_done')+'?page=3')
        self.assertEquals(response.status_code, 404)


class NewInvitationTest(TestUserMixIn, TestCase):
    def setUp(self):
        self.create_users()
        self.client = Client()

    def test_create_new_invitation_link(self):
        self.client.force_login(User.objects.get_or_create(username='pbrlionocde')[0])
        response = self.client.post(reverse('create_new_invitation'))
        self.assertRedirects(response, reverse('invitation_link', kwargs={'pk':1}), 302)
        object = self.client.get(reverse('invitation_link', kwargs={'pk':1})).context['object']
        self.assertEquals(object.inviting_user, self.user1)
        self.client.force_login(User.objects.get_or_create(username='prince_blood')[0])
        self.client.post(reverse('confirm'), {'key': object.key})
        test_user = User.objects.get(username='pbrlionocde')
        friend = test_user.friends.all()
        self.assertEquals(friend[0], self.user2)

    def test_create_new_invitation_link_anonymous(self):
        response = self.client.post(reverse('create_new_invitation'))
        self.assertRedirects(response, reverse('login')+'?next=/friends/create_new_invitation/', 302)
        response = self.client.get(reverse('invitation_link', kwargs={'pk':1}))
        self.assertRedirects(response, reverse('login')+'?next=/friends/new_invitation/1', 302)


class DownloadCsvTest(TestCase):
    def test_download_csv_anonymous(self):
        self.client = Client()
        response = self.client.get(reverse('download'))
        self.assertRedirects(response, reverse('login')+'?next=/downloadcsv/')

    def test_download_csv(self):
        self.client.force_login(User.objects.get_or_create(username='pbrlionocde')[0])
        response = self.client.get(reverse('download'))
        self.assertContains(response, b'date of creation,text note,date of end\r\n')
