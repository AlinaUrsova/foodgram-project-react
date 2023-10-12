from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

MAX_LENGTH_150 = 150
MAX_LENGTH_254 = 254


class User(AbstractUser):
    """Модель юзера."""

    username = models.CharField(
        max_length=MAX_LENGTH_150,
        unique=True,
        validators=(
            RegexValidator(
                regex=r"^[\w.@+-]+\Z",
                message="Логин пользователя имеет некорректный формат!",
            ),
        ),
    )
    email = models.EmailField(
        verbose_name="E-mail", max_length=MAX_LENGTH_254, unique=True, blank=False
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=MAX_LENGTH_150, blank=False)
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=MAX_LENGTH_150,
        blank=False)
    password = models.CharField(
        verbose_name="Пароль",
        max_length=MAX_LENGTH_150,
        blank=False,
    )
    is_subscribed = models.BooleanField(
        default=False,
        verbose_name="Подписка на автора",
        help_text="Отметка о подписке на автора",
    )

    class Meta:
        verbose_name = 'Пользователь'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User, verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="following"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(fields=["author", "user"],
                                    name="unique_follower")
        ]

    def __str__(self):
        return f'{self.user} подписан на: {self.author}'
