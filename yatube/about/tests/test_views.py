from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_views(self):
        templates_name = {'about:author': 'about/author.html',
                          'about:tech': 'about/tech.html'}
        for url_name, template_name in templates_name.items():
            with self.subTest(url_name=url_name):
                response = self.guest_client.get(reverse(url_name))
                self.assertTemplateUsed(response, template_name)
