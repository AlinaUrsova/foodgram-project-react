from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Модель юзера."""

    USER = "user"
    ADMIN = "admin"

    CHOICES_ROLE = ((USER, "Пользователь"), (ADMIN, "Администратор"))

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=(
            RegexValidator(
                regex=r"^[\w.@+-]+\Z",
                message="Логин пользователя имеет некорректный формат!",
            ),
        ),
    )
    email = models.EmailField(
        verbose_name="E-mail", max_length=254, unique=True, blank=False
    )
    first_name = models.CharField(verbose_name="Имя",
                                  max_length=150, blank=False)
    last_name = models.CharField(verbose_name="Фамилия",
                                 max_length=150, blank=False)
    password = models.CharField(
        verbose_name="Пароль",
        max_length=150,
        blank=False,
    )
    is_subscribed = models.BooleanField(
        default=False,
        verbose_name="Подписка на автора",
        help_text="Отметка о подписке на автора",
    )


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
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_follower')
        ]
