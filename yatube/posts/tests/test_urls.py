from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем тестовую группу
        cls.slug_test = Group.objects.create(title='test_slug',
                                             slug='test',
                                             description='group page')
        cls.test_user = 'Anastasiya'

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username=self.test_user)
        # Второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        # Создаем пост
        self.test_post = Post.objects.create(text='test post',
                                             author=self.user,
                                             group=self.slug_test)
        self.parameters = {'username': self.test_user,
                           'post_id': self.test_post.id}
        self.test_urls = {'home': '/',
                          'group': ('/group/' + self.slug_test.slug + '/'),
                          'new': '/new/',
                          'authorized_page': '/auth/login/?next=/new/',
                          'profile': ('/' + self.test_user + '/'), }

    # Проверяем общедоступные страницы
    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get(self.test_urls['home'])
        self.assertEqual(response.status_code, 200)

    def test_group_post_availability(self):
        """Страница /group/<slug> доступна любому пользователю."""
        response = self.guest_client.get(self.test_urls['group'])
        self.assertEqual(response.status_code, 200)

    # Проверяем, что new доступна авторизованному пользователю
    def test_new_page_available_auhtorized_user(self):
        """Страница /new/ доступна авторизавонному пользователю"""
        response = self.authorized_client.get(self.test_urls['new'])
        self.assertEqual(response.status_code, 200)

    # Проверяем redirect для неавторизованного пользователя для new
    def test_redirect_new_anonymous(self):
        """Страница /new/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get(self.test_urls['new'], follow=True)
        self.assertRedirects(response, self.test_urls['authorized_page'])

    # Проверка шаблонов
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': self.test_urls['home'],
            'posts/group.html': self.test_urls['group'],
            'posts/new.html': self.test_urls['new'], }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    # Проверяем, что доступен профайл пользователя
    def test_urls_profile(self):
        response = self.guest_client.get(self.test_urls['profile'])
        self.assertEqual(response.status_code, 200)

    # Проверяем, что доступен пост пользователя
    def test_urls_profile_post(self):
        response = self.guest_client.get(reverse('post',
                                                 kwargs=self.parameters))
        self.assertEqual(response.status_code, 200)

    # Доступность страницы редактирования поста
    def edit_post(self, user):
        return user.get(reverse('post_edit', kwargs=self.parameters))

    # Анонимного пользователя
    def test_urls_edit_post_guest_user(self):
        response = self.guest_client.get(reverse('post_edit',
                                                 kwargs=self.parameters),
                                         follow=True)
        log_in = reverse('login') + '?next=' + reverse('post_edit',
                                                       kwargs=self.parameters)
        self.assertRedirects(response, log_in)

    # Автор поста
    def test_urls_edit_post_author(self):
        response = self.edit_post(self.authorized_client)
        self.assertEqual(response.status_code, 200)

    # Авторизованный пользователь, не автор поста
    def test_urls_edit_post_not_author(self):
        user_not_author = User.objects.create_user(username='Not_author')
        authorized_client_not_author = Client()
        authorized_client_not_author.force_login(user_not_author)
        response = self.edit_post(authorized_client_not_author)
        self.assertRedirects(response, reverse('post',
                                               kwargs=self.parameters))

    # Шаблон страницы редактирования поста
    def test_urls_edit_post_templates(self):
        """post_edit использует правильный шаблон"""
        template_name = 'posts/new.html'
        response = self.edit_post(self.authorized_client)
        self.assertTemplateUsed(response, template_name)

    def test_redirect_add_comment_for_guest(self):
        """Комментирование неавторизованного пользователя"""
        parameters = {'username': self.user.username,
                      'post_id': self.test_post.id}
        response = self.guest_client.get(reverse('add_comment',
                                                 kwargs=parameters),
                                         follow=True)
        # проверяем redirect
        log_in = reverse('login') + '?next=' + reverse('add_comment',
                                                       kwargs=parameters)
        self.assertRedirects(response, log_in)
