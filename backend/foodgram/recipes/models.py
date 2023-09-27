from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

User = get_user_model()

class Tag(models.Model):
    """ Модель Тэг."""

    name = models.CharField(verbose_name='Название',
                            max_length=200)
    color = models.CharField(verbose_name='Цвет',
                             max_length=7)
    slug = models.CharField(verbose_name='Уникальный слаг',
                            max_length=200,
                            unique=True)


class Ingridient(models.Model):
    """ Модель Ингридиента."""

    name = models.CharField(
        max_length=200,
        verbose_name='Hазвание',
    )
    measurement_unit = models.CharField(
        max_length=10,
        verbose_name='единица измерения'
    )


class Recipe(models.Model):
    """ Модель Рецепта."""

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги'
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    ingridients = models.ManyToManyField(
        Ingridient,
        related_name='recipes',
        verbose_name='Ингридиенты',
        through='IngredientRecipes',
    )
    name = models.CharField('Название',
                            max_length=200)
    image = models.ImageField(
         verbose_name= 'изображение',
         upload_to='rescipes/',
    )
    text = models.TextField(verbose_name='описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name = 'время приготовления, в мин',
        validators=(MinValueValidator(
            limit_value=1,
            message='Время приготовления не может быть менее одной минуты.'),
        )
    )

class IngredientRecipes(models.Model):
    ''' Промежуточная модель для связи ингридиента и рецепта.'''
    ingredient = models.ForeignKey(
        Ingridient,
        on_delete=models.CASCADE,
        related_name='ingredientrecipe',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(Recipe, 
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator
                    (1, 'Количество должно быть равно хотя бы одному')]
    )