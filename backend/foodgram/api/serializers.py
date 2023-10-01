import base64
import uuid

from typing import Dict, List
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.core.files.base import ContentFile
from rest_framework.fields import IntegerField, SerializerMethodField
from django.db import transaction
from django.core.exceptions import ValidationError

from recipes.models import Tag, IngredientRecipes, Ingredient, Recipe
from users.models import Subscription

User = get_user_model()

class Base64ImageField(serializers.ImageField):
    """Serializer поля image"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            img_format, img_str = data.split(';base64,')
            ext = img_format.split('/')[-1]
            if ext.lower() not in ('jpeg', 'jpg', 'png'):
                raise serializers.ValidationError(
                    'Формат изображения не поддерживается. \
                    Используйте форматы JPEG или PNG.')

            uid = uuid.uuid4()
            data = ContentFile(
                base64.b64decode(img_str), name=uid.urn[9:] + '.' + ext
            )

        return super(Base64ImageField, self).to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    """Сериализатор для модели User."""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user is None or user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user,
            author=obj
        ).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания объекта класса User."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def validate(self, data):
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Использовать имя me запрещено'
            )
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует'
            )
        if User.objects.filter(email=data.get('email')):
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return data


class TagSerializer(ModelSerializer):
    """ Сериализатор для модели Тэг."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор для получения данных из модели с ингрединтами."""

    class Meta:
        fields = '__all__'
        model = Ingredient
        read_only_fields = '__all__',


class IngredientRecipesSerializer(ModelSerializer):
    '''
    Сериалайзер для модели IngredientRecipes.
    Используется для коректного отображения полей ингредиента при чтении.
    '''
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipes
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipteIngredientCreateSerializer(ModelSerializer):

    id = IntegerField(write_only=True)
    amount = IntegerField(write_only=True)


    class Meta:
        model = IngredientRecipes
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    '''
    Сериалайзер для модели Recipe.
    Используется на отображение необходимых полей при чтеннии.
    '''
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipesSerializer(
        many=True, source='amount_ingredients'
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для модели Recipe.
    Используется для записи рецепта.
    '''
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipteIngredientCreateSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'tags',
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        if not tags or not ingredients:
            raise ValidationError(
                'Минимум: 1 ингредиент и 1 тег'
            )
        ingredient_id = [ingredient['id'] for ingredient in ingredients]
        if len(ingredient_id) != len(set(ingredient_id)):
            raise ValidationError(
                'Ингредиенты не должны повторться в рецепте'
            )
        data.update(
            {
                'tags': tags,
                'ingredients': ingredients,
            }
        )
        return data

    def add_tags_ingredients(self, tags, ingredients, recipe):
        for tag in tags:
            recipe.tags.add(tag)
            recipe.save()
        for ingredient in ingredients:
            IngredientRecipes.objects.create(
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
                recipe=recipe
            )
        return recipe

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        return self.add_tags_ingredients(
            tags,
            ingredients,
            recipe,
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)