from django.test import TestCase
from posts.models import Group, Post, User


class TestModelStr(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='batalova.av')
        cls.group = Group.objects.create(title='testGroup',
                                         slug='test',
                                         description='Model testing croup')
        cls.post = Post.objects.create(text='t' * 15,
                                       author=cls.author,
                                       group=cls.group)

    def test_method_str(self):
        group = TestModelStr.group
        post = TestModelStr.post
        expected_post_text = 't' * 15
        expected_group_title = 'testGroup'
        self.assertEqual(expected_post_text, str(post))
        self.assertEqual(expected_group_title, str(group))
