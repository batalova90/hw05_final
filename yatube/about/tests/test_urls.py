from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_url_exists(self):
        """Проверка доступности /author/."""
        urls = ['/about/author/', '/about/tech/']
        for url_name in urls:
            with self.subTest(url_name=url_name):
                response = self.guest_client.get(url_name)
                self.assertEqual(response.status_code, 200)
