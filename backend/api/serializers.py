import base64
import uuid

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.transaction import atomic
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Favorite, Ingredient, IngredientRecipes, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator
from users.models import Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Сериализатор для поля image."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            img_format, img_str = data.split(";base64,")
            ext = img_format.split("/")[-1]
            if ext.lower() not in ("jpeg", "jpg", "png"):
                raise serializers.ValidationError(
                    "Формат изображения не поддерживается. \
                    Используйте форматы JPEG или PNG."
                )

            uid = uuid.uuid4()
            data = ContentFile(base64.b64decode(img_str),
                               name=uid.urn[9:] + "." + ext)

        return super(Base64ImageField, self).to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField(
        method_name="get_is_subscribed")

    class Meta:
        model = User
        fields = ("email", "id", "username",
                  "first_name", "last_name", "is_subscribed")

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user is None or user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для модели User. Создание."""

    class Meta:
        model = User
        fields = ("email", "id", "username",
                  "first_name", "last_name", "password")

    def validate(self, data):
        if data.get("username") == "me":
            raise serializers.ValidationError("Нельзя использовать имя me")
        if User.objects.filter(username=data.get("username")):
            raise serializers.ValidationError(
                "Пользователь с таким именем уже существует"
            )
        if User.objects.filter(email=data.get("email")):
            raise serializers.ValidationError("Эта почта уже зарегистрироана")
        return data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор компактного отображения рецептов."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionSerializer(ModelSerializer):
    """Сериализатор для модели Subscription."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            "recipes", "recipes_count")

    def get_recipes(self, obj):
        recipes = obj.recipes.all()[:3]
        request = self.context.get("request")
        return RecipeShortSerializer(
            recipes, many=True, context={"request": request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        fields = "__all__"
        model = Ingredient
        read_only_fields = ("__all__",)


class IngredientRecipesSerializer(ModelSerializer):
    """
    Сериалайзер для модели IngredientRecipes.
    """

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit")

    class Meta:
        model = IngredientRecipes
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для модели Recipe.
    Используется на отображение необходимых полей при чтеннии.
    """

    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipesSerializer(
        many=True,
        source="amount_ingredients",
        read_only=True,
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "image",
            "name",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_is_favorited(self, object):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return request.user.favoriting.filter(recipe=object).exists()

    def get_is_in_shopping_cart(self, object):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return request.user.shopping_cart.filter(recipe=object).exists()


class RecipteIngredientCreateSerializer(ModelSerializer):
    """
    Сериалайзер для модели Recipe.
    Используется на отображение необходимых полей при чтеннии.
    """

    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientRecipes
        fields = ("id", "amount")


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Recipe.
    Используется для записи рецепта.
    """

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = RecipteIngredientCreateSerializer(
        many=True,
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "tags",
            "ingredients",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredients, status = IngredientRecipes.objects.get_or_create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient["id"]),
                amount=ingredient["amount"],
            )

    @atomic
    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        instance = super(RecipeCreateSerializer,
                         self).update(instance, validated_data)
        instance.tags.set(tags)
        self.create_ingredients(recipe=instance, ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context={"request": self.context.get("request")}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели Favorite."""

    class Meta:
        model = Favorite
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "recipe"),
                message="Вы уже добавили это рецепт в избранное.",
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор модели ShoppingCart."""

    class Meta:
        model = ShoppingCart
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=("user", "recipe"),
                message="Вы уже добавили это рецепт в список покупок.",
            )
        ]
