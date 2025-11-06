from django import forms
from django.contrib.auth import get_user_model
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'location', 'pub_date', 'category', 'image']
        labels = {
            'title': 'Заголовок',
            'text': 'Текст публикации',
            'location': 'Местоположение',
            'pub_date': 'Дата публикации',
            'category': 'Категория',
            'image': 'Изображение для поста'
        }
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name', 'username']
        labels = {
            'email': 'Эл. почта',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Логин'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария'
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3})
        }
