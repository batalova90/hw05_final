from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostsCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(title='testGroup',
                                         slug='test',
                                         description='Model testing croup', )
        cls.form = PostForm()
        test_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                    b'\x01\x00\x80\x00\x00\x00\x00\x00'
                    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                    b'\x0A\x00\x3B')
        cls.uploaded = SimpleUploadedFile(name='test.gif',
                                          content=test_gif,
                                          content_type='image/gif')

    def setUp(self):
        self.user = User.objects.create_user(username='Anastasiya')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_test = Post.objects.create(text='post text before editing',
                                             author=self.user,
                                             group=self.group)

    def test_create_post_from_form(self):
        """Cоздание поста через форму."""
        post_count = Post.objects.count()
        form = {'text': 'test form new_post',
                'group': self.group.id,
                'image': self.uploaded, }
        response = self.authorized_client.post(reverse('new_post'),
                                               data=form,
                                               follow=True)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(Post.objects.first().text, form['text'])
        self.assertEqual(Post.objects.first().author.username,
                         self.user.username)
        self.assertTrue(Post.objects.first().image)

    def test_post_create_guest(self):
        post_count = Post.objects.count()
        guest_client = Client()
        form = {'text': self.post_test.text,
                'group': self.group.id,
                'image': self.uploaded}
        response = guest_client.post(reverse('new_post'),
                                     data=form,
                                     follow=True)
        log_in = reverse('login') + '?next=' + reverse('new_post')
        self.assertRedirects(response, log_in)
        self.assertEqual(Post.objects.count(), post_count)

    def test_post_edit_from_form(self):
        post_count = Post.objects.count()
        text_after_edit = 'post text after editing'
        form = {'text': text_after_edit,
                'group': self.group.id, }
        parameters = {'username': self.post_test.author.username,
                      'post_id': self.post_test.id, }
        response = self.authorized_client.post(reverse('post_edit',
                                                       kwargs=parameters),
                                               data=form,
                                               follow=True)
        self.post_test.refresh_from_db()
        self.assertRedirects(response, reverse('post', kwargs=parameters))
        # проверка, что текст в посте изменился
        self.assertEqual(self.post_test.text, text_after_edit)
        self.assertEqual(Post.objects.count(), post_count)

    def return_404(self):
        response = self.guest_client.get('/check_return_404/')
        self.Equal(response.status_code, 404)
