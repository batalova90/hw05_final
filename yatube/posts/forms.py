from django.forms import ModelForm, Textarea

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {'text': 'Текст поста',
                  'group': 'Группа',
                  'image': 'Изображение', }
        help_texts = {'text': 'Введите текст поста',
                      'group': 'Выберите группу'}


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': 'Текст комментария', }
        widget = {'text': Textarea(attrs={'class': 'form-control'}), }
