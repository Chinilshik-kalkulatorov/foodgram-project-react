from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q

MAX_LEN_FIELD = 150
USER_HELP = ('Обязательно для заполнения. '
             f'Максимум {MAX_LEN_FIELD} букв.')


class User(AbstractUser):
    """Модель для пользователей."""
    username = models.CharField('Уникальный юзернейм',
                                max_length=MAX_LEN_FIELD,
                                blank=False,
                                unique=True,
                                help_text=USER_HELP)
    password = models.CharField('Пароль',
                                max_length=MAX_LEN_FIELD,
                                blank=False,
                                help_text=USER_HELP)
    email = models.CharField(max_length=254,
                             blank=False,
                             verbose_name='Адрес электронной почты',
                             help_text='Обязательно для заполнения')
    first_name = models.CharField('Имя',
                                  max_length=MAX_LEN_FIELD,
                                  blank=False,
                                  help_text=USER_HELP)
    last_name = models.CharField('Фамилия',
                                 max_length=MAX_LEN_FIELD,
                                 blank=False,
                                 help_text=USER_HELP)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}: {self.first_name}'


class Follow(models.Model):
    """Модель для подписчиков."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='Вы уже подписаны на данного автора'),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='Нельзя подписаться на себя')
        ]
        ordering = ['-id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        def __str__(self):
            return f'{self.user} подписался на {self.author}'
