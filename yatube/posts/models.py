from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField("Title of group", max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True, null=True, related_name="posts")

    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text

    def get_name_image(self):
        return self.image.name.split('/')[1].split('_')[0]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField()
    created = models.DateTimeField("date published", auto_now_add=True)

    class Meta:
        ordering = ["-created"]


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,
                             blank=True, null=True, default=User,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.SET_NULL,
                               blank=True, null=True, related_name="following")
