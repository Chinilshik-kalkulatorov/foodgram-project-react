from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q

MAX_LEN = 150
USER_HELP = ('Обязательно для заполнения. '
             f'Максимум {MAX_LEN} .')


class User(AbstractUser):
    username = models.CharField('Уникальный юзернейм',
                                max_length=MAX_LEN,
                                blank=False,
                                unique=True,
                                help_text=USER_HELP)
    password = models.CharField('Пароль',
                                max_length=MAX_LEN,
                                blank=False,
                                help_text=USER_HELP)
    email = models.CharField(max_length=254,
                             blank=False,
                             verbose_name='Адрес электронной почты',
                             help_text='Обязательно для заполнения')
    first_name = models.CharField('Имя',
                                  max_length=MAX_LEN,
                                  blank=False,
                                  help_text=USER_HELP)
    last_name = models.CharField('Фамилия',
                                 max_length=MAX_LEN,
                                 blank=False,
                                 help_text=USER_HELP)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}: {self.first_name}'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписка'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique follow'
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.author}'