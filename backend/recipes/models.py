from django.db import models
from django.core.validators import MinValueValidator

from users.models import User


class Tag(models.Model):
    """Модель Тэг."""

    name = models.CharField(verbose_name="Название", max_length=200)
    color = models.CharField(verbose_name="Цвет", max_length=7)
    slug = models.CharField(verbose_name="Уникальный слаг", max_length=200, unique=True)


class Ingredient(models.Model):
    """Модель Ингридиента."""

    name = models.CharField(
        max_length=200,
        verbose_name="Hазвание",
    )
    measurement_unit = models.CharField(max_length=10, verbose_name="единица измерения")


class Recipe(models.Model):
    """Модель Рецепта."""

    tags = models.ManyToManyField(Tag, related_name="recipes", verbose_name="Тэги")
    author = models.ForeignKey(
        User,
        related_name="recipes",
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        verbose_name="Ингридиенты",
        through="IngredientRecipes",
    )
    name = models.CharField("Название", max_length=200)
    image = models.ImageField(
        verbose_name="изображение",
        upload_to="recipes/",
    )
    text = models.TextField(verbose_name="описание")
    cooking_time = models.PositiveIntegerField(
        verbose_name="время приготовления, в мин",
        validators=(
            MinValueValidator(
                limit_value=1,
                message="Время приготовления не может быть менее одной минуты.",
            ),
        ),
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self) -> str:
        return f"{self.name}. Автор: {self.author.username}"

    def clean(self) -> None:
        self.name = self.name.capitalize()
        return super().clean()

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)


class IngredientRecipes(models.Model):
    """Промежуточная модель для связи ингридиента и рецепта."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient",
        verbose_name="Ингредиент",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="amount_ingredients",
        verbose_name="Рецепт",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество",
        validators=[
            MinValueValidator(1, "Количество должно быть равно хотя бы одному")
        ],
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("id",)
        unique_together = ("recipe", "ingredient")


class Favorite(models.Model):
    """Модель для избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favoriting",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favoriting",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        ordering = ("id",)
        constraints = (
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favorite_recipe"
            ),
        )

    def __str__(self):
        return f"{self.user} добавил в избранное {self.recipe}!"


class ShoppingCart(models.Model):
    """Класс составления списка покупок."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Рецепт",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
    )

    class Meta:
        verbose_name = "Рецепт пользователя для списка покупок"
        verbose_name_plural = "Рецепты пользователей для списка покупок"
        ordering = ("user",)
        constraints = (
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_cart"
            ),
        )

    def __str__(self):
        return f"{self.recipe} в списке покупок у {self.user}"