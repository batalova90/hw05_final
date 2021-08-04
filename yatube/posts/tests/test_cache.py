from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from yatube.settings import CACHES

User = get_user_model()


class cacheTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.group = Group.objects.create(title='test cache group',
                                          slug='test',
                                          description='cache group')
        self.guest = Client()

    def test_cache_index(self):
        response = self.guest.get(reverse('index'))
        post_not_in_cache = Post.objects.create(text='test_post_cache',
                                                author=self.user,
                                                group=self.group)
        self.assertTrue(Post.objects.filter(id=post_not_in_cache.id).exists())
        self.assertEqual(len(response.context["page"].object_list),
                         Post.objects.count() - 1)
        CACHES.clear()
        response = self.guest.get(reverse('index'))
        self.assertEqual(len(response.context["page"].object_list),
                         Post.objects.count())
