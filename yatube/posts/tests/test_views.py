from django import forms
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username='test')
        cls.test_group = Group.objects.create(title='testGroup',
                                              slug='test',
                                              description='group for testing')
        test_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                    b'\x01\x00\x80\x00\x00\x00\x00\x00'
                    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                    b'\x0A\x00\x3B')
        cls.uploaded = SimpleUploadedFile(name='test.gif',
                                          content=test_gif,
                                          content_type="image/gif")
        cls.test_username = 'Anastasiya'

    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username=self.test_username)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_follower = User.objects.create_user(username='follower')
        self.authorized_client_follower = Client()
        self.authorized_client_follower.force_login(self.user_follower)
        # посты для тестирования паджинатора
        for i in range(15):
            Post.objects.create(text='i' * 20,
                                author=self.test_user,
                                group=self.test_group,
                                image=self.uploaded)

        # Проверяем используемые шаблоны
    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: name"
        templates_pages_names = {
            'posts/index.html': reverse('index'),
            'posts/new.html': reverse('new_post'),
            'posts/group.html': reverse('group_posts',
                                        kwargs={'slug': 'test'}),
        }
        # Проверяем, что при обращении к name вызывается
        # соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

        # context
    def correct_show_of_posts(self, response):
        for post in response.context['page']:
            self.assertEqual(post.author.username, 'test')
            self.assertEqual(post.text, 'i' * 20)
            self.assertTrue(post.image)

    def test_home_page_shows_correct_context(self):
        """Шаблон домашней страницы сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        self.correct_show_of_posts(response)

        # group
    def test_group_page_shows_context(self):
        """Шаблон group_page сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('group_posts',
                                                      kwargs={'slug': 'test'}))
        self.correct_show_of_posts(response)

    # new_post
    def test_new_post_correct_type_data(self):
        """Форма new_post имеет ожидаемые типы данных."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {'text': forms.fields.CharField,
                       'group': forms.models.ModelChoiceField,
                       'image': forms.ImageField}
        for value, expected in form_fields.items():
            form_field = response.context['form'].fields[value]
            self.assertIsInstance(form_field, expected)

    def test_new_post_shows_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        object_operation = response.context['operation']
        object_add_or_save = response.context['add_or_save']
        self.assertEqual(object_operation, 'Добавить запись')
        self.assertEqual(object_add_or_save, 'Добавить')

    def test_profile_shows_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        post_test = Post.objects.create(text='test post_edit and post_view',
                                        author=self.user,
                                        group=self.test_group,
                                        image=self.uploaded)
        parameter = {'username': self.test_username}
        response = self.authorized_client.get(reverse('profile',
                                                      kwargs=parameter))
        context_profile = {'author': post_test.author,
                           'count': self.user.posts.count}
        self.assertEqual(response.context['author'], context_profile['author'])
        self.assertEqual(response.context['count'], context_profile['count'])
        post_image = response.context['page'][0]
        self.assertTrue(post_image.image)

    def test_post_edit_shows_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        post_test = Post.objects.create(text='test post edit',
                                        author=self.user,
                                        group=self.test_group)
        parameters = {'username': self.test_username, 'post_id': post_test.id}
        response = self.authorized_client.get(reverse('post_edit',
                                              kwargs=parameters))
        context_post_edit = {'operation': 'Редактировать запись',
                             'add_or_save': 'Сохранить',
                             'post': post_test}
        for context in context_post_edit:
            self.assertEqual(response.context[context],
                             context_post_edit[context])

    def test_post_view_shows_context(self):
        """Шаблон post_view сформирован с правильным контекстом"""
        post_test = Post.objects.create(text='test post_view',
                                        author=self.user,
                                        group=self.test_group,
                                        image=self.uploaded)
        parameters = {'username': self.test_username,
                      'post_id': post_test.id}
        response = self.authorized_client.get(reverse('post',
                                              kwargs=parameters))
        context_post_view = {'author': self.user, 'post': post_test,
                             'count': self.user.posts.count}
        for context in context_post_view:
            self.assertEqual(response.context[context],
                             context_post_view[context])
        # image
        post_image = response.context['post']
        self.assertTrue(post_image.image)

    # paginator
    def test_paginator_contains_ten_records(self):
        """Кол-во постов на первой странице"""
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context['page'].object_list), 10)

    def test_paginator_last_page(self):
        """Кол-во постов на последней странице"""
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context['page'].object_list), 5)

    def test_create_post_index(self):
        """Созданный пост отображается на главной странице"""
        post = Post.objects.create(text='i' * 20,
                                   author=self.test_user,
                                   group=self.test_group)
        response = self.client.get(reverse('index'))
        post_first_on_page = response.context['page'].object_list[0].id
        self.assertEqual(post.id, post_first_on_page)

    def test_create_post_group(self):
        """Созданный пост отображается на странице группы"""
        post = Post.objects.create(text='i' * 20,
                                   author=self.test_user,
                                   group=self.test_group)
        response = self.client.get(reverse('group_posts',
                                           kwargs={'slug': 'test'}))
        post_first_on_page_group = response.context['page'].object_list[0].id
        self.assertEqual(post.id, post_first_on_page_group)

    def authorized_follow(self):
        """Авторизованный клиент может подписываться на автора"""
        parameter = {'username': self.test_user}
        profile = reverse('profile_follow')
        count = self.authorized_client.following.count()
        response = self.authorized_client_follower.get(profile,
                                                       kwargs=parameter)
        self.assertEqual(self.authorized_client.following.count(), count + 1)
        self.assertEqual(response.status_code, 200)
        response = self.authorized_client_follower.get(profile,
                                                       kwargs=parameter)
        self.assertEqual(self.authorized_client.following.count(), count + 1)

    def authorized_following_show(self):
        """Просмотр подписок"""
        response = self.authorized_client_follower.get(reverse('follower'))
        self.correct_show_of_post(response)

    def new_post_show_follower(self):
        """Новый пост отображается у подписанных пользователей"""
        new_post_following = Post.objects.create(text='i' * 20,
                                                 author=self.test_user,
                                                 group=self.test_group,
                                                 image=self.uploaded)
        response = self.authorized_client_follower.get(reverse('follower'))
        self.assertEqual(response.context['page'][0], new_post_following)

    def authorized_unfollow(self):
        """Авторизованный клиент может отписываться от автора"""
        parameter = {'username': self.test_username, }
        unfollow = 'profile_unfollow'
        response = self.authorized_client_follower.get(reverse(unfollow),
                                                       kwargs=parameter)
        self.assertEqual(response.status_code, 200)

    def authorized_unfollow_model(self):
        """Посты авторов не отображаются у авторизованного пользователя,"""
        """если он на них не подписан"""
        user = self.user_follower
        test = self.test_username
        self.assertFalse(Follow.objects.filter(user__username=user,
                                               author__username=test).exists())

    def post_add_comment(self):
        """Авторизованный пользователь может комментировать посты"""
        commentator = User.objects.create_user(username='Commentator')
        authorized_commentator = Client()
        authorized_commentator.force_login(commentator)
        new_comment = Comment.object.create(post=Post.objects.first(),
                                            author=commentator,
                                            text='authorized commentator')
        self.assertTrue(Comment.objects.get(id=new_comment.id).exists())

    def test_follow_yourself(self):
        parameter = {'username': self.test_username}
        response = self.authorized_client.get(reverse('profile_follow',
                                                      kwargs=parameter))
        self.assertRedirects(response, reverse('follow_index'))
